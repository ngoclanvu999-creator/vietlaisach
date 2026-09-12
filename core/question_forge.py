"""
Lò sinh câu hỏi: dùng AI sinh bài tập mới cho ngân hàng, KÈM BỘ KIỂM CHỨNG.

Vì sao phải kiểm chứng gắt: mô hình ngôn ngữ sinh đề rất trôi chảy nhưng đáp án
thì hay sai, và sai một cách rất thuyết phục. Dự án này từng có 2 câu hard-code
sai đáp án được chèn vào 100% sách xuất ra mà không ai phát hiện. Với tài liệu
dạy học, một câu sai đáp án là lỗi không thể chấp nhận.

Nguyên tắc: KHÔNG câu nào vào ngân hàng nếu chưa qua đủ các cửa kiểm tra.

Ba lớp kiểm chứng, từ rẻ tới đắt:

  Lớp 1 — Cấu trúc (không tốn hạn mức API)
      Đủ 4 phương án, không trùng nhau, đáp án nằm trong A-D và khớp một phương
      án, có lời giải, đề bài đủ dài. Lớp này bắt được đúng loại lỗi từng lọt.

  Lớp 2 — Giải lại độc lập (1 lượt gọi cho cả lô)
      Đưa lại đề cho mô hình nhưng GIẤU đáp án và lời giải, bắt nó giải từ đầu.
      Chỉ nhận câu nào hai lần cho cùng một đáp án. Đây là cửa chặn mạnh nhất.

  Lớp 3 — Đối chiếu số bằng sympy (không tốn hạn mức)
      Khi mô hình cung cấp được biểu thức kiểm tra, tính lại bằng sympy và so
      với đáp số. Dùng parse_expr với danh sách tên được phép, không dùng eval.

Câu trượt không bị vứt đi mà lưu lại kèm lý do, để người dùng xem AI sai ở đâu.
"""

import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from config import BASE_DIR
from core.math_engine import clean_paragraph_text
from core.theory_bank import (
    MATH_THEORY_DATABASE, PHYSICS_THEORY_DATABASE,
    get_casio_tip, get_trap_warning,
)

DATA_DIR = BASE_DIR / "data"
BANK_FILE = DATA_DIR / "question_bank.json"
REJECTED_FILE = DATA_DIR / "question_bank_rejected.json"

CAP_DO = ["Nhận biết", "Thông hiểu", "Vận dụng", "Vận dụng cao"]
KHOI_LOP = ["Lớp 10", "Lớp 11", "Lớp 12"]

MAX_PER_BATCH = 8          # sinh quá nhiều một lượt thì chất lượng tụt rõ rệt
MIN_CONTENT_LEN = 25       # đề bài ngắn hơn thế gần như chắc chắn là rác


@dataclass
class ForgedQuestion:
    """Một câu hỏi do AI sinh, kèm toàn bộ dấu vết kiểm chứng."""
    topic_key: str
    subject: str
    grade: str
    level: str
    content: str
    options: List[str]
    correct: str
    solution: str
    casio_tip: str = ""
    trap_warning: str = ""
    check_expression: str = ""     # biểu thức sympy để đối chiếu (nếu có)
    check_expected: str = ""
    # Dấu vết kiểm chứng
    verified: bool = False
    checks_passed: List[str] = field(default_factory=list)
    reject_reasons: List[str] = field(default_factory=list)
    resolve_answer: str = ""       # đáp án khi giải lại độc lập
    created_at: str = ""
    source_model: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# LỚP 1: KIỂM TRA CẤU TRÚC
# ---------------------------------------------------------------------------

def _option_label(text: str) -> str:
    m = re.match(r"\s*([A-Da-d])\s*[.)\-:]", text or "")
    return m.group(1).upper() if m else ""


def _option_body(text: str) -> str:
    body = re.sub(r"^\s*[A-Da-d]\s*[.)\-:]\s*", "", text or "")
    return re.sub(r"\s+", " ", body).strip().lower().rstrip(".")


def kiem_tra_cau_truc(q: ForgedQuestion) -> Tuple[bool, List[str]]:
    """Các lỗi bắt được ở đây đều là lỗi chắc chắn, không cần gọi API."""
    loi: List[str] = []

    if len(q.content.strip()) < MIN_CONTENT_LEN:
        loi.append(f"Đề bài quá ngắn ({len(q.content.strip())} ký tự)")

    if len(q.options) != 4:
        loi.append(f"Có {len(q.options)} phương án thay vì 4")

    nhan = [_option_label(o) for o in q.options]
    if sorted(n for n in nhan if n) != ["A", "B", "C", "D"]:
        loi.append(f"Nhãn phương án không đủ A-D: {nhan}")

    than = [_option_body(o) for o in q.options]
    if len(set(than)) != len(than):
        loi.append("Có phương án trùng nội dung nhau")
    if any(not t for t in than):
        loi.append("Có phương án rỗng")

    dap_an = (q.correct or "").strip().upper()
    if dap_an not in ("A", "B", "C", "D"):
        loi.append(f"Đáp án '{q.correct}' không phải A/B/C/D")
    elif dap_an not in nhan:
        loi.append(f"Đáp án {dap_an} không khớp phương án nào")

    if len(q.solution.strip()) < 30:
        loi.append("Lời giải quá sơ sài")

    if q.level not in CAP_DO:
        loi.append(f"Cấp độ '{q.level}' không hợp lệ")

    return (not loi), loi


# ---------------------------------------------------------------------------
# LỚP 3: ĐỐI CHIẾU SỐ BẰNG SYMPY
# ---------------------------------------------------------------------------

# Chỉ những ký tự này được xuất hiện trong biểu thức kiểm tra
_KY_TU_HOP_LE = re.compile(r"^[0-9A-Za-z+\-*/^(),.\s]*$")


def _bieu_thuc_an_toan(bieu_thuc: str, ten_cho_phep: set) -> Tuple[bool, str]:
    """
    Kiểm duyệt biểu thức trước khi đưa vào sympy.

    Biểu thức do mô hình AI sinh ra, phải coi như dữ liệu không đáng tin.
    sympy.parse_expr dùng eval bên trong nên một chuỗi như
    "__import__('os').system('rm -rf /')" sẽ chạy thật nếu không chặn.
    """
    s = (bieu_thuc or "").strip()
    if not s:
        return False, "rỗng"
    if len(s) > 200:
        return False, "quá dài"
    if "__" in s:
        return False, "chứa dấu gạch dưới kép"
    if "'" in s or '"' in s:
        return False, "chứa chuỗi ký tự"
    if not _KY_TU_HOP_LE.match(s):
        la = sorted({c for c in s if not re.match(r"[0-9A-Za-z+\-*/^(),.\s]", c)})
        return False, f"chứa ký tự không cho phép: {''.join(la)}"

    # Dấu chấm chỉ được dùng trong số thập phân, không được dùng để truy cập thuộc tính
    for m in re.finditer(r"\.", s):
        i = m.start()
        truoc = s[i - 1] if i > 0 else ""
        sau = s[i + 1] if i + 1 < len(s) else ""
        if not (truoc.isdigit() or sau.isdigit()):
            return False, "dùng dấu chấm để truy cập thuộc tính"

    for ten in re.findall(r"[A-Za-z_]\w*", s):
        if ten not in ten_cho_phep:
            return False, f"dùng tên không được phép: {ten}"

    return True, ""


def kiem_tra_bang_sympy(q: ForgedQuestion) -> Tuple[Optional[bool], str]:
    """
    Tính lại biểu thức kiểm tra và so với giá trị mong đợi.

    Trả về (None, lý do) khi không áp dụng được — không có biểu thức, hoặc biểu
    thức không phân tích nổi. Không áp dụng được thì KHÔNG tính là trượt, vì
    phần lớn câu hỏi (tập nghiệm, mệnh đề, hình học tổng hợp) vốn không quy về
    được một con số.
    """
    if not q.check_expression.strip() or not q.check_expected.strip():
        return None, "Không có biểu thức kiểm tra"

    try:
        import sympy
        from sympy.parsing.sympy_parser import (
            parse_expr, standard_transformations, implicit_multiplication_application
        )
    except ImportError:
        return None, "Máy chưa cài sympy"

    cho_phep = {
        name: getattr(sympy, name) for name in (
            "sqrt", "pi", "E", "exp", "log", "ln", "sin", "cos", "tan",
            "asin", "acos", "atan", "Rational", "Abs", "factorial",
            "binomial", "Integer", "Float", "oo",
        ) if hasattr(sympy, name)
    }
    bien_doi = standard_transformations + (implicit_multiplication_application,)

    # parse_expr dùng eval bên trong: chỉ truyền local_dict là KHÔNG đủ an toàn.
    # Đã thử nghiệm và xác nhận biểu thức "__import__('os').system(...)" chạy
    # được thật. Biểu thức ở đây do mô hình AI sinh ra nên phải coi là dữ liệu
    # không đáng tin. Vì vậy chặn hai lớp trước khi phân tích:
    #   1. Mọi định danh phải nằm trong danh sách hàm toán được phép.
    #   2. Ký tự lạ, dấu chấm truy cập thuộc tính, dấu gạch dưới đều bị loại.
    for bieu_thuc in (q.check_expression, q.check_expected):
        an_toan, vi_pham = _bieu_thuc_an_toan(bieu_thuc, set(cho_phep))
        if not an_toan:
            return None, f"Biểu thức bị từ chối vì lý do an toàn: {vi_pham}"

    # Chặn nốt lớp cuối: không cho eval thấy builtins
    global_dict = dict(cho_phep)
    global_dict["__builtins__"] = {}

    try:
        thu = parse_expr(q.check_expression, local_dict=cho_phep,
                         global_dict=global_dict,
                         transformations=bien_doi, evaluate=True)
        mong_doi = parse_expr(q.check_expected, local_dict=cho_phep,
                              global_dict=global_dict,
                              transformations=bien_doi, evaluate=True)
    except Exception as e:
        return None, f"Không phân tích được biểu thức: {e}"

    try:
        hieu = sympy.simplify(thu - mong_doi)
        if hieu == 0:
            return True, f"sympy xác nhận {q.check_expression} = {q.check_expected}"
        # So sánh số thực cho trường hợp biểu thức không rút gọn về 0 tuyệt đối
        gia_tri = complex(sympy.N(hieu))
        if abs(gia_tri) < 1e-9:
            return True, f"sympy xác nhận (sai số {abs(gia_tri):.2e})"
        return False, f"sympy BÁC BỎ: {q.check_expression} ≠ {q.check_expected} (lệch {sympy.N(hieu)})"
    except Exception as e:
        return None, f"Không so sánh được: {e}"


# ---------------------------------------------------------------------------
# GỌI AI
# ---------------------------------------------------------------------------

def _mo_ta_chuyen_de(topic_key: str, subject: str) -> Dict[str, Any]:
    db = MATH_THEORY_DATABASE if subject == "toan" else PHYSICS_THEORY_DATABASE
    return db.get(topic_key, next(iter(db.values())))


class LoiHanMuc(RuntimeError):
    """Hết hạn mức gọi API — khác hẳn lỗi hệ thống, cần báo cho người dùng rõ."""


def _goi_json(client, model_name: str, prompt: str) -> Dict[str, Any]:
    from google.genai import types
    try:
        res = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
    except Exception as e:
        loi = str(e)
        if "RESOURCE_EXHAUSTED" in loi or "429" in loi:
            raise LoiHanMuc(
                f"Đã hết hạn mức gọi API trong ngày của khóa này (model {model_name}). "
                "Gói miễn phí chỉ cho 20 lượt/ngày. Hãy thử lại vào ngày mai, "
                "đổi sang khóa khác, hoặc nâng cấp gói Gemini API."
            ) from e
        if "API_KEY_INVALID" in loi or "API key not valid" in loi:
            raise RuntimeError("Khóa API không hợp lệ. Kiểm tra lại trong phần Cài Đặt AI.") from e
        raise RuntimeError(f"Gọi AI thất bại: {loi[:200]}") from e

    try:
        return json.loads(res.text)
    except (json.JSONDecodeError, TypeError) as e:
        raise RuntimeError(f"AI trả về dữ liệu không đúng định dạng JSON: {e}") from e


def sinh_cau_hoi(
    topic_key: str,
    subject: str = "toan",
    grade: str = "Lớp 12",
    level: str = "Vận dụng",
    so_luong: int = 4,
    api_key: str = "",
    model_name: str = "gemini-3.6-flash",
) -> List[ForgedQuestion]:
    """Gọi AI sinh một lô câu hỏi thô. Chưa kiểm chứng gì ở bước này."""
    if not api_key.strip():
        raise ValueError("Cần API key Gemini để sinh câu hỏi mới")

    so_luong = max(1, min(int(so_luong), MAX_PER_BATCH))
    from google import genai
    client = genai.Client(api_key=api_key.strip())

    chu_de = _mo_ta_chuyen_de(topic_key, subject)
    mon = "Toán học" if subject == "toan" else "Vật lý"

    prompt = f"""
Bạn là giáo viên {mon} giàu kinh nghiệm ra đề thi THPT theo chương trình GDPT 2018.

Hãy soạn {so_luong} câu hỏi TRẮC NGHIỆM MỚI cho:
- Chuyên đề: {chu_de.get('title')}
- Khối lớp: {grade}
- Mức độ: {level}

Kiến thức nền của chuyên đề này:
{chr(10).join(chu_de.get('concepts', [])[:4])}
{chr(10).join(chu_de.get('formulas', [])[:4])}

YÊU CẦU BẮT BUỘC:
1. Mỗi câu có đúng 4 phương án A, B, C, D. Bốn phương án phải KHÁC NHAU.
2. Đáp án đúng phải thực sự nằm trong 4 phương án đó.
3. Ba phương án sai phải là các sai lầm điển hình học sinh hay mắc, KHÔNG được
   là số ngẫu nhiên vô nghĩa.
4. Lời giải phải trình bày từng bước, ra đúng đáp án đã chọn.
5. TỰ KIỂM TRA LẠI phép tính trước khi trả về. Đây là tài liệu cho học sinh, một
   câu sai đáp án là không chấp nhận được.
6. Nếu đáp số quy về được một giá trị số, hãy điền "check_expression" là biểu
   thức tính ra đáp số đó theo cú pháp sympy (ví dụ "sqrt(18)/1000" hoặc
   "Rational(14,3)/2") và "check_expected" là giá trị đáp số (ví dụ "3*sqrt(2)/1000").
   Nếu không quy về số được (tập nghiệm, mệnh đề, phương trình mặt phẳng...) thì
   để cả hai trường là chuỗi rỗng. TUYỆT ĐỐI không bịa biểu thức cho có.
7. Dùng ký hiệu toán Unicode (², ³, √, π, ≤, ≥, ∫, ∈, ℝ), không dùng LaTeX.

TRẢ VỀ JSON THUẦN:
{{
  "questions": [
    {{
      "content": "Đề bài đầy đủ",
      "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
      "correct": "B",
      "solution": "• Bước 1: ...\\n• Bước 2: ...\\n• Chọn đáp án B.",
      "check_expression": "",
      "check_expected": ""
    }}
  ]
}}
"""
    data = _goi_json(client, model_name, prompt)
    now = datetime.now().isoformat(timespec="seconds")

    ket_qua: List[ForgedQuestion] = []
    for item in data.get("questions", [])[:so_luong]:
        ket_qua.append(ForgedQuestion(
            topic_key=topic_key,
            subject=subject,
            grade=grade,
            level=level,
            content=clean_paragraph_text(item.get("content", "")),
            options=[clean_paragraph_text(o) for o in item.get("options", [])],
            correct=(item.get("correct", "") or "").strip().upper()[:1],
            solution=(item.get("solution", "") or "").strip(),
            check_expression=(item.get("check_expression", "") or "").strip(),
            check_expected=(item.get("check_expected", "") or "").strip(),
            created_at=now,
            source_model=model_name,
        ))
    return ket_qua


def giai_lai_doc_lap(
    ds: List[ForgedQuestion],
    api_key: str,
    model_name: str = "gemini-3.6-flash",
) -> Dict[int, str]:
    """
    Đưa lại đề cho mô hình nhưng GIẤU đáp án và lời giải, bắt nó giải từ đầu.

    Đây là cửa chặn mạnh nhất: một câu sai đáp án thường không sống sót khi bị
    giải lại mà không được nhìn đáp án cũ. Chỉ tốn 1 lượt gọi cho cả lô.
    """
    if not ds:
        return {}

    from google import genai
    client = genai.Client(api_key=api_key.strip())

    khoi = []
    for i, q in enumerate(ds):
        khoi.append(f"--- Câu {i} ---\n{q.content}\n" + "\n".join(q.options))

    prompt = f"""
Bạn là giám khảo chấm thi. Hãy GIẢI ĐỘC LẬP từng câu trắc nghiệm dưới đây và
chọn đáp án đúng. Bạn KHÔNG được biết đáp án của người ra đề — hãy tự tính toán
từ đầu một cách cẩn thận.

Nếu một câu có lỗi (không phương án nào đúng, đề thiếu dữ kiện, hai phương án
cùng đúng) thì trả "answer" là "LOI" và ghi rõ vấn đề vào "note".

{chr(10).join(khoi)}

TRẢ VỀ JSON THUẦN:
{{
  "results": [
    {{"index": 0, "answer": "B", "note": ""}},
    {{"index": 1, "answer": "LOI", "note": "Không phương án nào đúng, đáp số thật là 5/2"}}
  ]
}}
"""
    try:
        data = _goi_json(client, model_name, prompt)
    except Exception as e:
        raise RuntimeError(f"Không giải lại được để đối chiếu: {e}")

    out: Dict[int, str] = {}
    for r in data.get("results", []):
        try:
            idx = int(r.get("index"))
        except (TypeError, ValueError):
            continue
        ans = (r.get("answer", "") or "").strip().upper()
        note = (r.get("note", "") or "").strip()
        out[idx] = ans if ans in ("A", "B", "C", "D") else f"LOI:{note or 'không rõ'}"
    return out


# ---------------------------------------------------------------------------
# QUY TRÌNH TỔNG: SINH → KIỂM CHỨNG → LƯU
# ---------------------------------------------------------------------------

def sinh_va_tham_dinh(
    topic_key: str,
    subject: str = "toan",
    grade: str = "Lớp 12",
    level: str = "Vận dụng",
    so_luong: int = 4,
    api_key: str = "",
    model_name: str = "gemini-3.6-flash",
) -> Dict[str, Any]:
    """Sinh một lô câu hỏi rồi chạy đủ ba lớp kiểm chứng."""
    tho = sinh_cau_hoi(topic_key, subject, grade, level, so_luong, api_key, model_name)
    if not tho:
        return {"dat": [], "truot": [], "tong": 0, "so_luot_goi_api": 1}

    # Lớp 1: cấu trúc — lọc trước để không phí lượt gọi cho câu đã hỏng rõ ràng
    qua_cau_truc: List[Tuple[int, ForgedQuestion]] = []
    for i, q in enumerate(tho):
        ok, loi = kiem_tra_cau_truc(q)
        if ok:
            q.checks_passed.append("Cấu trúc hợp lệ")
            qua_cau_truc.append((i, q))
        else:
            q.reject_reasons.extend(loi)

    so_luot = 1
    # Lớp 2: giải lại độc lập
    if qua_cau_truc:
        so_luot += 1
        try:
            ds_giai = [q for _, q in qua_cau_truc]
            ket = giai_lai_doc_lap(ds_giai, api_key, model_name)
            for vi_tri, (_, q) in enumerate(qua_cau_truc):
                tra_loi = ket.get(vi_tri, "")
                q.resolve_answer = tra_loi
                if not tra_loi:
                    q.reject_reasons.append("Không giải lại được để đối chiếu")
                elif tra_loi.startswith("LOI"):
                    q.reject_reasons.append(f"Giải lại phát hiện đề có vấn đề — {tra_loi[4:].lstrip(':')}")
                elif tra_loi != q.correct:
                    q.reject_reasons.append(
                        f"Giải lại ra đáp án {tra_loi} nhưng đề ghi {q.correct}"
                    )
                else:
                    q.checks_passed.append(f"Giải lại độc lập cũng ra {tra_loi}")
        except Exception as e:
            for _, q in qua_cau_truc:
                q.reject_reasons.append(str(e))

    # Lớp 3: đối chiếu sympy.
    # Chạy cho MỌI câu qua được lớp cấu trúc, kể cả câu đã bị lớp 2 loại — vì
    # lớp này không tốn lượt gọi API, mà lại cho người dùng biết đầy đủ hơn câu
    # đó sai ở đâu. Bỏ qua câu hỏng cấu trúc vì dữ liệu đã không đáng tin.
    da_qua_cau_truc = {id(q) for _, q in qua_cau_truc}
    for q in tho:
        if id(q) not in da_qua_cau_truc:
            continue
        kq, ly_do = kiem_tra_bang_sympy(q)
        if kq is True:
            q.checks_passed.append(ly_do)
        elif kq is False:
            q.reject_reasons.append(ly_do)
        # kq is None: không áp dụng được, bỏ qua chứ không tính là trượt

    # Chốt: chỉ câu không có lý do trượt nào mới được nhận
    for q in tho:
        q.verified = not q.reject_reasons
        if q.verified:
            # Bổ sung mẹo Casio và cảnh báo bẫy đúng chuyên đề
            q.casio_tip = q.casio_tip or get_casio_tip(topic_key, 0)
            q.trap_warning = q.trap_warning or get_trap_warning(topic_key, 0)

    dat = [q for q in tho if q.verified]
    truot = [q for q in tho if not q.verified]

    if dat:
        luu_vao_ngan_hang(dat)
    if truot:
        luu_cau_bi_loai(truot)

    return {
        "dat": [q.to_dict() for q in dat],
        "truot": [q.to_dict() for q in truot],
        "tong": len(tho),
        "so_luot_goi_api": so_luot,
    }


# ---------------------------------------------------------------------------
# LƯU TRỮ
# ---------------------------------------------------------------------------

def _doc_json(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _ghi_json(path: Path, data: List[Dict[str, Any]]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(path)   # ghi nguyên tử, tránh hỏng tệp khi ngắt giữa chừng


def _dau_van(q: Dict[str, Any]) -> str:
    """Nhận diện câu trùng: so theo nội dung đề đã chuẩn hóa."""
    return re.sub(r"\s+", " ", (q.get("content") or "")).strip().lower()


def luu_vao_ngan_hang(ds: List[ForgedQuestion]) -> int:
    """Thêm câu đã thẩm định vào ngân hàng, bỏ qua câu trùng đề."""
    hien_co = _doc_json(BANK_FILE)
    da_co = {_dau_van(q) for q in hien_co}
    them = 0
    for q in ds:
        d = q.to_dict()
        if _dau_van(d) in da_co:
            continue
        hien_co.append(d)
        da_co.add(_dau_van(d))
        them += 1
    if them:
        _ghi_json(BANK_FILE, hien_co)
    return them


def luu_cau_bi_loai(ds: List[ForgedQuestion]) -> int:
    """Giữ lại câu trượt kèm lý do, để người dùng xem AI sai ở đâu."""
    hien_co = _doc_json(REJECTED_FILE)
    hien_co.extend(q.to_dict() for q in ds)
    hien_co = hien_co[-300:]          # chỉ giữ 300 câu gần nhất
    _ghi_json(REJECTED_FILE, hien_co)
    return len(ds)


def doc_ngan_hang(topic_key: str = "", subject: str = "") -> List[Dict[str, Any]]:
    """Đọc các câu đã thẩm định, lọc theo chuyên đề hoặc môn nếu cần."""
    ds = _doc_json(BANK_FILE)
    if topic_key:
        ds = [q for q in ds if q.get("topic_key") == topic_key]
    if subject:
        ds = [q for q in ds if q.get("subject") == subject]
    return ds


def thong_ke_ngan_hang() -> Dict[str, Any]:
    """Số liệu tổng quan để hiển thị trên giao diện."""
    ds = _doc_json(BANK_FILE)
    bi_loai = _doc_json(REJECTED_FILE)

    theo_chuyen_de: Dict[str, int] = {}
    theo_cap_do: Dict[str, int] = {}
    for q in ds:
        theo_chuyen_de[q.get("topic_key", "?")] = theo_chuyen_de.get(q.get("topic_key", "?"), 0) + 1
        theo_cap_do[q.get("level", "?")] = theo_cap_do.get(q.get("level", "?"), 0) + 1

    return {
        "tong_da_tham_dinh": len(ds),
        "tong_bi_loai": len(bi_loai),
        "theo_chuyen_de": theo_chuyen_de,
        "theo_cap_do": theo_cap_do,
    }


def xoa_khoi_ngan_hang(content_prefix: str) -> int:
    """Xóa câu khỏi ngân hàng theo phần đầu của đề bài."""
    ds = _doc_json(BANK_FILE)
    moc = re.sub(r"\s+", " ", content_prefix).strip().lower()
    if not moc:
        return 0
    con_lai = [q for q in ds if not _dau_van(q).startswith(moc)]
    da_xoa = len(ds) - len(con_lai)
    if da_xoa:
        _ghi_json(BANK_FILE, con_lai)
    return da_xoa
