import os
import sys
import secrets
from pathlib import Path
from typing import Optional, List

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config import (
    BASE_DIR, INPUT_DIR, OUTPUT_DIR, TEMPLATES_DIR, STATIC_DIR,
    LOCAL_MODE, ACCESS_TOKEN, load_settings, save_settings
)
from core.parser import parse_input_file, scan_directory
from core.rewriter import process_rewrite_pipeline, create_master_book_from_chapters
from core.ai_namer import generate_creative_titles_gemini
from core.exporter import DocxBookExporter
from core.validator import PreFlightValidator

app = FastAPI(title="Biên Soạn Sách Toán - Vật Lý Pro")


# ===========================================================================
# LỚP BẢO VỆ: LÀM SẠCH TÊN TỆP & GIỚI HẠN PHẠM VI TRUY CẬP Ổ ĐĨA
# ===========================================================================

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
    index_file = TEMPLATES_DIR / "index.html"
    with open(index_file, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

def _mask_settings(settings: dict) -> dict:
    """Che giấu API key trước khi gửi ra trình duyệt (tránh lộ khóa Gemini)."""
    masked = dict(settings)
    raw_key = (masked.get("gemini_api_key") or "").strip()
    masked["gemini_api_key"] = ""
    masked["gemini_api_key_set"] = bool(raw_key)
    masked["gemini_api_key_hint"] = f"••••••••{raw_key[-4:]}" if len(raw_key) >= 4 else ""
    return masked


@app.get("/api/settings")
def get_settings():
    return _mask_settings(load_settings())

@app.post("/api/settings")
def update_settings(settings: dict):
    # Gửi chuỗi rỗng đồng nghĩa "giữ nguyên khóa cũ", không phải "xóa khóa".
    payload = dict(settings or {})
    if not (payload.get("gemini_api_key") or "").strip():
        payload.pop("gemini_api_key", None)
    saved = save_settings(payload)
    return {"status": "success", "settings": _mask_settings(saved)}

class ScanFolderRequest(BaseModel):
    folder_path: str

@app.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "service": "Bien Soan Sach Pro",
        "version": "2.5",
        "web_deploy_ready": True
    }

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

class SuggestTitlesRequest(BaseModel):
    filename: str = ""
    sample_text: str = ""
    subject: str = "toan"

@app.post("/api/suggest-titles")
def api_suggest_titles(req: SuggestTitlesRequest):
    settings = load_settings()
    api_key = settings.get("gemini_api_key", "").strip()
    model_name = settings.get("gemini_model", "gemini-3.6-flash")

    titles = generate_creative_titles_gemini(
        sample_text=req.sample_text,
        filename=req.filename,
        subject=req.subject,
        api_key=api_key,
        model_name=model_name
    )
    return {
        "status": "success",
        "total": len(titles),
        "titles": titles
    }

@app.post("/api/upload")
def upload_file(
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

    settings = load_settings()
    api_key = settings.get("gemini_api_key", "").strip()

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

@app.post("/api/process")
def process_single_document(
    filename: str = Form(...),
    subject: str = Form("toan"),
    add_count: int = Form(2),
    custom_title: Optional[str] = Form(None)
):
    input_path = resolve_within(INPUT_DIR, filename)
    if not input_path.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy file nguồn đã tải lên")

    settings = load_settings()
    api_key = settings.get("gemini_api_key", "").strip()
    model_name = settings.get("gemini_model", "gemini-3.6-flash")
    paper_format = settings.get("output_format", "a4")

    try:
        # 1. Bóc tách
        questions = parse_input_file(input_path, subject=subject, api_key=api_key)
        if not questions:
            raise HTTPException(status_code=400, detail="Không trích xuất được bài toán nào từ file này")

        # 2. Tái cấu trúc & Bổ sung lý thuyết chuẩn BGD
        book = process_rewrite_pipeline(
            questions=questions,
            subject=subject,
            add_count=int(add_count),
            api_key=api_key,
            model_name=model_name
        )

        if custom_title and custom_title.strip():
            book.new_title = custom_title.strip()

        # 3. Xuất Word chuẩn Nghị định 30
        stem = safe_filename(Path(filename).stem + ".docx").rsplit(".", 1)[0]
        clean_title_slug = "".join(c for c in book.new_title[:30] if c.isalnum() or c in (" ", "-", "_")).strip().replace(" ", "_")
        out_filename = f"Sach_Bien_Soan_{stem}_{clean_title_slug}.docx"
        out_path = resolve_within(OUTPUT_DIR, out_filename)
        DocxBookExporter.export(book, out_path, paper_format=paper_format)
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
    folder_path: str = Form(...),
    mode: str = Form("merge"),  # "merge" (1 cuốn) hoặc "split" (từng cuốn riêng)
    subject: str = Form("toan"),
    add_count: int = Form(2),
    master_title: Optional[str] = Form(None)
):
    p = resolve_user_folder(folder_path)

    settings = load_settings()
    api_key = settings.get("gemini_api_key", "").strip()
    model_name = settings.get("gemini_model", "gemini-3.6-flash")
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
            DocxBookExporter.export(master_book, out_path, paper_format=paper_format)
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
                    DocxBookExporter.export(single_book, out_path, paper_format=paper_format)

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
