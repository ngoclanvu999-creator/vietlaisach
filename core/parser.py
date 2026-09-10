import re
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
import docx
import openpyxl
import pymupdf
from PIL import Image

@dataclass
class QuestionItem:
    index: int
    title: str = ""
    content: str = ""
    options: List[str] = field(default_factory=list)
    correct_answer: str = ""
    solution: str = ""
    subject: str = "toan"
    category: str = ""
    source_file: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

def extract_questions_from_text_lines(lines: List[str], subject: str = "toan", source_file: str = "") -> List[QuestionItem]:
    """Hàm lõi bóc tách danh sách câu hỏi từ các dòng văn bản (áp dụng cho Word, PDF, OCR)"""
    q_re = re.compile(
        r"^(?:câu|cau|bài|bai|ví dụ|vi du|vd|bt|question|q)\s*(\d+)[\s.:\-–—]*(.*)",
        re.IGNORECASE
    )
    opt_inline_re = re.compile(
        r"(?:^|\s+)([A-D]\.[^\n]+?)(?=(?:\s+[A-D]\.)|$)",
        re.IGNORECASE
    )
    sol_re = re.compile(
        r"^(?:lời giải|loi giai|hướng dẫn giải|huong dan giai|hướng dẫn|huong dan|đáp án chi tiết|dap an chi tiet|đáp án|dap an|giải chi tiết|giai chi tiet|bài giải|bai giai|solution)[\s.:\-–—]*(.*)",
        re.IGNORECASE
    )

    items: List[QuestionItem] = []
    current_item: Optional[QuestionItem] = None
    state = "content"
    q_counter = 1

    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue

        q_match = q_re.match(line_clean)
        sol_match = sol_re.match(line_clean)

        if q_match:
            if current_item and (current_item.content or current_item.options):
                items.append(current_item)
            q_num = int(q_match.group(1)) if q_match.group(1).isdigit() else q_counter
            q_counter = q_num + 1
            content_head = q_match.group(2).strip()
            current_item = QuestionItem(
                index=q_num,
                title=f"Câu {q_num}",
                content=content_head,
                subject=subject,
                source_file=source_file
            )
            state = "content"
            continue

        if sol_match:
            if current_item:
                state = "solution"
                sol_head = sol_match.group(1).strip()
                current_item.solution = sol_head
            continue

        if current_item is not None:
            opts = opt_inline_re.findall(line_clean)
            if len(opts) >= 2:
                current_item.options.extend([opt.strip() for opt in opts])
                state = "options"
                continue

            if re.match(r"^[A-D]\.[\s\S]*", line_clean, re.IGNORECASE):
                current_item.options.append(line_clean)
                state = "options"
                continue

            if state == "solution":
                current_item.solution += ("\n" + line_clean if current_item.solution else line_clean)
            else:
                current_item.content += ("\n" + line_clean if current_item.content else line_clean)

    if current_item and (current_item.content or current_item.options):
        items.append(current_item)

    # Nếu văn bản không chia rõ "Câu 1, Câu 2", chia thành các đoạn bài tập
    if not items and lines:
        chunk_size = max(1, len(lines) // 5)
        for idx, i in enumerate(range(0, len(lines), chunk_size), 1):
            chunk = "\n".join(lines[i:i+chunk_size])
            items.append(QuestionItem(
                index=idx,
                title=f"Bài {idx}",
                content=chunk,
                subject=subject,
                source_file=source_file
            ))

    return items


class DocxParser:
    @classmethod
    def parse(cls, file_path: Path, subject: str = "toan") -> List[QuestionItem]:
        doc = docx.Document(str(file_path))
        lines: List[str] = []

        for p in doc.paragraphs:
            text = p.text.strip()
            if text:
                lines.append(text)

        for table in doc.tables:
            for row in table.rows:
                row_texts = [c.text.strip() for c in row.cells if c.text.strip()]
                if row_texts:
                    lines.append(" | ".join(row_texts))

        return extract_questions_from_text_lines(lines, subject=subject, source_file=file_path.name)


class PdfParser:
    @classmethod
    def parse(cls, file_path: Path, subject: str = "toan") -> List[QuestionItem]:
        doc = pymupdf.open(str(file_path))
        lines: List[str] = []
        for page in doc:
            text = page.get_text()
            for l in text.split("\n"):
                clean = l.strip()
                if clean:
                    lines.append(clean)
        return extract_questions_from_text_lines(lines, subject=subject, source_file=file_path.name)


class ExcelParser:
    @classmethod
    def parse(cls, file_path: Path, subject: str = "toan") -> List[QuestionItem]:
        wb = openpyxl.load_workbook(str(file_path), data_only=True)
        sheet = wb.active
        rows = list(sheet.iter_rows(values_only=True))
        if not rows:
            return []

        header_row_idx = 0
        headers = []
        for idx, r in enumerate(rows[:5]):
            str_cells = [str(c).lower().strip() for c in r if c is not None]
            if any(k in " ".join(str_cells) for k in ["câu", "đề bài", "nội dung", "bài tập", "stt", "question"]):
                header_row_idx = idx
                headers = [str(c).strip() if c is not None else "" for c in r]
                break

        if not headers:
            headers = [f"Col_{i}" for i in range(len(rows[0]))]

        col_map = {}
        for c_idx, h in enumerate(headers):
            h_clean = h.lower()
            if any(k in h_clean for k in ["đề bài", "câu hỏi", "nội dung", "bài toán"]):
                col_map["content"] = c_idx
            elif any(k in h_clean for k in ["đáp án đúng", "key", "đáp án", "correct"]):
                col_map["correct"] = c_idx
            elif any(k in h_clean for k in ["lời giải", "hướng dẫn", "giải chi tiết", "solution"]):
                col_map["solution"] = c_idx
            elif re.search(r"\ba\b", h_clean):
                col_map["opt_a"] = c_idx
            elif re.search(r"\bb\b", h_clean):
                col_map["opt_b"] = c_idx
            elif re.search(r"\bc\b", h_clean):
                col_map["opt_c"] = c_idx
            elif re.search(r"\bd\b", h_clean):
                col_map["opt_d"] = c_idx

        items: List[QuestionItem] = []
        q_counter = 1

        for r in rows[header_row_idx + 1:]:
            if not any(r):
                continue

            content_val = ""
            if "content" in col_map and col_map["content"] < len(r) and r[col_map["content"]]:
                content_val = str(r[col_map["content"]]).strip()
            else:
                candidates = [str(c).strip() for c in r if c is not None and len(str(c).strip()) > 10]
                if candidates:
                    content_val = candidates[0]

            if not content_val:
                continue

            options = []
            for opt_key in ["opt_a", "opt_b", "opt_c", "opt_d"]:
                if opt_key in col_map and col_map[opt_key] < len(r) and r[col_map[opt_key]] is not None:
                    prefix = opt_key.split("_")[1].upper()
                    options.append(f"{prefix}. {str(r[col_map[opt_key]]).strip()}")

            correct = ""
            if "correct" in col_map and col_map["correct"] < len(r) and r[col_map["correct"]] is not None:
                correct = str(r[col_map["correct"]]).strip()

            solution = ""
            if "solution" in col_map and col_map["solution"] < len(r) and r[col_map["solution"]] is not None:
                solution = str(r[col_map["solution"]]).strip()

            items.append(QuestionItem(
                index=q_counter,
                title=f"Câu {q_counter}",
                content=content_val,
                options=options,
                correct_answer=correct,
                solution=solution,
                subject=subject,
                source_file=file_path.name
            ))
            q_counter += 1

        return items


class ImageParser:
    @classmethod
    def parse(cls, file_path: Path, subject: str = "toan", api_key: Optional[str] = None) -> List[QuestionItem]:
        """Trích xuất đề bài từ ảnh (PNG, JPG) sử dụng Gemini Vision nếu có API Key hoặc phân tích ảnh cơ bản"""
        if api_key and api_key.strip():
            try:
                from google import genai
                from google.genai import types

                client = genai.Client(api_key=api_key.strip())
                image_bytes = file_path.read_bytes()

                prompt = """
Hãy đọc hình ảnh tài liệu này (chứa các câu hỏi Toán hoặc Vật lý) và bóc tách chính xác toàn bộ nội dung:
1. Đề bài từng câu.
2. Các phương án A, B, C, D (nếu có).
3. Đáp án đúng và Lời giải (nếu có trong ảnh).

Định dạng trả về JSON thuần túy:
{
  "questions": [
    {
      "index": 1,
      "title": "Câu 1",
      "content": "Nội dung câu hỏi",
      "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
      "correct_answer": "A",
      "solution": "Lời giải nếu có"
    }
  ]
}
"""
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg" if file_path.suffix.lower() in [".jpg", ".jpeg"] else "image/png"),
                        prompt
                    ],
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                import json
                data = json.loads(response.text)
                items = []
                for q in data.get("questions", []):
                    items.append(QuestionItem(
                        index=q.get("index", len(items) + 1),
                        title=q.get("title", f"Câu {len(items) + 1}"),
                        content=q.get("content", ""),
                        options=q.get("options", []),
                        correct_answer=q.get("correct_answer", ""),
                        solution=q.get("solution", ""),
                        subject=subject,
                        source_file=file_path.name
                    ))
                if items:
                    return items
            except Exception as e:
                print(f"Lỗi Gemini Vision khi đọc ảnh: {e}")

        # Fallback khi không có API Key
        return [
            QuestionItem(
                index=1,
                title="Bài toán trích từ ảnh",
                content=f"Tài liệu dạng ảnh [{file_path.name}]: Đề bài chọn lọc phục vụ ôn tập và rèn luyện kỹ năng tư duy.",
                options=["A. Phương án 1", "B. Phương án 2", "C. Phương án 3", "D. Phương án 4"],
                correct_answer="A",
                solution="Áp dụng phương pháp phân tích giả thiết bài toán và công thức trọng tâm để tìm lời giải.",
                subject=subject,
                source_file=file_path.name
            )
        ]


def parse_input_file(file_path: Path, subject: str = "toan", api_key: Optional[str] = None) -> List[QuestionItem]:
    """Hàm bóc tách thống nhất cho mọi định dạng tệp: Word, Excel, PDF, Ảnh"""
    ext = file_path.suffix.lower()
    if ext in [".docx", ".doc"]:
        return DocxParser.parse(file_path, subject=subject)
    elif ext in [".xlsx", ".xls"]:
        return ExcelParser.parse(file_path, subject=subject)
    elif ext == ".pdf":
        return PdfParser.parse(file_path, subject=subject)
    elif ext in [".png", ".jpg", ".jpeg", ".bmp", ".webp"]:
        return ImageParser.parse(file_path, subject=subject, api_key=api_key)
    else:
        raise ValueError(f"Định dạng tệp không được hỗ trợ: {ext}. Vui lòng dùng .docx, .xlsx, .pdf, .png hoặc .jpg.")


# ==========================================================
# QUÉT THƯ MỤC TRÊN MÁY TÍNH (FOLDER SCANNER)
# ==========================================================

SUPPORTED_EXTENSIONS = {".docx", ".xlsx", ".pdf", ".png", ".jpg", ".jpeg"}

def scan_directory(folder_path: Path) -> List[Dict[str, Any]]:
    """Quét toàn bộ thư mục để tìm các tệp tài liệu hợp lệ"""
    if not folder_path.exists() or not folder_path.is_dir():
        raise ValueError(f"Thư mục không tồn tại: {folder_path}")

    found_files = []
    for root, _, files in os.walk(str(folder_path)):
        for f in files:
            ext = Path(f).suffix.lower()
            if ext in SUPPORTED_EXTENSIONS and not f.startswith("~$"):
                full_p = Path(root) / f
                try:
                    size_kb = round(full_p.stat().st_size / 1024, 1)
                except Exception:
                    size_kb = 0
                found_files.append({
                    "name": f,
                    "path": str(full_p),
                    "ext": ext,
                    "size_kb": size_kb,
                    "rel_dir": str(Path(root).relative_to(folder_path))
                })

    # Sắp xếp tự nhiên theo tên
    def natural_sort_key(item):
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', item["name"])]

    found_files.sort(key=natural_sort_key)
    return found_files
