import sys
from pathlib import Path
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import docx
from core.parser import parse_input_file
from core.rewriter import process_rewrite_pipeline
from core.exporter import DocxBookExporter
from config import INPUT_DIR, OUTPUT_DIR

def test_full_pipeline():
    print("=== TEST 1: KIỂM TRA FILE WORD DOCX ===")
    docx_file = INPUT_DIR / "sample_toan_goc.docx"
    assert docx_file.exists(), f"Không tìm thấy {docx_file}"
    
    questions = parse_input_file(docx_file, subject="toan")
    print(f"[*] Đã bóc tách thành công {len(questions)} câu hỏi từ Word.")
    assert len(questions) == 5, f"Mong đợi 5 câu, nhận được {len(questions)}"

    print("[*] Đang biên soạn lại bằng Rule-based Engine...")
    book = process_rewrite_pipeline(questions, subject="toan", add_count=2)
    print(f"[*] Tựa đề mới: {book.new_title}")
    print(f"[*] Tổng số câu sau khi nâng cấp: {len(book.questions)} câu")
    assert len(book.questions) == 7, f"Mong đợi 7 câu (5 gốc + 2 thêm), nhận được {len(book.questions)}"

    out_docx = OUTPUT_DIR / "Test_Output_From_Docx.docx"
    DocxBookExporter.export(book, out_docx)
    assert out_docx.exists(), f"Không tạo được {out_docx}"
    
    # Kiểm tra file docx vừa tạo có hợp lệ không
    check_doc = docx.Document(str(out_docx))
    assert len(check_doc.paragraphs) > 10, "File docx rỗng hoặc thiếu đoạn văn"
    print(f"[OK] File Word thành phẩm đã tạo thành công tại: {out_docx}")

    print("\n=== TEST 2: KIỂM TRA FILE EXCEL XLSX ===")
    xlsx_file = INPUT_DIR / "sample_toan_goc.xlsx"
    assert xlsx_file.exists(), f"Không tìm thấy {xlsx_file}"

    questions_excel = parse_input_file(xlsx_file, subject="toan")
    print(f"[*] Đã bóc tách thành công {len(questions_excel)} câu hỏi từ Excel.")
    assert len(questions_excel) == 4, f"Mong đợi 4 câu từ Excel, nhận được {len(questions_excel)}"

    book_excel = process_rewrite_pipeline(questions_excel, subject="toan", add_count=3)
    out_xlsx_docx = OUTPUT_DIR / "Test_Output_From_Xlsx.docx"
    DocxBookExporter.export(book_excel, out_xlsx_docx)
    assert out_xlsx_docx.exists(), f"Không tạo được {out_xlsx_docx}"
    print(f"[OK] File Word từ nguồn Excel đã tạo thành công tại: {out_xlsx_docx}")

    print("\n🎉 TOÀN BỘ CÁC BƯỚC TEST PIPELINE ĐÃ ĐẠT 100% HOÀN HẢO!")

if __name__ == "__main__":
    test_full_pipeline()
