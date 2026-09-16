# -*- coding: utf-8 -*-
"""
Thư viện trình bày chung cho SÁCH TOÁN TIỂU HỌC — phong cách "bài tập cuối tuần":
viền trang trí, tiêu đề dạng băng-rôn màu, mỗi bài là một thẻ màu có huy hiệu số,
phông chữ thân thiện, dòng ghi họ tên/lớp, lời động viên.

Dùng cho Family A (có newdoc()):   from kidbook import *
Dùng cho Family B (doc dựng sẵn):  import kidbook; kidbook.restyle(doc, grade="LỚP 4")
"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ---- màu ----
NAVY = RGBColor(0x1A, 0x2E, 0x53)
CORAL = RGBColor(0xC0, 0x3A, 0x2C)
TEAL = RGBColor(0x0D, 0x76, 0x5C)
GREEN = RGBColor(0x1E, 0x6B, 0x3A)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
INK = RGBColor(0x22, 0x22, 0x22)

_GRADES = {
    "MẦM NON": ("EC407A", "TỦ SÁCH TOÁN NHÍ — MẦM NON"),
    "LỚP 1": ("F57C00", "TỦ SÁCH TOÁN NHÍ — LỚP 1"),
    "LỚP 2": ("2E7D32", "TỦ SÁCH TOÁN NHÍ — LỚP 2"),
    "LỚP 3": ("1565C0", "TỦ SÁCH TOÁN NHÍ — LỚP 3"),
    "LỚP 4": ("6A1B9A", "TỦ SÁCH TOÁN NHÍ — LỚP 4"),
    "LỚP 5": ("00695C", "TỦ SÁCH TOÁN NHÍ — LỚP 5"),
}
_STATE = {"grade": "LỚP 3", "accent": "1565C0", "kicker": "TỦ SÁCH TOÁN NHÍ", "n": 0}

# thẻ bài: (nền, viền, emoji)
_CARDS = [
    ("FFF3E0", "F57C00", "✏️"),
    ("E8F5E9", "2E7D32", "🔢"),
    ("E3F2FD", "1565C0", "📐"),
    ("F3E5F5", "6A1B9A", "⭐"),
    ("FCE4EC", "EC407A", "🧮"),
    ("E0F2F1", "00695C", "📏"),
    ("FFFDE7", "F9A825", "🎯"),
    ("EDE7F6", "5E35B1", "🌈"),
]
BODY_FONT = "Times New Roman"
HEAD_FONT = "Times New Roman"


def set_grade(label):
    label = label.strip().upper()
    _STATE["grade"] = label
    acc, kicker = _GRADES.get(label, ("1565C0", "TỦ SÁCH TOÁN NHÍ"))
    _STATE["accent"] = acc
    _STATE["kicker"] = kicker


# ---------------------------------------------------------------- xml helpers
def _shd(el_parent, hx):
    s = OxmlElement('w:shd')
    s.set(qn('w:val'), 'clear'); s.set(qn('w:color'), 'auto'); s.set(qn('w:fill'), hx)
    el_parent.append(s)


def _cell_shade(c, hx):
    _shd(c._tc.get_or_add_tcPr(), hx)


def _cell_border(c, hx, sz=8):
    tcPr = c._tc.get_or_add_tcPr()
    b = OxmlElement('w:tcBorders')
    for e in ('top', 'left', 'bottom', 'right'):
        el = OxmlElement(f'w:{e}')
        el.set(qn('w:val'), 'single'); el.set(qn('w:sz'), str(sz))
        el.set(qn('w:space'), '4'); el.set(qn('w:color'), hx)
        b.append(el)
    tcPr.append(b)
    # canh le trong cell cho deu
    mar = OxmlElement('w:tcMar')
    for e, v in (('top', '80'), ('left', '120'), ('bottom', '80'), ('right', '120')):
        m = OxmlElement(f'w:{e}'); m.set(qn('w:w'), v); m.set(qn('w:type'), 'dxa'); mar.append(m)
    tcPr.append(mar)


def _fullwidth(t):
    """dat bang rong 100% + layout co dinh -> vien ve deu 4 canh."""
    t.autofit = False
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    tblPr = t._tbl.tblPr
    tw = OxmlElement('w:tblW'); tw.set(qn('w:w'), '5000'); tw.set(qn('w:type'), 'pct'); tblPr.append(tw)
    lay = OxmlElement('w:tblLayout'); lay.set(qn('w:type'), 'fixed'); tblPr.append(lay)


def _para_shade_border(style_or_para, fill, border=None, sz=6):
    el = style_or_para.element if hasattr(style_or_para, 'element') else style_or_para._p
    pPr = el.get_or_add_pPr()
    for tag in ('w:shd', 'w:pBdr'):
        old = pPr.find(qn(tag))
        if old is not None:
            pPr.remove(old)
    if fill:
        _shd(pPr, fill)
    if border:
        pb = OxmlElement('w:pBdr')
        for e in ('top', 'left', 'bottom', 'right'):
            b = OxmlElement(f'w:{e}')
            b.set(qn('w:val'), 'single'); b.set(qn('w:sz'), str(sz))
            b.set(qn('w:space'), '4'); b.set(qn('w:color'), border)
            pb.append(b)
        pPr.append(pb)


def _page_border(section, accent):
    sectPr = section._sectPr
    old = sectPr.find(qn('w:pgBorders'))
    if old is not None:
        sectPr.remove(old)
    pb = OxmlElement('w:pgBorders')
    pb.set(qn('w:offsetFrom'), 'page')
    for e in ('top', 'left', 'bottom', 'right'):
        el = OxmlElement(f'w:{e}')
        el.set(qn('w:val'), 'doubleWave')
        el.set(qn('w:sz'), '10')
        el.set(qn('w:space'), '24')
        el.set(qn('w:color'), accent)
        pb.append(el)
    sectPr.append(pb)


# ---------------------------------------------------------------- doc setup
def _setup(d, grade=None):
    if grade:
        set_grade(grade)
    acc = _STATE["accent"]
    n = d.styles['Normal']
    n.font.name = BODY_FONT; n.font.size = Pt(12.5)
    n.paragraph_format.space_after = Pt(5); n.paragraph_format.line_spacing = 1.3
    # Heading 1 — băng-rôn màu
    h1 = d.styles['Heading 1']
    h1.font.name = HEAD_FONT; h1.font.size = Pt(15); h1.font.bold = True; h1.font.color.rgb = WHITE
    h1.paragraph_format.space_before = Pt(14); h1.paragraph_format.space_after = Pt(8)
    h1.paragraph_format.keep_with_next = True
    _para_shade_border(h1, acc, acc, sz=2)
    # Heading 2 — tên bài
    h2 = d.styles['Heading 2']
    h2.font.name = HEAD_FONT; h2.font.size = Pt(13); h2.font.bold = True
    h2.font.color.rgb = RGBColor.from_string(acc)
    h2.paragraph_format.space_before = Pt(10); h2.paragraph_format.space_after = Pt(3)
    h2.paragraph_format.keep_with_next = True
    _para_shade_border(h2, None, None)
    _p2 = h2.element.get_or_add_pPr()
    _pb = OxmlElement('w:pBdr')
    _bt = OxmlElement('w:bottom')
    _bt.set(qn('w:val'), 'single'); _bt.set(qn('w:sz'), '8'); _bt.set(qn('w:space'), '2'); _bt.set(qn('w:color'), acc)
    _pb.append(_bt); _p2.append(_pb)
    # Heading 3 — lời giải
    h3 = d.styles['Heading 3']
    h3.font.name = HEAD_FONT; h3.font.size = Pt(12); h3.font.bold = True; h3.font.italic = True
    h3.font.color.rgb = RGBColor(0x6D, 0x4C, 0x41)
    h3.paragraph_format.space_before = Pt(6); h3.paragraph_format.space_after = Pt(2)
    for sec in d.sections:
        sec.top_margin = sec.bottom_margin = Cm(1.9)
        sec.left_margin = sec.right_margin = Cm(2.1)
        _page_border(sec, acc)
    _STATE["n"] = 0
    return d


def restyle(doc, grade=None):
    """Cho Family B: áp phong cách lên doc đã dựng sẵn."""
    return _setup(doc, grade)


def newdoc(grade=None):
    return _setup(Document(), grade)


# ---------------------------------------------------------------- các khối
def _boxpara(doc, lines, fill, border, bsz=6, align=None):
    """Một đoạn văn có nền + viền 4 cạnh (Word vẽ đều), các dòng ngăn bằng line-break.
    lines: list các dòng, mỗi dòng là list (text, bold, size, rgb_or_None)."""
    p = doc.add_paragraph()
    if align:
        p.alignment = align
    p.paragraph_format.space_before = Pt(4); p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.25
    first_line = True
    for segs in lines:
        if not first_line:
            br = p.add_run(); br.add_break()
        first_line = False
        for (text, bold, size, col) in segs:
            r = p.add_run(text)
            r.bold = bold; r.font.size = Pt(size)
            if col is not None:
                r.font.color.rgb = col if isinstance(col, RGBColor) else RGBColor.from_string(col)
    _para_shade_border(p, fill, border, sz=bsz)
    return p


def nameline(doc):
    _boxpara(doc, [[("Họ và tên: …………………………………………      Lớp: ………      Ngày: ……/……", False, 12, INK)]],
             "F7F7F7", _STATE["accent"], bsz=4)


def banner(doc, text, emoji="📘"):
    _boxpara(doc, [[(f"{emoji}  {text}  {emoji}", True, 15.5, _STATE["accent"])]],
             "FFF6D6", _STATE["accent"], bsz=14, align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def footerbanner(doc, text="EM ĐÃ CỐ GẮNG RẤT NHIỀU — GIỎI QUÁ!"):
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    _boxpara(doc, [[(f"🌟  {text}  🌟", True, 14, GREEN)]],
             "EAF7E9", "2E7D32", bsz=14, align=WD_ALIGN_PARAGRAPH.CENTER)


def cover(doc, title, sub):
    acc = _STATE["accent"]
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before = Pt(36)
    r = p.add_run("✏️  🔢  ⭐  🧮  📐  🌈  📚"); r.font.size = Pt(18)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before = Pt(14)
    r = p.add_run(_STATE["kicker"]); r.font.size = Pt(13); r.font.color.rgb = RGBColor.from_string(acc); r.bold = True
    tlines = [[(seg, True, 25, acc)] for seg in str(title).split("\n")]
    _boxpara(doc, tlines, "FFF6D6", acc, bsz=16, align=WD_ALIGN_PARAGRAPH.CENTER)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before = Pt(12)
    r = p.add_run(sub); r.font.size = Pt(13.5); r.italic = True; r.font.color.rgb = CORAL
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before = Pt(34)
    r = p.add_run("Họ và tên: ………………………………………      Lớp: …………"); r.font.size = Pt(12.5)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before = Pt(6)
    r = p.add_run("Trường: ………………………………………………………………"); r.font.size = Pt(12.5)
    p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(36); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("🌈  CỐ LÊN! MỖI NGÀY MỘT BÀI, GIỎI TOÁN KHÔNG SAI!  🌈")
    r.font.size = Pt(12.5); r.bold = True; r.font.color.rgb = GREEN
    p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(10); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Biên soạn nội bộ — mọi đáp số được tính và kiểm chứng bằng phần mềm."); r.font.size = Pt(10.5)
    doc.add_page_break()


def probbox(doc, lines):
    """Thẻ bài màu, huy hiệu emoji, đổi màu luân phiên."""
    _STATE["n"] += 1
    fill, bd, emo = _CARDS[(_STATE["n"] - 1) % len(_CARDS)]
    spec = []
    for k, ln in enumerate(lines):
        if k == 0:
            spec.append([(emo + "  ", False, 12.5, None), (ln, True, 12.5, INK)])
        else:
            spec.append([(ln, False, 12.5, INK)])
    _boxpara(doc, spec, fill, bd, bsz=10)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def answerlines(doc, k=4):
    for _ in range(k):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(10)
        pb = OxmlElement('w:pBdr')
        b = OxmlElement('w:bottom')
        b.set(qn('w:val'), 'dotted'); b.set(qn('w:sz'), '6'); b.set(qn('w:space'), '1'); b.set(qn('w:color'), '9E9E9E')
        pb.append(b)
        p._p.get_or_add_pPr().append(pb)


def ghinho(doc, title, lines=None):
    if lines is None:                       # goi kieu ghinho(doc, noi_dung)
        lines = title if not isinstance(title, str) else [title]
        title = ""
    head = ("💡  GHI NHỚ — " + title).rstrip(" —").rstrip()
    spec = [[(head, True, 12.5, RGBColor(0x8D, 0x6E, 0x00))]]
    for ln in lines:
        spec.append([("• " + str(ln), False, 12, RGBColor(0x5D, 0x4A, 0x00))])
    _boxpara(doc, spec, "FFF8E1", "F9A825", bsz=10)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


# ghinho_box: chữ ký khác dùng trong l5_book23
def ghinho_box(doc, text):
    ghinho(doc, "", [text] if isinstance(text, str) else list(text))


def toc(doc):
    para = doc.add_paragraph(); run = para.add_run()
    for tag, txt in (('begin', None), ('instr', 'TOC \\o "1-2" \\h \\z \\u'), ('separate', None),
                     ('t', "Bấm chuột phải > Update Field."), ('end', None)):
        if tag == 'instr':
            e = OxmlElement('w:instrText'); e.set(qn('xml:space'), 'preserve'); e.text = txt
        elif tag == 't':
            e = OxmlElement('w:t'); e.text = txt
        else:
            e = OxmlElement('w:fldChar'); e.set(qn('w:fldCharType'), tag)
        run._r.append(e)


# ---------------------------------------------------------------- khối ĐỀ KIỂM TRA
def exam_header(doc, mon_lop, ky, thoigian="40 phút", de_so=None):
    """Đầu đề kiểm tra chuẩn nhà trường: TRƯỜNG / Lớp / Họ tên + tiêu đề + bảng chấm điểm."""
    acc = _STATE["accent"]
    t = doc.add_table(rows=1, cols=2); _fullwidth(t)
    lc, rc = t.rows[0].cells
    for c in (lc, rc):
        _no_cell_border(c)
    p = lc.paragraphs[0]
    p.add_run("Trường: ………………………………\n").font.size = Pt(12)
    p.add_run("Lớp: ………    Họ và tên: ………………………").font.size = Pt(12)
    p = rc.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(f"{ky}\n"); r.bold = True; r.font.size = Pt(13); r.font.color.rgb = RGBColor.from_string(acc)
    r = p.add_run(f"MÔN: {mon_lop}" + (f"  (Đề số {de_so})" if de_so else "") + "\n"); r.bold = True; r.font.size = Pt(12.5)
    r = p.add_run(f"(Thời gian làm bài: {thoigian})"); r.italic = True; r.font.size = Pt(11)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    # bảng Điểm - Nhận xét - GV chấm
    g = doc.add_table(rows=2, cols=3); _fullwidth(g)
    hdr = ["Điểm", "Nhận xét của thầy cô", "Giáo viên chấm"]
    for j, txt in enumerate(hdr):
        cc = g.rows[0].cells[j]; _cell_shade(cc, "F2F2F2"); _cell_border(cc, "9E9E9E", sz=6)
        rr = cc.paragraphs[0]; rr.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = rr.add_run(txt); run.bold = True; run.font.size = Pt(11.5)
    for j in range(3):
        cc = g.rows[1].cells[j]; _cell_border(cc, "9E9E9E", sz=6)
        cc.paragraphs[0].add_run("\n\n" if j != 2 else "1. ……………………\n2. ……………………").font.size = Pt(10)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def _no_cell_border(c):
    tcPr = c._tc.get_or_add_tcPr()
    b = OxmlElement('w:tcBorders')
    for e in ('top', 'left', 'bottom', 'right'):
        el = OxmlElement(f'w:{e}'); el.set(qn('w:val'), 'nil'); b.append(el)
    tcPr.append(b)


def phan_header(doc, text):
    """VD: 'I. PHẦN TRẮC NGHIỆM. (4 điểm)  Khoanh vào chữ cái trước câu trả lời đúng:'"""
    p = doc.add_paragraph()
    r = p.add_run(text); r.bold = True; r.font.size = Pt(12.5)
    r.font.color.rgb = RGBColor.from_string(_STATE["accent"])
    p.paragraph_format.space_before = Pt(8); p.paragraph_format.space_after = Pt(3)


def answerkey_table(doc, answers, per_row=8):
    """answers: list ('C', '0,5 điểm') hoặc chỉ 'C'. Bảng đáp án trắc nghiệm."""
    n = len(answers)
    for base in range(0, n, per_row):
        chunk = answers[base:base + per_row]
        g = doc.add_table(rows=2, cols=len(chunk)); _fullwidth(g)
        for j, a in enumerate(chunk):
            letter, diem = (a if isinstance(a, tuple) else (a, "0,5 điểm"))
            c0 = g.rows[0].cells[j]; _cell_shade(c0, "F2F2F2"); _cell_border(c0, "9E9E9E", sz=6)
            r = c0.paragraphs[0]; r.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = r.add_run(f"Câu {base + j + 1}\n({diem})"); run.bold = True; run.font.size = Pt(10)
            c1 = g.rows[1].cells[j]; _cell_border(c1, "9E9E9E", sz=6)
            r = c1.paragraphs[0]; r.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = r.add_run(letter); run.bold = True; run.font.size = Pt(12)
        doc.add_paragraph().paragraph_format.space_after = Pt(2)


# tương thích ngược: vài driver gọi _sh / _bd trực tiếp
def _sh(c, hx):
    _cell_shade(c, hx)


def _bd(c, rgb, sz=14):
    hx = rgb if isinstance(rgb, str) else '%02X%02X%02X' % tuple(rgb)
    _cell_border(c, hx, sz)
