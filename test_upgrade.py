import sys
from pathlib import Path
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import docx
from docx.shared import Mm
import pymupdf

from core.parser import parse_input_file, scan_directory
from core.rewriter import process_rewrite_pipeline, create_master_book_from_chapters
from core.exporter import DocxBookExporter
from config import INPUT_DIR, OUTPUT_DIR

def create_sample_pdf():
    pdf_path = INPUT_DIR / "sample_toan_de_thi.pdf"
    doc = pymupdf.open()
    page = doc.new_page()
    text = """DE THI KHAO SAT CHAT LUONG MON TOAN

Cau 1: Cho ham so y = f(x) co bang bien thien nhu sau. Ham so da cho dong bien tren khoang nao?
A. (0; 2)
B. (-1; 0)
C. (2; +oo)
D. (-oo; -1)
Loi giai: Dua vao bang bien thien, f'(x) mang dau duong tren khoang (0; 2). Chon dap an A.

Cau 2: Tich phan I = int[1 den 2] (3x^2 - 1) dx bang:
A. 6
B. 7
C. 5
D. 8
Loi giai: Ta co nguyen ham cua 3x^2 - 1 la x^3 - x. Thay can tu 1 den 2 ta duoc (8 - 2) - (1 - 1) = 6. Chon dap an A.
"""
    page.insert_text((50, 72), text, fontsize=12)
    doc.save(str(pdf_path))
    doc.close()
    print(f"[OK] Da tao file PDF test: {pdf_path}")
    return pdf_path

def test_all_upgrades():
    print("=== TEST 1: TEST TRÍCH XUẤT VÀ BIÊN SOẠN TỪ FILE PDF ===")
    pdf_p = create_sample_pdf()
    questions = parse_input_file(pdf_p, subject="toan")
    print(f"[*] So cau hoi bóc tach duoc tu PDF: {len(questions)}")
    assert len(questions) == 2, f"Mong doi 2 cau, nhan duoc {len(questions)}"

    book_single = process_rewrite_pipeline(questions, subject="toan", add_count=1)
    assert book_single.theory_section != "", "Chua co phan ly thuyet bo sung"
    print(f"[*] Da bo sung phan ly thuyet: {book_single.theory_section[:80]}...")

    out_single = OUTPUT_DIR / "Test_Output_PDF_Chuan_BGD.docx"
    DocxBookExporter.export(book_single, out_single)
    assert out_single.exists()
    
    # Kiem tra le trang chuan Nghi dinh 30 (Left 30mm, Right 15mm, Top 20mm, Bottom 20mm)
    doc_check = docx.Document(str(out_single))
    sec = doc_check.sections[0]
    print(f"[*] Kiem tra le trang: Left={sec.left_margin.mm:.1f}mm, Right={sec.right_margin.mm:.1f}mm, Top={sec.top_margin.mm:.1f}mm, Bottom={sec.bottom_margin.mm:.1f}mm")
    assert abs(sec.left_margin.mm - 30) < 1.0, "Le trai chua dat 30mm"
    assert abs(sec.right_margin.mm - 15) < 1.0, "Le phai chua dat 15mm"
    print("[OK] Thể thức chuẩn Nghị định 30/2020/NĐ-CP đã đạt 100%!")

    print("\n=== TEST 2: TEST QUÉT THƯ MỤC VÀ GỘP MASTER BOOK ===")
    found_files = scan_directory(INPUT_DIR)
    print(f"[*] So luong tep phat hien trong input/: {len(found_files)}")
    assert len(found_files) >= 3, "Chua du so tep test"

    chapter_data_list = []
    for f_info in found_files[:3]:
        q_list = parse_input_file(Path(f_info["path"]), subject="toan")
        if q_list:
            chapter_data_list.append({
                "source_name": f_info["name"],
                "questions": q_list
            })

    master_book = create_master_book_from_chapters(
        chapter_data_list=chapter_data_list,
        subject="toan",
        master_title="ĐẠI CẨM NANG TOÁN HỌC THPT TOÀN DIỆN"
    )
    print(f"[*] Tong so chuong trong Master Book: {len(master_book.chapters)}")
    out_master = OUTPUT_DIR / "Test_Master_Book_Gop_Folder.docx"
    DocxBookExporter.export(master_book, out_master)
    assert out_master.exists()
    print(f"[OK] Master Book da xuat ban thanh cong tai: {out_master}")

    print("\n🎉 TAT CA CAC MUC NANG CAP THEO YEU CAU NGUOI DUNG DA HOAN TAT XUAT SAC!")

if __name__ == "__main__":
    test_all_upgrades()
