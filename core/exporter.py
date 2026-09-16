from pathlib import Path
from typing import Optional, List
import docx
from docx.shared import Inches, Pt, RGBColor, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
from core.rewriter import RewrittenBook, RewrittenChapter, RewrittenQuestionItem
from core.loai_dau_ra import la_de as la_loai_de

# Bảng màu sắc chuẩn sư phạm & thanh lịch
COLOR_PRIMARY = RGBColor(26, 54, 93)       # Xanh Navy Đậm #1A365D (Chuẩn sách Bộ GD)
COLOR_SECONDARY = RGBColor(43, 108, 176)   # Xanh Dương #2B6CB0
COLOR_SUCCESS = RGBColor(47, 133, 90)      # Xanh Lá Sư Phạm #2F855A
COLOR_WARNING = RGBColor(197, 48, 48)      # Đỏ Cảnh Báo Bẫy #C53030
COLOR_TEXT_MAIN = RGBColor(26, 32, 44)     # Đen Than #1A202C (Dễ đọc, không chói)
COLOR_TEXT_MUTED = RGBColor(74, 85, 104)   # Xám #4A5568

FONT_MAIN = "Times New Roman"

def set_cell_background(cell, fill_hex: str):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_callout_borders(cell, border_color_hex: str, border_size_pt: int = 18):
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'  <w:top w:val="none"/>'
        f'  <w:left w:val="single" w:sz="{border_size_pt}" w:space="0" w:color="{border_color_hex}"/>'
        f'  <w:bottom w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)

def add_callout_box(doc: docx.Document, title: str, content: str, bg_hex: str, border_hex: str, title_color: RGBColor):
    """Chèn hộp ghi chú sư phạm chuẩn mực"""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(6.5)

    cell = table.cell(0, 0)
    set_cell_background(cell, bg_hex)
    set_callout_borders(cell, border_hex, border_size_pt=18)

    p_title = cell.paragraphs[0]
    p_title.paragraph_format.space_before = Pt(4)
    p_title.paragraph_format.space_after = Pt(4)
    run_title = p_title.add_run(title)
    run_title.bold = True
    run_title.font.name = FONT_MAIN
    run_title.font.size = Pt(11.5)
    run_title.font.color.rgb = title_color

    for line in content.strip().split("\n"):
        if not line.strip():
            continue
        p = cell.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.2
        run = p.add_run(line.strip())
        run.font.name = FONT_MAIN
        run.font.size = Pt(11)
        run.font.color.rgb = COLOR_TEXT_MAIN

    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(0)
    p_spacer.paragraph_format.space_after = Pt(4)


# Kích thước khổ giấy được hỗ trợ (rộng x cao, đơn vị milimét)
PAPER_SIZES_MM = {
    "a4": (210, 297),
    "b5": (176, 250),
}


class DocxBookExporter:
    @classmethod
    def apply_standard_page_setup(cls, section, paper_format: str = "a4"):
        """
        Thiết lập thể thức văn bản chuẩn Nghị định 30/2020/NĐ-CP.
        Mặc định khổ A4 với lề Trái 30mm (chừa gáy sách), Phải 15mm, Trên/Dưới 20mm.
        Khổ B5 dùng khi in sách bỏ túi.
        """
        width_mm, height_mm = PAPER_SIZES_MM.get((paper_format or "a4").lower(), PAPER_SIZES_MM["a4"])
        section.page_width = Mm(width_mm)
        section.page_height = Mm(height_mm)

        # Lề trang: Trái 30mm (đóng gáy sách), Phải 15mm, Trên 20mm, Dưới 20mm
        section.left_margin = Mm(30)
        section.right_margin = Mm(15)
        section.top_margin = Mm(20)
        section.bottom_margin = Mm(20)

    @classmethod
    def apply_default_style(cls, doc):
        """
        Đặt font mặc định cho toàn tài liệu. Nếu không làm bước này, mọi đoạn văn
        không được gán font tường minh sẽ rơi về Calibri 11pt của Word, sai thể thức.
        """
        try:
            style = doc.styles["Normal"]
            style.font.name = FONT_MAIN
            style.font.size = Pt(13)
            # Word dùng thuộc tính riêng cho bảng mã Đông Á, phải đặt kèm mới ăn chắc
            rpr = style.element.get_or_add_rPr()
            rfonts = rpr.get_or_add_rFonts()
            rfonts.set(qn("w:eastAsia"), FONT_MAIN)
            rfonts.set(qn("w:cs"), FONT_MAIN)
            style.paragraph_format.line_spacing = 1.25
        except Exception:
            pass

    # Mặc định bật hết. Người dùng tắt mục nào thì mục đó biến mất khỏi file Word.
    # Vị trí phần lời giải trong sách
    LOI_GIAI_SAU_MOI_BAI = "sau_moi_bai"   # in ngay dưới từng câu
    LOI_GIAI_CUOI_SACH = "cuoi_sach"       # dồn hết về cuối, học sinh tự làm trước

    DEFAULT_OPTIONS = {
        "theory": True,      # Phần I: lý thuyết nền tảng
        "foreword": True,    # Lời tựa truyền cảm hứng
        "secrets": True,     # Bí kíp thủ khoa
        "stem": True,        # Góc kết nối STEM
        "solution": True,    # Lời giải tự luận chi tiết
        "casio": True,       # Mẹo Casio
        "traps": True,       # Cảnh báo bẫy
        "answer_key": True,  # Bảng đáp án tra nhanh (khi lời giải dồn về cuối)
    }

    @classmethod
    def merge_options(cls, options: Optional[dict]) -> dict:
        merged = dict(cls.DEFAULT_OPTIONS)
        vi_tri = cls.LOI_GIAI_SAU_MOI_BAI
        if options:
            merged.update({k: bool(v) for k, v in options.items() if k in merged})
            gt = str(options.get("vi_tri_loi_giai", "") or "").strip()
            if gt in (cls.LOI_GIAI_SAU_MOI_BAI, cls.LOI_GIAI_CUOI_SACH):
                vi_tri = gt
        merged["vi_tri_loi_giai"] = vi_tri
        return merged

    @classmethod
    def render_question_item(cls, doc: docx.Document, q: RewrittenQuestionItem, options: Optional[dict] = None):
        """Trình bày từng câu hỏi theo chuẩn sư phạm Bộ GD&ĐT"""
        opts = cls.merge_options(options)

        # Đề mục câu hỏi
        p_qtitle = doc.add_paragraph()
        p_qtitle.paragraph_format.space_before = Pt(12)
        p_qtitle.paragraph_format.space_after = Pt(3)
        
        r_num = p_qtitle.add_run(f"▶ {q.title}")
        r_num.bold = True
        r_num.font.name = FONT_MAIN
        r_num.font.size = Pt(13)
        r_num.font.color.rgb = COLOR_PRIMARY if not q.is_added_new else COLOR_SUCCESS

        if q.is_added_new:
            r_badge = p_qtitle.add_run(" [MỚI BỔ SUNG]")
            r_badge.bold = True
            r_badge.font.size = Pt(10)
            r_badge.font.color.rgb = COLOR_SUCCESS

        # Nội dung đề bài
        p_qcontent = doc.add_paragraph()
        p_qcontent.paragraph_format.space_before = Pt(2)
        p_qcontent.paragraph_format.space_after = Pt(5)
        p_qcontent.paragraph_format.line_spacing = 1.25
        r_qc = p_qcontent.add_run(q.new_content)
        r_qc.font.name = FONT_MAIN
        r_qc.font.size = Pt(13)
        r_qc.font.color.rgb = COLOR_TEXT_MAIN

        # Các phương án trắc nghiệm A, B, C, D (dàn ô đều)
        if q.new_options:
            table_opt = doc.add_table(rows=2, cols=2)
            table_opt.alignment = WD_TABLE_ALIGNMENT.CENTER
            table_opt.autofit = False
            col_width = Inches(3.1)
            for row in table_opt.rows:
                for cell in row.cells:
                    cell.width = col_width

            for o_idx, opt_text in enumerate(q.new_options[:4]):
                row_i = o_idx // 2
                col_i = o_idx % 2
                c = table_opt.cell(row_i, col_i)
                set_cell_background(c, "F7FAFC")
                p_opt = c.paragraphs[0]
                p_opt.paragraph_format.space_before = Pt(3)
                p_opt.paragraph_format.space_after = Pt(3)
                r_opt = p_opt.add_run(opt_text)
                r_opt.font.name = FONT_MAIN
                r_opt.font.size = Pt(12)
                if q.correct_answer and opt_text.strip().startswith(q.correct_answer):
                    r_opt.bold = True
                    r_opt.font.color.rgb = COLOR_SUCCESS

            p_sp = doc.add_paragraph()
            p_sp.paragraph_format.space_before = Pt(0)
            p_sp.paragraph_format.space_after = Pt(4)

        # Ba phần dưới đây chỉ in kèm câu hỏi khi người dùng chọn để lời giải
        # NGAY SAU MỖI BÀI. Nếu chọn dồn về cuối sách thì bỏ qua hết ở đây,
        # phần render_solution_section() sẽ lo.
        if opts["vi_tri_loi_giai"] == cls.LOI_GIAI_CUOI_SACH:
            cls.render_separator(doc)
            return

        # Lời giải Tự luận chuẩn mực sư phạm
        if q.solution_method1 and opts["solution"]:
            p_sol1_head = doc.add_paragraph()
            p_sol1_head.paragraph_format.space_before = Pt(6)
            p_sol1_head.paragraph_format.space_after = Pt(2)
            r_s1_h = p_sol1_head.add_run("✎ Hướng dẫn giải chi tiết (Tự luận chuẩn mực):")
            r_s1_h.bold = True
            r_s1_h.italic = True
            r_s1_h.font.name = FONT_MAIN
            r_s1_h.font.size = Pt(12.5)
            r_s1_h.font.color.rgb = COLOR_SECONDARY

            for line in q.solution_method1.strip().split("\n"):
                if not line.strip():
                    continue
                p_sol_l = doc.add_paragraph()
                p_sol_l.paragraph_format.space_before = Pt(1)
                p_sol_l.paragraph_format.space_after = Pt(3)
                p_sol_l.paragraph_format.line_spacing = 1.25
                r_sol_l = p_sol_l.add_run(line.strip())
                r_sol_l.font.name = FONT_MAIN
                r_sol_l.font.size = Pt(12.5)
                r_sol_l.font.color.rgb = COLOR_TEXT_MAIN

        # Khung Kỹ thuật Casio & Mẹo nhanh
        if q.solution_method2 and opts["casio"]:
            add_callout_box(
                doc,
                title="💡 KỸ THUẬT BẤM MÁY CASIO FX-580VN X & TƯ DUY GIẢI NHANH",
                content=q.solution_method2,
                bg_hex="F0FDF4",
                border_hex="2F855A",
                title_color=COLOR_SUCCESS
            )

        # Khung Cảnh báo bẫy sai lầm
        if q.trap_warning and opts["traps"]:
            add_callout_box(
                doc,
                title="⚠️ BẪY ĐỀ THI & LỖI SAI HỌC SINH HAY MẮC PHẢI",
                content=q.trap_warning,
                bg_hex="FFF5F5",
                border_hex="C53030",
                title_color=COLOR_WARNING
            )

        cls.render_separator(doc)

    @classmethod
    def render_separator(cls, doc: docx.Document):
        """Đường kẻ phân cách nhẹ giữa các bài."""
        p_sep = doc.add_paragraph()
        p_sep.paragraph_format.space_before = Pt(4)
        p_sep.paragraph_format.space_after = Pt(8)
        p_sep.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_sep = p_sep.add_run("· · · — — — · · ·")
        r_sep.font.color.rgb = RGBColor(203, 213, 225)
        r_sep.font.size = Pt(8)

    @classmethod
    def render_solution_section(cls, doc: docx.Document, book: RewrittenBook, opts: dict):
        """
        Phần lời giải dồn về cuối sách.

        Dùng khi người dùng muốn học sinh tự làm hết bài rồi mới xem đáp án —
        in lời giải ngay dưới đề thì nhìn xuống là thấy, mất tác dụng luyện tập.
        """
        if not opts["solution"] and not opts["casio"] and not opts["traps"] and not opts["answer_key"]:
            return

        doc.add_page_break()
        p_head = doc.add_paragraph()
        p_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_head.paragraph_format.space_after = Pt(14)
        r_head = p_head.add_run("PHẦN LỜI GIẢI CHI TIẾT")
        r_head.bold = True
        r_head.font.name = FONT_MAIN
        r_head.font.size = Pt(17)
        r_head.font.color.rgb = COLOR_PRIMARY

        # Gom câu theo chương để lời giải bám đúng bố cục sách
        nhom = []
        if book.chapters:
            for ch in book.chapters:
                nhom.append((ch.title, ch.questions))
        else:
            nhom.append(("", book.questions))

        # Bảng đáp án tra nhanh đặt trước, để dò kết quả mà chưa cần đọc lời giải
        if opts["answer_key"]:
            for tieu_de, ds_cau in nhom:
                co_dap_an = [q for q in ds_cau if (q.correct_answer or "").strip()]
                if not co_dap_an:
                    continue
                if tieu_de:
                    p_ch = doc.add_paragraph()
                    p_ch.paragraph_format.space_before = Pt(10)
                    r_ch = p_ch.add_run(tieu_de)
                    r_ch.bold = True
                    r_ch.font.name = FONT_MAIN
                    r_ch.font.size = Pt(13)
                    r_ch.font.color.rgb = COLOR_SECONDARY
                cls.render_answer_key(doc, ds_cau)

        for tieu_de, ds_cau in nhom:
            if tieu_de:
                p_ch = doc.add_paragraph()
                p_ch.paragraph_format.space_before = Pt(16)
                p_ch.paragraph_format.space_after = Pt(8)
                r_ch = p_ch.add_run(tieu_de)
                r_ch.bold = True
                r_ch.font.name = FONT_MAIN
                r_ch.font.size = Pt(14)
                r_ch.font.color.rgb = COLOR_PRIMARY

            for q in ds_cau:
                p_t = doc.add_paragraph()
                p_t.paragraph_format.space_before = Pt(10)
                p_t.paragraph_format.space_after = Pt(3)
                r_t = p_t.add_run(f"{q.title}. ")
                r_t.bold = True
                r_t.font.name = FONT_MAIN
                r_t.font.size = Pt(13)
                r_t.font.color.rgb = COLOR_PRIMARY
                if q.correct_answer:
                    r_da = p_t.add_run(f"Đáp án {q.correct_answer.strip().upper()[:1]}")
                    r_da.bold = True
                    r_da.font.name = FONT_MAIN
                    r_da.font.size = Pt(12.5)
                    r_da.font.color.rgb = COLOR_SUCCESS

                if q.solution_method1 and opts["solution"]:
                    for line in q.solution_method1.strip().split("\n"):
                        if not line.strip():
                            continue
                        p_l = doc.add_paragraph()
                        p_l.paragraph_format.space_after = Pt(2)
                        p_l.paragraph_format.line_spacing = 1.25
                        r_l = p_l.add_run(line.strip())
                        r_l.font.name = FONT_MAIN
                        r_l.font.size = Pt(12.5)
                        r_l.font.color.rgb = COLOR_TEXT_MAIN

                if q.solution_method2 and opts["casio"]:
                    add_callout_box(doc, "💡 KỸ THUẬT BẤM MÁY CASIO FX-580VN X",
                                    q.solution_method2, "F0FDF4", "2F855A", COLOR_SUCCESS)
                if q.trap_warning and opts["traps"]:
                    add_callout_box(doc, "⚠️ BẪY ĐỀ THI & LỖI SAI HỌC SINH HAY MẮC",
                                    q.trap_warning, "FFF5F5", "C53030", COLOR_WARNING)


    # =======================================================================
    # KIỂU RIÊNG CHO ĐỀ THI
    # Đề thi phải đọc được như một đề thi thật: học sinh làm bài trước, xem đáp
    # án sau. Chen lời giải và mẹo Casio ngay dưới từng câu là hỏng mục đích sử
    # dụng — nhìn xuống là thấy đáp án, không còn gì để luyện.
    # =======================================================================

    @classmethod
    def render_exam_header(cls, doc: docx.Document, book: RewrittenBook):
        """Dựng lại phần đầu đề thi theo thể thức hành chính quen thuộc."""
        info = book.exam_info or {}

        table = doc.add_table(rows=1, cols=2)
        table.autofit = False
        table.columns[0].width = Inches(3.2)
        table.columns[1].width = Inches(3.3)

        trai = table.cell(0, 0)
        p_trai = trai.paragraphs[0]
        p_trai.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p_trai.add_run(info.get("don_vi") or "ĐƠN VỊ TỔ CHỨC")
        r.bold = True
        r.font.name = FONT_MAIN
        r.font.size = Pt(12)
        p2 = trai.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r2 = p2.add_run("(Đề thi gồm nhiều trang)")
        r2.italic = True
        r2.font.name = FONT_MAIN
        r2.font.size = Pt(10)
        r2.font.color.rgb = COLOR_TEXT_MUTED

        phai = table.cell(0, 1)
        p_phai = phai.paragraphs[0]
        p_phai.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r3 = p_phai.add_run(info.get("ky_thi") or book.new_title.upper())
        r3.bold = True
        r3.font.name = FONT_MAIN
        r3.font.size = Pt(13)
        r3.font.color.rgb = COLOR_PRIMARY

        dong_phu = []
        if info.get("mon"):
            dong_phu.append(f"Môn: {info['mon']}")
        if info.get("thoi_gian"):
            dong_phu.append(f"Thời gian làm bài: {info['thoi_gian']}")
        if not dong_phu:
            dong_phu.append("Thời gian làm bài: 90 phút (không kể thời gian phát đề)")
        p4 = phai.add_paragraph()
        p4.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r4 = p4.add_run(" — ".join(dong_phu))
        r4.italic = True
        r4.font.name = FONT_MAIN
        r4.font.size = Pt(11)

        if info.get("ma_de"):
            p5 = phai.add_paragraph()
            p5.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r5 = p5.add_run(f"Mã đề: {info['ma_de']}")
            r5.bold = True
            r5.font.name = FONT_MAIN
            r5.font.size = Pt(11.5)

        # Dòng họ tên và số báo danh
        p_hs = doc.add_paragraph()
        p_hs.paragraph_format.space_before = Pt(14)
        p_hs.paragraph_format.space_after = Pt(12)
        r_hs = p_hs.add_run("Họ và tên thí sinh: " + "." * 42 + "   Số báo danh: " + "." * 14)
        r_hs.font.name = FONT_MAIN
        r_hs.font.size = Pt(12.5)

    @classmethod
    def render_exam_question(cls, doc: docx.Document, q: RewrittenQuestionItem, so_thu_tu: int):
        """Câu hỏi trong phần đề: chỉ đề bài và 4 phương án, KHÔNG lộ đáp án."""
        p_q = doc.add_paragraph()
        p_q.paragraph_format.space_before = Pt(8)
        p_q.paragraph_format.space_after = Pt(3)
        p_q.paragraph_format.line_spacing = 1.25

        r_num = p_q.add_run(f"Câu {so_thu_tu}. ")
        r_num.bold = True
        r_num.font.name = FONT_MAIN
        r_num.font.size = Pt(13)
        r_num.font.color.rgb = COLOR_PRIMARY

        r_ct = p_q.add_run(q.new_content)
        r_ct.font.name = FONT_MAIN
        r_ct.font.size = Pt(13)
        r_ct.font.color.rgb = COLOR_TEXT_MAIN

        if not q.new_options:
            return

        # Bốn phương án dàn 2x2, KHÔNG tô đậm đáp án đúng
        table = doc.add_table(rows=2, cols=2)
        table.autofit = False
        for row in table.rows:
            for cell in row.cells:
                cell.width = Inches(3.25)

        for i, opt in enumerate(q.new_options[:4]):
            c = table.cell(i // 2, i % 2)
            p_opt = c.paragraphs[0]
            p_opt.paragraph_format.space_before = Pt(1)
            p_opt.paragraph_format.space_after = Pt(1)
            r_opt = p_opt.add_run(opt)
            r_opt.font.name = FONT_MAIN
            r_opt.font.size = Pt(12.5)
            r_opt.font.color.rgb = COLOR_TEXT_MAIN

    @classmethod
    def render_answer_key(cls, doc: docx.Document, questions: list):
        """Bảng đáp án 10 câu mỗi hàng, tra cứu nhanh như đáp án đề thi thật."""
        p_head = doc.add_paragraph()
        p_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_head.paragraph_format.space_after = Pt(12)
        r = p_head.add_run("BẢNG ĐÁP ÁN")
        r.bold = True
        r.font.name = FONT_MAIN
        r.font.size = Pt(16)
        r.font.color.rgb = COLOR_PRIMARY

        moi_hang = 10
        for bat_dau in range(0, len(questions), moi_hang):
            nhom = questions[bat_dau:bat_dau + moi_hang]
            table = doc.add_table(rows=2, cols=len(nhom))
            table.alignment = WD_TABLE_ALIGNMENT.CENTER

            for i, q in enumerate(nhom):
                o_cau = table.cell(0, i)
                set_cell_background(o_cau, "EFF6FF")
                p_c = o_cau.paragraphs[0]
                p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r_c = p_c.add_run(str(bat_dau + i + 1))
                r_c.bold = True
                r_c.font.name = FONT_MAIN
                r_c.font.size = Pt(11)
                r_c.font.color.rgb = COLOR_PRIMARY

                o_da = table.cell(1, i)
                p_d = o_da.paragraphs[0]
                p_d.alignment = WD_ALIGN_PARAGRAPH.CENTER
                dap_an = (q.correct_answer or "—").strip().upper()[:1] or "—"
                r_d = p_d.add_run(dap_an)
                r_d.bold = True
                r_d.font.name = FONT_MAIN
                r_d.font.size = Pt(12)
                r_d.font.color.rgb = COLOR_SUCCESS

            doc.add_paragraph().paragraph_format.space_after = Pt(6)

    @classmethod
    def export_exam(cls, book: RewrittenBook, doc: docx.Document, opts: dict):
        """Bố cục đề thi: phần đề → bảng đáp án → hướng dẫn giải chi tiết."""
        ds_cau = book.questions or [q for ch in book.chapters for q in ch.questions]

        cls.render_exam_header(doc, book)

        for i, q in enumerate(ds_cau, 1):
            cls.render_exam_question(doc, q, i)

        p_het = doc.add_paragraph()
        p_het.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_het.paragraph_format.space_before = Pt(16)
        r_het = p_het.add_run("---------- HẾT ----------")
        r_het.bold = True
        r_het.font.name = FONT_MAIN
        r_het.font.size = Pt(12)

        p_note = doc.add_paragraph()
        p_note.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_note = p_note.add_run("Thí sinh không được sử dụng tài liệu. Cán bộ coi thi không giải thích gì thêm.")
        r_note.italic = True
        r_note.font.name = FONT_MAIN
        r_note.font.size = Pt(10.5)
        r_note.font.color.rgb = COLOR_TEXT_MUTED

        # ---- Bảng đáp án ----
        doc.add_page_break()
        cls.render_answer_key(doc, ds_cau)

        # ---- Hướng dẫn giải chi tiết ----
        doc.add_page_break()
        p_hd = doc.add_paragraph()
        p_hd.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_hd.paragraph_format.space_after = Pt(14)
        r_hd = p_hd.add_run("HƯỚNG DẪN GIẢI CHI TIẾT")
        r_hd.bold = True
        r_hd.font.name = FONT_MAIN
        r_hd.font.size = Pt(16)
        r_hd.font.color.rgb = COLOR_PRIMARY

        for i, q in enumerate(ds_cau, 1):
            p_t = doc.add_paragraph()
            p_t.paragraph_format.space_before = Pt(10)
            p_t.paragraph_format.space_after = Pt(3)
            r_t = p_t.add_run(f"Câu {i}. ")
            r_t.bold = True
            r_t.font.name = FONT_MAIN
            r_t.font.size = Pt(13)
            r_t.font.color.rgb = COLOR_PRIMARY
            if q.correct_answer:
                r_da = p_t.add_run(f"Đáp án {q.correct_answer.strip().upper()[:1]}")
                r_da.bold = True
                r_da.font.name = FONT_MAIN
                r_da.font.size = Pt(12.5)
                r_da.font.color.rgb = COLOR_SUCCESS

            if q.solution_method1:
                for line in q.solution_method1.strip().split("\n"):
                    if not line.strip():
                        continue
                    p_l = doc.add_paragraph()
                    p_l.paragraph_format.space_after = Pt(2)
                    p_l.paragraph_format.line_spacing = 1.2
                    r_l = p_l.add_run(line.strip())
                    r_l.font.name = FONT_MAIN
                    r_l.font.size = Pt(12.5)
                    r_l.font.color.rgb = COLOR_TEXT_MAIN

            if q.solution_method2 and opts["casio"]:
                add_callout_box(doc, "💡 KỸ THUẬT CASIO fx-580VN X",
                                q.solution_method2, "F0FDF4", "2F855A", COLOR_SUCCESS)
            if q.trap_warning and opts["traps"]:
                add_callout_box(doc, "⚠️ BẪY & LỖI SAI THƯỜNG GẶP",
                                q.trap_warning, "FFF5F5", "C53030", COLOR_WARNING)

        return doc

    @classmethod
    def export(
        cls,
        book: RewrittenBook,
        output_path: Path,
        paper_format: str = "a4",
        options: Optional[dict] = None
    ) -> Path:
        opts = cls.merge_options(options)
        doc = docx.Document()
        cls.apply_default_style(doc)
        section = doc.sections[0]
        cls.apply_standard_page_setup(section, paper_format=paper_format)

        # Header & Footer chuẩn công văn
        header = section.header
        p_hdr = header.paragraphs[0]
        p_hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_hdr = p_hdr.add_run(f"TÀI LIỆU LƯU HÀNH NỘI BỘ - CHƯƠNG TRÌNH GDPT 2018 | {book.new_title}")
        r_hdr.font.name = FONT_MAIN
        r_hdr.font.size = Pt(9)
        r_hdr.font.color.rgb = COLOR_TEXT_MUTED

        footer = section.footer
        p_ftr = footer.paragraphs[0]
        p_ftr.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_ftr = p_ftr.add_run("Trang được biên soạn & tối ưu hóa tự động - Chuẩn thể thức Bộ GD&ĐT")
        r_ftr.font.name = FONT_MAIN
        r_ftr.font.size = Pt(9)
        r_ftr.font.color.rgb = COLOR_TEXT_MUTED

        # ==========================================
        # RẼ NHÁNH THEO LOẠI TÀI LIỆU
        # Đầu vào là đề thi thì đầu ra cũng phải là đề thi: học sinh làm bài
        # trước rồi mới xem đáp án. Đầu vào là sách thì giữ bố cục sách.
        # ==========================================
        # Chín loại đầu ra: năm loại đề đi qua bộ dựng chuẩn 2025 (ma trận, bản
        # đặc tả, đề ba phần, hướng dẫn chấm). Các loại còn lại giữ bố cục cũ.
        loai_ra = getattr(book, "loai_dau_ra", "") or ""
        mon = getattr(book, "subject", "") or "toan"
        if la_loai_de(loai_ra):
            from core.exporter_de import xuat_bo_de
            xuat_bo_de(doc, book, loai_ra, mon,
                       kem_loi_giai=bool(opts.get("solution", True)))
            output_path.parent.mkdir(parents=True, exist_ok=True)
            doc.save(str(output_path))
            return output_path

        # Tài liệu HSG không dùng chung bộ dựng sách: đề HSG là tự luận, phải
        # giấu phương án đi chứ không cho sẵn bốn lựa chọn để đoán.
        if loai_ra == "TAI_LIEU_HSG":
            from core.exporter_hsg import xuat_tai_lieu_hsg
            xuat_tai_lieu_hsg(doc, book, mon, opts)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            doc.save(str(output_path))
            return output_path

        # Giao an: khung Cong van 5512. La ho so chuyen mon nen o MOI cap hoc
        # deu giu nghiem ngat, khong bieu tuong, khong trang tri.
        if loai_ra == "GIAO_AN":
            from core.exporter_giao_an import xuat_giao_an
            xuat_giao_an(doc, book, mon,
                         cap_hoc=getattr(book, "cap_hoc", "THPT"),
                         ten_bai=getattr(book, "ten_bai", "") or "",
                         options=opts)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            doc.save(str(output_path))
            return output_path

        if getattr(book, "doc_type", "") == "DE_THI":
            cls.export_exam(book, doc, opts)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            doc.save(str(output_path))
            return output_path

        # ==========================================
        # TRANG TIÊU ĐỀ & LỜI TỰA
        # ==========================================
        p_sp = doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(30)

        # Tên sách chuẩn hóa
        p_title = doc.add_paragraph()
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_title.paragraph_format.space_after = Pt(12)
        r_title = p_title.add_run(book.new_title.upper())
        r_title.bold = True
        r_title.font.name = FONT_MAIN
        r_title.font.size = Pt(20)
        r_title.font.color.rgb = COLOR_PRIMARY

        # Phụ đề
        p_sub = doc.add_paragraph()
        p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_sub.paragraph_format.space_after = Pt(20)
        r_sub = p_sub.add_run(book.subtitle)
        r_sub.italic = True
        r_sub.font.name = FONT_MAIN
        r_sub.font.size = Pt(13)
        r_sub.font.color.rgb = COLOR_SECONDARY

        # Lời tựa truyền cảm hứng
        if book.author_note and opts["foreword"]:
            add_callout_box(
                doc,
                title="✨ LỜI TỰA TRUYỀN CẢM HỨNG & SỨ MỆNH CUỐN SÁCH",
                content=book.author_note,
                bg_hex="F8FAFC",
                border_hex="2B6CB0",
                title_color=COLOR_PRIMARY
            )

        # Bí kíp thủ khoa
        if opts["secrets"] and getattr(book, "valedictorian_secrets", None):
            secrets_content = "\n".join(f"• {sec}" for sec in book.valedictorian_secrets)
            add_callout_box(
                doc,
                title="🏆 BÍ KÍP VÀNG PHÒNG THI & CHIẾN THUẬT TỪ THỦ KHOA",
                content=secrets_content,
                bg_hex="FFFDF5",
                border_hex="D69E2E",
                title_color=COLOR_WARNING
            )

        # Góc kết nối STEM thực tế đời sống
        if opts["stem"] and getattr(book, "stem_connection", ""):
            add_callout_box(
                doc,
                title="🌐 GÓC KẾT NỐI THỰC TIỄN ĐỜI SỐNG & CÔNG NGHỆ (GDPT 2018)",
                content=book.stem_connection,
                bg_hex="F0FFF4",
                border_hex="38A169",
                title_color=COLOR_SUCCESS
            )


        # ==========================================
        # KIỂU 1: ĐẠI CẨM NANG GỘP TỪ NHIỀU CHƯƠNG (MASTER BOOK)
        # ==========================================
        if book.chapters:
            # Mục lục tổng quan
            p_toc_head = doc.add_paragraph()
            p_toc_head.paragraph_format.space_before = Pt(14)
            p_toc_head.paragraph_format.space_after = Pt(10)
            r_th = p_toc_head.add_run("MỤC LỤC CÁC CHUYÊN ĐỀ")
            r_th.bold = True
            r_th.font.name = FONT_MAIN
            r_th.font.size = Pt(15)
            r_th.font.color.rgb = COLOR_PRIMARY

            for ch in book.chapters:
                p_ch_item = doc.add_paragraph()
                p_ch_item.paragraph_format.space_after = Pt(4)
                r_ci = p_ch_item.add_run(f"• {ch.title} ({len(ch.questions)} bài toán trọng tâm)")
                r_ci.font.name = FONT_MAIN
                r_ci.font.size = Pt(12)

            doc.add_page_break()

            # Lặp qua từng chương
            for ch in book.chapters:
                # Tiêu đề chương
                p_ch_title = doc.add_paragraph()
                p_ch_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_ch_title.paragraph_format.space_before = Pt(18)
                p_ch_title.paragraph_format.space_after = Pt(14)
                r_ct = p_ch_title.add_run(ch.title)
                r_ct.bold = True
                r_ct.font.name = FONT_MAIN
                r_ct.font.size = Pt(16)
                r_ct.font.color.rgb = COLOR_PRIMARY

                # PHẦN I: LÝ THUYẾT TRỌNG TÂM CỦA CHƯƠNG
                if ch.theory_section and opts["theory"]:
                    add_callout_box(
                        doc,
                        title="PHẦN I: KIẾN THỨC TRỌNG TÂM & LÝ THUYẾT CỐT LÕI",
                        content=ch.theory_section,
                        bg_hex="EFF6FF",
                        border_hex="1A365D",
                        title_color=COLOR_PRIMARY
                    )

                # PHẦN II: HỆ THỐNG BÀI TOÁN RÈN LUYỆN
                p_sec_title = doc.add_paragraph()
                p_sec_title.paragraph_format.space_before = Pt(12)
                p_sec_title.paragraph_format.space_after = Pt(10)
                r_st = p_sec_title.add_run("PHẦN II: HỆ THỐNG BÀI TOÁN CHỌN LỌC & LỜI GIẢI ĐA CHIỀU")
                r_st.bold = True
                r_st.font.name = FONT_MAIN
                r_st.font.size = Pt(14)
                r_st.font.color.rgb = COLOR_PRIMARY

                for q in ch.questions:
                    cls.render_question_item(doc, q, options=opts)

                doc.add_page_break()

        # ==========================================
        # KIỂU 2: CUỐN SÁCH ĐƠN (SINGLE BOOK)
        # ==========================================
        else:
            # PHẦN I: KIẾN THỨC TRỌNG TÂM & LÝ THUYẾT CỐT LÕI
            if book.theory_section and opts["theory"]:
                add_callout_box(
                    doc,
                    title="PHẦN I: KIẾN THỨC TRỌNG TÂM & LÝ THUYẾT NỀN TẢNG CHUẨN BGD",
                    content=book.theory_section,
                    bg_hex="EFF6FF",
                    border_hex="1A365D",
                    title_color=COLOR_PRIMARY
                )

            doc.add_page_break()

            # PHẦN II: HỆ THỐNG BÀI TOÁN VÀ LỜI GIẢI ĐA CHIỀU
            p_sec_title = doc.add_paragraph()
            p_sec_title.paragraph_format.space_before = Pt(10)
            p_sec_title.paragraph_format.space_after = Pt(14)
            r_st = p_sec_title.add_run("PHẦN II: HỆ THỐNG BÀI TOÁN RÈN LUYỆN THEO CẤP ĐỘ NHẬN THỨC")
            r_st.bold = True
            r_st.font.name = FONT_MAIN
            r_st.font.size = Pt(14)
            r_st.font.color.rgb = COLOR_PRIMARY

            for q in book.questions:
                cls.render_question_item(doc, q, options=opts)

        if opts["vi_tri_loi_giai"] == cls.LOI_GIAI_CUOI_SACH:
            cls.render_solution_section(doc, book, opts)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(output_path))
        return output_path
