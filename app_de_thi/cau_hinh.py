# -*- coding: utf-8 -*-
"""
Khai báo app SOẠN ĐỀ THI làm gì.

Năm loại đề dùng CHUNG một bộ dựng và một chuẩn nghiệp vụ; chúng chỉ khác nhau
ở thời gian làm bài, số câu và phạm vi kiến thức. Vì vậy app này thực chất là
MỘT việc, năm biến thể — không phải năm việc.
"""

from pathlib import Path

from core.loai_dau_ra import (DE_CHUONG_BAI, DE_GIUA_KI_1, DE_GIUA_KI_2,
                              DE_HOC_KI_1, DE_HOC_KI_2)

THU_MUC = Path(__file__).resolve().parent

TEN_APP = "Soạn Đề Thi"
MO_TA = "Bộ đề chuẩn 2025: ma trận · bản đặc tả · đề ba phần · hướng dẫn chấm"
CONG = 8502

LOAI_DAU_RA = [DE_CHUONG_BAI, DE_GIUA_KI_1, DE_GIUA_KI_2, DE_HOC_KI_1, DE_HOC_KI_2]
LOAI_MAC_DINH = DE_HOC_KI_1

THU_MUC_VAO = THU_MUC / "input"
THU_MUC_RA = THU_MUC / "output"
THU_MUC_TEMPLATES = THU_MUC / "templates"
THU_MUC_STATIC = THU_MUC / "static"

THU_MUC_VAO.mkdir(exist_ok=True)
THU_MUC_RA.mkdir(exist_ok=True)
