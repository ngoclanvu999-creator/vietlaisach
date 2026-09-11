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
from config import OUTPUT_DIR

pdf_path = Path("input/[PDF] Đề thi chọn học sinh giỏi môn Toán lớp 11 năm học 2019 - 2020 cụm Tân Yên - Bắc Giang.pdf")
print(f"[*] Đang bóc tách tệp PDF thực tế của người dùng: {pdf_path.name}")
questions = parse_input_file(pdf_path, subject="toan")
print(f"[*] Số câu bóc tách được: {len(questions)}")

for q in questions[:5]:
    print(f"\n--- {q.title} ---")
    print(f"Content: {q.content}")
    print(f"Options: {q.options}")

print("\n[*] Đang biên soạn lại theo chuẩn sư phạm Bộ GD&ĐT...")
book = process_rewrite_pipeline(questions, subject="toan", add_count=2)

out_file = OUTPUT_DIR / "Sach_Sua_Loi_Chuan_Dinh_Dang_BGD.docx"
DocxBookExporter.export(book, out_file)
print(f"[OK] Đã xuất file thành công tại: {out_file}")

# Kiểm tra nội dung câu 1 trong file docx mới tạo
doc = docx.Document(str(out_file))
print(f"[*] Tổng số đoạn văn trong file Word: {len(doc.paragraphs)}")
print(f"[*] Tổng số bảng trong file Word: {len(doc.tables)}")
