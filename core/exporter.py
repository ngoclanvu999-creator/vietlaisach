from pathlib import Path
from typing import Optional
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
from core.rewriter import RewrittenBook, RewrittenQuestionItem

COLOR_PRIMARY = RGBColor(30, 58, 138)      # Deep Blue #1E3A8A
COLOR_SECONDARY = RGBColor(59, 130, 246)   # Bright Blue #3B82F6
COLOR_SUCCESS = RGBColor(16, 185, 129)     # Green Emerald #10B981
COLOR_WARNING = RGBColor(220, 38, 38)      # Red Trap #DC2626
COLOR_TEXT_MAIN = RGBColor(17, 24, 39)     # Gray 900
COLOR_TEXT_MUTED = RGBColor(75, 85, 99)    # Gray 600

def set_cell_background(cell, fill_hex: str):
    """Đặt màu nền cho một ô trong bảng Word"""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_callout_borders(cell, border_color_hex: str, border_size_pt: int = 24):
    """Tạo đường viền trái dày cho khung Callout (kiểu hiện đại)"""
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
    """Chèn một hộp ghi chú Callout màu sắc chuyên nghiệp vào văn bản"""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(6.5)

    cell = table.cell(0, 0)
    set_cell_background(cell, bg_hex)
    set_callout_borders(cell, border_hex, border_size_pt=24)

    # Tiêu đề callout
    p_title = cell.paragraphs[0]
    p_title.paragraph_format.space_before = Pt(4)
    p_title.paragraph_format.space_after = Pt(4)
    run_title = p_title.add_run(title)
    run_title.bold = True
    run_title.font.name = "Cambria"
    run_title.font.size = Pt(11)
    run_title.font.color.rgb = title_color

    # Nội dung callout
    for line in content.strip().split("\n"):
        if not line.strip():
            continue
        p = cell.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(line.strip())
        run.font.name = "Cambria"
        run.font.size = Pt(10)
        run.font.color.rgb = COLOR_TEXT_MAIN

    # Khoảng đệm sau bảng
    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(0)
    p_spacer.paragraph_format.space_after = Pt(6)


class DocxBookExporter:
    @classmethod
    def export(cls, book: RewrittenBook, output_path: Path, paper_format: str = "a4") -> Path:
        doc = docx.Document()

        # Thiết lập lề trang chuẩn sách (Top/Bottom 2cm, Left 2.5cm, Right 2cm)
        section = doc.sections[0]
        if paper_format == "b5":
            section.page_width = Inches(7.17)   # B5: 182mm
            section.page_height = Inches(10.12) # B5: 257mm
        else:
            section.page_width = Inches(8.27)   # A4: 210mm
            section.page_height = Inches(11.69) # A4: 297mm

        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(0.8)

        # Header & Footer
        header = section.header
        p_hdr = header.paragraphs[0]
        p_hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_hdr = p_hdr.add_run(f"📖 {book.new_title} | Cẩm Nang Chuyên Sâu")
        r_hdr.font.name = "Cambria"
        r_hdr.font.size = Pt(8.5)
        r_hdr.font.color.rgb = COLOR_TEXT_MUTED

        footer = section.footer
        p_ftr = footer.paragraphs[0]
        p_ftr.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_ftr = p_ftr.add_run("Trang được biên soạn và tối ưu hóa tự động - Bản quyền nội dung thuộc tác giả")
        r_ftr.font.name = "Cambria"
        r_ftr.font.size = Pt(8)
        r_ftr.font.color.rgb = COLOR_TEXT_MUTED

        # ==========================================
        # TRANG BÌA SÁCH (COVER / TITLE SECTION)
        # ==========================================
        p_top_spacer = doc.add_paragraph()
        p_top_spacer.paragraph_format.space_before = Pt(40)

        # Tiêu đề sách chính
        p_title = doc.add_paragraph()
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_title.paragraph_format.space_after = Pt(12)
        r_title = p_title.add_run(book.new_title.upper())
        r_title.bold = True
        r_title.font.name = "Cambria"
        r_title.font.size = Pt(22)
        r_title.font.color.rgb = COLOR_PRIMARY

        # Phụ đề
        p_sub = doc.add_paragraph()
        p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_sub.paragraph_format.space_after = Pt(24)
        r_sub = p_sub.add_run(book.subtitle)
        r_sub.italic = True
        r_sub.font.name = "Cambria"
        r_sub.font.size = Pt(13)
        r_sub.font.color.rgb = COLOR_SECONDARY

        # Đường kẻ ngang phân cách
        p_divider = doc.add_paragraph()
        p_divider.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_divider.paragraph_format.space_after = Pt(24)
        r_div = p_divider.add_run("❖  ❖  ❖")
        r_div.font.color.rgb = COLOR_SECONDARY

        # Lời tựa (Preface)
        add_callout_box(
            doc,
            title="LỜI TỰA BIÊN SOẠN & ĐỊNH HƯỚNG TƯ DUY",
            content=book.author_note,
            bg_hex="F8FAFC",
            border_hex="3B82F6",
            title_color=COLOR_PRIMARY
        )

        # Bảng công thức vàng & Sơ đồ phương pháp (Chapter Summary)
        if book.chapter_summary:
            add_callout_box(
                doc,
                title="BẢNG CÔNG THỨC VÀNG & PHƯƠNG PHÁP CỐT LÕI",
                content=book.chapter_summary,
                bg_hex="EFF6FF",
                border_hex="1E40AF",
                title_color=COLOR_PRIMARY
            )

        doc.add_page_break()

        # ==========================================
        # PHẦN NỘI DUNG CHI TIẾT CÁC BÀI TOÁN
        # ==========================================
        p_sec_title = doc.add_paragraph()
        p_sec_title.paragraph_format.space_before = Pt(10)
        p_sec_title.paragraph_format.space_after = Pt(18)
        r_sec = p_sec_title.add_run("HỆ THỐNG BÀI TOÁN CHỌN LỌC & LỜI GIẢI ĐA CHIỀU")
        r_sec.bold = True
        r_sec.font.name = "Cambria"
        r_sec.font.size = Pt(15)
        r_sec.font.color.rgb = COLOR_PRIMARY

        for q in book.questions:
            # Tiêu đề bài toán
            p_qtitle = doc.add_paragraph()
            p_qtitle.paragraph_format.space_before = Pt(14)
            p_qtitle.paragraph_format.space_after = Pt(4)
            r_qt = p_qtitle.add_run(f"▶ {q.title}")
            r_qt.bold = True
            r_qt.font.name = "Cambria"
            r_qt.font.size = Pt(12)
            r_qt.font.color.rgb = COLOR_PRIMARY if not q.is_added_new else COLOR_SUCCESS

            if q.is_added_new:
                r_badge = p_qtitle.add_run(" [MỚI BỔ SUNG]")
                r_badge.bold = True
                r_badge.font.size = Pt(9.5)
                r_badge.font.color.rgb = COLOR_SUCCESS

            # Đề bài
            p_qcontent = doc.add_paragraph()
            p_qcontent.paragraph_format.space_before = Pt(2)
            p_qcontent.paragraph_format.space_after = Pt(6)
            p_qcontent.paragraph_format.line_spacing = 1.2
            r_qc = p_qcontent.add_run(q.new_content)
            r_qc.font.name = "Cambria"
            r_qc.font.size = Pt(11)
            r_qc.font.color.rgb = COLOR_TEXT_MAIN

            # Các phương án trắc nghiệm A, B, C, D
            if q.new_options:
                table_opt = doc.add_table(rows=2, cols=2)
                table_opt.alignment = WD_TABLE_ALIGNMENT.CENTER
                table_opt.autofit = False
                col_width = Inches(3.2)
                for row in table_opt.rows:
                    for cell in row.cells:
                        cell.width = col_width

                for o_idx, opt_text in enumerate(q.new_options[:4]):
                    row_i = o_idx // 2
                    col_i = o_idx % 2
                    c = table_opt.cell(row_i, col_i)
                    set_cell_background(c, "F9FAFB")
                    p_opt = c.paragraphs[0]
                    p_opt.paragraph_format.space_before = Pt(3)
                    p_opt.paragraph_format.space_after = Pt(3)
                    r_opt = p_opt.add_run(opt_text)
                    r_opt.font.name = "Cambria"
                    r_opt.font.size = Pt(10)
                    if q.correct_answer and opt_text.strip().startswith(q.correct_answer):
                        r_opt.bold = True
                        r_opt.font.color.rgb = COLOR_SUCCESS

                doc.add_paragraph().paragraph_format.space_after = Pt(6)

            # Lời giải cách 1: Tự luận chuẩn mực
            p_sol1_head = doc.add_paragraph()
            p_sol1_head.paragraph_format.space_before = Pt(6)
            p_sol1_head.paragraph_format.space_after = Pt(2)
            r_s1_h = p_sol1_head.add_run("✎ Hướng dẫn giải tự luận chi tiết:")
            r_s1_h.bold = True
            r_s1_h.font.name = "Cambria"
            r_s1_h.font.size = Pt(10.5)
            r_s1_h.font.color.rgb = COLOR_SECONDARY

            for line in q.solution_method1.strip().split("\n"):
                if not line.strip():
                    continue
                p_sol_l = doc.add_paragraph()
                p_sol_l.paragraph_format.space_before = Pt(1)
                p_sol_l.paragraph_format.space_after = Pt(2)
                p_sol_l.paragraph_format.line_spacing = 1.15
                r_sol_l = p_sol_l.add_run(line.strip())
                r_sol_l.font.name = "Cambria"
                r_sol_l.font.size = Pt(10.5)

            # Lời giải cách 2: Hộp Mẹo Casio / Giải nhanh
            if q.solution_method2:
                add_callout_box(
                    doc,
                    title="💡 KỸ THUẬT CASIO FX-580VN X & MẸO GIẢI NHANH",
                    content=q.solution_method2,
                    bg_hex="ECFDF5",
                    border_hex="10B981",
                    title_color=COLOR_SUCCESS
                )

            # Khung cảnh báo bẫy
            if q.trap_warning:
                add_callout_box(
                    doc,
                    title="⚠️ BẪY ĐỀ THI & SAI LẦM PHỔ BIẾN HỌC SINH HAY MẮC",
                    content=q.trap_warning,
                    bg_hex="FEF2F2",
                    border_hex="DC2626",
                    title_color=COLOR_WARNING
                )

            # Đường phân cách nhẹ giữa các câu
            p_sep = doc.add_paragraph()
            p_sep.paragraph_format.space_before = Pt(6)
            p_sep.paragraph_format.space_after = Pt(8)
            p_sep.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r_sep = p_sep.add_run("· · · — — — · · ·")
            r_sep.font.color.rgb = RGBColor(209, 213, 219)
            r_sep.font.size = Pt(8)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(output_path))
        return output_path
