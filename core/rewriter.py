import os
import re
import json
import random
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from core.parser import QuestionItem
from core.math_engine import latex_to_unicode
from core.theory_bank import detect_subject_and_topic, build_pedagogical_theory_section

@dataclass
class RewrittenQuestionItem:
    index: int
    title: str = ""
    level: str = "Vận dụng"    # "Nhận biết", "Thông hiểu", "Vận dụng", "Vận dụng cao"
    original_content: str = ""
    original_solution: str = ""
    new_content: str = ""
    new_options: List[str] = field(default_factory=list)
    correct_answer: str = ""
    solution_method1: str = ""  # Lời giải Tự luận chuẩn mực sư phạm
    solution_method2: str = ""  # Kỹ thuật Casio fx-580VN X / Mẹo nhanh
    trap_warning: str = ""      # Cảnh báo bẫy & Sai lầm thường gặp
    is_added_new: bool = False  # Đánh dấu câu mới bổ sung
    source_file: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class RewrittenChapter:
    index: int
    title: str
    source_name: str
    theory_section: str
    questions: List[RewrittenQuestionItem] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "title": self.title,
            "source_name": self.source_name,
            "theory_section": self.theory_section,
            "total_questions": len(self.questions),
            "questions": [q.to_dict() for q in self.questions]
        }

@dataclass
class RewrittenBook:
    original_title: str
    new_title: str
    subtitle: str
    author_note: str
    chapter_summary: str
    theory_section: str = ""    # PHẦN I: KIẾN THỨC TRỌNG TÂM & LÝ THUYẾT NỀN TẢNG
    chapters: List[RewrittenChapter] = field(default_factory=list) # Hỗ trợ sách gộp nhiều chương
    questions: List[RewrittenQuestionItem] = field(default_factory=list) # Dành cho sách đơn

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_title": self.original_title,
            "new_title": self.new_title,
            "subtitle": self.subtitle,
            "author_note": self.author_note,
            "chapter_summary": self.chapter_summary,
            "theory_section": self.theory_section,
            "is_master_book": len(self.chapters) > 0,
            "total_chapters": len(self.chapters),
            "total_questions": sum(len(c.questions) for c in self.chapters) if self.chapters else len(self.questions),
            "chapters": [c.to_dict() for c in self.chapters],
            "questions": [q.to_dict() for q in self.questions]
        }


# ==========================================
# CƠ CHẾ SINH NỘI DUNG TỰ ĐỘNG & BẢO TOÀN KIẾN THỨC
# ==========================================

STEM_CONTEXTS_MATH = [
    "Trong một mô hình dự báo kinh tế số,",
    "Một kỹ sư thiết kế nhịp cầu dây văng cần xác định biên độ dao động thỏa mãn:",
    "Để tối ưu hóa chi phí sản xuất pin năng lượng mặt trời,",
    "Một hồ chứa nước thủy điện có lưu lượng xả thay đổi theo thời gian được mô hình hóa bởi:",
    "Trong quá trình phóng vệ tinh viễn thông lên quỹ đạo địa tĩnh,",
    "Một kiến trúc sư thiết kế vòm mái tòa nhà nghệ thuật có mặt cắt là đường cong:"
]

STEM_CONTEXTS_PHYSICS = [
    "Trong một thí nghiệm đo gia tốc trọng trường sử dụng cảm biến quang học,",
    "Một xe điện thông minh đang tăng tốc trên đường thử nghiệm với công suất không đổi:",
    "Khảo sát dao động của hệ giảm chấn trên tàu cao tốc Bắc - Nam khi qua khúc cua:",
    "Trong hệ thống truyền tải điện năng thông minh từ nhà máy điện gió ngoài khơi:",
    "Một chùm tia laser quang phổ hẹp được chiếu qua lăng kính trong buồng chân không:",
    "Một máy bay không người lái (UAV) đang bay tuần tra trên không phận biển đảo:"
]

CASIO_TIPS = [
    "Sử dụng tính năng TABLE (Menu 8 trên Casio fx-580VN X): Nhập hàm f(x) trên đoạn [Start, End] với Step = (End - Start)/29 để quét nhanh cực trị hoặc nghiệm.",
    "Sử dụng lệnh SHIFT SOLVE: Nhập phương trình, gán giá trị x xấp xỉ gần các đáp án để máy tính lặp Newton-Raphson tìm nghiệm nhanh chóng.",
    "Kỹ thuật CALC giá trị đại diện: Thay các giá trị đặc biệt của tham số (ví dụ m = 0, m = 100 hoặc m = 10) để loại trừ ngay 2-3 phương án sai trong 15 giây.",
    "Kỹ thuật tích phân vi phân: Nhấn phím tích phân ∫ hoặc đạo hàm d/dx tại điểm x₀ bất kỳ để so sánh trực tiếp kết quả với đạo hàm của từng đáp án.",
    "Dùng tính năng VECTOR / COMPLEX: Chuyển máy sang mode số phức (Menu 2) để cộng trừ biên độ và pha dao động cực nhanh mà không cần vẽ giản đồ Fresnel."
]

TRAP_WARNINGS = [
    "⚠️ Bẫy điều kiện xác định: Học sinh rất hay quên đặt điều kiện cho biểu thức dưới dấu căn bậc chẵn (≥ 0) hoặc biểu thức trong logarit (> 0), dẫn đến nhận nghiệm ngoại lai.",
    "⚠️ Bẫy đơn vị đo lường: Đề bài cho khoảng cách theo km nhưng vận tốc lại tính bằng m/s, hoặc tần số theo kHz. Không đổi về đơn vị chuẩn SI sẽ dẫn tới kết quả sai gấp bội số 10.",
    "⚠️ Bẫy pha ban đầu (Vật lý): Chú ý chiều chuyển động ban đầu. Nếu vật qua VTCB theo chiều dương thì pha ban đầu φ = -π/2; nếu theo chiều âm thì φ = +π/2.",
    "⚠️ Bẫy cực trị hàm số: Điểm cực trị của hàm số là x, giá trị cực trị là y, còn điểm cực trị của đồ thị hàm số là tọa độ (x; y). Đọc kỹ câu hỏi để không chọn nhầm.",
    "⚠️ Bẫy chia cho 0 khi biện luận tham số: Khi chia cả 2 vế cho biểu thức chứa tham số m, bắt buộc phải xét trường hợp hệ số bằng 0 trước."
]

LEVELS = ["Nhận biết", "Thông hiểu", "Vận dụng", "Vận dụng cao"]

def assign_cognitive_level(idx: int, total: int) -> str:
    """Phân loại cấp độ nhận thức chuẩn Bộ GD&ĐT: 30% NB, 40% TH, 20% VD, 10% VDC"""
    ratio = idx / max(1, total)
    if ratio <= 0.3:
        return "Nhận biết"
    elif ratio <= 0.7:
        return "Thông hiểu"
    elif ratio <= 0.9:
        return "Vận dụng"
    else:
        return "Vận dụng cao"

def generate_offline_enhancement(q: QuestionItem, idx: int, total: int, subject: str = "toan") -> RewrittenQuestionItem:
    """Sinh nội dung nâng cấp giữ nguyên cấu trúc gốc và bổ sung lời giải kép chuẩn mực"""
    clean_content = latex_to_unicode(q.content)

    # Làm mới văn phong nhẹ nhàng nhưng giữ trọn vẹn bản chất bài toán gốc
    prefix = random.choice(STEM_CONTEXTS_MATH if subject == "toan" else STEM_CONTEXTS_PHYSICS)
    if not clean_content.lower().startswith("trong") and not clean_content.lower().startswith("cho"):
        new_content = f"{prefix} {clean_content}"
    else:
        new_content = clean_content

    new_options = [latex_to_unicode(opt) for opt in q.options]

    sol1 = latex_to_unicode(q.solution)
    if not sol1:
        if subject == "toan":
            sol1 = (
                f"• Bước 1: Thiết lập điều kiện xác định và phân tích giả thiết của bài toán.\n"
                f"• Bước 2: Biến đổi biểu thức toán học, áp dụng định lý trọng tâm.\n"
                f"• Bước 3: Tìm ra kết quả cuối cùng, đối chiếu điều kiện để chọn đáp án chính xác: "
                f"{q.correct_answer or 'phương án tối ưu'}."
            )
        else:
            sol1 = (
                f"• Bước 1: Phân tích hiện tượng vật lý và chọn hệ quy chiếu chuẩn.\n"
                f"• Bước 2: Viết phương trình định luật vật lý cơ bản liên quan.\n"
                f"• Bước 3: Thay số liệu chuẩn SI và tính toán kết quả: "
                f"Đáp án chính xác là {q.correct_answer or 'phương án tối ưu'}."
            )

    sol2 = random.choice(CASIO_TIPS)
    trap = random.choice(TRAP_WARNINGS)
    level = assign_cognitive_level(idx, total)

    return RewrittenQuestionItem(
        index=idx,
        title=f"Câu {idx} [{level}]",
        level=level,
        original_content=q.content,
        original_solution=q.solution,
        new_content=new_content,
        new_options=new_options,
        correct_answer=q.correct_answer,
        solution_method1=sol1,
        solution_method2=sol2,
        trap_warning=trap,
        is_added_new=False,
        source_file=q.source_file
    )

def create_added_question(idx: int, subject: str = "toan") -> RewrittenQuestionItem:
    """Tạo thêm bài tập vận dụng cao mới theo chuẩn ma trận đề Bộ GD&ĐT"""
    if subject == "toan":
        content = (
            "Một mô hình sinh thái có sự biến thiên sinh khối theo thời gian t (ngày) "
            "thỏa mãn phương trình P(t) = 1200 / (1 + 8e^(-0.4t)). Xác định thời điểm t để "
            "tốc độ tăng trưởng sinh khối đạt giá trị lớn nhất."
        )
        opts = [
            "A. t = 2.5 ln 8 (ngày)",
            "B. t = ln 4 (ngày)",
            "C. t = 5 ln 2 (ngày)",
            "D. t = 3 ln 8 (ngày)"
        ]
        correct = "A"
        sol1 = (
            "• Tốc độ tăng trưởng sinh khối là đạo hàm bậc nhất P'(t).\n"
            "• Để P'(t) đạt cực đại thì đạo hàm bậc hai P''(t) = 0.\n"
            "• Giải phương trình P''(t) = 0 ta tìm được e^(-0.4t) = 1/8 ⇔ -0.4t = -ln 8 ⇔ t = ln 8 / 0.4 = 2.5 ln 8.\n"
            "• Kết luận: Tại thời điểm t = 2.5 ln 8 ngày, tốc độ tăng trưởng sinh khối đạt cực đại."
        )
        sol2 = "Dùng chức năng TABLE hoặc SOLVE trên Casio fx-580VN X: Nhập d/dx[P(X)] tại X, khảo sát giá trị cực đại để chọn nhanh đáp án A."
        trap = "⚠️ Nhầm lẫn giữa 'tốc độ tăng trưởng cực đại' (P'(t) max) và 'sinh khối cực đại' (P(t) max khi t → ∞)."
    else:
        content = (
            "Một mạch dao động LC lý tưởng có L = 2 mH, C = 8 nF. Tại thời điểm điện tích trên tụ điện "
            "bằng một nửa giá trị cực đại (q = Q₀/2) thì tỉ số giữa năng lượng từ trường trong cuộn cảm "
            "và năng lượng điện trường trong tụ điện là bao nhiêu?"
        )
        opts = [
            "A. 1",
            "B. 3",
            "C. 2",
            "D. 4"
        ]
        correct = "B"
        sol1 = (
            "• Năng lượng điện trường: W_C = q² / (2C) = (Q₀/2)² / (2C) = W / 4.\n"
            "• Năng lượng từ trường: W_L = W - W_C = W - W/4 = 3W / 4.\n"
            "• Tỉ số: W_L / W_C = (3W / 4) / (W / 4) = 3.\n"
            "• Đáp án chính xác là B."
        )
        sol2 = "Dùng trục thời gian lượng giác: Vị trí q = Q₀/2 tương ứng góc 60° trên đường tròn, tại đó thế năng bằng 1/4 cơ năng, suy ra từ năng chiếm 3/4 ➔ Tỉ số = 3."
        trap = "⚠️ Nhầm lẫn tỉ số giữa W_L / W_C với tỉ số W_L / W (dẫn đến chọn nhầm 3/4 hoặc 75%)."

    return RewrittenQuestionItem(
        index=idx,
        title=f"Câu {idx} [Vận dụng cao - Phân hóa điểm 10]",
        level="Vận dụng cao",
        original_content="[Bài toán bổ sung phân hóa]",
        original_solution="",
        new_content=content,
        new_options=opts,
        correct_answer=correct,
        solution_method1=sol1,
        solution_method2=sol2,
        trap_warning=trap,
        is_added_new=True
    )


# ==========================================
# CƠ CHẾ GOOGLE GEMINI AI REWRITER
# ==========================================

def rewrite_with_gemini(
    questions: List[QuestionItem],
    api_key: str,
    model_name: str = "gemini-2.5-flash",
    subject: str = "toan",
    add_count: int = 2
) -> RewrittenBook:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    total_orig = len(questions)
    new_total = total_orig + add_count

    # Trích xuất lý thuyết nền tảng
    all_texts = [q.content for q in questions]
    topic_data = detect_subject_and_topic(all_texts, subject=subject)
    theory_text = build_pedagogical_theory_section(topic_data)

    sample_text = ""
    for q in questions[:20]:
        opts = "\n".join(q.options) if q.options else ""
        sample_text += f"\n--- Câu {q.index} ---\nĐề: {q.content}\n{opts}\nĐáp án: {q.correct_answer}\nGiải: {q.solution}\n"

    prompt = f"""
Bạn là chuyên gia biên soạn tài liệu giảng dạy { 'Toán học' if subject == 'toan' else 'Vật lý' } theo chuẩn chương trình GDPT 2018 của Bộ Giáo dục và Đào tạo Việt Nam.
Tôi có tài liệu gồm {total_orig} bài tập. Nhiệm vụ của bạn là:
1. GIỮ NGUYÊN MẠCH KIẾN THỨC VÀ CẤU TRÚC GỐC, nâng cấp câu từ mạch lạc, khoa học, sư phạm.
2. Phân cấp độ từng câu: 'Nhận biết', 'Thông hiểu', 'Vận dụng', 'Vận dụng cao'.
3. Viết lời giải 2 cách: Cách 1 (Tự luận chuẩn mực) + Cách 2 (Mẹo Casio fx-580VN X).
4. Chỉ ra cảnh báo bẫy sai lầm của học sinh.
5. Thêm {add_count} câu hỏi vận dụng cao sáng tạo vào cuối sách (tổng {new_total} câu).

Dữ liệu gốc:
{sample_text}

TRẢ VỀ ĐỊNH DẠNG JSON:
{{
  "new_title": "Tên sách/cẩm nang chuẩn",
  "subtitle": "Phụ đề phân hóa",
  "author_note": "Lời tựa sư phạm",
  "questions": [
    {{
      "index": 1,
      "title": "Câu 1",
      "level": "Thông hiểu",
      "new_content": "Đề bài đã nâng cấp",
      "new_options": ["A. ...", "B. ...", "C. ...", "D. ..."],
      "correct_answer": "A",
      "solution_method1": "Lời giải tự luận bài bản",
      "solution_method2": "Mẹo Casio / Giải nhanh",
      "trap_warning": "Bẫy sai lầm"
    }}
  ]
}}
Chỉ trả về JSON thuần túy.
"""
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        data = json.loads(response.text)
        rewritten_items: List[RewrittenQuestionItem] = []
        q_map = {q.index: q for q in questions}

        for q_json in data.get("questions", []):
            orig_q = q_map.get(q_json.get("index"))
            rewritten_items.append(RewrittenQuestionItem(
                index=q_json.get("index", len(rewritten_items) + 1),
                title=f"Câu {len(rewritten_items) + 1} [{q_json.get('level', 'Vận dụng')}]",
                level=q_json.get("level", "Vận dụng"),
                original_content=orig_q.content if orig_q else "",
                original_solution=orig_q.solution if orig_q else "",
                new_content=latex_to_unicode(q_json.get("new_content", "")),
                new_options=[latex_to_unicode(o) for o in q_json.get("new_options", [])],
                correct_answer=q_json.get("correct_answer", ""),
                solution_method1=latex_to_unicode(q_json.get("solution_method1", "")),
                solution_method2=latex_to_unicode(q_json.get("solution_method2", "")),
                trap_warning=latex_to_unicode(q_json.get("trap_warning", "")),
                is_added_new=False
            ))

        if len(rewritten_items) < total_orig:
            for idx in range(len(rewritten_items), total_orig):
                rewritten_items.append(generate_offline_enhancement(questions[idx], idx + 1, new_total, subject))

        while len(rewritten_items) < new_total:
            rewritten_items.append(create_added_question(len(rewritten_items) + 1, subject))

        return RewrittenBook(
            original_title=f"Tài liệu {total_orig} bài toán",
            new_title=data.get("new_title", f"{new_total} Tuyệt Kỹ Chinh Phục Điểm 9+ { 'Toán Học' if subject == 'toan' else 'Vật Lý' }"),
            subtitle=data.get("subtitle", "Hệ Thống Kiến Thức Trọng Tâm, Phân Dạng & Lời Giải Đa Chiều"),
            author_note=data.get("author_note", "Tài liệu được biên soạn đồng bộ theo định hướng phát triển năng lực học sinh, chuẩn chương trình GDPT 2018."),
            chapter_summary=topic_data.get("title", ""),
            theory_section=theory_text,
            questions=rewritten_items
        )
    except Exception as e:
        print(f"Gemini API gặp lỗi: {e}. Tự động chạy chế độ Offline Engine.")
        return rewrite_offline(questions, subject=subject, add_count=add_count)


# ==========================================
# CƠ CHẾ OFFLINE ENGINE & GỘP NHIỀU FILE THÀNH MASTER BOOK
# ==========================================

def rewrite_offline(questions: List[QuestionItem], subject: str = "toan", add_count: int = 2) -> RewrittenBook:
    """Biên soạn giữ nguyên cấu trúc gốc và bổ sung Lý thuyết chuẩn GDPT 2018"""
    total_orig = len(questions)
    new_total = total_orig + add_count

    all_texts = [q.content for q in questions]
    topic_data = detect_subject_and_topic(all_texts, subject=subject)
    theory_text = build_pedagogical_theory_section(topic_data)

    rewritten_items: List[RewrittenQuestionItem] = []
    for idx, q in enumerate(questions, 1):
        enh = generate_offline_enhancement(q, idx, new_total, subject=subject)
        rewritten_items.append(enh)

    for i in range(1, add_count + 1):
        rewritten_items.append(create_added_question(total_orig + i, subject=subject))

    sub_name = "Toán Học" if subject == "toan" else "Vật Lý"
    return RewrittenBook(
        original_title=f"{total_orig} Bài tập {sub_name}",
        new_title=f"{new_total} Tuyệt Kỹ Chinh Phục Điểm 9+ {sub_name}",
        subtitle="Hệ Thống Kiến Thức Trọng Tâm, Phân Dạng Bài Tập & Lời Giải Đa Chiều Chuẩn BGD",
        author_note=(
            "Tài liệu này được tái cấu trúc toàn diện theo chuẩn chương trình GDPT 2018: "
            "Trình bày mạch lạc từ Kiến thức trọng tâm, Phương pháp tư duy đến Hệ thống bài tập 4 cấp độ nhận thức. "
            "Bổ sung lời giải tự luận bài bản, kỹ thuật giải nhanh máy tính cầm tay và phân tích bẫy đề thi."
        ),
        chapter_summary=topic_data.get("title", ""),
        theory_section=theory_text,
        questions=rewritten_items
    )

def create_master_book_from_chapters(
    chapter_data_list: List[Dict[str, Any]],
    subject: str = "toan",
    master_title: Optional[str] = None
) -> RewrittenBook:
    """Gom toàn bộ các tài liệu trong một thư mục thành 1 cuốn ĐẠI CẨM NANG duy nhất"""
    chapters: List[RewrittenChapter] = []

    for c_idx, data in enumerate(chapter_data_list, 1):
        source_name = data.get("source_name", f"Tài liệu {c_idx}")
        questions = data.get("questions", [])

        # Phát hiện chuyên đề lý thuyết riêng cho từng chương
        all_texts = [q.content for q in questions]
        topic_data = detect_subject_and_topic(all_texts, subject=subject)
        theory_text = build_pedagogical_theory_section(topic_data)

        # Xử lý các câu hỏi trong chương
        rewritten_items: List[RewrittenQuestionItem] = []
        for q_idx, q in enumerate(questions, 1):
            enh = generate_offline_enhancement(q, q_idx, len(questions), subject=subject)
            rewritten_items.append(enh)

        clean_chapter_name = Path(source_name).stem.replace("_", " ").replace("-", " ")
        chapters.append(RewrittenChapter(
            index=c_idx,
            title=f"CHƯƠNG {c_idx}: {clean_chapter_name.upper()}",
            source_name=source_name,
            theory_section=theory_text,
            questions=rewritten_items
        ))

    sub_name = "Toán Học" if subject == "toan" else "Vật Lý"
    final_title = master_title or f"ĐẠI CẨM NANG TOÀN DIỆN MÔN {sub_name.upper()}"

    return RewrittenBook(
        original_title="Bộ tài liệu tổng hợp",
        new_title=final_title,
        subtitle="Tuyển Tập Chuyên Đề Bồi Dưỡng - Kiến Thức Trọng Tâm & Lời Giải Chi Tiết Chuẩn BGD",
        author_note=(
            f"Cuốn đại cẩm nang được tổng hợp và biên soạn đồng bộ từ toàn bộ thư mục tài liệu gốc. "
            f"Bố cục sách gồm {len(chapters)} chương bài bản, tích hợp đầy đủ lý thuyết nền tảng, "
            f"hệ thống bài tập phân loại theo cấp độ nhận thức và hướng dẫn giải chi tiết."
        ),
        chapter_summary=f"Tuyển tập {len(chapters)} chương chuyên đề trọng tâm môn {sub_name}",
        theory_section="",
        chapters=chapters,
        questions=[]
    )

def process_rewrite_pipeline(
    questions: List[QuestionItem],
    subject: str = "toan",
    add_count: int = 2,
    api_key: Optional[str] = None,
    model_name: str = "gemini-2.5-flash"
) -> RewrittenBook:
    if api_key and api_key.strip():
        return rewrite_with_gemini(questions, api_key=api_key.strip(), model_name=model_name, subject=subject, add_count=add_count)
    else:
        return rewrite_offline(questions, subject=subject, add_count=add_count)
