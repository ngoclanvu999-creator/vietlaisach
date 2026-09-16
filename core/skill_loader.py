# -*- coding: utf-8 -*-
"""
Nạp chuẩn nghiệp vụ từ tệp skill vào câu lệnh gửi cho AI.

Vì sao có mô-đun này: câu lệnh cũ trong rewriter chỉ dài khoảng 1.800 ký tự và
không hề biết đề thi từ 2025 có ba phần I/II/III hay thang điểm lũy tiến. Trong
khi đó các tệp skill đã mô tả đầy đủ. Skill thực chất CHÍNH LÀ câu lệnh — việc
còn thiếu chỉ là đem nó sang đúng chỗ.

Skill nằm trong repo (`skills/`) chứ không phải `~/.claude/skills`, vì trên máy
chủ triển khai không có thư mục cá nhân đó. Dùng `scripts/dong_bo_skill.py` để
đồng bộ hai nơi, giữ một nguồn sự thật duy nhất.
"""

import os
import re
from pathlib import Path
from typing import List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent

# Cấp học — quyết định cả giọng văn lẫn mức trang trí
TIEU_HOC = "TIEU_HOC"
THCS = "THCS"
THPT = "THPT"
CAP_HOC = (TIEU_HOC, THCS, THPT)

TEN_CAP_HOC = {
    TIEU_HOC: "Tiểu học",
    THCS: "Trung học cơ sở",
    THPT: "Trung học phổ thông",
}


def thu_muc_skill() -> Path:
    """Thư mục skill; đổi được bằng biến môi trường SKILL_DIR khi cần thử nghiệm."""
    tu_moi_truong = os.environ.get("SKILL_DIR", "").strip()
    if tu_moi_truong:
        p = Path(tu_moi_truong)
        if p.is_dir():
            return p
    return BASE_DIR / "skills"


# ---------------------------------------------------------------------------
# Chọn skill nào cho tình huống nào
# ---------------------------------------------------------------------------
# Mỗi mục: (tên thư mục skill, danh sách tệp tham khảo kèm theo)
BANG_CHON = {
    (THPT, "DE_THI"): ("de-thi-thpt-2025", ["references/ma-tran-de.md"]),
    (THCS, "DE_THI"): ("de-thi-thpt-2025", []),
    (TIEU_HOC, "DE_THI"): ("toan-tieu-hoc", ["references/pham-vi-theo-lop.md"]),
    (TIEU_HOC, "SACH"): ("toan-tieu-hoc", ["references/pham-vi-theo-lop.md"]),
    (TIEU_HOC, "CHUYEN_DE"): ("toan-tieu-hoc", ["references/pham-vi-theo-lop.md"]),
}

# Những mục viết cho lập trình viên, không phải cho người soạn nội dung.
# Gửi chúng cho mô hình chỉ tốn token và làm loãng phần hướng dẫn thật.
_MUC_BO_QUA = re.compile(
    r"^#{1,3}\s*\d*\.?\s*("
    r"liên hệ|nguồn|kiến trúc|pipeline|deploy|dựng lại|tham chiếu mã|"
    r"engine|script|cấu trúc thư mục"
    r")",
    re.IGNORECASE | re.MULTILINE,
)

_FRONTMATTER = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.DOTALL)

_bo_nho: dict = {}


def _doc_sach_se(duong_dan: Path) -> str:
    """Đọc tệp skill, bỏ phần đầu YAML và các mục dành cho lập trình viên."""
    try:
        van_ban = duong_dan.read_text(encoding="utf-8")
    except OSError:
        return ""

    van_ban = _FRONTMATTER.sub("", van_ban)

    # Cắt bỏ từng mục nằm trong danh sách bỏ qua, tới đầu mục cùng cấp kế tiếp
    ket_qua = []
    dang_bo = False
    for dong in van_ban.splitlines():
        if dong.startswith("#"):
            dang_bo = bool(_MUC_BO_QUA.match(dong))
        if not dang_bo:
            ket_qua.append(dong)

    return "\n".join(ket_qua).strip()


def nap_van_ban_skill(
    cap_hoc: str = THPT,
    doc_type: str = "CHUYEN_DE",
    gioi_han_ky_tu: int = 14000,
) -> str:
    """
    Trả về phần chuẩn nghiệp vụ để chèn vào đầu câu lệnh.

    Chuỗi rỗng nghĩa là không có skill nào khớp — khi đó câu lệnh vẫn chạy với
    phần hướng dẫn chung, không được vì thiếu skill mà hỏng cả luồng.
    """
    khoa = (cap_hoc, doc_type, gioi_han_ky_tu)
    if khoa in _bo_nho:
        return _bo_nho[khoa]

    chon = BANG_CHON.get((cap_hoc, doc_type))
    if not chon:
        _bo_nho[khoa] = ""
        return ""

    ten_skill, ds_tham_khao = chon
    goc = thu_muc_skill() / ten_skill

    phan = []
    chinh = _doc_sach_se(goc / "SKILL.md")
    if chinh:
        phan.append(chinh)
    for rel in ds_tham_khao:
        them = _doc_sach_se(goc / rel)
        if them:
            phan.append(them)

    van_ban = "\n\n".join(phan).strip()
    if len(van_ban) > gioi_han_ky_tu:
        # Cắt ở ranh giới dòng để không đứt giữa một bảng hay một câu
        van_ban = van_ban[:gioi_han_ky_tu].rsplit("\n", 1)[0]
        van_ban += "\n\n(Phần chuẩn còn dài, đã lược bớt phần cuối.)"

    _bo_nho[khoa] = van_ban
    return van_ban


# ---------------------------------------------------------------------------
# Giọng văn và mức trang trí theo cấp học
# ---------------------------------------------------------------------------
GIONG_VAN = {
    TIEU_HOC: (
        "GIỌNG VĂN — TIỂU HỌC:\n"
        "- Câu ngắn, mỗi câu một ý. Dùng từ đời thường, tránh từ Hán Việt khó.\n"
        "- Xưng hô thân thiện: \"em\", \"chúng mình\". Đề bài gắn với đồ vật, con vật,\n"
        "  đồ ăn, trò chơi mà trẻ quen thuộc.\n"
        "- Lời giải viết như đang giảng cho trẻ: nói rõ làm bước nào trước, vì sao.\n"
        "- TUYỆT ĐỐI không dùng kiến thức vượt quá phạm vi lớp."
    ),
    THCS: (
        "GIỌNG VĂN — TRUNG HỌC CƠ SỞ:\n"
        "- Trung tính, rõ ràng, bắt đầu dùng thuật ngữ toán học chuẩn.\n"
        "- Lời giải trình bày từng bước có căn cứ, nêu rõ định lý hay công thức đã dùng."
    ),
    THPT: (
        "GIỌNG VĂN — TRUNG HỌC PHỔ THÔNG:\n"
        "- Trang trọng, học thuật, đúng thuật ngữ chuyên môn.\n"
        "- Lời giải chặt chẽ như bài mẫu của giáo viên, nêu rõ căn cứ từng bước.\n"
        "- Không dùng biểu tượng cảm xúc, không văn phong vui nhộn."
    ),
}


def huong_dan_giong_van(cap_hoc: str = THPT) -> str:
    return GIONG_VAN.get(cap_hoc, GIONG_VAN[THPT])


def duoc_trang_tri(cap_hoc: str, doc_type: str) -> bool:
    """
    Tiểu học được thêm biểu tượng và trang trí cho bắt mắt — TRỪ giáo án.

    Giáo án ở mọi cấp là hồ sơ chuyên môn nộp cho tổ và trường, phải bám khung
    Công văn 5512, không trang trí. Đây là quy tắc người dùng đặt ra.
    """
    if str(doc_type or "").upper() == "GIAO_AN":
        return False
    return cap_hoc == TIEU_HOC


# ---------------------------------------------------------------------------
# Đoán cấp học từ nội dung
# ---------------------------------------------------------------------------
# Tên tệp trong kho thường viết không dấu ("BT_cuoi_tuan_lop_2.docx"), nên mọi
# mẫu đều phải nhận cả dạng có dấu lẫn không dấu. Đây chính là chỗ đã sai lần đầu.
# Tên tệp trong kho viết không dấu và ngăn bằng gạch dưới ("BT_cuoi_tuan_lop_2"),
# nên mẫu phải nhận cả dạng có dấu lẫn không dấu, và coi "_", "-", "." là dấu
# ngăn y như khoảng trắng. Hai chỗ này đều đã sai ở lần viết đầu.
_NGAN = r"[\s_.\-]*"
_LOP = r"l[ớo]p" + _NGAN

_DAU_HIEU_TIEU_HOC = re.compile(
    r"(ti[ểe]u" + _NGAN + r"h[ọo]c"
    r"|" + _LOP + r"[1-5](?!\d)"
    r"|m[ầa]m" + _NGAN + r"non"
    r"|m[ẫa]u" + _NGAN + r"gi[áa]o"
    r"|cu[ốo]i" + _NGAN + r"tu[ầa]n"
    r"|phi[ếe]u" + _NGAN + r"b[àa]i" + _NGAN + r"t[ậa]p"
    r"|b[ảa]ng" + _NGAN + r"nh[âa]n)",
    re.IGNORECASE,
)
_DAU_HIEU_THCS = re.compile(
    r"(thcs"
    r"|trung" + _NGAN + r"h[ọo]c" + _NGAN + r"c[ơo]" + _NGAN + r"s[ởo]"
    r"|" + _LOP + r"[6-9](?!\d))",
    re.IGNORECASE,
)
_DAU_HIEU_THPT = re.compile(
    r"(thpt"
    r"|trung" + _NGAN + r"h[ọo]c" + _NGAN + r"ph[ổo]" + _NGAN + r"th[ôo]ng"
    r"|" + _LOP + r"1[0-2](?!\d)"
    r"|t[ốo]t" + _NGAN + r"nghi[ệe]p"
    r"|t[íi]ch" + _NGAN + r"ph[âa]n"
    r"|logarit|nguy[êe]n" + _NGAN + r"h[àa]m"
    r"|dao" + _NGAN + r"đ[ộo]ng"
    r"|h[ìi]nh" + _NGAN + r"ch[óo]p)",
    re.IGNORECASE,
)


def phat_hien_cap_hoc(cac_doan: Optional[List[str]] = None, ten_tep: str = "") -> str:
    """
    Đoán cấp học. Chỉ để GỢI Ý SẴN cho người dùng, không quyết định thay họ —
    cùng nguyên tắc với nhận diện loại tài liệu.

    Mặc định trả về THPT vì đó là phần lớn kho tài liệu hiện có.
    """
    van_ban = " ".join([ten_tep] + list(cac_doan or [])[:40])[:12000]

    diem = {
        TIEU_HOC: len(_DAU_HIEU_TIEU_HOC.findall(van_ban)),
        THCS: len(_DAU_HIEU_THCS.findall(van_ban)),
        THPT: len(_DAU_HIEU_THPT.findall(van_ban)),
    }
    cao_nhat = max(diem, key=lambda k: diem[k])
    return cao_nhat if diem[cao_nhat] > 0 else THPT
