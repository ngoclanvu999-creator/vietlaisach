# -*- coding: utf-8 -*-
"""
App VIẾT LẠI SÁCH — điểm vào.

Mỏng, chỉ điều phối: nhận tệp, gọi lõi bóc tách và biên soạn, gọi bộ dựng của
app này, trả kết quả. Không chứa logic biên soạn nào.

Khác hai app kia: KHÔNG có bước chọn loại đầu ra. Đầu ra luôn là một cuốn sách
biên soạn lại — bìa, lời tựa, mục lục, các chương, lời giải.

Chạy:  python -m uvicorn app_viet_sach.main:app --port 8501
"""

import shutil
import sys
import time
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

if sys.platform == "win32":
    for luong in (sys.stdout, sys.stderr):
        try:
            luong.reconfigure(encoding="utf-8")
        except Exception:
            pass

from config import LOCAL_MODE, STATIC_DIR as STATIC_DUNG_CHUNG, load_settings, save_settings
from core import tien_do
from core.ai_provider import (LoiDauRaThieu, LoiHanMuc, MODEL_CLAUDE_CHO_PHEP,
                              MODEL_CLAUDE_MAC_DINH, TEN_HIEN_THI, chuan_hoa, goi_ai)
from core.doc_type import detect_document_type
# App này không dùng sổ đăng ký loại đầu ra: nó chỉ làm đúng một việc.
from core.parser import (bat_dau_thu_thap_dau_hieu, lay_dau_hieu_tai_lieu,
                         parse_input_file, scan_directory)
from core.rewriter import (AI_SCOPE_KHONG, AI_SCOPE_TAT_CA, AI_SCOPE_THIEU,
                           process_rewrite_pipeline)
from core.skill_loader import THCS, THPT, TIEU_HOC
from core.validator import PreFlightValidator
from core.web_chung import (DUOI_NEN, DUOI_NHAN, dau_an_ai, don_phien_vao,
                            don_thu_muc_ra, duong_con_trong, giai_nen_vao,
                            khoa_cua_yeu_cau, phien_ban_tai_nguyen, ten_khong_trung,
                            ten_tep_an_toan, thu_muc_nguoi_dung)

from . import cau_hinh as CH
from .bo_dung.dung import dung_tai_lieu

app = FastAPI(title=CH.TEN_APP)
app.mount("/static", StaticFiles(directory=str(CH.THU_MUC_STATIC)), name="static")
app.mount("/chung", StaticFiles(directory=str(STATIC_DUNG_CHUNG)), name="chung")


# ---------------------------------------------------------------------------
# Trang và trạng thái
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def trang_chu():
    html = (CH.THU_MUC_TEMPLATES / "index.html").read_text(encoding="utf-8")
    html = html.replace("__ASSET_VERSION__",
                        phien_ban_tai_nguyen(CH.THU_MUC_STATIC, STATIC_DUNG_CHUNG))
    # Trang HTML không được lưu đệm, nếu không trình duyệt vẫn nhận trang cũ
    # trỏ tới số phiên bản cũ.
    return HTMLResponse(content=html,
                        headers={"Cache-Control": "no-cache, no-store, must-revalidate"})


@app.get("/api/health")
async def suc_khoe():
    return {
        "status": "online",
        "app": CH.TEN_APP,
        "cong": CH.CONG,
        "loai_dau_ra": CH.LOAI_DAU_RA,
        "asset_version": phien_ban_tai_nguyen(CH.THU_MUC_STATIC, STATIC_DUNG_CHUNG),
        "local_mode": LOCAL_MODE,
    }


@app.get("/api/tien-do")
def api_tien_do():
    return tien_do.doc()


# Những tùy chọn KHÔNG phải bí mật. Khóa API cố tình không nằm ở đây.
TUY_CHON_CONG_KHAI = {
    "default_subject", "default_add_count", "enable_casio", "enable_traps",
    "enable_summary_box", "enable_dual_solutions", "output_format",
}


@app.get("/api/settings")
def doc_cai_dat():
    s = load_settings()
    ra = {k: v for k, v in s.items() if k in TUY_CHON_CONG_KHAI}
    ra["local_mode"] = LOCAL_MODE
    ra["allowed_models"] = sorted(MODEL_CLAUDE_CHO_PHEP)
    ra["default_model"] = MODEL_CLAUDE_MAC_DINH
    ra["server_key_available"] = bool(
        LOCAL_MODE and (s.get("claude_api_key") or "").strip())
    ra["ten_app"] = CH.TEN_APP
    return ra


@app.post("/api/settings")
def ghi_cai_dat(cai_dat: dict):
    """Chỉ ghi tùy chọn công khai. Khóa API không bao giờ đi qua đây."""
    sach = {k: v for k, v in (cai_dat or {}).items() if k in TUY_CHON_CONG_KHAI}
    return {"status": "success", "settings": save_settings(sach)}


@app.post("/api/thu-khoa")
def thu_khoa(request: Request):
    """
    Gọi thật một lượt rất ngắn để người dùng biết khóa có dùng được không.

    Khóa hỏng có nhiều kiểu rất khác nhau mà thông báo lại giống nhau: sai ký
    tự, hết tín dụng, hoặc khóa cấp tổ chức chưa gắn workspace. Không có nút này
    thì người dùng chỉ thấy tài liệu ra bằng bộ máy ngoại tuyến mà không hiểu vì sao.
    """
    api_key, model_name = khoa_cua_yeu_cau(request)
    if not api_key:
        return {"status": "error", "dung_duoc": False,
                "thong_bao": f"Chưa dán khóa {TEN_HIEN_THI}. "
                             "Ứng dụng sẽ chạy bằng bộ máy ngoại tuyến."}

    tt = chuan_hoa(api_key, model_name)
    t0 = time.time()
    try:
        # 1500 token là dư, nhưng vẫn cần rộng: model có suy luận thích ứng sẽ
        # tiêu token cho phần nghĩ trước khi viết được chữ nào.
        tra_loi = goi_ai(tt, "Trả lời đúng một số, không thêm gì khác: 12 x 12 bằng mấy?",
                         max_tokens=1500)
    except LoiHanMuc as e:
        return {"status": "error", "dung_duoc": False,
                "thong_bao": "Khóa đúng nhưng đã hết hạn mức hoặc hết tín dụng.",
                "chi_tiet": str(e)[:300]}
    except LoiDauRaThieu as e:
        return {"status": "error", "dung_duoc": False,
                "thong_bao": "Gọi được nhưng đầu ra không dùng được.",
                "chi_tiet": str(e)[:300]}
    except Exception as e:
        tin, ma = str(e), getattr(e, "status_code", None)
        goi_y = ""
        if ma == 401 or "authentication_error" in tin:
            goi_y = "Khóa sai hoặc đã bị thu hồi. Hãy tạo khóa mới."
        elif "not scoped to a workspace" in tin:
            goi_y = ("Khóa này ở cấp tổ chức, chưa gắn workspace nào. Vào console "
                     "tạo lại khóa và chọn một Workspace cụ thể.")
        elif ma == 429:
            goi_y = "Bị chặn vì gọi quá nhanh. Thử lại sau ít phút."
        return {"status": "error", "dung_duoc": False,
                "thong_bao": goi_y or "Không gọi được Claude.", "chi_tiet": tin[:300]}

    giay = round(time.time() - t0, 2)
    return {"status": "success", "dung_duoc": True, "model": tt.model, "giay": giay,
            "dap_so_dung": "144" in (tra_loi or ""),
            "thong_bao": f"Khóa dùng được — {tt.model} trả lời trong {giay} giây."}


# ---------------------------------------------------------------------------
# Nạp tài liệu
# ---------------------------------------------------------------------------

class YeuCauThuMuc(BaseModel):
    folder_path: str


@app.post("/api/quet-thu-muc")
def quet_thu_muc(req: YeuCauThuMuc):
    p = thu_muc_nguoi_dung(req.folder_path, CH.THU_MUC_VAO)
    try:
        ds = scan_directory(p)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi quét thư mục: {e}")
    return {"status": "success", "folder": str(p), "total": len(ds),
            "files": [{"name": Path(f).name, "path": str(f)} for f in ds]}


@app.post("/api/nap-lieu")
def nap_lieu(
    request: Request,
    files: List[UploadFile] = File(default=[]),
    folder_path: str = Form(default=""),
    subject: str = Form(default="toan"),
):
    """
    Nhận tệp lẻ, nhiều tệp, hoặc một thư mục — rồi bóc tách hết thành câu hỏi.

    Mỗi lần nạp là một PHIÊN riêng trong `input/phien_<thời điểm>` để lần nạp
    sau không lẫn với lần trước.
    """
    api_key, model_name = khoa_cua_yeu_cau(request)
    don_phien_vao(CH.THU_MUC_VAO)

    phien = CH.THU_MUC_VAO / f"phien_{int(time.time() * 1000)}"
    phien.mkdir(parents=True, exist_ok=True)

    # Dấu hiệu hành chính (tên trường, "ĐỀ CHÍNH THỨC"...) do bộ bóc tách gom
    # lại trong lúc đọc tệp; phải xóa dấu hiệu của phiên trước rồi mới bóc.
    bat_dau_thu_thap_dau_hieu()

    da_luu: List[Path] = []
    for f in files or []:
        if not f.filename:
            continue
        ten = ten_tep_an_toan(f.filename)
        duoi = Path(ten).suffix.lower()
        if ten.startswith("~$") or duoi not in (DUOI_NHAN | DUOI_NEN):
            continue
        dich = ten_khong_trung(phien, ten)
        with open(dich, "wb") as ra:
            shutil.copyfileobj(f.file, ra)
        if duoi in DUOI_NEN:
            giai_nen_vao(dich, phien)
            dich.unlink(missing_ok=True)
        else:
            da_luu.append(dich)

    if folder_path.strip():
        goc = thu_muc_nguoi_dung(folder_path, CH.THU_MUC_VAO)
        for p in scan_directory(goc):
            da_luu.append(Path(p))

    # Tệp giải nén từ .zip cũng phải được tính vào
    for p in phien.iterdir():
        if p.is_file() and p.suffix.lower() in DUOI_NHAN and p not in da_luu:
            da_luu.append(p)

    if not da_luu:
        raise HTTPException(status_code=400,
                            detail="Không có tệp nào hợp lệ. Nhận .docx .xlsx .pdf "
                                   ".png .jpg và .zip chứa các loại đó.")

    cau_hoi, hong = [], []
    for p in da_luu:
        try:
            kq = parse_input_file(Path(p), subject=subject, api_key=api_key)
            ds = kq.get("questions") if isinstance(kq, dict) else kq
            cau_hoi.extend(ds or [])
        except Exception as e:
            hong.append({"tep": Path(p).name, "loi": str(e)[:200]})

    if not cau_hoi:
        raise HTTPException(status_code=400,
                            detail="Không bóc tách được câu hỏi nào từ các tệp đã nạp.")

    nhan_dien = detect_document_type(cau_hoi, lay_dau_hieu_tai_lieu(),
                                     Path(da_luu[0]).name)
    return {
        "status": "success",
        "phien": phien.name,
        "tong_cau": len(cau_hoi),
        "so_tep": len(da_luu),
        "tep_hong": hong,
        "nhan_dien": nhan_dien,
        "xem_truoc": [
            {"index": q.index, "title": q.title, "content": q.content[:400],
             "options": q.options, "correct_answer": q.correct_answer}
            for q in cau_hoi[:15]
        ],
        "duong_dan": [str(p) for p in da_luu],
    }


# ---------------------------------------------------------------------------
# Biên soạn
# ---------------------------------------------------------------------------

def _co(gia_tri: Optional[str], mac_dinh: bool = True) -> bool:
    if gia_tri is None:
        return mac_dinh
    return str(gia_tri).strip().lower() in ("1", "true", "on", "yes", "có", "co")


@app.post("/api/bien-soan")
def bien_soan(
    request: Request,
    duong_dan: str = Form(...),
    subject: str = Form(default="toan"),
    cap_hoc: str = Form(default=""),
    ai_scope: str = Form(default=AI_SCOPE_THIEU),
    paper_format: str = Form(default="a4"),
    tieu_de_rieng: str = Form(default=""),
    them_cau: int = Form(default=0),
    solution: Optional[str] = Form(default=None),
    casio: Optional[str] = Form(default=None),
    traps: Optional[str] = Form(default=None),
    theory: Optional[str] = Form(default=None),
):
    """Bóc tách lại từ các tệp đã nạp rồi biên soạn thành tài liệu chuyên đề."""
    api_key, model_name = khoa_cua_yeu_cau(request)

    cac_tep = [d.strip() for d in duong_dan.split("|") if d.strip()]
    if not cac_tep:
        raise HTTPException(status_code=400, detail="Chưa có tệp nào để biên soạn")

    cau_hoi = []
    for d in cac_tep:
        p = Path(d)
        if not p.exists():
            continue
        kq = parse_input_file(p, subject=subject, api_key=api_key)
        ds = kq.get("questions") if isinstance(kq, dict) else kq
        cau_hoi.extend(ds or [])

    if not cau_hoi:
        raise HTTPException(status_code=400, detail="Không bóc tách được câu hỏi nào")

    tuy_chon = {
        "solution": _co(solution), "casio": _co(casio),
        "traps": _co(traps), "theory": _co(theory),
    }

    try:
        book = process_rewrite_pipeline(
            questions=cau_hoi, subject=subject, add_count=int(them_cau),
            api_key=api_key, model_name=model_name,
            ai_scope=ai_scope if ai_scope in (AI_SCOPE_THIEU, AI_SCOPE_TAT_CA,
                                              AI_SCOPE_KHONG) else AI_SCOPE_THIEU,
            options=tuy_chon,
            cap_hoc=cap_hoc if cap_hoc in (TIEU_HOC, THCS, THPT) else "",
        )
        if tieu_de_rieng.strip():
            book.new_title = tieu_de_rieng.strip()

        than = "".join(c for c in book.new_title[:40]
                       if c.isalnum() or c in " -_").strip().replace(" ", "_")
        ten_ra = f"Sach_{than or 'Bien_Soan'}.docx"
        duong_ra = CH.THU_MUC_RA / ten_ra
        dung_tai_lieu(book, duong_ra, kho_giay=paper_format, tuy_chon=tuy_chon)
        don_thu_muc_ra(CH.THU_MUC_RA)

        bao_cao = PreFlightValidator.validate(
            book_title=book.new_title, subtitle=book.subtitle,
            chapters=book.chapters, questions=book.questions,
            doc_type="THEMATIC_BOOK" if book.chapters else "SINGLE_BOOK",
            subject=subject, exported_path=duong_ra,
        )

        return {
            "status": "success",
            "book": book.to_dict(),
            "validation_report": bao_cao.to_dict(),
            "nha_cung_cap": dau_an_ai(model_name, api_key),
            "ten_tep": ten_ra,
            "download_url": f"/api/tai-ve/{ten_ra}",
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Lỗi khi biên soạn: {e}")
    finally:
        tien_do.ket_thuc()


@app.get("/api/tai-ve/{duong_dan:path}")
def tai_ve(duong_dan: str):
    p = duong_con_trong(CH.THU_MUC_RA, duong_dan)
    if not p.exists() or not p.is_file():
        raise HTTPException(status_code=404, detail="Không thấy tệp kết quả")
    return FileResponse(
        str(p), filename=p.name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")


@app.post("/api/mo-thu-muc-ket-qua")
def mo_thu_muc():
    """Chỉ chạy trên máy cá nhân — máy chủ không có màn hình để mở cửa sổ nào."""
    if not (LOCAL_MODE and sys.platform == "win32"):
        raise HTTPException(status_code=400,
                            detail="Chỉ mở được thư mục khi chạy trên máy cá nhân")
    import subprocess
    subprocess.Popen(["explorer", str(CH.THU_MUC_RA)])
    return {"status": "success", "thu_muc": str(CH.THU_MUC_RA)}


if __name__ == "__main__":
    import uvicorn
    print(f"[*] {CH.TEN_APP} đang chạy tại: http://127.0.0.1:{CH.CONG}")
    uvicorn.run(app, host="127.0.0.1", port=CH.CONG)
