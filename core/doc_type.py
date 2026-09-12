"""
Nhận diện loại tài liệu đầu vào để xuất ra ĐÚNG dạng tương ứng.

Người dùng đưa vào đề thi thì mong nhận lại một đề thi hoàn chỉnh, chứ không
phải một cuốn sách có lý thuyết chen giữa các câu. Ngược lại đưa vào sách thì
mong nhận lại sách có chương mục, lý thuyết và lời giải ngay dưới mỗi bài.

Ba loại:
  DE_THI    — đề kiểm tra, đề thi: câu hỏi liên tục, phần lớn trắc nghiệm,
              có dấu vết hành chính (Sở GD&ĐT, mã đề, thời gian làm bài).
              Xuất ra: đề sạch ở đầu, đáp án và lời giải dồn về cuối.
  SACH      — sách, tuyển tập nhiều chương: có phân chương rõ ràng.
              Xuất ra: mục lục, từng chương có lý thuyết rồi tới bài tập.
  CHUYEN_DE — tài liệu một chủ đề: có lý thuyết nhưng không chia chương.
              Xuất ra: lý thuyết nền tảng ở đầu rồi tới hệ thống bài tập.
"""

import re
from typing import List, Dict, Any, Optional

DE_THI = "DE_THI"
SACH = "SACH"
CHUYEN_DE = "CHUYEN_DE"

TEN_HIEN_THI = {
    DE_THI: "Đề thi / Đề kiểm tra",
    SACH: "Sách nhiều chương",
    CHUYEN_DE: "Tài liệu chuyên đề",
}

# Dấu vết hành chính chỉ có ở đề thi thật
DAU_VET_DE_THI = [
    (re.compile(r"sở\s*g(iáo\s*dục|d)", re.I), 3),
    (re.compile(r"đề\s*(thi|kiểm\s*tra)", re.I), 3),
    (re.compile(r"mã\s*đề", re.I), 3),
    (re.compile(r"thời\s*gian\s*làm\s*bài", re.I), 3),
    (re.compile(r"họ\s*(và\s*)?tên\s*(thí\s*sinh|học\s*sinh)", re.I), 2),
    (re.compile(r"\bsbd\b|số\s*báo\s*danh", re.I), 2),
    (re.compile(r"đề\s*chính\s*thức", re.I), 3),
    (re.compile(r"trường\s*th(pt|cs)", re.I), 1),
    (re.compile(r"năm\s*học\s*\d{4}", re.I), 1),
    (re.compile(r"học\s*kỳ|giữa\s*kỳ|cuối\s*kỳ", re.I), 2),
    (re.compile(r"tốt\s*nghiệp\s*thpt", re.I), 2),
    (re.compile(r"---+\s*hết\s*---+|^\s*hết\s*$", re.I), 2),
]

# Dấu vết của sách / tài liệu biên soạn
DAU_VET_SACH = [
    (re.compile(r"chương\s+\d+", re.I), 3),
    (re.compile(r"chuyên\s*đề\s+\d+", re.I), 2),
    (re.compile(r"mục\s*lục", re.I), 3),
    (re.compile(r"lời\s*(nói\s*đầu|tựa|mở\s*đầu)", re.I), 3),
    (re.compile(r"sổ\s*tay|cẩm\s*nang|tuyển\s*tập", re.I), 2),
    (re.compile(r"lý\s*thuyết\s*(trọng\s*tâm|cơ\s*bản|cần\s*nhớ)", re.I), 2),
    (re.compile(r"kiến\s*thức\s*cần\s*nhớ|ghi\s*nhớ", re.I), 2),
    (re.compile(r"ví\s*dụ\s*(minh\s*họa|mẫu)", re.I), 1),
    (re.compile(r"bài\s*tập\s*(tự\s*luyện|vận\s*dụng|rèn\s*luyện)", re.I), 1),
]


def _diem_theo_mau(van_ban: str, mau_list) -> int:
    return sum(diem for mau, diem in mau_list if mau.search(van_ban))


def detect_document_type(
    questions: List[Any],
    raw_signals: Optional[List[str]] = None,
    filename: str = "",
) -> Dict[str, Any]:
    """
    Xác định loại tài liệu dựa trên ba nguồn chứng cứ:
      1. Các dòng hành chính mà bộ bóc tách đã loại ra (raw_signals) — đây là
         nguồn mạnh nhất, vì "Mã đề 132" hay "Thời gian làm bài" chỉ có ở đề thi.
      2. Tên tệp.
      3. Hình dạng nội dung: có chia chương không, tỉ lệ câu trắc nghiệm đủ 4
         phương án, có sẵn phần lý thuyết không.
    """
    tin_hieu = " \n ".join(raw_signals or [])
    ten_tep = (filename or "").replace("_", " ").replace("-", " ")
    van_ban_dau = tin_hieu + "\n" + ten_tep

    diem_de_thi = _diem_theo_mau(van_ban_dau, DAU_VET_DE_THI)
    diem_sach = _diem_theo_mau(van_ban_dau, DAU_VET_SACH)

    tong_cau = len(questions or [])
    so_chuong = len({
        (getattr(q, "chapter_title", "") or "").strip()
        for q in (questions or [])
        if (getattr(q, "chapter_title", "") or "").strip()
    })
    co_ly_thuyet = any(
        len((getattr(q, "theory_box", "") or "").strip()) > 15
        for q in (questions or [])
    )
    so_trac_nghiem = sum(
        1 for q in (questions or [])
        if len(getattr(q, "options", None) or []) >= 4
    )
    ti_le_tn = so_trac_nghiem / max(1, tong_cau)

    # Hình dạng nội dung
    if so_chuong >= 2:
        diem_sach += 4
    if co_ly_thuyet:
        diem_sach += 2
    # Đề thi điển hình: 20-60 câu, gần như toàn trắc nghiệm, không chia chương
    if ti_le_tn >= 0.7 and so_chuong == 0:
        diem_de_thi += 3
    if 20 <= tong_cau <= 60 and so_chuong == 0:
        diem_de_thi += 2

    if diem_de_thi > diem_sach and diem_de_thi >= 4:
        loai = DE_THI
    elif so_chuong >= 2 or diem_sach >= 5:
        loai = SACH
    else:
        loai = CHUYEN_DE

    # Độ tin cậy: chênh lệch càng lớn càng chắc
    chenh = abs(diem_de_thi - diem_sach)
    if chenh >= 6:
        do_tin = "cao"
    elif chenh >= 3:
        do_tin = "vừa"
    else:
        do_tin = "thấp"

    return {
        "doc_type": loai,
        "ten_hien_thi": TEN_HIEN_THI[loai],
        "do_tin_cay": do_tin,
        "diem_de_thi": diem_de_thi,
        "diem_sach": diem_sach,
        "so_chuong": so_chuong,
        "ti_le_trac_nghiem": round(ti_le_tn, 2),
        "tong_cau": tong_cau,
        "co_ly_thuyet_san": co_ly_thuyet,
    }


def trich_thong_tin_de_thi(raw_signals: Optional[List[str]] = None) -> Dict[str, str]:
    """
    Rút các thông tin hành chính từ đề gốc để dựng lại đúng phần đầu đề thi:
    đơn vị ra đề, tên kỳ thi, môn, thời gian, mã đề.
    """
    van_ban = " \n ".join(raw_signals or [])
    out = {"don_vi": "", "ky_thi": "", "mon": "", "thoi_gian": "", "ma_de": ""}

    m = re.search(r"(sở\s*g(?:iáo\s*dục)?[^\n]{0,60})", van_ban, re.I)
    if m:
        out["don_vi"] = m.group(1).strip().upper()
    else:
        m = re.search(r"(trường\s*th(?:pt|cs)[^\n]{0,50})", van_ban, re.I)
        if m:
            out["don_vi"] = m.group(1).strip().upper()

    m = re.search(r"(đề\s*(?:thi|kiểm\s*tra)[^\n]{0,70})", van_ban, re.I)
    if m:
        out["ky_thi"] = m.group(1).strip().upper()

    m = re.search(r"môn\s*[:\s]*([^\n,;]{2,30})", van_ban, re.I)
    if m:
        out["mon"] = m.group(1).strip()

    m = re.search(r"thời\s*gian\s*(?:làm\s*bài)?\s*[:\s]*(\d{2,3})\s*phút", van_ban, re.I)
    if m:
        out["thoi_gian"] = f"{m.group(1)} phút"

    m = re.search(r"mã\s*đề\s*(?:thi)?\s*[:\s]*(\d{3,4})", van_ban, re.I)
    if m:
        out["ma_de"] = m.group(1)

    return out
