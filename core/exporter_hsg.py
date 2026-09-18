# -*- coding: utf-8 -*-
"""
Dựng TÀI LIỆU HỌC SINH GIỎI.

Khác hẳn tài liệu ôn thi thường, nên không dùng chung bộ dựng sách được:

  - Chủ yếu TỰ LUẬN. Đề HSG không cho sẵn bốn phương án để đoán; bắt học sinh
    trình bày lập luận đầy đủ. Vì vậy ở đây các phương án bị GIẤU ĐI và chỉ
    hiện lại trong phần đáp án cuối, như một gợi ý đối chiếu. Đây không phải
    suy đoán: 12/13 đề HSG thật trong mẫu không có một câu trắc nghiệm nào.
  - CHIA THEO CHUYÊN ĐỀ. Chủ dự án chỉ định tài liệu HSG phải chia theo chuyên
    đề bám đề HSG các năm. Thứ tự chuyên đề lấy theo tần suất đo được trên 13
    đề thật — hình học không gian trước vì có mặt ở 12/13 đề và chiếm 19,8%
    điểm. Xem `core/chuyen_de_hsg.py`.
  - Trong mỗi chuyên đề, độ khó dồn về vận dụng cao. Bài xếp theo mức độ tăng
    dần chứ không theo thứ tự tài liệu gốc, để học sinh vào guồng rồi mới gặp
    bài khó.
  - Lời giải viết kỹ hơn, kèm phần "nhận xét" nêu ý tưởng then chốt — cái học
    sinh giỏi cần là hướng nghĩ, không phải các bước bấm máy.
"""

from typing import List, Any, Dict, Tuple

from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from core.chuyen_de_hsg import TEN as TEN_CHUYEN_DE, gom_theo_chuyen_de

FONT_MAIN = "Times New Roman"
COLOR_PRIMARY = RGBColor(26, 54, 93)
COLOR_MUTED = RGBColor(74, 85, 104)
COLOR_KHO = RGBColor(197, 48, 48)

# Xếp bài theo độ khó tăng dần
THU_TU_MUC = {"biết": 0, "biet": 0, "nhận biết": 0, "nhan biet": 0,
              "hiểu": 1, "hieu": 1, "thông hiểu": 1, "thong hieu": 1,
              "vận dụng": 2, "van dung": 2,
              "vận dụng cao": 3, "van dung cao": 3}


def _p(doc, text="", *, bold=False, italic=False, size=12, align=None,
       color=None, before=0, after=0):
    para = doc.add_paragraph()
    if align is not None:
        para.alignment = align
    para.paragraph_format.space_before = Pt(before)
    para.paragraph_format.space_after = Pt(after)
    if text:
        r = para.add_run(text)
        r.bold = bold
        r.italic = italic
        r.font.name = FONT_MAIN
        r.font.size = Pt(size)
        if color is not None:
            r.font.color.rgb = color
    return para


def _do_kho(q) -> int:
    lv = (getattr(q, "level", "") or "").strip().lower()
    return THU_TU_MUC.get(lv, 2)


def _nhan_do_kho(muc: int) -> str:
    """
    Tên ba mức độ PHẢI khớp skill `tai-lieu-hsg`, nếu không thì mô hình được
    dặn một đằng mà tệp dựng ra một nẻo. Tài liệu HSG bỏ hẳn mức dễ: bài dễ
    nhất cũng đã ở mức vận dụng.
    """
    return ("Vận dụng", "Vận dụng", "Vận dụng cao", "Olympic")[min(muc, 3)]


def _dap_so_cua(q) -> str:
    """Lấy nội dung phương án đúng, để in ở phần đáp án cuối tài liệu."""
    dap = (getattr(q, "correct_answer", "") or "").strip().upper()[:1]
    for o in (getattr(q, "new_options", None) or []):
        s = str(o).strip()
        if s[:1].upper() == dap:
            return s[2:].strip() if len(s) > 2 else s
    return ""


def xuat_tai_lieu_hsg(doc, book, subject: str = "toan", options: Dict[str, Any] = None):
    """Dựng trọn tài liệu HSG vào tài liệu Word đang mở."""
    opts = options or {}
    ds: List[Any] = list(getattr(book, "questions", None) or [])
    if not ds:
        for ch in getattr(book, "chapters", None) or []:
            ds.extend(ch.questions)

    # Chia theo chuyên đề trước, trong mỗi chuyên đề mới xếp theo độ khó tăng
    # dần. Danh sách phẳng `ds` được dựng lại theo đúng thứ tự in ra, để số
    # hiệu bài ở phần đề và phần hướng dẫn giải luôn khớp nhau.
    khoi: List[Tuple[str, List[Any]]] = [
        (ma, sorted(v, key=_do_kho)) for ma, v in gom_theo_chuyen_de(ds).items()
    ]
    ds = [q for _, v in khoi for q in v]

    mon = "TOÁN" if subject == "toan" else "VẬT LÍ"
    _p(doc, "TÀI LIỆU BỒI DƯỠNG HỌC SINH GIỎI", bold=True, size=16,
       color=COLOR_PRIMARY, align=WD_ALIGN_PARAGRAPH.CENTER, after=4)
    _p(doc, f"Môn {mon} — {getattr(book, 'new_title', '')}", italic=True, size=12,
       align=WD_ALIGN_PARAGRAPH.CENTER, after=6)
    _p(doc, "Yêu cầu: trình bày lời giải đầy đủ, có lập luận. "
            "Không chấp nhận đáp số không kèm cách làm.",
       italic=True, size=11, color=COLOR_MUTED,
       align=WD_ALIGN_PARAGRAPH.CENTER, after=14)

    # ----- Mục lục chuyên đề -----
    # Chỉ in khi tài liệu có từ hai chuyên đề trở lên; một chuyên đề thì mục lục
    # chỉ tổ chiếm chỗ.
    if len(khoi) > 1:
        _p(doc, "MỤC LỤC CHUYÊN ĐỀ", bold=True, size=13, color=COLOR_PRIMARY,
           before=6, after=4)
        for j, (ma, v) in enumerate(khoi, 1):
            _p(doc, f"Chuyên đề {j}. {TEN_CHUYEN_DE.get(ma, ma)} ({len(v)} bài)",
               size=12, after=1)

    # ----- Phần đề: KHÔNG hiện phương án -----
    i = 0
    for j, (ma, v) in enumerate(khoi, 1):
        _p(doc, f"CHUYÊN ĐỀ {j}. {TEN_CHUYEN_DE.get(ma, ma).upper()}",
           bold=True, size=14, color=COLOR_PRIMARY, before=20, after=6)

        muc_hien_tai = -1
        for q in v:
            i += 1
            muc = _do_kho(q)
            if muc != muc_hien_tai:
                muc_hien_tai = muc
                _p(doc, f"MỨC ĐỘ: {_nhan_do_kho(muc).upper()}", bold=True, size=13,
                   color=COLOR_KHO if muc >= 3 else COLOR_PRIMARY, before=14, after=4)

            _p(doc, f"Bài {i}. {getattr(q, 'new_content', '')}", size=12,
               before=8, after=2)
            _p(doc, "Lời giải:", italic=True, size=11, color=COLOR_MUTED, after=0)
            for _ in range(4):
                _p(doc, "." * 96, size=11, color=COLOR_MUTED, after=0)

    # ----- Phần hướng dẫn giải -----
    doc.add_page_break()
    _p(doc, "HƯỚNG DẪN GIẢI", bold=True, size=15, color=COLOR_PRIMARY,
       align=WD_ALIGN_PARAGRAPH.CENTER, after=10)

    for i, q in enumerate(ds, 1):
        _p(doc, f"Bài {i} — {_nhan_do_kho(_do_kho(q))}", bold=True, size=12.5,
           color=COLOR_PRIMARY, before=12, after=2)

        lg = (getattr(q, "solution_method1", "") or "").strip()
        if lg:
            _p(doc, lg, size=12, after=3)

        dap_so = _dap_so_cua(q)
        if dap_so:
            _p(doc, f"Đáp số: {dap_so}", bold=True, size=12, after=3)

        # Nhận xét: ý tưởng then chốt — thứ học sinh giỏi thực sự cần
        nhan_xet = (getattr(q, "trap_warning", "") or "").strip()
        if nhan_xet and opts.get("traps", True):
            _p(doc, f"Nhận xét: {nhan_xet}", italic=True, size=11.5,
               color=COLOR_MUTED, after=2)

    return {
        "so_bai": len(ds),
        "so_chuyen_de": len(khoi),
        "chuyen_de": [TEN_CHUYEN_DE.get(ma, ma) for ma, _ in khoi],
    }
