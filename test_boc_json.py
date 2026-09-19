# -*- coding: utf-8 -*-
"""
Kiểm bộ bóc JSON trước những kiểu trả lời thật mà mô hình hay sinh ra.

Mỗi ca dưới đây là một dạng đã gặp hoặc rất dễ gặp khi gọi Claude — nhà cung
cấp này KHÔNG có chế độ ép JSON như Gemini, nên chuỗi trả về phải tự lo.
"""

import sys

from core.ai_provider import boc_json

CA = [
    ("JSON thuần",
     '{"a": 1, "b": "hai"}', {"a": 1, "b": "hai"}),

    ("Bọc trong rào ```json",
     '```json\n{"a": 1}\n```', {"a": 1}),

    ("Có câu dẫn trước JSON",
     'Đây là kết quả bạn cần:\n{"a": 1}', {"a": 1}),

    # Ca này làm hỏng nguyên một lô 25 câu ngày 19/09/2026
    ("Xuống dòng THẬT bên trong chuỗi",
     '{"loi_tua": "Dòng một\nDòng hai"}', {"loi_tua": "Dòng một\nDòng hai"}),

    ("Tab thật bên trong chuỗi",
     '{"x": "cột1\tcột2"}', {"x": "cột1\tcột2"}),

    ("Rào + câu dẫn + xuống dòng thật",
     'Kết quả:\n```json\n{"q": "Giải:\nx = 2"}\n```', {"q": "Giải:\nx = 2"}),

    ("Mảng ở ngoài cùng",
     '[{"a": 1}, {"a": 2}]', [{"a": 1}, {"a": 2}]),
]

HONG = [
    ("Chuỗi rỗng", ""),
    ("Không có JSON nào", "Xin lỗi, tôi không thể trả lời."),
]


def main() -> int:
    loi = 0
    print("CÁC DẠNG PHẢI BÓC ĐƯỢC")
    print("-" * 74)
    for ten, vao, mong in CA:
        try:
            ra = boc_json(vao)
            ok = ra == mong
            if not ok:
                print("  HỎNG  %-38s -> %r" % (ten, ra))
                loi += 1
            else:
                print("  ĐẠT   %s" % ten)
        except Exception as e:
            print("  HỎNG  %-38s -> ném %s: %s" % (ten, type(e).__name__, e))
            loi += 1

    print()
    print("CÁC DẠNG PHẢI BÁO LỖI, KHÔNG ĐƯỢC ÂM THẦM TRẢ VỀ RỖNG")
    print("-" * 74)
    for ten, vao in HONG:
        try:
            ra = boc_json(vao)
            print("  HỎNG  %-38s -> trả về %r thay vì báo lỗi" % (ten, ra))
            loi += 1
        except Exception:
            print("  ĐẠT   %s" % ten)

    print()
    print("KẾT QUẢ:", "ĐẠT" if loi == 0 else "%d LỖI" % loi)
    return loi


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
