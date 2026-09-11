import sys
from pathlib import Path
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import pymupdf

pdf_path = Path("input/[PDF] Đề thi chọn học sinh giỏi môn Toán lớp 11 năm học 2019 - 2020 cụm Tân Yên - Bắc Giang.pdf")
doc = pymupdf.open(str(pdf_path))
page = doc[0]

data = page.get_text("dict")
spans = []
for b in data.get("blocks", []):
    if "lines" in b:
        for l in b["lines"]:
            for s in l["spans"]:
                spans.append(s)

print(f"Total spans on page 0: {len(spans)}")
for idx, s in enumerate(spans[:60]):
    text = s["text"]
    bbox = [round(x, 1) for x in s["bbox"]]
    font = s["font"]
    print(f"[{idx}] {bbox} Font: {font:<20} Text: {repr(text)}")
