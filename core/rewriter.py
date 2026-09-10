import os
import re
import json
import random
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from core.parser import QuestionItem
from core.math_engine import latex_to_unicode

@dataclass
class RewrittenQuestionItem:
    index: int
    title: str = ""
    original_content: str = ""
    original_solution: str = ""
    new_content: str = ""
    new_options: List[str] = field(default_factory=list)
    correct_answer: str = ""
    solution_method1: str = ""  # Tự luận chuẩn mực
    solution_method2: str = ""  # Mẹo Casio / Giải nhanh
    trap_warning: str = ""      # Cảnh báo bẫy & Sai lầm thường gặp
    is_added_new: bool = False  # Đánh dấu bài tập bổ sung thêm

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class RewrittenBook:
    original_title: str
    new_title: str
    subtitle: str
    author_note: str
    chapter_summary: str
    questions: List[RewrittenQuestionItem] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_title": self.original_title,
            "new_title": self.new_title,
            "subtitle": self.subtitle,
            "author_note": self.author_note,
            "chapter_summary": self.chapter_summary,
            "total_questions": len(self.questions),
            "questions": [q.to_dict() for q in self.questions]
        }


# ==========================================
# CƠ CHẾ SINH NỘI DUNG THÔNG MINH (OFFLINE ENGINE)
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

def generate_offline_enhancement(q: QuestionItem, idx: int, subject: str = "toan") -> RewrittenQuestionItem:
    """Sinh nội dung nâng cấp khi chạy ở chế độ Offline (Template Rule-based)"""
    # Làm mới đề bài
    prefix = random.choice(STEM_CONTEXTS_MATH if subject == "toan" else STEM_CONTEXTS_PHYSICS)
    clean_content = latex_to_unicode(q.content)
    
    # Biến đổi nhẹ câu từ để tạo phong cách cẩm nang chuyên sâu
    new_content = f"{prefix} {clean_content}" if not clean_content.lower().startswith("trong") else clean_content

    # Tạo phương án mới nếu có
    new_options = [latex_to_unicode(opt) for opt in q.options]

    # Lời giải cách 1: Tự luận chuẩn mực
    sol1 = latex_to_unicode(q.solution)
    if not sol1:
        if subject == "toan":
            sol1 = (
                f"• Bước 1: Thiết lập điều kiện xác định của bài toán.\n"
                f"• Bước 2: Biến đổi biểu thức đại số, áp dụng các tính chất giải tích/hình học trọng tâm.\n"
                f"• Bước 3: Tìm ra kết quả cuối cùng và đối chiếu điều kiện để kết luận: "
                f"Đáp án chính xác là {q.correct_answer or 'phương án tối ưu'}."
            )
        else:
            sol1 = (
                f"• Bước 1: Phân tích hiện tượng vật lý và chọn hệ quy chiếu phù hợp.\n"
                f"• Bước 2: Viết phương trình định luật vật lý cơ bản liên quan đến bài toán.\n"
                f"• Bước 3: Thay số liệu chuẩn SI và tính toán kết quả: "
                f"Đáp án chính xác là {q.correct_answer or 'phương án tối ưu'}."
            )

    # Lời giải cách 2: Mẹo Casio / Giải nhanh
    sol2 = random.choice(CASIO_TIPS)

    # Cảnh báo bẫy
    trap = random.choice(TRAP_WARNINGS)

    return RewrittenQuestionItem(
        index=idx,
        title=f"Bài toán {idx} [Trọng điểm bứt phá]",
        original_content=q.content,
        original_solution=q.solution,
        new_content=new_content,
        new_options=new_options,
        correct_answer=q.correct_answer,
        solution_method1=sol1,
        solution_method2=sol2,
        trap_warning=trap,
        is_added_new=False
    )

def create_added_question(idx: int, subject: str = "toan") -> RewrittenQuestionItem:
    """Tạo thêm bài tập phân hóa vận dụng cao (+2, +5 bài mới)"""
    if subject == "toan":
        content = (
            "Một hồ chứa sinh thái có lượng vi sinh vật phát triển theo hàm số P(t) = 1000 / (1 + 9e^(-0.5t)), "
            "với t tính bằng ngày. Hãy xác định thời điểm mà tốc độ gia tăng sinh khối đạt giá trị lớn nhất."
        )
        opts = [
            "A. t = 2 ln 9 (ngày)",
            "B. t = ln 3 (ngày)",
            "C. t = 4 ln 3 (ngày)",
            "D. t = ln 9 (ngày)"
        ]
        correct = "A"
        sol1 = (
            "Tốc độ gia tăng sinh khối là đạo hàm P'(t). Để P'(t) đạt cực đại, ta khảo sát P''(t) = 0.\n"
            "Tính đạo hàm cấp 2 và giải phương trình P''(t) = 0 ta thu được e^(-0.5t) = 1/9 ⇔ -0.5t = -ln 9 ⇔ t = 2 ln 9.\n"
            "Kết luận: Sau t = 2 ln 9 ngày, tốc độ gia tăng vi sinh vật đạt cực đại."
        )
        sol2 = "Bấm TABLE trên máy tính: Nhập d/dx[P(x)] tại x = X với Start = 0, End = 10, Step = 0.5. Tìm giá trị đạo hàm lớn nhất tương ứng với đáp án A."
        trap = "⚠️ Nhầm lẫn giữa 'sinh khối đạt cực đại' (khi t → ∞) và 'tốc độ gia tăng sinh khối đạt cực đại' (khi P''(t) = 0). Đọc kỹ câu hỏi để không xét sai hàm."
    else:
        content = (
            "Trong mạch dao động LC lý tưởng đang có dao động điện từ tự do. "
            "Tại thời điểm điện tích trên bản tụ q = Q₀/√2 thì năng lượng từ trường trong cuộn cảm "
            "chiếm bao nhiêu phần trăm tổng năng lượng điện từ của mạch?"
        )
        opts = [
            "A. 25%",
            "B. 50%",
            "C. 75%",
            "D. 100%"
        ]
        correct = "B"
        sol1 = (
            "Năng lượng điện trường: W_C = q² / (2C) = (Q₀² / 2C) * (1/2) = W / 2.\n"
            "Do năng lượng điện từ bảo toàn: W_L = W - W_C = W - W/2 = W/2 = 50% W.\n"
            "Chọn đáp án B."
        )
        sol2 = "Dùng vòng tròn lượng giác hoặc trục phân bố thời gian: Tại vị trí q = Q₀/√2 (tương đương góc 45°), thế năng bằng động năng (W_C = W_L = 50% W) chỉ mất 5 giây suy luận."
        trap = "⚠️ Nhầm lẫn giữa biên độ điện áp và cường độ dòng điện tức thời, hoặc nhầm công thức năng lượng từ trường W_L = 1/2 L i²."

    return RewrittenQuestionItem(
        index=idx,
        title=f"Bài toán {idx} [Bổ sung nâng cao - Vận dụng thực chiến]",
        original_content="[Bài toán sáng tạo mới]",
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
    """Sử dụng Google GenAI SDK để biên soạn lại sách một cách tự nhiên và sáng tạo"""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    total_orig = len(questions)
    new_total = total_orig + add_count

    # Rút gọn danh sách câu hỏi mẫu gửi cho AI
    sample_questions_text = ""
    for q in questions[:15]:  # Xử lý theo đợt
        opts_txt = "\n".join(q.options) if q.options else ""
        sample_questions_text += f"\n--- Câu {q.index} ---\nĐề: {q.content}\n{opts_txt}\nĐáp án: {q.correct_answer}\nGiải: {q.solution}\n"

    prompt = f"""
Bạn là chuyên gia biên soạn sách giáo khoa và sách tham khảo luyện thi { 'Toán học' if subject == 'toan' else 'Vật lý' } hàng đầu Việt Nam.
Tôi có một tài liệu gốc gồm {total_orig} bài toán. 
Nhiệm vụ của bạn là BIÊN SOẠN LẠI HOÀN TOÀN để xuất bản một cuốn sách mới đẳng cấp hơn:
1. Đặt tựa đề sách mới ấn tượng, cuốn hút (Ví dụ: Từ '{total_orig} bài toán hay' thành '{new_total} Tuyệt Kỹ Chinh Phục...').
2. Tạo Lời tựa (Author note) ngắn gọn, truyền cảm hứng.
3. Bảng công thức vàng & Sơ đồ tư duy trọng tâm của chủ đề này (Chapter summary).
4. Viết lại từng bài toán:
   - Đề bài: Thay đổi ngữ cảnh thực tế (STEM, đời sống), đổi câu từ, đảm bảo số liệu khoa học chính xác.
   - Giữ hoặc tạo 4 phương án trắc nghiệm A, B, C, D (nếu là trắc nghiệm).
   - Lời giải Cách 1: Tự luận bài bản, chuẩn mực sư phạm.
   - Lời giải Cách 2: Kỹ thuật bấm máy tính Casio fx-580VN X hoặc mẹo suy luận nhanh.
   - Khung Cảnh báo bẫy: Chỉ ra lỗi sai phổ biến học sinh hay mắc phải tại dạng toán này.
5. Bổ sung thêm {add_count} bài toán vận dụng cao sáng tạo mới vào cuối sách để nâng tổng số lên {new_total} bài.

Dữ liệu đầu vào:
{sample_questions_text}

HÃY TRẢ VỀ ĐỊNH DẠNG JSON HỢP LỆ VỚI CẤU TRÚC:
{{
  "new_title": "Tên sách mới cuốn hút",
  "subtitle": "Phụ đề sách",
  "author_note": "Lời tựa sách",
  "chapter_summary": "Bảng tổng hợp công thức & phương pháp tư duy trọng tâm",
  "questions": [
    {{
      "index": 1,
      "title": "Tên đề mục câu",
      "new_content": "Nội dung đề bài viết lại",
      "new_options": ["A. ...", "B. ...", "C. ...", "D. ..."],
      "correct_answer": "A",
      "solution_method1": "Lời giải tự luận chuẩn mực",
      "solution_method2": "Mẹo Casio / Giải nhanh",
      "trap_warning": "Cảnh báo bẫy sai lầm"
    }}
  ]
}}
Chỉ trả về chuỗi JSON thuần túy, không bao bọc thêm code block hay văn bản giải thích.
"""

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                response_mime_type="application/json"
            )
        )
        data = json.loads(response.text)

        rewritten_items: List[RewrittenQuestionItem] = []
        q_map = {q.index: q for q in questions}

        for q_json in data.get("questions", []):
            orig_q = q_map.get(q_json.get("index"), None)
            item = RewrittenQuestionItem(
                index=q_json.get("index", len(rewritten_items) + 1),
                title=q_json.get("title", f"Bài toán {len(rewritten_items) + 1}"),
                original_content=orig_q.content if orig_q else "",
                original_solution=orig_q.solution if orig_q else "",
                new_content=latex_to_unicode(q_json.get("new_content", "")),
                new_options=[latex_to_unicode(opt) for opt in q_json.get("new_options", [])],
                correct_answer=q_json.get("correct_answer", ""),
                solution_method1=latex_to_unicode(q_json.get("solution_method1", "")),
                solution_method2=latex_to_unicode(q_json.get("solution_method2", "")),
                trap_warning=latex_to_unicode(q_json.get("trap_warning", "")),
                is_added_new=False
            )
            rewritten_items.append(item)

        # Nếu AI trả về ít câu hơn số câu gốc, bổ sung các câu còn lại bằng engine offline
        if len(rewritten_items) < total_orig:
            for idx in range(len(rewritten_items), total_orig):
                rewritten_items.append(generate_offline_enhancement(questions[idx], idx + 1, subject))

        # Thêm các câu sáng tạo mới nếu chưa đủ
        while len(rewritten_items) < new_total:
            next_idx = len(rewritten_items) + 1
            rewritten_items.append(create_added_question(next_idx, subject))

        return RewrittenBook(
            original_title=f"{total_orig} Bài toán chọn lọc",
            new_title=data.get("new_title", f"{new_total} Tuyệt Kỹ Bứt Phá Điểm 9+ { 'Toán Học' if subject == 'toan' else 'Vật Lý' }"),
            subtitle=data.get("subtitle", "Hệ thống bài tập phân hóa - Tích hợp mẹo Casio & Tránh bẫy đề thi"),
            author_note=data.get("author_note", "Cuốn sách được biên soạn lại với phương pháp tư duy đột phá, giúp bạn làm chủ mọi dạng đề thi."),
            chapter_summary=data.get("chapter_summary", "Tổng hợp toàn bộ công thức trọng tâm và phương pháp giải nhanh theo từng chuyên đề."),
            questions=rewritten_items
        )
    except Exception as e:
        print(f"Gemini API gặp lỗi: {e}. Tự động chuyển sang chế độ Offline Rule-based Engine.")
        return rewrite_offline(questions, subject=subject, add_count=add_count)


# ==========================================
# CƠ CHẾ TỔNG HỢP & ĐIỀU PHỐI (MAIN PIPELINE)
# ==========================================

def rewrite_offline(questions: List[QuestionItem], subject: str = "toan", add_count: int = 2) -> RewrittenBook:
    """Biên soạn lại hoàn toàn bằng Rule-based Math Engine (Không cần API Key)"""
    total_orig = len(questions)
    new_total = total_orig + add_count

    rewritten_items: List[RewrittenQuestionItem] = []
    for idx, q in enumerate(questions, 1):
        enh = generate_offline_enhancement(q, idx, subject=subject)
        rewritten_items.append(enh)

    for i in range(1, add_count + 1):
        added = create_added_question(total_orig + i, subject=subject)
        rewritten_items.append(added)

    sub_name = "Toán Học" if subject == "toan" else "Vật Lý"
    return RewrittenBook(
        original_title=f"{total_orig} Bài tập {sub_name} cơ bản",
        new_title=f"{new_total} Tuyệt Kỹ Bứt Phá Điểm 9+ {sub_name}",
        subtitle="Hệ thống bài tập phân hóa - Tích hợp mẹo bấm máy Casio fx-580VN X & Cảnh báo bẫy đề thi",
        author_note=(
            "Tài liệu này được tái cấu trúc toàn diện nhằm cung cấp cho học sinh và giáo viên "
            "một góc nhìn đa chiều: Không chỉ dừng lại ở lời giải tự luận truyền thống mà còn "
            "trang bị kỹ năng giải nhanh máy tính cầm tay và nhận diện bẫy đề thi sắc bén."
        ),
        chapter_summary=(
            f"BẢNG CÔNG THỨC VÀNG & PHƯƠNG PHÁP CỐT LÕI - CHỦ ĐỀ {sub_name.upper()}:\n"
            f"1. Luôn kiểm tra điều kiện tồn tại và đơn vị chuẩn SI trước khi bắt đầu tính toán.\n"
            f"2. Ưu tiên biểu diễn các đại lượng phức tạp về dạng hàm số đơn giản hoặc sơ đồ tư duy.\n"
            f"3. Tận dụng tối đa kỹ thuật thử đáp án ngược và quét bảng TABLE trên máy tính cầm tay."
        ),
        questions=rewritten_items
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
