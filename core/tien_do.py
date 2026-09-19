# -*- coding: utf-8 -*-
"""
Theo dõi tiến độ biên soạn, để giao diện báo SỐ THẬT thay vì hoạt cảnh.

VÌ SAO CÓ MÔ-ĐUN NÀY. Thanh tiến trình cũ trong `static/app.js` chạy theo đồng
hồ: cứ 1,8 giây nhảy một nấc, lên tới 92% rồi dừng, hoàn toàn không biết phía
sau làm tới đâu. Với tài liệu 348 câu — mười hai lô gọi AI, mỗi lô một tới hai
phút — người dùng nhìn thanh chạy xong rồi đứng im hai mươi phút và kết luận
phần mềm treo. Nó không treo; nó chỉ không nói gì.

Thiết kế cố ý đơn giản: phần mềm chạy trên máy cá nhân, mỗi lúc một người dùng
và một việc, nên chỉ cần MỘT trạng thái toàn cục chứ không cần hàng đợi hay mã
công việc. Có khoá để luồng báo tiến độ và luồng trả lời HTTP không giẫm nhau.
"""

import threading
import time
from typing import Any, Dict, Optional

_khoa = threading.Lock()

_TRANG_THAI: Dict[str, Any] = {
    "dang_chay": False,
    "viec": "",           # mô tả ngắn việc đang làm
    "lo_hien_tai": 0,
    "tong_lo": 0,
    "cau_xong": 0,
    "tong_cau": 0,
    "bat_dau": 0.0,
    "giay_moi_lo": [],    # thời gian từng lô, để ước lượng còn bao lâu
    "loi": "",
}


def bat_dau(tong_cau: int = 0, tong_lo: int = 0, viec: str = "Đang chuẩn bị"):
    with _khoa:
        _TRANG_THAI.update({
            "dang_chay": True, "viec": viec,
            "lo_hien_tai": 0, "tong_lo": tong_lo,
            "cau_xong": 0, "tong_cau": tong_cau,
            "bat_dau": time.time(), "giay_moi_lo": [], "loi": "",
        })


def dat_viec(viec: str):
    with _khoa:
        _TRANG_THAI["viec"] = viec


def xong_mot_lo(lo: int, tong_lo: int, so_cau: int, giay: float, ghi_chu: str = ""):
    with _khoa:
        _TRANG_THAI["lo_hien_tai"] = lo
        _TRANG_THAI["tong_lo"] = tong_lo
        _TRANG_THAI["cau_xong"] += so_cau
        _TRANG_THAI["giay_moi_lo"].append(round(giay, 1))
        _TRANG_THAI["viec"] = ghi_chu or f"Đã biên soạn xong lô {lo}/{tong_lo}"


def ghi_loi(tin: str):
    with _khoa:
        _TRANG_THAI["loi"] = tin[:300]


def ket_thuc():
    with _khoa:
        _TRANG_THAI["dang_chay"] = False
        _TRANG_THAI["viec"] = "Đã xong"


def doc() -> Dict[str, Any]:
    """
    Ảnh chụp trạng thái cho giao diện.

    `phan_tram` tính từ số lô đã xong, KHÔNG phải từ đồng hồ. Chừa lại 8% cuối
    cho các bước sau khi gọi AI (dựng file Word, thẩm định) — báo 100% trong khi
    còn việc là quay lại đúng thói xấu của thanh tiến trình cũ.
    """
    with _khoa:
        t = dict(_TRANG_THAI)

    tong = t["tong_lo"] or 0
    xong = t["lo_hien_tai"] or 0
    t["phan_tram"] = round(min(92, (xong / tong) * 92)) if tong else 0

    ds = t["giay_moi_lo"]
    if ds and tong > xong:
        t["uoc_con_lai_giay"] = round(sum(ds) / len(ds) * (tong - xong))
    else:
        t["uoc_con_lai_giay"] = None

    t["da_chay_giay"] = round(time.time() - t["bat_dau"]) if t["bat_dau"] else 0
    return t
