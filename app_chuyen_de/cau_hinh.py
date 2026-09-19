# -*- coding: utf-8 -*-
"""
Khai báo app SOẠN CHUYÊN ĐỀ làm gì.

Mỗi app chỉ khai ở đây: tên, cổng, những loại đầu ra nó nhận, và thư mục làm
việc của riêng nó. Phần còn lại dùng chung ở `core/`.

Vì sao thư mục vào/ra phải RIÊNG: `prune_output_dir()` và `prune_ingest_dirs()`
quét cả thư mục để dọn tệp cũ. Ba app dùng chung một thư mục thì app này xóa
mất kết quả của app kia.
"""

from pathlib import Path

from core.loai_dau_ra import CHUYEN_DE_BT, TAI_LIEU_HSG

THU_MUC = Path(__file__).resolve().parent

TEN_APP = "Soạn Chuyên Đề"
MO_TA = "Chuyên đề bài tập và tài liệu bồi dưỡng học sinh giỏi"
CONG = 8503

# Chỉ hai loại. Người dùng không phải chọn giữa chín thứ như công cụ cũ.
LOAI_DAU_RA = [CHUYEN_DE_BT, TAI_LIEU_HSG]
LOAI_MAC_DINH = CHUYEN_DE_BT

THU_MUC_VAO = THU_MUC / "input"
THU_MUC_RA = THU_MUC / "output"
THU_MUC_TEMPLATES = THU_MUC / "templates"
THU_MUC_STATIC = THU_MUC / "static"

THU_MUC_VAO.mkdir(exist_ok=True)
THU_MUC_RA.mkdir(exist_ok=True)
