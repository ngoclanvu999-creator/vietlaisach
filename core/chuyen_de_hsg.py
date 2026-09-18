# -*- coding: utf-8 -*-
"""
Danh mục chuyên đề của tài liệu học sinh giỏi, và bộ phân loại câu vào chuyên đề.

Danh mục KHÔNG phải do trợ lý nghĩ ra. Nó là thống kê 108 ý hỏi của 13 đề HSG
Toán 11 thật do chủ dự án chỉ định; số liệu và cách đo ghi ở
`skills/tai-lieu-hsg/references/chuyen-de-do-tu-de.md`. Sửa danh mục ở đây thì
phải sửa cả tệp đó, nếu không skill dặn một đằng mà tệp dựng ra một nẻo — lỗi
này đã xảy ra một lần với tên các mức độ khó.

Ba nhóm ứng ba vòng thi:
    A  cốt lõi   85,5% điểm, có mặt ở >= 9/13 đề  -> ôn vòng trường là đủ
    B  bổ trợ    10,2% điểm                       -> thêm cho vòng tỉnh
    C  nâng cao   4,3% điểm, hiếm nhưng rất khó   -> đội tuyển quốc gia

Bộ phân loại chấm điểm theo từ khóa chứ không khớp câu đầu tiên trúng: một bài
"Cho hình chóp S.ABC ... tìm giá trị lớn nhất" vừa có dấu hiệu hình không gian
vừa có dấu hiệu bất đẳng thức, phải để trọng số quyết định chứ không để thứ tự
duyệt quyết định.
"""

import re
import unicodedata
from collections import OrderedDict
from typing import Any, Dict, List, Tuple

NHOM_A = "A"   # Cốt lõi
NHOM_B = "B"   # Bổ trợ
NHOM_C = "C"   # Nâng cao

TEN_NHOM = {
    NHOM_A: "Cốt lõi",
    NHOM_B: "Bổ trợ",
    NHOM_C: "Nâng cao",
}

# (mã, tên chuyên đề, nhóm, số đề có mặt trên 13, % điểm đo được)
DANH_MUC: Tuple[Tuple[str, str, str, int, float], ...] = (
    ("KHONG_GIAN", "Hình học không gian", NHOM_A, 12, 19.8),
    ("LUONG_GIAC", "Phương trình lượng giác", NHOM_A, 12, 12.4),
    ("DAY_SO", "Dãy số - cấp số - giới hạn dãy", NHOM_A, 12, 11.8),
    ("TO_HOP", "Tổ hợp - xác suất", NHOM_A, 11, 11.1),
    ("BAT_DANG_THUC", "Bất đẳng thức, GTLN - GTNN", NHOM_A, 11, 10.7),
    ("PHUONG_TRINH", "Phương trình, hệ phương trình, bất phương trình", NHOM_A, 9, 12.1),
    ("OXY", "Hình học phẳng và tọa độ Oxy", NHOM_A, 9, 7.6),
    ("GIOI_HAN", "Giới hạn hàm số - hàm số liên tục", NHOM_B, 8, 6.5),
    ("NHI_THUC", "Nhị thức Newton", NHOM_B, 4, 3.7),
    ("SO_HOC", "Số học", NHOM_C, 2, 1.3),
    ("DAO_HAM", "Đạo hàm - tiếp tuyến", NHOM_C, 1, 1.5),
    ("PHUONG_TRINH_HAM", "Phương trình hàm", NHOM_C, 1, 0.8),
    ("BIEN_HINH", "Phép biến hình", NHOM_C, 1, 0.7),
)

MA_KHAC = "KHAC"
TEN_KHAC = "Chưa xếp được chuyên đề"

TEN = {ma: ten for ma, ten, _, _, _ in DANH_MUC}
TEN[MA_KHAC] = TEN_KHAC
NHOM = {ma: nhom for ma, _, nhom, _, _ in DANH_MUC}
THU_TU = {ma: i for i, (ma, _, _, _, _) in enumerate(DANH_MUC)}


def danh_sach(nhom: str = "") -> List[str]:
    """Mã các chuyên đề, lọc theo nhóm nếu có. Giữ thứ tự đo được."""
    return [ma for ma, _, n, _, _ in DANH_MUC if not nhom or n == nhom]


def cho_vong_thi(vong: str) -> List[str]:
    """
    Chuyên đề cần soạn cho từng vòng thi. Vòng sau bao gồm vòng trước, vì học
    sinh thi tỉnh vẫn phải chắc phần cốt lõi.
    """
    v = (vong or "").strip().lower()
    if v.startswith("truong"):
        return danh_sach(NHOM_A)
    if v.startswith("tinh"):
        return danh_sach(NHOM_A) + danh_sach(NHOM_B)
    return [ma for ma, _, _, _, _ in DANH_MUC]


# ---------------------------------------------------------------------------
# Phân loại câu vào chuyên đề
# ---------------------------------------------------------------------------
# Trọng số đặt theo mức ĐẶC TRƯNG của dấu hiệu, không theo mức phổ biến:
#   4  chỉ chuyên đề này mới có ("hình chóp", "cấp số cộng", "nhị thức newton")
#   3  gần như chỉ chuyên đề này ("xác suất", "tiếp tuyến")
#   2  thường là chuyên đề này nhưng chuyên đề khác cũng dùng ("giải phương trình")
#   1  dấu hiệu yếu, chỉ đủ để phá thế hòa
#
# Mẫu viết KHÔNG DẤU và so trên chuỗi đã bỏ dấu, vì đề bóc từ PDF hay rụng dấu
# và tên tệp trong kho cũng viết không dấu.

_TU_KHOA: Dict[str, Tuple[Tuple[str, int], ...]] = {
    "KHONG_GIAN": (
        (r"hinh chop", 4), (r"tu dien", 4), (r"lang tru", 4), (r"hinh hop", 4),
        (r"thiet dien", 4), (r"hinh cau", 3), (r"mat cau", 3),
        (r"mat phang \(", 3), (r"mat ben", 3), (r"mat day", 3),
        # Tên hình chóp "S.ABC", "S.ABCD". Bắt buộc có dấu chấm: bỏ dấu chấm đi
        # thì mẫu ăn luôn chữ "song" trong "song song".
        (r"\bs\.[a-z]{3,4}\b", 3),
        (r"goc giua .{0,30}mat phang", 3),
        (r"khoang cach .{0,40}mat phang", 3),
        (r"cheo nhau", 3), (r"dong phang", 2), (r"trong khong gian", 2),
    ),
    "LUONG_GIAC": (
        # Không dùng \bsin\b: "sin2x" có \b sai chỗ nên trượt, mà \bsin lại ăn
        # luôn chữ "sinh" trong "học sinh" — đề HSG nào cũng có chữ đó.
        (r"\bsin(?!h)", 3), (r"\bcos", 3),
        (r"\btan(?![gh])", 2),          # tránh "tăng", "tanh"
        (r"\bcot ?[x0-9]", 3),          # tránh "cột", "cốt"
        (r"luong giac", 4),
    ),
    "DAY_SO": (
        (r"day so", 4), (r"cap so cong", 4), (r"cap so nhan", 4),
        (r"so hang tong quat", 4), (r"so hang dau", 3), (r"cong sai", 4),
        (r"cong boi", 4), (r"truy hoi", 4), (r"\bu_?n\b", 2), (r"\bx_?n\b", 1),
        (r"bi chan", 3), (r"lim\s*u", 3),
    ),
    "TO_HOP": (
        (r"xac suat", 4), (r"to hop", 3), (r"chinh hop", 4), (r"hoan vi", 4),
        (r"bien co", 4), (r"chon ngau nhien", 4), (r"lay ngau nhien", 4),
        (r"bao nhieu cach", 4), (r"co bao nhieu so", 3), (r"lap duoc bao nhieu", 4),
        (r"xep ngau nhien", 4), (r"gieo", 3), (r"quan bai|con suc sac|dong xu", 3),
    ),
    "BAT_DANG_THUC": (
        (r"bat dang thuc", 4), (r"gia tri lon nhat", 3), (r"gia tri nho nhat", 3),
        (r"\bgtln\b", 4), (r"\bgtnn\b", 4), (r"dat gia tri", 3),
        (r"cauchy|bunhiacopxki|bunyakovsky|am-gm", 4),
        (r"chung minh rang\s*:?\s*$", 1),
    ),
    "PHUONG_TRINH": (
        (r"giai phuong trinh", 2), (r"he phuong trinh", 4),
        (r"bat phuong trinh", 4), (r"bien luan", 3), (r"giai he", 4),
        (r"nghiem phan biet", 2), (r"tap nghiem", 2), (r"tam thuc", 3),
    ),
    "OXY": (
        (r"mat phang toa do", 4), (r"he truc toa do", 4), (r"he toa do", 4),
        (r"\boxy\b", 4), (r"phuong trinh duong thang", 3),
        (r"phuong trinh duong tron", 4), (r"duong tron ngoai tiep", 3),
        (r"duong tron noi tiep", 3), (r"toa do dinh", 4), (r"toa do diem", 3),
        (r"truc tam", 3), (r"trong tam tam giac", 2),
    ),
    "GIOI_HAN": (
        (r"tinh gioi han", 4), (r"lim\s*_?\s*x", 4), (r"lien tuc tai", 4),
        (r"ham so lien tuc", 4), (r"co it nhat .{0,15}nghiem", 3),
        (r"co duy nhat .{0,15}nghiem", 3), (r"co ba nghiem", 3),
    ),
    "NHI_THUC": (
        (r"nhi thuc newton", 4), (r"khai trien", 4), (r"he so cua", 3),
        (r"so hang chua", 3), (r"so hang khong chua", 4),
        (r"\bc_?\{?n\b|\bc\d+_?\d+\b", 2),
    ),
    "SO_HOC": (
        (r"so nguyen to", 4), (r"chinh phuong", 4), (r"chia het cho", 2),
        (r"uoc chung|boi chung", 4), (r"so nguyen duong n", 2), (r"dong du", 4),
    ),
    "DAO_HAM": (
        (r"tiep tuyen", 4), (r"dao ham", 3), (r"tiep xuc", 3),
    ),
    "PHUONG_TRINH_HAM": (
        (r"phuong trinh ham", 4), (r"ham so f lien tuc tren", 2),
        (r"f\(f\(", 4), (r"thoa man .{0,25}f\(x", 2),
    ),
    "BIEN_HINH": (
        (r"phep tinh tien", 4), (r"phep vi tu", 4), (r"phep quay", 4),
        (r"phep doi xung", 4), (r"phep bien hinh", 4), (r"phep dong dang", 4),
    ),
}

_DA_DICH = {ma: tuple((re.compile(p), w) for p, w in ds) for ma, ds in _TU_KHOA.items()}


def bo_dau(s: str) -> str:
    """Bỏ dấu tiếng Việt và hạ chữ thường, để mẫu không dấu khớp được cả hai kiểu."""
    s = (s or "").replace("đ", "d").replace("Đ", "D")
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s).lower()


def cham_diem(noi_dung: str) -> Dict[str, int]:
    """Điểm từng chuyên đề cho một câu. Công khai ra để gỡ lỗi khi xếp sai."""
    s = bo_dau(noi_dung)
    return {ma: sum(w for rx, w in ds if rx.search(s)) for ma, ds in _DA_DICH.items()}


def phan_loai(noi_dung: str) -> str:
    """
    Xếp một câu vào chuyên đề. Trả về MA_KHAC khi không đủ dấu hiệu — thà để
    trống còn hơn xếp bừa, vì tài liệu chia sai chuyên đề thì học sinh ôn trật.
    """
    diem = cham_diem(noi_dung)
    # Hòa điểm thì chuyên đề HIẾM thắng, không phải chuyên đề phổ biến thắng:
    # hòa nghĩa là hai dấu hiệu mạnh ngang nhau, mà dấu hiệu của chuyên đề hiếm
    # ("phép vị tự") đặc trưng hơn dấu hiệu của chuyên đề phổ biến ("Oxy").
    ma, cao = max(diem.items(), key=lambda kv: (kv[1], THU_TU[kv[0]]))
    return ma if cao >= 3 else MA_KHAC


def _noi_dung(q: Any) -> str:
    return " ".join(str(getattr(q, t, "") or "") for t in
                    ("title", "new_content", "original_content", "content"))


def gom_theo_chuyen_de(items: List[Any]) -> "OrderedDict[str, List[Any]]":
    """
    Gom danh sách câu thành các chuyên đề, theo đúng thứ tự đo được (chuyên đề
    hay ra nhất đứng trước). Chuyên đề không có câu nào thì không tạo mục rỗng.
    """
    tui: Dict[str, List[Any]] = {}
    for q in items:
        tui.setdefault(phan_loai(_noi_dung(q)), []).append(q)

    ra: "OrderedDict[str, List[Any]]" = OrderedDict()
    for ma, _, _, _, _ in DANH_MUC:
        if tui.get(ma):
            ra[ma] = tui[ma]
    if tui.get(MA_KHAC):
        ra[MA_KHAC] = tui[MA_KHAC]
    return ra
