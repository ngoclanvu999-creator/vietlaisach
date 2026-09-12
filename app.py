import os
import sys
import secrets
import hashlib
from pathlib import Path
from typing import Optional, List

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config import (
    BASE_DIR, INPUT_DIR, OUTPUT_DIR, TEMPLATES_DIR, STATIC_DIR,
    LOCAL_MODE, ACCESS_TOKEN, load_settings, save_settings
)
from core.parser import parse_input_file, scan_directory, lay_dau_hieu_tai_lieu
from core.doc_type import detect_document_type, trich_thong_tin_de_thi, TEN_HIEN_THI, DE_THI, SACH, CHUYEN_DE
from core.rewriter import process_rewrite_pipeline, create_master_book_from_chapters
from core.ai_namer import generate_creative_titles_gemini
from core.exporter import DocxBookExporter
from core.validator import PreFlightValidator
from core.question_forge import (
    sinh_va_tham_dinh, thong_ke_ngan_hang, doc_ngan_hang,
    xoa_khoi_ngan_hang, LoiHanMuc, CAP_DO, KHOI_LOP, MAX_PER_BATCH
)

app = FastAPI(title="Biên Soạn Sách Toán - Vật Lý Pro")


# ===========================================================================
# LỚP BẢO VỆ: LÀM SẠCH TÊN TỆP & GIỚI HẠN PHẠM VI TRUY CẬP Ổ ĐĨA
# ===========================================================================

_ASSET_VERSION_CACHE: dict = {}


def _asset_version() -> str:
    """
    Dấu vân theo NỘI DUNG của app.js + style.css, dùng làm số phiên bản chống lưu đệm.

    Băm nội dung chứ không băm thời gian sửa: `git checkout` hay sao chép tệp đều
    làm đổi mtime dù nội dung y nguyên, băm theo mtime sẽ bắt mọi trình duyệt tải
    lại tài nguyên một cách vô ích.
    """
    key = []
    for name in ("app.js", "style.css"):
        f = STATIC_DIR / name
        try:
            st = f.stat()
            key.append((name, st.st_mtime_ns, st.st_size))
        except OSError:
            key.append((name, 0, 0))
    cache_key = tuple(key)

    cached = _ASSET_VERSION_CACHE.get(cache_key)
    if cached:
        return cached

    h = hashlib.md5()
    for name in ("app.js", "style.css"):
        f = STATIC_DIR / name
        try:
            h.update(f.read_bytes())
        except OSError:
            h.update(f"{name}:missing".encode())

    version = h.hexdigest()[:10]
    _ASSET_VERSION_CACHE.clear()          # chỉ giữ đúng bản mới nhất
    _ASSET_VERSION_CACHE[cache_key] = version
    return version


def safe_filename(raw_name: str) -> str:
    """Chỉ giữ lại phần tên tệp, loại bỏ mọi thành phần đường dẫn (../, C:\\, ...)."""
    name = Path(str(raw_name or "").replace("\\", "/")).name
    name = name.replace("\x00", "").strip()
    # Loại bỏ các tên đặc biệt có thể thoát khỏi thư mục
    if not name or name in (".", ".."):
        raise HTTPException(status_code=400, detail="Tên tệp không hợp lệ")
    return name


def resolve_within(base_dir: Path, raw_name: str) -> Path:
    """Ghép tên tệp vào thư mục gốc và xác nhận kết quả KHÔNG thoát ra ngoài."""
    candidate = (base_dir / safe_filename(raw_name)).resolve()
    base_resolved = base_dir.resolve()
    if candidate != base_resolved and base_resolved not in candidate.parents:
        raise HTTPException(status_code=400, detail="Đường dẫn tệp không hợp lệ")
    return candidate


def resolve_subpath_within(base_dir: Path, raw_rel: str) -> Path:
    """
    Giống resolve_within nhưng CHO PHÉP đường dẫn nhiều cấp bên trong base_dir
    (ví dụ "ingest_1726/De_thi.docx"), vẫn chặn mọi mưu toan thoát ra ngoài.
    """
    rel = str(raw_rel or "").replace("\\", "/").strip().lstrip("/")
    if not rel or "\x00" in rel:
        raise HTTPException(status_code=400, detail="Đường dẫn tệp không hợp lệ")

    parts = [seg for seg in rel.split("/") if seg not in ("", ".")]
    if any(seg == ".." for seg in parts):
        raise HTTPException(status_code=400, detail="Đường dẫn tệp không hợp lệ")

    candidate = base_dir.joinpath(*parts).resolve()
    base_resolved = base_dir.resolve()
    if candidate != base_resolved and base_resolved not in candidate.parents:
        raise HTTPException(status_code=400, detail="Đường dẫn tệp không hợp lệ")
    return candidate


def resolve_user_folder(raw_path: str) -> Path:
    """
    Kiểm duyệt thư mục do người dùng nhập.
    - Chế độ Local (máy cá nhân): cho phép mọi thư mục trên ổ đĩa.
    - Chế độ Cloud: CHỈ cho phép các thư mục nằm bên trong input/ (nơi chứa
      tệp do chính người dùng tải lên), chặn hoàn toàn việc dò quét máy chủ.
    """
    p = Path(str(raw_path or "").strip().strip('"').strip("'"))
    try:
        resolved = p.resolve()
    except Exception:
        raise HTTPException(status_code=400, detail="Đường dẫn thư mục không hợp lệ")

    if not LOCAL_MODE:
        input_resolved = INPUT_DIR.resolve()
        if resolved != input_resolved and input_resolved not in resolved.parents:
            raise HTTPException(
                status_code=403,
                detail=(
                    "Chế độ Web/Cloud không cho phép truy cập thư mục trên máy chủ. "
                    "Vui lòng dùng chức năng Tải lên thư mục hoặc Tải lên file .ZIP."
                )
            )

    if not resolved.exists() or not resolved.is_dir():
        raise HTTPException(status_code=400, detail=f"Đường dẫn thư mục không tồn tại: {raw_path}")
    return resolved


@app.middleware("http")
async def access_token_guard(request, call_next):
    """Nếu người dùng đặt APP_ACCESS_TOKEN, mọi API đều phải kèm token hợp lệ."""
    if ACCESS_TOKEN and request.url.path.startswith("/api/") and request.url.path != "/api/health":
        supplied = request.headers.get("X-Access-Token") or request.query_params.get("token") or ""
        if not secrets.compare_digest(supplied, ACCESS_TOKEN):
            return JSONResponse(status_code=401, content={"detail": "Truy cập bị từ chối: thiếu hoặc sai mã truy cập."})
    return await call_next(request)

STATIC_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

SUPPORTED_UPLOAD_EXTENSIONS = {".docx", ".doc", ".xlsx", ".xls", ".pdf", ".png", ".jpg", ".jpeg"}

# Giữ tối đa bao nhiêu file thành phẩm trong output/ trước khi tự dọn file cũ nhất.
# Không có bước này thư mục output phình vô hạn; trên Render (đĩa tạm) còn gây đầy dung lượng.
MAX_OUTPUT_FILES = int(os.environ.get("MAX_OUTPUT_FILES", "200"))


def prune_output_dir(max_files: int = MAX_OUTPUT_FILES) -> int:
    """Xóa bớt các file thành phẩm cũ nhất, giữ lại max_files file mới nhất."""
    try:
        files = [f for f in OUTPUT_DIR.iterdir() if f.is_file() and f.suffix.lower() in (".docx", ".zip")]
    except Exception:
        return 0
    if len(files) <= max_files:
        return 0

    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    removed = 0
    for old in files[max_files:]:
        try:
            old.unlink()
            removed += 1
        except Exception:
            pass
    return removed

@app.get("/", response_class=HTMLResponse)
async def serve_home():
    """
    Trả về trang chủ kèm số phiên bản tài nguyên tính theo NỘI DUNG THẬT của
    app.js và style.css.

    Vì sao cần: trước đây index.html gắn cứng "?v=2.6". Khi mã JS đổi mà con số
    này không đổi, trình duyệt vẫn dùng bản JS cũ trong bộ nhớ đệm. JS cũ đi tìm
    những phần tử đã bị xóa khỏi HTML mới, ném TypeError và chết ngay dòng đầu —
    hậu quả là cả trang không bấm được gì. Tính version theo nội dung thì mỗi lần
    sửa mã là trình duyệt tự nạp bản mới, không cần nhớ tăng số thủ công.
    """
    index_file = TEMPLATES_DIR / "index.html"
    with open(index_file, "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("__ASSET_VERSION__", _asset_version())

    # Bản thân trang HTML không được lưu đệm, nếu không người dùng vẫn nhận
    # trang cũ trỏ tới số phiên bản cũ.
    return HTMLResponse(
        content=html,
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )

DEFAULT_MODEL = "gemini-3.6-flash"

# Các model người dùng được phép chọn. Chặn giá trị lạ để không ai lợi dụng
# trường này gọi sang endpoint khác.
ALLOWED_MODELS = {
    "gemini-3.6-flash",
    "gemini-3.6-pro",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.0-flash",
}


def request_credentials(request: Request) -> tuple:
    """
    Lấy khóa Gemini và model THEO TỪNG NGƯỜI DÙNG, gửi kèm mỗi yêu cầu qua header.

    Nguyên tắc: khóa là tài sản riêng của mỗi người, máy chủ không lưu và không
    dùng chung. Trên bản Web/Cloud, nếu người dùng chưa dán khóa thì coi như
    không có khóa — tuyệt đối KHÔNG mượn khóa của chủ máy chủ để chạy, vì như vậy
    là tiêu hạn mức của người khác.

    Riêng khi chạy trên máy cá nhân (LOCAL_MODE) thì vẫn cho phép lấy khóa đã lưu
    trong app_settings.json hoặc biến môi trường, vì đó chính là máy của bạn.
    """
    key = (request.headers.get("X-Gemini-Key") or "").strip()
    model = (request.headers.get("X-Gemini-Model") or "").strip()

    if not key and LOCAL_MODE:
        settings = load_settings()
        key = (settings.get("gemini_api_key") or "").strip()
        if not model:
            model = (settings.get("gemini_model") or "").strip()

    if model not in ALLOWED_MODELS:
        model = DEFAULT_MODEL

    return key, model


# Những tùy chọn KHÔNG phải bí mật, lưu chung trên máy chủ được.
# Khóa API cố tình không nằm trong danh sách này: nó là của riêng từng người.
PUBLIC_SETTING_KEYS = {
    "default_subject", "default_add_count", "default_rewrite_level",
    "enable_casio", "enable_traps", "enable_summary_box",
    "enable_dual_solutions", "output_format",
}


def _public_settings(settings: dict) -> dict:
    """Chỉ trả ra các tùy chọn công khai. Khóa API không bao giờ rời khỏi máy chủ."""
    out = {k: v for k, v in settings.items() if k in PUBLIC_SETTING_KEYS}
    out["local_mode"] = LOCAL_MODE
    out["allowed_models"] = sorted(ALLOWED_MODELS)
    out["default_model"] = DEFAULT_MODEL
    # Trên máy cá nhân, báo cho giao diện biết máy đã có sẵn khóa để dùng
    out["server_key_available"] = bool(
        LOCAL_MODE and (
            (load_settings().get("gemini_api_key") or "").strip()
            or os.environ.get("GEMINI_API_KEY", "").strip()
        )
    )
    return out


@app.get("/api/settings")
def get_settings():
    return _public_settings(load_settings())

@app.post("/api/settings")
def update_settings(settings: dict):
    # Khóa API bị loại bỏ khỏi mọi yêu cầu lưu: mỗi người tự giữ khóa của mình
    # trong trình duyệt, máy chủ không nhận và không lưu hộ.
    payload = {k: v for k, v in (settings or {}).items() if k in PUBLIC_SETTING_KEYS}
    saved = save_settings(payload)
    return {"status": "success", "settings": _public_settings(saved)}

class ScanFolderRequest(BaseModel):
    folder_path: str

@app.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "service": "Bien Soan Sach Pro",
        "version": "2.5",
        "web_deploy_ready": True,
        # Dấu vân của app.js + style.css đang chạy trên máy chủ này. Nhờ nó mà
        # biết chắc bản deploy đã lên hay máy chủ còn phục vụ mã cũ, thay vì
        # phải mở trang ra nhìn bằng mắt.
        "asset_version": _asset_version(),
        "local_mode": LOCAL_MODE,
        # Trang có đang khóa hay không. Giao diện dựa vào đây để hiện màn hình
        # nhập mã truy cập. Chỉ báo CÓ/KHÔNG, không hé lộ mã.
        "auth_required": bool(ACCESS_TOKEN)
    }


@app.post("/api/verify-access")
def verify_access():
    """
    Kiểm tra mã truy cập người dùng vừa nhập.

    Middleware đã chặn sẵn mọi /api/ khác, endpoint này chỉ để giao diện biết
    mã đúng hay sai mà báo lại cho người dùng. Nếu trang không khóa thì luôn
    trả hợp lệ.
    """
    return {"status": "success", "valid": True, "auth_required": bool(ACCESS_TOKEN)}

@app.post("/api/scan-folder")
def api_scan_folder(req: ScanFolderRequest):
    p = resolve_user_folder(req.folder_path)

    try:
        files = scan_directory(p)
        return {
            "status": "success",
            "folder_path": str(p),
            "total_files": len(files),
            "files": files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi quét thư mục: {str(e)}")

# ===========================================================================
# CỔNG NẠP LIỆU HỢP NHẤT
# Người dùng chỉ cần thả vào một chỗ duy nhất: tệp lẻ, nhiều tệp, cả thư mục
# hay file .zip đều được. Máy chủ tự phân loại, tự giải nén, tự bỏ qua tệp lạ
# rồi trả về một danh sách tài liệu thống nhất.
# ===========================================================================

MAX_INGEST_SESSIONS = int(os.environ.get("MAX_INGEST_SESSIONS", "20"))


def prune_ingest_dirs(max_sessions: int = MAX_INGEST_SESSIONS) -> int:
    """Xóa bớt các thư mục nạp liệu cũ, giữ lại max_sessions phiên gần nhất."""
    try:
        dirs = [d for d in INPUT_DIR.iterdir() if d.is_dir() and d.name.startswith("ingest_")]
    except Exception:
        return 0
    if len(dirs) <= max_sessions:
        return 0

    dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)
    removed = 0
    for old in dirs[max_sessions:]:
        try:
            shutil.rmtree(old, ignore_errors=True)
            removed += 1
        except Exception:
            pass
    return removed


def _unique_target(folder: Path, filename: str) -> Path:
    """Tránh ghi đè khi hai tệp trùng tên đến từ hai thư mục con khác nhau."""
    target = resolve_within(folder, filename)
    if not target.exists():
        return target
    stem, suffix = target.stem, target.suffix
    for i in range(2, 1000):
        candidate = resolve_within(folder, f"{stem}_{i}{suffix}")
        if not candidate.exists():
            return candidate
    raise HTTPException(status_code=400, detail="Quá nhiều tệp trùng tên")


def _extract_zip_into(zip_path: Path, dest: Path) -> int:
    """Giải nén an toàn: chặn Zip Slip, chặn Zip Bomb, chỉ lấy tệp hợp lệ."""
    import zipfile
    MAX_TOTAL_UNCOMPRESSED = 500 * 1024 * 1024  # 500 MB
    count = 0
    with zipfile.ZipFile(str(zip_path), "r") as z:
        if sum(max(0, i.file_size) for i in z.infolist()) > MAX_TOTAL_UNCOMPRESSED:
            raise HTTPException(
                status_code=400,
                detail="File nén sau khi giải nén vượt quá 500 MB, vui lòng chia nhỏ thư mục."
            )
        for info in z.infolist():
            if info.is_dir():
                continue
            member = Path(info.filename.replace("\\", "/")).name
            if not member or member.startswith("~$"):
                continue
            if Path(member).suffix.lower() not in SUPPORTED_UPLOAD_EXTENSIONS:
                continue
            target = _unique_target(dest, member)
            with z.open(info, "r") as src, open(target, "wb") as dst:
                shutil.copyfileobj(src, dst)
            count += 1
    return count


@app.post("/api/ingest")
def ingest_documents(
    request: Request,
    files: List[UploadFile] = File(...),
    subject: str = Form("toan")
):
    """
    Nhận mọi thứ người dùng thả vào: một tệp, nhiều tệp, cả cây thư mục hoặc
    file .zip (kể cả trộn lẫn nhau), rồi tự phân loại thành một danh sách
    tài liệu duy nhất để biên soạn.
    """
    if not files:
        raise HTTPException(status_code=400, detail="Không có tệp nào được chọn")

    import time
    session_dir = resolve_within(INPUT_DIR, f"ingest_{int(time.time() * 1000)}")
    session_dir.mkdir(parents=True, exist_ok=True)

    saved_docs = 0
    zip_count = 0
    extracted = 0
    skipped: List[str] = []

    for f in files:
        try:
            fname = safe_filename(f.filename)
        except HTTPException:
            continue

        ext = Path(fname).suffix.lower()
        if fname.startswith("~$"):
            continue

        if ext == ".zip":
            tmp_zip = _unique_target(session_dir, fname)
            with open(tmp_zip, "wb") as buf:
                shutil.copyfileobj(f.file, buf)
            try:
                extracted += _extract_zip_into(tmp_zip, session_dir)
                zip_count += 1
            except HTTPException:
                raise
            except Exception as e:
                skipped.append(f"{fname} (không giải nén được: {e})")
            finally:
                tmp_zip.unlink(missing_ok=True)

        elif ext in SUPPORTED_UPLOAD_EXTENSIONS:
            target = _unique_target(session_dir, fname)
            with open(target, "wb") as buf:
                shutil.copyfileobj(f.file, buf)
            saved_docs += 1

        else:
            skipped.append(fname)

    found = scan_directory(session_dir)
    if not found:
        shutil.rmtree(session_dir, ignore_errors=True)
        detail = "Không tìm thấy tài liệu hợp lệ (Word, Excel, PDF hoặc Ảnh) trong những gì bạn đã chọn."
        if skipped:
            detail += " Đã bỏ qua: " + ", ".join(skipped[:5])
        raise HTTPException(status_code=400, detail=detail)

    prune_ingest_dirs()

    # Gợi ý cách xử lý: đúng một tài liệu thì làm thành một cuốn sách,
    # nhiều tài liệu thì để người dùng chọn gộp chung hay tách riêng.
    kind = "single" if len(found) == 1 else "batch"

    # Với đúng một tài liệu, bóc tách luôn để người dùng xem trước ngay,
    # khỏi phải chờ thêm một vòng gọi nữa.
    preview: List[dict] = []
    total_items = 0
    single_rel = ""
    nhan_dien: dict = {}
    if kind == "single":
        only = Path(found[0]["path"])
        single_rel = f"{session_dir.name}/{only.name}"
        try:
            api_key, _ = request_credentials(request)
            parsed = parse_input_file(only, subject=subject, api_key=api_key)
            total_items = len(parsed)
            preview = [item.to_dict() for item in parsed[:15]]
            nhan_dien = detect_document_type(parsed, lay_dau_hieu_tai_lieu(), only.name)
        except Exception as e:
            print(f"Không xem trước được {only.name}: {e}")

    # Mô tả nguồn gốc để hiển thị lại cho người dùng biết hệ thống đã hiểu gì
    sources = []
    if saved_docs:
        sources.append(f"{saved_docs} tài liệu")
    if zip_count:
        sources.append(f"{zip_count} file nén (.zip) → {extracted} tài liệu")

    return {
        "status": "success",
        "kind": kind,
        "folder_path": str(session_dir),
        "relative_path": session_dir.name,
        "single_file_path": single_rel,
        "total_files": len(found),
        "files": found,
        "skipped": skipped,
        "total_items": total_items,
        "preview": preview,
        "nhan_dien": nhan_dien,
        "source_summary": " + ".join(sources) if sources else f"{len(found)} tài liệu"
    }


class SuggestTitlesRequest(BaseModel):
    filename: str = ""
    sample_text: str = ""
    subject: str = "toan"
    # Các tựa đã đề xuất lần trước — để nút "Đổi 5 tựa khác" cho ra phương án
    # thực sự mới chứ không lặp lại.
    exclude_titles: List[str] = []
    doc_type: str = ""

@app.post("/api/suggest-titles")
def api_suggest_titles(req: SuggestTitlesRequest, request: Request):
    api_key, model_name = request_credentials(request)

    titles = generate_creative_titles_gemini(
        sample_text=req.sample_text,
        filename=req.filename,
        subject=req.subject,
        api_key=api_key,
        model_name=model_name,
        exclude_titles=req.exclude_titles,
        doc_type=req.doc_type
    )
    return {
        "status": "success",
        "total": len(titles),
        "titles": titles
    }

@app.post("/api/upload")
def upload_file(
    request: Request,
    file: UploadFile = File(...),
    subject: str = Form("toan")
):
    clean_name = safe_filename(file.filename)
    ext = Path(clean_name).suffix.lower()
    allowed = [".docx", ".doc", ".xlsx", ".xls", ".pdf", ".png", ".jpg", ".jpeg"]
    if ext not in allowed:
        raise HTTPException(status_code=400, detail="Định dạng không được hỗ trợ. Vui lòng tải lên file: Word, Excel, PDF hoặc Ảnh.")

    save_path = resolve_within(INPUT_DIR, clean_name)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    api_key, _ = request_credentials(request)

    try:
        parsed_items = parse_input_file(save_path, subject=subject, api_key=api_key)
        preview = [item.to_dict() for item in parsed_items[:15]]
        return {
            "status": "success",
            "filename": clean_name,
            "total_items": len(parsed_items),
            "preview": preview
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi đọc file: {str(e)}")

@app.post("/api/upload-batch")
def upload_batch(
    files: List[UploadFile] = File(...),
    subject: str = Form("toan")
):
    """Tải lên nhiều tệp hoặc tải lên cả thư mục tài liệu từ trình duyệt Web (Web Folder Upload)"""
    if not files:
        raise HTTPException(status_code=400, detail="Không có tệp nào được chọn")

    batch_dir = INPUT_DIR / "web_upload_batch"
    batch_dir.mkdir(parents=True, exist_ok=True)

    saved_files = []
    allowed = {".docx", ".doc", ".xlsx", ".xls", ".pdf", ".png", ".jpg", ".jpeg"}

    for f in files:
        try:
            fname = safe_filename(f.filename)
        except HTTPException:
            continue
        ext = Path(fname).suffix.lower()
        if ext in allowed and not fname.startswith("~$"):
            save_p = resolve_within(batch_dir, fname)
            with open(save_p, "wb") as buf:
                shutil.copyfileobj(f.file, buf)
            try:
                size_kb = round(save_p.stat().st_size / 1024, 1)
            except Exception:
                size_kb = 0
            saved_files.append({
                "name": fname,
                "path": str(save_p),
                "ext": ext,
                "size_kb": size_kb
            })

    if not saved_files:
        raise HTTPException(status_code=400, detail="Không có tệp Word, Excel, PDF hoặc Ảnh nào hợp lệ")

    return {
        "status": "success",
        "folder_path": str(batch_dir),
        "total_files": len(saved_files),
        "files": saved_files
    }

@app.post("/api/upload-zip")
def upload_zip(
    zip_file: UploadFile = File(...),
    subject: str = Form("toan")
):
    """Tải lên file nén .zip chứa thư mục tài liệu từ bất kỳ máy tính/thiết bị nào lên web"""
    import zipfile
    clean_zip_name = safe_filename(zip_file.filename)
    if not clean_zip_name.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ tải lên file nén định dạng .zip")

    zip_path = resolve_within(INPUT_DIR, clean_zip_name)
    with open(zip_path, "wb") as buf:
        shutil.copyfileobj(zip_file.file, buf)

    extract_dir = resolve_within(INPUT_DIR, f"unzipped_{Path(clean_zip_name).stem}")
    extract_dir.mkdir(parents=True, exist_ok=True)

    # Giải nén an toàn: bỏ qua mọi entry có đường dẫn thoát ra ngoài thư mục đích
    # (lỗ hổng Zip Slip) và giới hạn tổng dung lượng sau giải nén (chống Zip Bomb).
    MAX_TOTAL_UNCOMPRESSED = 500 * 1024 * 1024  # 500 MB
    try:
        with zipfile.ZipFile(str(zip_path), "r") as z:
            total_size = sum(max(0, info.file_size) for info in z.infolist())
            if total_size > MAX_TOTAL_UNCOMPRESSED:
                raise HTTPException(
                    status_code=400,
                    detail="File nén sau khi giải nén vượt quá 500 MB, vui lòng chia nhỏ thư mục."
                )
            for info in z.infolist():
                if info.is_dir():
                    continue
                member_name = Path(info.filename.replace("\\", "/")).name
                if not member_name or member_name.startswith("~$"):
                    continue
                if Path(member_name).suffix.lower() not in SUPPORTED_UPLOAD_EXTENSIONS:
                    continue
                target = resolve_within(extract_dir, member_name)
                with z.open(info, "r") as src, open(target, "wb") as dst:
                    shutil.copyfileobj(src, dst)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Không thể giải nén file zip: {str(e)}")

    files = scan_directory(extract_dir)
    return {
        "status": "success",
        "folder_path": str(extract_dir),
        "total_files": len(files),
        "files": files
    }

def _bool_form(value: Optional[str], default: bool = True) -> bool:
    """Ô tick trên web gửi lên dạng chuỗi 'true'/'false'."""
    if value is None:
        return default
    return str(value).strip().lower() in ("1", "true", "yes", "on")


def book_options_from_form(
    theory: Optional[str], foreword: Optional[str], secrets_: Optional[str],
    stem: Optional[str], casio: Optional[str], traps: Optional[str]
) -> dict:
    """Gom các ô tick thành bộ tùy chọn cho bộ xuất bản."""
    return {
        "theory": _bool_form(theory),
        "foreword": _bool_form(foreword),
        "secrets": _bool_form(secrets_),
        "stem": _bool_form(stem),
        "casio": _bool_form(casio),
        "traps": _bool_form(traps),
    }


@app.post("/api/process")
def process_single_document(
    request: Request,
    filename: str = Form(...),
    subject: str = Form("toan"),
    add_count: int = Form(2),
    custom_title: Optional[str] = Form(None),
    doc_type: Optional[str] = Form(None),
    include_theory: Optional[str] = Form(None),
    include_foreword: Optional[str] = Form(None),
    include_secrets: Optional[str] = Form(None),
    include_stem: Optional[str] = Form(None),
    include_casio: Optional[str] = Form(None),
    include_traps: Optional[str] = Form(None)
):
    book_options = book_options_from_form(
        include_theory, include_foreword, include_secrets,
        include_stem, include_casio, include_traps
    )
    # Chấp nhận cả tên tệp trực tiếp trong input/ lẫn đường dẫn nhiều cấp bên
    # trong thư mục phiên nạp liệu (ví dụ "ingest_1726.../De_thi.docx").
    input_path = resolve_subpath_within(INPUT_DIR, filename)
    if not input_path.exists() or not input_path.is_file():
        raise HTTPException(status_code=404, detail="Không tìm thấy file nguồn đã tải lên")

    settings = load_settings()
    api_key, model_name = request_credentials(request)
    paper_format = settings.get("output_format", "a4")

    try:
        # 1. Bóc tách
        questions = parse_input_file(input_path, subject=subject, api_key=api_key)
        if not questions:
            raise HTTPException(status_code=400, detail="Không trích xuất được bài toán nào từ file này")

        # 1b. Nhận diện loại tài liệu để xuất ra đúng dạng tương ứng.
        # Người dùng chọn tay thì tôn trọng lựa chọn của họ.
        dau_hieu = lay_dau_hieu_tai_lieu()
        nhan_dien = detect_document_type(questions, dau_hieu, input_path.name)
        loai = doc_type if doc_type in (DE_THI, SACH, CHUYEN_DE) else nhan_dien["doc_type"]
        thong_tin_de = trich_thong_tin_de_thi(dau_hieu) if loai == DE_THI else {}

        # 2. Tái cấu trúc & Bổ sung lý thuyết chuẩn BGD
        book = process_rewrite_pipeline(
            questions=questions,
            subject=subject,
            add_count=int(add_count),
            api_key=api_key,
            model_name=model_name,
            doc_type=loai,
            exam_info=thong_tin_de
        )

        if custom_title and custom_title.strip():
            book.new_title = custom_title.strip()

        # 3. Xuất Word chuẩn Nghị định 30
        stem = input_path.stem
        clean_title_slug = "".join(c for c in book.new_title[:30] if c.isalnum() or c in (" ", "-", "_")).strip().replace(" ", "_")
        out_filename = f"Sach_Bien_Soan_{stem}_{clean_title_slug}.docx"
        out_path = resolve_within(OUTPUT_DIR, out_filename)
        DocxBookExporter.export(book, out_path, paper_format=paper_format, options=book_options)
        prune_output_dir()

        # 4. Thẩm định — chạy SAU khi xuất để đo được thể thức thật trên file thành phẩm
        val_report = PreFlightValidator.validate(
            book_title=book.new_title,
            subtitle=book.subtitle,
            chapters=book.chapters,
            questions=book.questions,
            doc_type="THEMATIC_BOOK" if book.chapters else "SINGLE_BOOK",
            subject=subject,
            exported_path=out_path
        )

        return {
            "status": "success",
            "book": book.to_dict(),
            "nhan_dien": nhan_dien,
            "validation_report": val_report.to_dict(),
            "output_filename": out_filename,
            "download_url": f"/api/download/{out_filename}"
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Lỗi khi biên soạn: {str(e)}")

@app.post("/api/process-folder")
def process_folder(
    request: Request,
    folder_path: str = Form(...),
    mode: str = Form("merge"),  # "merge" (1 cuốn) hoặc "split" (từng cuốn riêng)
    subject: str = Form("toan"),
    add_count: int = Form(2),
    master_title: Optional[str] = Form(None),
    include_theory: Optional[str] = Form(None),
    include_foreword: Optional[str] = Form(None),
    include_secrets: Optional[str] = Form(None),
    include_stem: Optional[str] = Form(None),
    include_casio: Optional[str] = Form(None),
    include_traps: Optional[str] = Form(None)
):
    book_options = book_options_from_form(
        include_theory, include_foreword, include_secrets,
        include_stem, include_casio, include_traps
    )
    p = resolve_user_folder(folder_path)

    settings = load_settings()
    api_key, model_name = request_credentials(request)
    paper_format = settings.get("output_format", "a4")

    files = scan_directory(p)
    if not files:
        raise HTTPException(status_code=400, detail="Thư mục không chứa tệp Word, Excel, PDF hoặc Ảnh nào hợp lệ")

    try:
        # CHẾ ĐỘ 1: GỘP TOÀN BỘ THÀNH 1 CUỐN ĐẠI CẨM NANG
        if mode == "merge":
            chapter_data_list = []
            for item in files:
                f_path = Path(item["path"])
                try:
                    q_list = parse_input_file(f_path, subject=subject, api_key=api_key)
                    if q_list:
                        chapter_data_list.append({
                            "source_name": f_path.name,
                            "questions": q_list
                        })
                except Exception as e:
                    print(f"Bỏ qua file {f_path.name} do lỗi đọc: {e}")

            if not chapter_data_list:
                raise HTTPException(status_code=400, detail="Không bóc tách được bài tập nào từ các tệp trong thư mục")

            master_book = create_master_book_from_chapters(
                chapter_data_list=chapter_data_list,
                subject=subject,
                master_title=master_title,
                api_key=api_key,
                model_name=model_name
            )

            clean_folder_name = p.name.replace(" ", "_")
            out_filename = f"Dai_Cam_Nang_{clean_folder_name}_Chuan_BGD.docx"
            out_path = resolve_within(OUTPUT_DIR, out_filename)
            DocxBookExporter.export(master_book, out_path, paper_format=paper_format, options=book_options)
            prune_output_dir()

            val_report = PreFlightValidator.validate(
                book_title=master_book.new_title,
                subtitle=master_book.subtitle,
                chapters=master_book.chapters,
                questions=master_book.questions,
                doc_type="MASTER_BOOK",
                subject=subject,
                exported_path=out_path
            )

            return {
                "status": "success",
                "mode": "merge",
                "book": master_book.to_dict(),
                "validation_report": val_report.to_dict(),
                "output_filename": out_filename,
                "download_url": f"/api/download/{out_filename}"
            }

        # CHẾ ĐỘ 2: BIÊN SOẠN TỪNG TÀI LIỆU THÀNH TỪNG CUỐN SÁCH RIÊNG LẺ
        else:
            processed_books = []
            for item in files:
                f_path = Path(item["path"])
                try:
                    q_list = parse_input_file(f_path, subject=subject, api_key=api_key)
                    if not q_list:
                        continue
                    single_book = process_rewrite_pipeline(
                        questions=q_list,
                        subject=subject,
                        add_count=int(add_count),
                        api_key=api_key,
                        model_name=model_name
                    )

                    clean_slug = "".join(c for c in single_book.new_title[:25] if c.isalnum() or c in (" ", "-", "_")).strip().replace(" ", "_")
                    out_name = f"Sach_{f_path.stem}_{clean_slug}.docx"
                    out_path = resolve_within(OUTPUT_DIR, out_name)
                    DocxBookExporter.export(single_book, out_path, paper_format=paper_format, options=book_options)

                    val_report = PreFlightValidator.validate(
                        book_title=single_book.new_title,
                        subtitle=single_book.subtitle,
                        chapters=single_book.chapters,
                        questions=single_book.questions,
                        doc_type="THEMATIC_BOOK" if single_book.chapters else "SINGLE_BOOK",
                        subject=subject,
                        exported_path=out_path
                    )

                    processed_books.append({
                        "source": f_path.name,
                        "output_filename": out_name,
                        "download_url": f"/api/download/{out_name}",
                        "title": single_book.new_title,
                        "total_questions": sum(len(c.questions) for c in single_book.chapters) if single_book.chapters else len(single_book.questions),
                        "validation_report": val_report.to_dict()
                    })
                except Exception as e:
                    print(f"Lỗi khi xử lý {f_path.name}: {e}")

            if not processed_books:
                raise HTTPException(status_code=400, detail="Không thể biên soạn tài liệu nào từ thư mục này")

            # Tự động nén toàn bộ sách thành 1 file ZIP để tải về 1-click trên Web
            import zipfile
            import time
            clean_zip_stem = "".join(c for c in p.name if c.isalnum() or c in (" ", "-", "_")).strip().replace(" ", "_") or "Sach"
            zip_filename = f"Tron_Bo_Sach_{clean_zip_stem}_{int(time.time())}.zip"
            zip_path = resolve_within(OUTPUT_DIR, zip_filename)
            with zipfile.ZipFile(str(zip_path), "w", zipfile.ZIP_DEFLATED) as zf:
                for b in processed_books:
                    b_path = resolve_within(OUTPUT_DIR, b["output_filename"])
                    if b_path.exists():
                        zf.write(str(b_path), arcname=b["output_filename"])

            return {
                "status": "success",
                "mode": "split",
                "total_books": len(processed_books),
                "books": processed_books,
                "zip_filename": zip_filename,
                "zip_download_url": f"/api/download/{zip_filename}"
            }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý thư mục: {str(e)}")

# ===========================================================================
# LÒ SINH CÂU HỎI: AI soạn đề mới cho ngân hàng, có thẩm định trước khi nhận
# ===========================================================================

class GenerateRequest(BaseModel):
    topic_key: str
    subject: str = "toan"
    grade: str = "Lớp 12"
    level: str = "Vận dụng"
    so_luong: int = 4


@app.get("/api/question-bank")
def api_question_bank(topic_key: str = "", subject: str = ""):
    """Thống kê ngân hàng và danh sách câu đã thẩm định."""
    return {
        "status": "success",
        "thong_ke": thong_ke_ngan_hang(),
        "cau_hoi": doc_ngan_hang(topic_key=topic_key, subject=subject),
        "cap_do": CAP_DO,
        "khoi_lop": KHOI_LOP,
        "toi_da_moi_lo": MAX_PER_BATCH,
    }


@app.post("/api/generate-questions")
def api_generate_questions(req: GenerateRequest, request: Request):
    """
    Sinh câu hỏi mới bằng AI rồi chạy đủ ba lớp thẩm định.
    Chỉ câu qua được TẤT CẢ mới vào ngân hàng; câu trượt trả về kèm lý do.
    """
    api_key, model_name = request_credentials(request)
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="Cần có Gemini API Key để sinh câu hỏi mới. Vào ⚙️ Cài Đặt AI để dán khóa của bạn."
        )

    try:
        ket_qua = sinh_va_tham_dinh(
            topic_key=req.topic_key,
            subject=req.subject,
            grade=req.grade,
            level=req.level,
            so_luong=req.so_luong,
            api_key=api_key,
            model_name=model_name,
        )
    except LoiHanMuc as e:
        raise HTTPException(status_code=429, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Lỗi khi sinh câu hỏi: {str(e)}")

    ket_qua["status"] = "success"
    ket_qua["thong_ke"] = thong_ke_ngan_hang()
    return ket_qua


class DeleteQuestionRequest(BaseModel):
    content_prefix: str


@app.post("/api/question-bank/delete")
def api_delete_question(req: DeleteQuestionRequest):
    """Xóa một câu khỏi ngân hàng khi người dùng thấy không ưng."""
    da_xoa = xoa_khoi_ngan_hang(req.content_prefix)
    return {"status": "success", "da_xoa": da_xoa, "thong_ke": thong_ke_ngan_hang()}


@app.get("/api/question-bank/export")
def api_export_bank():
    """
    Tải toàn bộ ngân hàng về máy.

    Cần thiết vì trên Render đĩa là tạm: mỗi lần deploy lại là ngân hàng soạn
    trên web bị xóa sạch. Tải về rồi nhập lại (hoặc commit vào repo) thì công
    soạn đề không mất.
    """
    from core.question_forge import BANK_FILE
    if not BANK_FILE.exists():
        raise HTTPException(status_code=404, detail="Ngân hàng còn trống, chưa có gì để tải về.")
    return FileResponse(
        path=str(BANK_FILE),
        filename="ngan_hang_cau_hoi.json",
        media_type="application/json"
    )


@app.post("/api/question-bank/import")
def api_import_bank(file: UploadFile = File(...)):
    """Nhập lại ngân hàng từ tệp đã tải về trước đó, gộp vào ngân hàng hiện có."""
    import json as _json
    from core.question_forge import ForgedQuestion, luu_vao_ngan_hang

    try:
        raw = file.file.read()
        data = _json.loads(raw.decode("utf-8"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Tệp không phải JSON hợp lệ: {e}")

    if not isinstance(data, list):
        raise HTTPException(status_code=400, detail="Tệp phải chứa một danh sách câu hỏi.")

    hop_le = []
    bo_qua = 0
    cho_phep = {f.name for f in ForgedQuestion.__dataclass_fields__.values()}
    for item in data:
        # Chỉ nhận câu ĐÃ thẩm định. Không cho đường vòng đưa câu chưa duyệt
        # vào ngân hàng bằng cách sửa tay tệp JSON rồi nhập lên.
        if not isinstance(item, dict) or not item.get("verified"):
            bo_qua += 1
            continue
        try:
            hop_le.append(ForgedQuestion(**{k: v for k, v in item.items() if k in cho_phep}))
        except Exception:
            bo_qua += 1

    them = luu_vao_ngan_hang(hop_le) if hop_le else 0
    return {
        "status": "success",
        "da_them": them,
        "bo_qua": bo_qua,
        "thong_ke": thong_ke_ngan_hang(),
    }


@app.get("/api/download/{filename}")
def download_file(filename: str):
    file_path = resolve_within(OUTPUT_DIR, filename)
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File không tồn tại hoặc đã bị xóa")
    ext = file_path.suffix.lower()
    media_type = "application/zip" if ext == ".zip" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type=media_type
    )

@app.post("/api/open-output-folder")
def open_output_folder():
    try:
        if LOCAL_MODE and sys.platform == "win32":
            os.startfile(str(OUTPUT_DIR))
            return {"status": "success", "folder": str(OUTPUT_DIR)}
        else:
            return {"status": "info", "message": "Đang chạy trên môi trường Web/Cloud Server. Vui lòng tải file trực tiếp qua trình duyệt."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading

    # Mặc định chỉ lắng nghe trên máy cục bộ để máy khác trong mạng LAN không
    # truy cập được vào dữ liệu cá nhân. Docker/Cloud tự đặt HOST=0.0.0.0.
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 8501))

    if os.environ.get("AUTO_OPEN_BROWSER", "1") == "1" and sys.platform == "win32":
        def open_browser():
            import time
            time.sleep(1.2)
            try:
                webbrowser.open(f"http://127.0.0.1:{port}")
            except Exception:
                pass
        threading.Thread(target=open_browser, daemon=True).start()

    display_host = "127.0.0.1" if host in ("0.0.0.0", "::") else host
    print(f"[*] Bien Soan Sach Pro dang chay tai: http://{display_host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")
