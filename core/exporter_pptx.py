# -*- coding: utf-8 -*-
"""
Dựng BÀI GIẢNG POWERPOINT (.pptx).

Đây là hạng mục độc lập, không dùng chung bộ dựng Word được: cả dự án chạy trên
python-docx, còn trình chiếu cần python-pptx và một cách nghĩ khác — slide là để
CHIẾU LÊN cho cả lớp nhìn, không phải để đọc. Vì vậy:

  - Mỗi slide một ý. Chữ to, ít dòng.
  - Đề bài và đáp án TÁCH thành hai slide liền nhau, để giáo viên cho học sinh
    suy nghĩ rồi mới bấm sang slide đáp án.
  - Không nhồi lời giải dài vào slide; phần đó đưa xuống ghi chú của người trình
    bày (notes), chỉ giáo viên nhìn thấy.

Trang trí theo cấp học: tiểu học được dùng màu tươi và biểu tượng, THPT giữ
trang nhã. Quy tắc này do người dùng đặt ra.
"""

from typing import Any, Dict, List

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# Khổ 16:9
RONG = Inches(13.333)
CAO = Inches(7.5)

BANG_MAU = {
    # (nền, tiêu đề, chữ, nhấn)
    "TIEU_HOC": (RGBColor(0xFF, 0xF8, 0xE7), RGBColor(0xD1, 0x5B, 0x1F),
                 RGBColor(0x33, 0x2C, 0x22), RGBColor(0x2E, 0x8B, 0x57)),
    "THCS": (RGBColor(0xF7, 0xFA, 0xFC), RGBColor(0x2B, 0x6C, 0xB0),
             RGBColor(0x1A, 0x20, 0x2C), RGBColor(0x2F, 0x85, 0x5A)),
    "THPT": (RGBColor(0xFF, 0xFF, 0xFF), RGBColor(0x1A, 0x36, 0x5D),
             RGBColor(0x1A, 0x20, 0x2C), RGBColor(0x2F, 0x85, 0x5A)),
}

FONT = "Times New Roman"
FONT_TRINH_CHIEU = "Arial"   # màn chiếu đọc chữ không chân dễ hơn


def _mau(cap_hoc: str):
    return BANG_MAU.get(cap_hoc, BANG_MAU["THPT"])


def _nen(slide, mau_nen):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = mau_nen


def _o_chu(slide, text, *, trai, tren, rong, cao, co=24, dam=False,
           mau=None, canh=PP_ALIGN.LEFT, font=FONT_TRINH_CHIEU):
    o = slide.shapes.add_textbox(trai, tren, rong, cao)
    khung = o.text_frame
    khung.word_wrap = True
    dong_dau = True
    for dong in str(text).split("\n"):
        p = khung.paragraphs[0] if dong_dau else khung.add_paragraph()
        dong_dau = False
        p.alignment = canh
        r = p.add_run()
        r.text = dong
        r.font.size = Pt(co)
        r.font.bold = dam
        r.font.name = font
        if mau is not None:
            r.font.color.rgb = mau
    return o


def _slide_trong(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])   # bố cục trống


def xuat_bai_giang(book, duong_dan, subject: str = "toan",
                   cap_hoc: str = "THPT", ten_bai: str = "",
                   options: Dict[str, Any] = None):
    """Dựng tệp .pptx và lưu ra đường dẫn."""
    opts = options or {}
    mau_nen, mau_tieu_de, mau_chu, mau_nhan = _mau(cap_hoc)
    trang_tri = cap_hoc == "TIEU_HOC"

    ds: List[Any] = list(getattr(book, "questions", None) or [])
    if not ds:
        for ch in getattr(book, "chapters", None) or []:
            ds.extend(ch.questions)

    prs = Presentation()
    prs.slide_width = RONG
    prs.slide_height = CAO

    mon = "TOÁN" if subject == "toan" else "VẬT LÍ"
    tieu_de = (ten_bai or getattr(book, "new_title", "") or "Bài giảng").strip()

    # ---- Slide bìa ----
    s = _slide_trong(prs)
    _nen(s, mau_nen)
    _o_chu(s, f"MÔN {mon}", trai=Inches(1), tren=Inches(2.2),
           rong=Inches(11.3), cao=Inches(0.8), co=26, mau=mau_nhan,
           canh=PP_ALIGN.CENTER)
    _o_chu(s, ("🌟 " if trang_tri else "") + tieu_de.upper(),
           trai=Inches(1), tren=Inches(3.0), rong=Inches(11.3), cao=Inches(1.6),
           co=44, dam=True, mau=mau_tieu_de, canh=PP_ALIGN.CENTER)
    _o_chu(s, "Giáo viên: ……………………", trai=Inches(1), tren=Inches(5.0),
           rong=Inches(11.3), cao=Inches(0.6), co=20, mau=mau_chu,
           canh=PP_ALIGN.CENTER)

    # ---- Slide mục tiêu ----
    s = _slide_trong(prs)
    _nen(s, mau_nen)
    _o_chu(s, ("🎯 " if trang_tri else "") + "MỤC TIÊU BÀI HỌC",
           trai=Inches(0.8), tren=Inches(0.6), rong=Inches(11.7), cao=Inches(1.0),
           co=34, dam=True, mau=mau_tieu_de)
    _o_chu(s,
           "• Nắm được kiến thức trọng tâm của bài\n"
           "• Vận dụng giải được các dạng bài cơ bản\n"
           "• Nhận ra và tránh được sai lầm thường gặp",
           trai=Inches(1.2), tren=Inches(2.0), rong=Inches(11.0), cao=Inches(3.0),
           co=28, mau=mau_chu)

    # ---- Mỗi bài: một slide đề + một slide đáp án ----
    for i, q in enumerate(ds, 1):
        # Slide đề
        s = _slide_trong(prs)
        _nen(s, mau_nen)
        _o_chu(s, ("✏️ " if trang_tri else "") + f"BÀI {i}",
               trai=Inches(0.8), tren=Inches(0.5), rong=Inches(11.7), cao=Inches(0.8),
               co=30, dam=True, mau=mau_tieu_de)
        _o_chu(s, getattr(q, "new_content", ""),
               trai=Inches(1.0), tren=Inches(1.6), rong=Inches(11.3), cao=Inches(1.8),
               co=26, mau=mau_chu)

        pa = (getattr(q, "new_options", None) or [])[:4]
        if pa:
            _o_chu(s, "\n".join(pa),
                   trai=Inches(1.4), tren=Inches(3.6), rong=Inches(10.5),
                   cao=Inches(2.6), co=24, mau=mau_chu)

        s.notes_slide.notes_text_frame.text = (
            "Cho học sinh suy nghĩ 1–2 phút trước khi chuyển slide đáp án.")

        # Slide đáp án
        s2 = _slide_trong(prs)
        _nen(s2, mau_nen)
        _o_chu(s2, ("✅ " if trang_tri else "") + f"BÀI {i} — ĐÁP ÁN",
               trai=Inches(0.8), tren=Inches(0.5), rong=Inches(11.7), cao=Inches(0.8),
               co=30, dam=True, mau=mau_nhan)

        dap = (getattr(q, "correct_answer", "") or "").strip().upper()[:1]
        than = ""
        for o in pa:
            if str(o).strip()[:1].upper() == dap:
                than = str(o).strip()
        _o_chu(s2, than or f"Đáp án: {dap}",
               trai=Inches(1.2), tren=Inches(1.8), rong=Inches(11.0), cao=Inches(1.2),
               co=34, dam=True, mau=mau_nhan)

        # Lời giải KHÔNG nhồi lên slide — đưa xuống ghi chú, chỉ giáo viên thấy
        lg = (getattr(q, "solution_method1", "") or "").strip()
        tom_tat = lg[:220] + ("…" if len(lg) > 220 else "")
        if tom_tat and opts.get("solution", True):
            _o_chu(s2, tom_tat,
                   trai=Inches(1.2), tren=Inches(3.2), rong=Inches(11.0),
                   cao=Inches(2.6), co=20, mau=mau_chu)
        s2.notes_slide.notes_text_frame.text = lg or "(chưa có lời giải)"

    # ---- Slide kết ----
    s = _slide_trong(prs)
    _nen(s, mau_nen)
    _o_chu(s, ("🎉 " if trang_tri else "") + "CẢM ƠN CÁC EM ĐÃ CHÚ Ý",
           trai=Inches(1), tren=Inches(3.0), rong=Inches(11.3), cao=Inches(1.4),
           co=40, dam=True, mau=mau_tieu_de, canh=PP_ALIGN.CENTER)

    duong_dan.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(duong_dan))
    return {"so_slide": len(prs.slides._sldIdLst), "so_bai": len(ds)}
