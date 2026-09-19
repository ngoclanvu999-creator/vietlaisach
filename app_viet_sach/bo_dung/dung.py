# -*- coding: utf-8 -*-
"""
Dựng tệp Word cho app VIẾT LẠI SÁCH.

TẠM THỜI ỦY THÁC CHO `core/exporter.py`. Bố cục sách hiện vẫn nằm trong đó cùng
với bảng rẽ nhánh chín loại, vì công cụ cũ còn chạy song song tới khi cả ba app
được nghiệm thu (đó là lựa chọn của chủ dự án, để luôn có đường lui).

Loại đầu ra để RỖNG nên `export()` rơi qua hết mọi nhánh và xuống đúng phần
dựng sách — không nhánh nào khớp thì đó chính là nhánh mặc định.

Bước 6 của kế hoạch: xóa công cụ cũ, chuyển bố cục sách sang
`app_viet_sach/bo_dung/exporter_sach.py` và bỏ hẳn bảng rẽ nhánh. Chép 600 dòng
sang đây ngay bây giờ thì hai bản sẽ trôi khác nhau trong lúc chuyển tiếp.
"""

from pathlib import Path
from typing import Any, Dict

from core.exporter import DocxBookExporter


def dung_tai_lieu(book, duong_ra: Path, kho_giay: str = "a4",
                  tuy_chon: Dict[str, Any] = None) -> Path:
    """Dựng trọn cuốn sách rồi lưu."""
    book.loai_dau_ra = ""          # bảo đảm rơi vào nhánh dựng sách
    duong_ra.parent.mkdir(parents=True, exist_ok=True)
    return DocxBookExporter.export(book, duong_ra,
                                   paper_format=kho_giay, options=tuy_chon)
