import re
from pathlib import Path
from typing import Optional, Dict

SYMBOL_CHAR_MAP: Dict[str, str] = {
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

def clean_symbol_text(text: str) -> str:
    """Chuyển đổi các ký tự Symbol/MathType độc quyền từ Word/PDF sang Unicode toán học chuẩn"""
    if not text:
        return ""
    res = []
    for c in text:
        res.append(SYMBOL_CHAR_MAP.get(c, c))
    cleaned = "".join(res)

    # Dọn dẹp các ký tự mũi tên vectơ bị nhân đôi do font ligature (→→→→ -> →)
    cleaned = re.sub(r'→+', '→', cleaned)
    # Dọn dẹp ngoặc kép MathType { { { -> {
    cleaned = re.sub(r'\{\s*\{+', '{', cleaned)
    cleaned = re.sub(r'\}\s*\}+', '}', cleaned)

    return cleaned

SUPERSCRIPT_DIGITS = {
    '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
    '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
    '+': '⁺', '-': '⁻', 'n': 'ⁿ', 'x': 'ˣ'
}

def format_math_typography(text: str) -> str:
    """Chuẩn hóa typography cho văn bản toán học (số mũ, khoảng cách, dấu)"""
    if not text:
        return ""

    s = clean_symbol_text(text)

    # Chuẩn hóa x 5 -> x⁵, x 2 -> x²
    def replace_pow(m):
        var = m.group(1)
        num = m.group(2)
        sup = "".join(SUPERSCRIPT_DIGITS.get(c, c) for c in num)
        return f"{var}{sup}"

    s = re.sub(r'\b([a-zA-Z\)])\s*([0-9]{1,2})\b(?!\s*(?:h|phút|giây|cm|m|kg|điểm))', replace_pow, s)

    # Chuẩn hóa vectơ: v → -> v⃗, AB → -> AB⃗
    s = re.sub(r'\b([A-Z]{1,2}|[a-z])\s*→', r'\1⃗', s)

    # Xóa khoảng trắng trước các dấu câu , . : ;
    s = re.sub(r'\s+([,.:;?])', r'\1', s)
    # Đảm bảo có khoảng trắng sau dấu câu
    s = re.sub(r'([,.:;?])(?=[^\s\d])', r'\1 ', s)

    # Chuẩn hóa nhiều khoảng trắng liên tiếp
    s = " ".join(s.split())
    return s

def clean_paragraph_text(text: str) -> str:
    """Xóa bỏ các ngắt dòng \n bất thường trong một câu văn bản"""
    if not text:
        return ""
    # Chuyển \r\n thành khoảng trắng nếu không phải xuống dòng kép
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    merged = " ".join(lines)
    return format_math_typography(merged)
