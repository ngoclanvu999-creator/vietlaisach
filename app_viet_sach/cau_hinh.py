# -*- coding: utf-8 -*-
"""
Khai báo app VIẾT LẠI SÁCH làm gì.

App này KHÔNG có "loại đầu ra" để chọn: đầu ra luôn là một cuốn sách biên soạn
lại từ tài liệu gốc. Vì vậy `LOAI_DAU_RA` để rỗng — trong `core/exporter.py`,
loại rỗng chính là nhánh mặc định dựng bố cục sách.
"""

from pathlib import Path

THU_MUC = Path(__file__).resolve().parent

TEN_APP = "Viết Lại Sách"
MO_TA = "Biên soạn lại tài liệu gốc thành sách Word chuẩn Nghị định 30"
# 8501 đang là cổng của công cụ cũ, còn chạy song song tới khi cả ba app được
# nghiệm thu. Dùng cổng riêng để hai bên không giành nhau.
CONG = 8504

# Rỗng = nhánh dựng sách. App này chỉ làm đúng một việc.
LOAI_DAU_RA = [""]
LOAI_MAC_DINH = ""

THU_MUC_VAO = THU_MUC / "input"
THU_MUC_RA = THU_MUC / "output"
THU_MUC_TEMPLATES = THU_MUC / "templates"
THU_MUC_STATIC = THU_MUC / "static"

THU_MUC_VAO.mkdir(exist_ok=True)
THU_MUC_RA.mkdir(exist_ok=True)
