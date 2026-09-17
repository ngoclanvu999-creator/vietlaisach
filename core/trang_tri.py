# -*- coding: utf-8 -*-
"""
Cách trình bày thay đổi theo CẤP HỌC.

Cùng một nội dung, trẻ lớp 2 và học sinh lớp 12 cần hai cách bày khác hẳn nhau.
Tài liệu tiểu học trình bày khô khan như đề thi THPT thì trẻ không muốn đọc;
ngược lại tài liệu THPT đầy biểu tượng thì mất tính nghiêm túc.

Quy tắc người dùng đặt ra:
  - Tiểu học : chữ to hơn, thoáng hơn, có biểu tượng, có dòng kẻ để viết bài
  - THCS     : trung tính
  - THPT     : trang trọng, không biểu tượng
  - GIÁO ÁN  : mọi cấp đều nghiêm ngặt, không trang trí — là hồ sơ chuyên môn

Mô-đun này chỉ mô tả CÁCH BÀY. Giọng văn nằm ở `skill_loader.huong_dan_giong_van()`
và đi vào câu lệnh gửi cho AI; hai thứ đó phải khớp nhau.
"""

from dataclasses import dataclass, field
from typing import Dict, List

from docx.shared import RGBColor

TIEU_HOC = "TIEU_HOC"
THCS = "THCS"
THPT = "THPT"


@dataclass
class CachBay:
    """Bộ tham số trình bày cho một cấp học."""
    co_chu: float = 13.0            # cỡ chữ thân bài
    co_de_bai: float = 13.0
    gian_dong: float = 1.25
    cach_bai: int = 12              # khoảng cách trước mỗi bài, point
    dau_bai: str = "▶"              # ký hiệu đứng trước số bài
    icon_muc: Dict[str, str] = field(default_factory=dict)
    dong_ke_lam_bai: int = 0        # số dòng chấm chừa cho học sinh viết
    co_dong_ho_ten: bool = False    # dòng "Họ và tên … Lớp …" đầu tài liệu
    mau_dau_bai: tuple = (26, 54, 93)

    @property
    def mau(self) -> RGBColor:
        return RGBColor(*self.mau_dau_bai)


BANG = {
    TIEU_HOC: CachBay(
        co_chu=14.0, co_de_bai=14.0, gian_dong=1.45, cach_bai=16,
        dau_bai="🔹",
        icon_muc={
            "ly_thuyet": "📖", "bai_tap": "✏️", "loi_giai": "💡",
            "dap_an": "✅", "meo": "🌟", "bay": "⚠️",
        },
        dong_ke_lam_bai=3,
        co_dong_ho_ten=True,
        mau_dau_bai=(209, 91, 31),      # cam ấm, hợp tài liệu cho trẻ
    ),
    THCS: CachBay(
        co_chu=13.0, co_de_bai=13.0, gian_dong=1.30, cach_bai=13,
        dau_bai="▶",
        mau_dau_bai=(43, 108, 176),
    ),
    THPT: CachBay(
        co_chu=13.0, co_de_bai=13.0, gian_dong=1.25, cach_bai=12,
        dau_bai="▶",
        mau_dau_bai=(26, 54, 93),
    ),
}

# Giáo án: mọi cấp đều dùng chung một cách bày nghiêm ngặt.
CACH_BAY_NGHIEM_NGAT = CachBay(
    co_chu=13.0, co_de_bai=13.0, gian_dong=1.25, cach_bai=12,
    dau_bai="", icon_muc={}, dong_ke_lam_bai=0,
    co_dong_ho_ten=False, mau_dau_bai=(26, 54, 93),
)


def cach_bay(cap_hoc: str = THPT, loai_dau_ra: str = "") -> CachBay:
    """
    Lấy bộ tham số trình bày.

    Giáo án luôn nghiêm ngặt bất kể cấp học: nó là hồ sơ chuyên môn nộp cho tổ
    và trường, không phải tài liệu phát cho học sinh.
    """
    if str(loai_dau_ra or "").upper() == "GIAO_AN":
        return CACH_BAY_NGHIEM_NGAT
    return BANG.get(cap_hoc, BANG[THPT])


def icon(cb: CachBay, ten_muc: str, mac_dinh: str = "") -> str:
    """Biểu tượng cho một mục; cấp không dùng biểu tượng thì trả về chuỗi rỗng."""
    bt = cb.icon_muc.get(ten_muc, mac_dinh)
    return f"{bt} " if bt else ""
