import re
from pathlib import Path
from typing import Optional, Tuple
import sympy as sp
import latex2mathml.commands
from lxml import etree

COMMON_XSL_PATHS = [
    Path(r"C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL"),
    Path(r"C:\Program Files (x86)\Microsoft Office\root\Office16\MML2OMML.XSL"),
    Path(r"C:\Program Files\Microsoft Office\Office16\MML2OMML.XSL"),
    Path(r"C:\Program Files (x86)\Microsoft Office\Office16\MML2OMML.XSL"),
    Path(r"C:\Program Files\Microsoft Office\Office15\MML2OMML.XSL"),
    Path(r"C:\Program Files (x86)\Microsoft Office\Office15\MML2OMML.XSL"),
]

_xslt_transformer = None

def get_xslt_transformer():
    global _xslt_transformer
    if _xslt_transformer is not None:
        return _xslt_transformer
    for path in COMMON_XSL_PATHS:
        if path.exists():
            try:
                xslt_doc = etree.parse(str(path))
                _xslt_transformer = etree.XSLT(xslt_doc)
                return _xslt_transformer
            except Exception:
                pass
    return None

def latex_to_omml(latex_code: str) -> Optional[etree._Element]:
    """Chuyển đổi chuỗi LaTeX thành thẻ XML OMML (<m:oMath>) để nhúng trực tiếp vào Word .docx"""
    if not latex_code or not latex_code.strip():
        return None
    try:
        mathml = latex2mathml.commands.process_latex(latex_code.strip())
        transformer = get_xslt_transformer()
        if transformer is not None:
            mml_tree = etree.fromstring(mathml.encode("utf-8"))
            omml_tree = transformer(mml_tree)
            return omml_tree.getroot()
    except Exception:
        pass
    return None

LATEX_TO_UNICODE_MAP = {
    r"\alpha": "α", r"\beta": "β", r"\gamma": "γ", r"\delta": "δ", r"\epsilon": "ε",
    r"\theta": "θ", r"\lambda": "λ", r"\mu": "μ", r"\pi": "π", r"\sigma": "σ",
    r"\omega": "ω", r"\Delta": "Δ", r"\Omega": "Ω", r"\Sigma": "Σ",
    r"\le": "≤", r"\leq": "≤", r"\ge": "≥", r"\geq": "≥", r"\ne": "≠", r"\neq": "≠",
    r"\approx": "≈", r"\pm": "±", r"\times": "×", r"\div": "÷", r"\cdot": "·",
    r"\in": "∈", r"\notin": "∉", r"\subset": "⊂", r"\cup": "∪", r"\cap": "∩",
    r"\infty": "∞", r"\forall": "∀", r"\exists": "∃", r"\rightarrow": "→",
    r"\Rightarrow": "⇒", r"\Leftrightarrow": "⇔", r"\perp": "⊥", r"\parallel": "∥",
    r"\degree": "°", r"^\circ": "°"
}

SUPERSCRIPT_MAP = {
    '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
    '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
    '+': '⁺', '-': '⁻', '=': '⁼', '(': '⁽', ')': '⁾',
    'n': 'ⁿ', 'i': 'ⁱ', 'x': 'ˣ', 'y': 'ʸ'
}

SUBSCRIPT_MAP = {
    '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
    '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉',
    '+': '₊', '-': '₋', '=': '₌', '(': '₍', ')': '₎',
    'a': 'ₐ', 'e': 'ₑ', 'o': 'ₒ', 'x': 'ₓ', 'h': 'ₕ',
    'k': 'ₖ', 'l': 'ₗ', 'm': 'ₘ', 'n': 'ₙ', 'p': 'ₚ',
    's': 'ₛ', 't': 'ₜ'
}

def latex_to_unicode(text: str) -> str:
    """Chuyển đổi các ký hiệu LaTeX thông dụng thành ký tự Unicode toán học dễ đọc"""
    if not text:
        return ""
    res = text
    for cmd, sym in LATEX_TO_UNICODE_MAP.items():
        res = res.replace(cmd, sym)
    
    # Xử lý mũ: x^{2} hoặc x^2 -> x²
    def replace_sup(match):
        content = match.group(1) or match.group(2)
        return "".join(SUPERSCRIPT_MAP.get(c, c) for c in content)
    res = re.sub(r"\^\{([^{}]+)\}|\^([0-9n+-])", replace_sup, res)
    
    # Xử lý chỉ số dưới: x_{1} hoặc x_1 -> x₁
    def replace_sub(match):
        content = match.group(1) or match.group(2)
        return "".join(SUBSCRIPT_MAP.get(c, c) for c in content)
    res = re.sub(r"_\{([^{}]+)\}|_([0-9a-z])", replace_sub, res)
    
    # Xử lý phân số đơn giản: \frac{a}{b} -> (a / b)
    res = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"(\1 / \2)", res)
    # Xử lý căn bậc hai: \sqrt{a} -> √(a)
    res = re.sub(r"\\sqrt\{([^{}]+)\}", r"√(\1)", res)
    
    # Xóa dấu $ của LaTeX
    res = res.replace("$", "")
    return res

def verify_math_expression(expr_str: str) -> Optional[str]:
    """Kiểm tra và tính toán thử biểu thức bằng sympy"""
    try:
        clean = expr_str.replace("^", "**").replace("×", "*").replace("÷", "/")
        expr = sp.sympify(clean)
        simplified = sp.simplify(expr)
        return str(simplified)
    except Exception:
        return None
