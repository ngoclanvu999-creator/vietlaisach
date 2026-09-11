import sys
from pathlib import Path
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import pymupdf

# Bảng dịch ký tự Symbol / MathType đặc biệt trong font PDF tiếng Việt
SYMBOL_CHAR_MAP = {
    '\uf0a1': 'ℝ',
    '\uf0a2': 'ℤ',
    '\uf070': 'π',
    '\uf072': '→',
    '\uf075': '→',
    '\uf8f1': '{',
    '\uf8f2': '{',
    '\uf8f3': '{',
    '\uf8fc': '}',
    '\uf8fd': '}',
    '\uf8fe': '}',
    '\uf0ce': '∈',
    '\uf0cf': '∉',
    '\uf0cc': '⊂',
    '\uf0c8': '∪',
    '\uf0c7': '∩',
    '\uf0b9': '≠',
    '\uf0a3': '≤',
    '\uf0b3': '≥',
    '\uf0b1': '±',
    '\uf0b4': '×',
    '\uf0b8': '÷',
    '\uf0a5': '∞',
    '\uf020': ' '
}

def clean_symbol_text(text: str) -> str:
    res = []
    for c in text:
        res.append(SYMBOL_CHAR_MAP.get(c, c))
    return "".join(res)

def extract_page_lines_spatially(page, line_threshold=14):
    """Trích xuất và phục hồi các dòng văn bản/công thức toán học dựa trên tọa độ không gian bbox"""
    data = page.get_text("dict")
    spans = []
    for b in data.get("blocks", []):
        if "lines" in b:
            for l in b["lines"]:
                for s in l["spans"]:
                    t = s["text"].strip()
                    if t:
                        spans.append({
                            "text": clean_symbol_text(s["text"]),
                            "bbox": s["bbox"],
                            "x0": s["bbox"][0],
                            "y0": s["bbox"][1],
                            "y1": s["bbox"][3],
                            "font": s["font"]
                        })

    # Nhóm các spans theo dải y (line band)
    # Sắp xếp thô theo y0
    spans.sort(key=lambda s: (s["y0"], s["x0"]))

    lines = []
    current_line = []
    current_y = None

    for s in spans:
        if current_y is None:
            current_line = [s]
            current_y = s["y0"]
        else:
            # Nếu cùng nằm trong khoảng dòng (math formula có thể chênh nhau tới 14-16pt)
            if abs(s["y0"] - current_y) <= line_threshold:
                current_line.append(s)
            else:
                # Sắp xếp các span trong cùng 1 dòng từ trái qua phải theo x0
                current_line.sort(key=lambda item: item["x0"])
                line_str = " ".join(item["text"].strip() for item in current_line if item["text"].strip())
                # Thu gọn khoảng trắng thừa
                line_str = " ".join(line_str.split())
                lines.append(line_str)

                current_line = [s]
                current_y = s["y0"]

    if current_line:
        current_line.sort(key=lambda item: item["x0"])
        line_str = " ".join(item["text"].strip() for item in current_line if item["text"].strip())
        line_str = " ".join(line_str.split())
        lines.append(line_str)

    return lines

pdf_path = Path("input/[PDF] Đề thi chọn học sinh giỏi môn Toán lớp 11 năm học 2019 - 2020 cụm Tân Yên - Bắc Giang.pdf")
doc = pymupdf.open(str(pdf_path))
page = doc[0]
reconstructed = extract_page_lines_spatially(page, line_threshold=15)

print("=== RECONSTRUCTED LINES ===")
for idx, l in enumerate(reconstructed):
    if "Câu" in l or "A." in l:
        print(f"[{idx}] {l}")
