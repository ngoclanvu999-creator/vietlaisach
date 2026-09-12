from pathlib import Path
from typing import Optional, List
import docx
from docx.shared import Inches, Pt, RGBColor, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
from core.rewriter import RewrittenBook, RewrittenChapter, RewrittenQuestionItem

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

    @classmethod
    def render_question_item(cls, doc: docx.Document, q: RewrittenQuestionItem):
        """Trình bày từng câu hỏi theo chuẩn sư phạm Bộ GD&ĐT"""
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

        # Lời giải Tự luận chuẩn mực sư phạm
        if q.solution_method1:
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
        if q.solution_method2:
            add_callout_box(
                doc,
                title="💡 KỸ THUẬT BẤM MÁY CASIO FX-580VN X & TƯ DUY GIẢI NHANH",
                content=q.solution_method2,
                bg_hex="F0FDF4",
                border_hex="2F855A",
                title_color=COLOR_SUCCESS
            )

        # Khung Cảnh báo bẫy sai lầm
        if q.trap_warning:
            add_callout_box(
                doc,
                title="⚠️ BẪY ĐỀ THI & LỖI SAI HỌC SINH HAY MẮC PHẢI",
                content=q.trap_warning,
                bg_hex="FFF5F5",
                border_hex="C53030",
                title_color=COLOR_WARNING
            )

        # Đường kẻ phân cách nhẹ
        p_sep = doc.add_paragraph()
        p_sep.paragraph_format.space_before = Pt(4)
        p_sep.paragraph_format.space_after = Pt(8)
        p_sep.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_sep = p_sep.add_run("· · · — — — · · ·")
        r_sep.font.color.rgb = RGBColor(203, 213, 225)
        r_sep.font.size = Pt(8)

    @classmethod
    def export(cls, book: RewrittenBook, output_path: Path, paper_format: str = "a4") -> Path:
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
        if book.author_note:
            add_callout_box(
                doc,
                title="✨ LỜI TỰA TRUYỀN CẢM HỨNG & SỨ MỆNH CUỐN SÁCH",
                content=book.author_note,
                bg_hex="F8FAFC",
                border_hex="2B6CB0",
                title_color=COLOR_PRIMARY
            )

        # Bí kíp thủ khoa
        if hasattr(book, "valedictorian_secrets") and book.valedictorian_secrets:
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
        if hasattr(book, "stem_connection") and book.stem_connection:
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
                if ch.theory_section:
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
                    cls.render_question_item(doc, q)

                doc.add_page_break()

        # ==========================================
        # KIỂU 2: CUỐN SÁCH ĐƠN (SINGLE BOOK)
        # ==========================================
        else:
            # PHẦN I: KIẾN THỨC TRỌNG TÂM & LÝ THUYẾT CỐT LÕI
            if book.theory_section:
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
                cls.render_question_item(doc, q)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(output_path))
        return output_path
