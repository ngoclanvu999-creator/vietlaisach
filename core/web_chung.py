# -*- coding: utf-8 -*-
"""
Lớp web dùng chung cho cả ba ứng dụng.

Tách ra ngày 19/09/2026 khi chia công cụ thành ba app. Ba app khác nhau ở loại
đầu ra và giao diện, nhưng giống hệt nhau ở phần này: chặn đường dẫn độc hại,
dọn tệp cũ, băm phiên bản tài nguyên, lấy khóa API theo từng yêu cầu.

MỌI HÀM ĐỀU NHẬN THƯ MỤC LÀM THAM SỐ. Không có hằng số thư mục toàn cục ở đây,
vì mỗi app có `input/` và `output/` riêng — dùng chung thì `don_thu_muc_ra()`
của app này sẽ xóa mất kết quả của app kia.
"""

import hashlib
import shutil
import zipfile
from pathlib import Path
from typing import Dict, Optional, Tuple

from fastapi import HTTPException, Request

from config import LOCAL_MODE, load_settings
from core.ai_provider import TEN_HIEN_THI, chuan_hoa

# Đuôi tệp nhận được. Ảnh cần khóa API mới đọc được (Claude đọc ảnh).
DUOI_NHAN = {".docx", ".doc", ".xlsx", ".xls", ".pdf", ".png", ".jpg", ".jpeg"}
DUOI_NEN = {".zip"}

MAX_TEP_RA = 300          # giữ lại bao nhiêu tệp kết quả trước khi dọn
MAX_PHIEN_VAO = 12        # giữ lại bao nhiêu phiên nạp liệu


# ---------------------------------------------------------------------------
# Chặn đường dẫn độc hại
# ---------------------------------------------------------------------------

def ten_tep_an_toan(ten_tho: str) -> str:
    """Chỉ giữ phần tên tệp, bỏ mọi thành phần đường dẫn (`../`, `C:\\`...)."""
    ten = Path(str(ten_tho or "").replace("\\", "/")).name
    ten = ten.replace("\x00", "").strip()
    if not ten or ten in (".", ".."):
        raise HTTPException(status_code=400, detail="Tên tệp không hợp lệ")
    return ten


def trong_thu_muc(goc: Path, ten_tho: str) -> Path:
    """Ghép tên tệp vào thư mục gốc, xác nhận kết quả KHÔNG thoát ra ngoài."""
    ung_vien = (goc / ten_tep_an_toan(ten_tho)).resolve()
    goc_that = goc.resolve()
    if ung_vien != goc_that and goc_that not in ung_vien.parents:
        raise HTTPException(status_code=400, detail="Đường dẫn tệp không hợp lệ")
    return ung_vien


def duong_con_trong(goc: Path, tuong_doi: str) -> Path:
    """
    Như `trong_thu_muc` nhưng CHO PHÉP nhiều cấp bên trong thư mục gốc
    (ví dụ `phien_1726/De_thi.docx`), vẫn chặn mọi mưu toan thoát ra.
    """
    rel = str(tuong_doi or "").replace("\\", "/").strip().lstrip("/")
    if not rel or "\x00" in rel:
        raise HTTPException(status_code=400, detail="Đường dẫn tệp không hợp lệ")

    phan = [s for s in rel.split("/") if s not in ("", ".")]
    if any(s == ".." for s in phan):
        raise HTTPException(status_code=400, detail="Đường dẫn tệp không hợp lệ")

    ung_vien = goc.joinpath(*phan).resolve()
    goc_that = goc.resolve()
    if ung_vien != goc_that and goc_that not in ung_vien.parents:
        raise HTTPException(status_code=400, detail="Đường dẫn tệp không hợp lệ")
    return ung_vien


def thu_muc_nguoi_dung(duong_tho: str, thu_muc_vao: Path) -> Path:
    """
    Thư mục người dùng trỏ tới. Trên bản Web chỉ cho phép bên trong `input/`.

    Đây là rào chặn quan trọng nhất của bản Web: máy chủ mà cho duyệt thư mục
    thì ai vào cũng đọc được ổ đĩa của nó.
    """
    tho = str(duong_tho or "").strip().strip('"').strip("'")
    if not tho:
        raise HTTPException(status_code=400, detail="Chưa nhập đường dẫn thư mục")
    try:
        p = Path(tho).expanduser().resolve()
    except Exception:
        raise HTTPException(status_code=400, detail="Đường dẫn thư mục không hợp lệ")

    if not LOCAL_MODE:
        vao = thu_muc_vao.resolve()
        if p != vao and vao not in p.parents:
            raise HTTPException(
                status_code=403,
                detail="Chế độ Web không cho phép truy cập thư mục trên máy chủ. "
                       "Hãy dùng chức năng tải lên thư mục hoặc tệp .ZIP.")

    if not p.exists() or not p.is_dir():
        raise HTTPException(status_code=404, detail=f"Không thấy thư mục: {p}")
    return p


# ---------------------------------------------------------------------------
# Dọn tệp cũ
# ---------------------------------------------------------------------------

def don_thu_muc_ra(thu_muc_ra: Path, giu_lai: int = MAX_TEP_RA) -> int:
    """Xóa bớt tệp kết quả cũ nhất. Dùng `rglob` vì kết quả nằm trong thư mục con."""
    try:
        tep = [p for p in thu_muc_ra.rglob("*") if p.is_file()]
    except OSError:
        return 0
    if len(tep) <= giu_lai:
        return 0
    tep.sort(key=lambda p: p.stat().st_mtime)
    da_xoa = 0
    for p in tep[: len(tep) - giu_lai]:
        try:
            p.unlink()
            da_xoa += 1
        except OSError:
            pass
    return da_xoa


def don_phien_vao(thu_muc_vao: Path, giu_lai: int = MAX_PHIEN_VAO) -> int:
    """Xóa bớt phiên nạp liệu cũ. Chỉ đụng thư mục `phien_*`, không đụng tệp mẫu."""
    try:
        phien = sorted((p for p in thu_muc_vao.glob("phien_*") if p.is_dir()),
                       key=lambda p: p.stat().st_mtime)
    except OSError:
        return 0
    if len(phien) <= giu_lai:
        return 0
    da_xoa = 0
    for p in phien[: len(phien) - giu_lai]:
        try:
            shutil.rmtree(p, ignore_errors=True)
            da_xoa += 1
        except OSError:
            pass
    return da_xoa


def ten_khong_trung(thu_muc: Path, ten_tep: str) -> Path:
    """Thêm hậu tố số nếu tên đã tồn tại, để tệp cùng tên không đè lên nhau."""
    dich = trong_thu_muc(thu_muc, ten_tep)
    if not dich.exists():
        return dich
    than, duoi = dich.stem, dich.suffix
    for i in range(2, 1000):
        thu = thu_muc / f"{than}_{i}{duoi}"
        if not thu.exists():
            return thu
    raise HTTPException(status_code=400, detail="Quá nhiều tệp trùng tên")


def giai_nen_vao(tep_zip: Path, dich: Path) -> int:
    """
    Giải nén, bỏ qua mọi lối vào có đường dẫn thoát ra ngoài.

    Tệp .zip là thứ người khác gửi tới; một lối vào tên `../../windows/x.dll`
    sẽ ghi đè ra ngoài thư mục đích nếu không chặn.
    """
    dem = 0
    with zipfile.ZipFile(tep_zip) as z:
        for loi_vao in z.infolist():
            if loi_vao.is_dir():
                continue
            ten = Path(loi_vao.filename.replace("\\", "/")).name
            if not ten or Path(ten).suffix.lower() not in (DUOI_NHAN | DUOI_NEN):
                continue
            ra = ten_khong_trung(dich, ten)
            with z.open(loi_vao) as nguon, open(ra, "wb") as dich_tep:
                shutil.copyfileobj(nguon, dich_tep)
            dem += 1
    return dem


# ---------------------------------------------------------------------------
# Phiên bản tài nguyên — chống lưu đệm
# ---------------------------------------------------------------------------
_BO_NHO_PHIEN_BAN: Dict[tuple, str] = {}


def phien_ban_tai_nguyen(thu_muc_static: Path, dung_chung: Optional[Path] = None) -> str:
    """
    Băm NỘI DUNG app.js + style.css làm số phiên bản.

    Băm nội dung chứ không băm thời gian sửa: `git checkout` hay chép tệp đều
    đổi mtime dù nội dung y nguyên, băm theo mtime sẽ bắt trình duyệt tải lại
    một cách vô ích. Không bao giờ gắn cứng số phiên bản — đã từng làm trình
    duyệt giữ JS cũ chạy với HTML mới, gây `TypeError` và chết cả trang.
    """
    cac_tep = [thu_muc_static / "app.js"]
    cac_tep.append((dung_chung or thu_muc_static) / "style.css")

    khoa = []
    for f in cac_tep:
        try:
            st = f.stat()
            khoa.append((str(f), st.st_mtime_ns, st.st_size))
        except OSError:
            khoa.append((str(f), 0, 0))
    khoa = tuple(khoa)

    if khoa in _BO_NHO_PHIEN_BAN:
        return _BO_NHO_PHIEN_BAN[khoa]

    h = hashlib.md5()
    for f in cac_tep:
        try:
            h.update(f.read_bytes())
        except OSError:
            h.update(f"{f.name}:thieu".encode())

    ban = h.hexdigest()[:10]
    _BO_NHO_PHIEN_BAN.clear()
    _BO_NHO_PHIEN_BAN[khoa] = ban
    return ban


# ---------------------------------------------------------------------------
# Khóa API
# ---------------------------------------------------------------------------

def khoa_cua_yeu_cau(request: Request) -> Tuple[str, str]:
    """
    Khóa Claude và model THEO TỪNG NGƯỜI DÙNG, gửi kèm mỗi yêu cầu qua header.

    Khóa là tài sản riêng của mỗi người, máy chủ không lưu. Trên bản Web nếu
    người dùng chưa dán khóa thì coi như không có — tuyệt đối KHÔNG mượn khóa
    của chủ máy chủ, vì như vậy là tiêu tiền của người khác.

    Riêng khi chạy trên máy cá nhân thì mới lấy khóa đã lưu trong
    `app_settings.json`, vì đó chính là máy của người dùng.
    """
    key = (request.headers.get("X-Claude-Key") or "").strip()
    model = (request.headers.get("X-Claude-Model") or "").strip()
    if not key and LOCAL_MODE:
        cai_dat = load_settings()
        key = (cai_dat.get("claude_api_key") or "").strip()
        if not model:
            model = (cai_dat.get("claude_model") or "").strip()

    tt = chuan_hoa(key, model)
    return tt.api_key, tt.model


def dau_an_ai(model_name: str, api_key: str) -> dict:
    """
    Ghi lại tài liệu này do AI hay bộ máy ngoại tuyến biên soạn.

    Nhìn file thành phẩm thì không phân biệt được, nên phải gắn dấu vào báo cáo.
    KHÔNG bao giờ ghi lại chính khóa API, chỉ ghi có khóa hay không.
    """
    co_khoa = bool((api_key or "").strip())
    return {
        "ten_hien_thi": TEN_HIEN_THI if co_khoa else "Bộ máy ngoại tuyến",
        "model": model_name if co_khoa else "",
        "dung_ai": co_khoa,
    }
