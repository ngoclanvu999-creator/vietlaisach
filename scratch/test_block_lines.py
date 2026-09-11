import sys
from pathlib import Path
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import pymupdf

SYMBOL_MAP = {
    '\uf0a1': 'ℝ',
    '\uf0a2': 'ℤ',
    '\uf070': 'π',
    '\uf072': '→',
    '\uf075': '→',
    '\uf8f1': '{', '\uf8f2': '{', '\uf8f3': '{',
    '\uf8fc': '}', '\uf8fd': '}', '\uf8fe': '}',
    '\uf0ce': '∈', '\uf0cf': '∉', '\uf0cc': '⊂',
    '\uf0c8': '∪', '\uf0c7': '∩', '\uf0b9': '≠',
    '\uf0a3': '≤', '\uf0b3': '≥', '\uf0b1': '±',
    '\uf0b4': '×', '\uf0b8': '÷', '\uf0a5': '∞',
    '\uf020': ' '
}

def clean_symbols(s: str) -> str:
    return "".join(SYMBOL_MAP.get(c, c) for c in s)

pdf_path = Path("input/[PDF] Đề thi chọn học sinh giỏi môn Toán lớp 11 năm học 2019 - 2020 cụm Tân Yên - Bắc Giang.pdf")
doc = pymupdf.open(str(pdf_path))
page = doc[0]
data = page.get_text("dict")

for b_idx, b in enumerate(data.get("blocks", [])):
    if "lines" not in b:
        continue
    # Thu thập toàn bộ spans trong block
    spans = []
    for l in b["lines"]:
        for s in l["spans"]:
            txt = clean_symbols(s["text"]).strip()
            if txt:
                spans.append({
                    "text": txt,
                    "x0": s["bbox"][0],
                    "y0": s["bbox"][1],
                    "x1": s["bbox"][2],
                    "y1": s["bbox"][3],
                    "ymid": (s["bbox"][1] + s["bbox"][3]) / 2
                })
    if not spans:
        continue

    # Sắp xếp các span trong block:
    # Gom theo line band (ngưỡng 10pt)
    spans.sort(key=lambda s: (s["ymid"], s["x0"]))
    lines = []
    curr_line = [spans[0]]
    curr_y = spans[0]["ymid"]
    for s in spans[1:]:
        if abs(s["ymid"] - curr_y) <= 12:
            curr_line.append(s)
            curr_y = sum(x["ymid"] for x in curr_line) / len(curr_line)
        else:
            curr_line.sort(key=lambda x: x["x0"])
            lines.append(" ".join(x["text"] for x in curr_line))
            curr_line = [s]
            curr_y = s["ymid"]
    if curr_line:
        curr_line.sort(key=lambda x: x["x0"])
        lines.append(" ".join(x["text"] for x in curr_line))

    block_text = " ".join(lines)
    block_text = " ".join(block_text.split())
    if any(k in block_text for k in ["Câu", "A.", "B."]):
        print(f"\n--- BLOCK {b_idx} ---")
        print(block_text)
