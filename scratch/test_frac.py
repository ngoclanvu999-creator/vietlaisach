import sys
from pathlib import Path
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import pymupdf

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

def reconstruct_math_lines(page, line_band_height=26):
    """
    Thuật toán không gian cao cấp:
    1. Lấy toàn bộ span của trang.
    2. Nhóm các span cùng thuộc một dòng lớn (line band ~ 26pt bao gồm cả phân số, số mũ, chỉ số dưới).
    3. Trong mỗi dòng, phát hiện các cụm phân số (top/bottom overlap horizontally) và ghép thành 'num / den'.
    4. Trả về các dòng văn bản toán học hoàn hảo, liền mạch!
    """
    data = page.get_text("dict")
    spans = []
    for b in data.get("blocks", []):
        if "lines" in b:
            for l in b["lines"]:
                for s in l["spans"]:
                    t = clean_symbol_text(s["text"]).strip()
                    if t:
                        spans.append({
                            "text": t,
                            "x0": s["bbox"][0],
                            "y0": s["bbox"][1],
                            "x1": s["bbox"][2],
                            "y1": s["bbox"][3],
                            "ymid": (s["bbox"][1] + s["bbox"][3]) / 2,
                            "font": s["font"]
                        })

    if not spans:
        return []

    # Sắp xếp thô theo ymid
    spans.sort(key=lambda s: (s["ymid"], s["x0"]))

    # Nhóm thành các dòng lớn
    lines_bands = []
    current_band = [spans[0]]
    current_band_y = spans[0]["ymid"]

    for s in spans[1:]:
        if abs(s["ymid"] - current_band_y) <= line_band_height:
            current_band.append(s)
            # Cập nhật trung bình ymid
            current_band_y = sum(item["ymid"] for item in current_band) / len(current_band)
        else:
            lines_bands.append(current_band)
            current_band = [s]
            current_band_y = s["ymid"]
    if current_band:
        lines_bands.append(current_band)

    # Xử lý từng dòng lớn
    result_lines = []
    for band in lines_bands:
        if not band:
            continue

        band_mean_y = sum(s["ymid"] for s in band) / len(band)

        # Sắp xếp theo x0
        band.sort(key=lambda s: s["x0"])

        # Gom các phần tử thành các cụm x
        # Nếu có các phần tử chồng lấn x (overlap x > 50%), phân biệt top/bottom thành phân số
        tokens = []
        i = 0
        while i < len(band):
            s = band[i]
            # Kiểm tra xem có span nào khác trong band overlap x với span s không
            overlap_group = [s]
            j = i + 1
            while j < len(band):
                next_s = band[j]
                # Kiểm tra giao khoảng [x0, x1]
                overlap_len = min(s["x1"], next_s["x1"]) - max(s["x0"], next_s["x0"])
                min_w = min(s["x1"] - s["x0"], next_s["x1"] - next_s["x0"])
                if min_w > 0 and (overlap_len / min_w) > 0.35 and abs(s["ymid"] - next_s["ymid"]) > 5:
                    overlap_group.append(next_s)
                    j += 1
                else:
                    break

            if len(overlap_group) > 1:
                # Có phân số hoặc chỉ số
                # Tách thành phần trên (ymid < mean) và phần dưới (ymid >= mean)
                top_spans = [item for item in overlap_group if item["ymid"] < band_mean_y]
                bot_spans = [item for item in overlap_group if item["ymid"] >= band_mean_y]

                top_spans.sort(key=lambda item: item["x0"])
                bot_spans.sort(key=lambda item: item["x0"])

                top_txt = "".join(item["text"] for item in top_spans)
                bot_txt = "".join(item["text"] for item in bot_spans)

                if top_txt and bot_txt:
                    tokens.append(f"({top_txt} / {bot_txt})")
                elif top_txt:
                    tokens.append(top_txt)
                elif bot_txt:
                    tokens.append(bot_txt)

                i = j
            else:
                tokens.append(s["text"])
                i += 1

        line_str = " ".join(tokens)
        # Làm sạch các dấu ngoặc { { } } thừa
        line_str = line_str.replace("{ {", "{").replace("} }", "}")
        # Làm sạch khoảng trắng xung quanh toán tử
        line_str = " ".join(line_str.split())
        result_lines.append(line_str)

    return result_lines

pdf_path = Path("input/[PDF] Đề thi chọn học sinh giỏi môn Toán lớp 11 năm học 2019 - 2020 cụm Tân Yên - Bắc Giang.pdf")
doc = pymupdf.open(str(pdf_path))
page = doc[0]
res = reconstruct_math_lines(page, line_band_height=24)

print("=== HOÀN THIỆN TÁI TẠO TOÁN HỌC TRANG 1 ===")
for idx, l in enumerate(res):
    print(f"L{idx}: {l}")
