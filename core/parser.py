import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
import docx
import openpyxl

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

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class DocxParser:
    QUESTION_START_RE = re.compile(
        r"^(?:câu|bài|ví dụ|bt)\s*(\d+)[\s.:\-–—]*(.*)",
        re.IGNORECASE
    )
    INLINE_OPTIONS_RE = re.compile(
        r"(?:^|\s+)([A-D]\.[^\n]+?)(?=(?:\s+[A-D]\.)|$)",
        re.IGNORECASE
    )
    SOLUTION_START_RE = re.compile(
        r"^(?:lời giải|hướng dẫn giải|hướng dẫn|đáp án chi tiết|giải chi tiết|bài giải)[\s.:\-–—]*(.*)",
        re.IGNORECASE
    )

    @classmethod
    def parse(cls, file_path: Path, subject: str = "toan") -> List[QuestionItem]:
        doc = docx.Document(str(file_path))
        lines: List[str] = []

        # Đọc đoạn văn
        for p in doc.paragraphs:
            text = p.text.strip()
            if text:
                lines.append(text)

        # Đọc dữ liệu từ bảng nếu có
        for table in doc.tables:
            for row in table.rows:
                row_texts = [c.text.strip() for c in row.cells if c.text.strip()]
                if row_texts:
                    lines.append(" | ".join(row_texts))

        items: List[QuestionItem] = []
        current_item: Optional[QuestionItem] = None
        state = "content"  # "content", "options", "solution"
        q_counter = 1

        for line in lines:
            q_match = cls.QUESTION_START_RE.match(line)
            sol_match = cls.SOLUTION_START_RE.match(line)

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
                    subject=subject
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
                # Kiểm tra 4 phương án trắc nghiệm trên 1 dòng
                opts = cls.INLINE_OPTIONS_RE.findall(line)
                if len(opts) >= 2:
                    current_item.options.extend([opt.strip() for opt in opts])
                    state = "options"
                    continue

                if re.match(r"^[A-D]\.[\s\S]*", line, re.IGNORECASE):
                    current_item.options.append(line)
                    state = "options"
                    continue

                if state == "solution":
                    current_item.solution += ("\n" + line if current_item.solution else line)
                else:
                    current_item.content += ("\n" + line if current_item.content else line)

        if current_item and (current_item.content or current_item.options):
            items.append(current_item)

        # Nếu không nhận diện được bằng regex (file văn xuôi hoặc bài tập liên tục)
        if not items and lines:
            chunk_size = max(1, len(lines) // 5)
            for idx, i in enumerate(range(0, len(lines), chunk_size), 1):
                chunk = "\n".join(lines[i:i+chunk_size])
                items.append(QuestionItem(
                    index=idx,
                    title=f"Bài {idx}",
                    content=chunk,
                    subject=subject
                ))

        return items


class ExcelParser:
    @classmethod
    def parse(cls, file_path: Path, subject: str = "toan") -> List[QuestionItem]:
        wb = openpyxl.load_workbook(str(file_path), data_only=True)
        sheet = wb.active
        rows = list(sheet.iter_rows(values_only=True))
        if not rows:
            return []

        # Xác định hàng tiêu đề
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

        # Ánh xạ cột
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
            elif "stt" in h_clean:
                col_map["stt"] = c_idx

        items: List[QuestionItem] = []
        q_counter = 1

        for r in rows[header_row_idx + 1:]:
            if not any(r):
                continue

            content_val = ""
            if "content" in col_map and col_map["content"] < len(r) and r[col_map["content"]]:
                content_val = str(r[col_map["content"]]).strip()
            else:
                # Tìm cột có văn bản dài nhất làm nội dung
                candidates = [str(c).strip() for c in r if c is not None and len(str(c).strip()) > 10]
                if candidates:
                    content_val = candidates[0]

            if not content_val:
                continue

            # Các phương án
            options = []
            for opt_key in ["opt_a", "opt_b", "opt_c", "opt_d"]:
                if opt_key in col_map and col_map[opt_key] < len(r) and r[col_map[opt_key]] is not None:
                    prefix = opt_key.split("_")[1].upper()
                    options.append(f"{prefix}. {str(r[col_map[opt_key]]).strip()}")

            # Đáp án đúng & lời giải
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
                subject=subject
            ))
            q_counter += 1

        return items

def parse_input_file(file_path: Path, subject: str = "toan") -> List[QuestionItem]:
    ext = file_path.suffix.lower()
    if ext in [".docx", ".doc"]:
        return DocxParser.parse(file_path, subject=subject)
    elif ext in [".xlsx", ".xls"]:
        return ExcelParser.parse(file_path, subject=subject)
    else:
        raise ValueError(f"Định dạng file không được hỗ trợ: {ext}. Vui lòng dùng file .docx hoặc .xlsx.")
