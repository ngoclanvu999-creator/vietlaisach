import os
import re
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from core.parser import QuestionItem
from core.math_engine import format_math_typography, clean_paragraph_text
from core.theory_bank import (
    detect_subject_and_topic, build_pedagogical_theory_section,
    get_casio_tip, get_trap_warning
)
from core.ai_namer import synthesize_book_metadata
from core.doc_type import DE_THI, SACH, CHUYEN_DE
from core.ai_provider import GEMINI, CLAUDE, chuan_hoa, goi_ai, boc_json, LoiHanMuc
from core.skill_loader import (
    nap_van_ban_skill, huong_dan_giong_van, phat_hien_cap_hoc,
    TIEU_HOC, THCS, THPT, TEN_CAP_HOC as TEN_CAP,
)

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
    valedictorian_secrets: List[str] = field(default_factory=list) # Lời khuyên vàng từ Thủ khoa
    stem_connection: str = ""   # Góc kết nối thực tiễn STEM GDPT 2018
    creative_options: List[Dict[str, Any]] = field(default_factory=list) # Danh sách 5 tựa sách thôi miên từ Gemini
    chapters: List[RewrittenChapter] = field(default_factory=list)
    questions: List[RewrittenQuestionItem] = field(default_factory=list)
    # Loại tài liệu quyết định cách trình bày đầu ra: DE_THI xuất ra đề sạch với
    # đáp án dồn về cuối; SACH và CHUYEN_DE xuất ra sách có lý thuyết và lời giải
    # ngay dưới mỗi bài. Xem core/doc_type.py.
    doc_type: str = "CHUYEN_DE"
    exam_info: Dict[str, str] = field(default_factory=dict)
    # Cap hoc quyet dinh giong van VA muc trang tri khi dung file Word.
    # Tieu hoc duoc them bieu tuong va trang tri, TRU giao an. Xem skill_loader.
    cap_hoc: str = "THPT"
    # Loai dau ra nguoi dung chon (mot trong chin loai). Rong thi dung bo
    # dung cu theo doc_type.
    loai_dau_ra: str = ""
    subject: str = "toan"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_type": self.doc_type,
            "exam_info": self.exam_info,
            "cap_hoc": self.cap_hoc,
            "loai_dau_ra": self.loai_dau_ra,
            "original_title": self.original_title,
            "new_title": self.new_title,
            "subtitle": self.subtitle,
            "author_note": self.author_note,
            "chapter_summary": self.chapter_summary,
            "theory_section": self.theory_section,
            "valedictorian_secrets": self.valedictorian_secrets,
            "stem_connection": self.stem_connection,
            "creative_options": self.creative_options,
            "is_master_book": len(self.chapters) > 0,
            "total_chapters": len(self.chapters),
            "total_questions": sum(len(c.questions) for c in self.chapters) if self.chapters else len(self.questions),
            "chapters": [c.to_dict() for c in self.chapters],
            "questions": [q.to_dict() for q in self.questions]
        }



def assign_cognitive_level(idx: int, total: int) -> str:
    """Phân loại cấp độ nhận thức chuẩn ma trận đề thi Bộ GD&ĐT"""
    ratio = idx / max(1, total)
    if ratio <= 0.35:
        return "Nhận biết"
    elif ratio <= 0.70:
        return "Thông hiểu"
    elif ratio <= 0.90:
        return "Vận dụng"
    else:
        return "Vận dụng cao"

def generate_offline_enhancement(
    q: QuestionItem,
    idx: int,
    total: int,
    subject: str = "toan",
    topic_key: Optional[str] = None
) -> RewrittenQuestionItem:
    """
    Chuẩn hóa nội dung câu hỏi:
    - GIỮ NGUYÊN 100% CẤU TRÚC VÀ BẢN CHẤT CÂU HỎI GỐC (Tuyệt đối không chèn tiền tố ngẫu nhiên gây sai nghĩa).
    - Làm sạch toàn bộ ngắt dòng \n, định dạng toán học chuẩn mực.
    - Bổ sung lời giải tự luận bài bản + Mẹo Casio + Cảnh báo bẫy sai lầm.
    """
    clean_content = clean_paragraph_text(q.content)
    clean_options = [clean_paragraph_text(opt) for opt in q.options if opt.strip()]

    sol1 = clean_paragraph_text(q.solution)
    if not sol1:
        if subject == "toan":
            sol1 = (
                f"• Bước 1: Thiết lập điều kiện xác định và phân tích giả thiết của bài toán.\n"
                f"• Bước 2: Biến đổi đại số, áp dụng định nghĩa và các công thức giải tích/hình học trọng tâm.\n"
                f"• Bước 3: Đối chiếu với điều kiện bài toán để kết luận nghiệm: "
                f"Đáp án chính xác là {q.correct_answer or 'phương án tương ứng'}."
            )
        else:
            sol1 = (
                f"• Bước 1: Phân tích hiện tượng vật lý và chọn hệ quy chiếu phù hợp.\n"
                f"• Bước 2: Thiết lập phương trình định luật vật lý cơ bản liên quan đến đại lượng cần tìm.\n"
                f"• Bước 3: Thay số liệu chuẩn SI và tính toán kết quả: "
                f"Đáp án chính xác là {q.correct_answer or 'phương án tương ứng'}."
            )

    # Mẹo Casio và cảnh báo bẫy phải KHỚP chuyên đề của bài. Trước đây dùng
    # random.choice nên một bài xác suất có thể bị gắn mẹo về dao động điều hòa.
    #
    # Nhận diện theo TỪNG CÂU chứ không theo cả tài liệu: một cuốn sách thường
    # trộn nhiều chuyên đề, lấy chuyên đề chung sẽ gắn mẹo hàm số cho cả bài
    # logarit lẫn bài tích phân. Câu nào không đủ từ khóa để nhận diện thì mới
    # lùi về chuyên đề chung của tài liệu.
    q_topic = detect_subject_and_topic([clean_content], subject=subject)
    effective_topic = q_topic["topic_key"] if q_topic.get("match_score", 0) > 0 else topic_key

    sol2 = get_casio_tip(effective_topic, idx - 1)
    trap = get_trap_warning(effective_topic, idx - 1)
    level = assign_cognitive_level(idx, total)

    return RewrittenQuestionItem(
        index=idx,
        title=f"Câu {idx} [{level}]",
        level=level,
        original_content=q.content,
        original_solution=q.solution,
        new_content=clean_content,
        new_options=clean_options,
        correct_answer=q.correct_answer,
        solution_method1=sol1,
        solution_method2=sol2,
        trap_warning=trap,
        is_added_new=False,
        source_file=q.source_file
    )

# ============================================================
# NGÂN HÀNG BÀI TẬP BỔ SUNG ĐÃ THẨM ĐỊNH ĐÁP ÁN
# Mỗi câu đều được kiểm chứng lại bằng tính toán độc lập trước khi đưa vào sách.
# Câu bổ sung được chọn theo ĐÚNG chuyên đề của tài liệu gốc, tránh việc chèn
# bài tích phân lớp 12 vào một cuốn sách Hình học lớp 10.
# ============================================================

VERIFIED_QUESTION_BANK: Dict[str, List[Dict[str, Any]]] = {
    "ham_so": [
        {
            "content": (
                "Cho hàm số y = x³ - 3mx² + 3(m² - 1)x với m là tham số thực. "
                "Tìm tất cả các giá trị của m để hàm số có hai điểm cực trị x₁, x₂ "
                "thỏa mãn x₁² + x₂² - x₁x₂ = 7."
            ),
            "options": ["A. m = ±1", "B. m = ±2", "C. m = 2", "D. m = ±3"],
            "correct": "B",
            "sol1": (
                "• Ta có y' = 3x² - 6mx + 3(m² - 1). Hàm số có hai cực trị ⇔ y' = 0 có hai nghiệm phân biệt.\n"
                "• Δ' = 9m² - 9(m² - 1) = 9 > 0 với mọi m, nên điều kiện này luôn được thỏa mãn.\n"
                "• Theo định lý Vi-ét: x₁ + x₂ = 2m và x₁x₂ = m² - 1.\n"
                "• Biến đổi: x₁² + x₂² - x₁x₂ = (x₁ + x₂)² - 3x₁x₂ = 4m² - 3(m² - 1) = m² + 3.\n"
                "• Do đó m² + 3 = 7 ⇔ m² = 4 ⇔ m = ±2. Chọn đáp án B."
            ),
            "sol2": (
                "Kỹ thuật Vi-ét hóa: Thay vì giải tường minh hai nghiệm, hãy đưa mọi biểu thức đối xứng về "
                "tổng S = x₁ + x₂ và tích P = x₁x₂. Sau đó dùng SHIFT SOLVE trên Casio fx-580VN X để giải "
                "nhanh phương trình ẩn m vừa thu được."
            ),
            "trap": (
                "⚠️ Bẫy quên điều kiện tồn tại cực trị: Nhiều học sinh áp dụng ngay Vi-ét mà bỏ qua bước kiểm tra "
                "Δ' > 0, dẫn đến nhận cả những giá trị m làm hàm số không có cực trị.\n"
                "⚠️ Bẫy thứ hai: chỉ nhận m = 2 mà đánh rơi nghiệm âm m = -2."
            ),
        },
        {
            "content": (
                "Tìm giá trị lớn nhất của hàm số y = x³ - 3x² + 2 trên đoạn [-1; 3]."
            ),
            "options": ["A. -2", "B. 0", "C. 2", "D. 18"],
            "correct": "C",
            "sol1": (
                "• Hàm số liên tục trên đoạn [-1; 3] nên chắc chắn đạt giá trị lớn nhất trên đoạn này.\n"
                "• Ta có y' = 3x² - 6x = 3x(x - 2), suy ra y' = 0 ⇔ x = 0 hoặc x = 2 (cả hai đều thuộc đoạn).\n"
                "• Tính giá trị tại các điểm tới hạn và hai đầu mút:\n"
                "  y(-1) = -2; y(0) = 2; y(2) = -2; y(3) = 2.\n"
                "• Giá trị lớn nhất bằng 2 (đạt tại x = 0 và x = 3). Chọn đáp án C."
            ),
            "sol2": (
                "Kỹ thuật TABLE (Menu 8 trên Casio fx-580VN X): Nhập f(X) = X³ - 3X² + 2, chọn Start = -1, "
                "End = 3, Step = 4/29 rồi dò cột kết quả để thấy ngay giá trị lớn nhất."
            ),
            "trap": (
                "⚠️ Bẫy quên hai đầu mút: Giá trị lớn nhất trên một ĐOẠN có thể rơi vào đầu mút chứ không chỉ "
                "tại điểm cực trị — ở bài này x = 3 cũng cho giá trị lớn nhất.\n"
                "⚠️ Bẫy thứ hai: nhầm giá trị lớn nhất (bằng 2) với điểm đạt giá trị lớn nhất (x = 0 hoặc x = 3)."
            ),
        }
    ],
    "mu_logarit": [
        {
            "content": (
                "Tìm nghiệm của phương trình log₂x + log₄x + log₈x = 11."
            ),
            "options": ["A. x = 32", "B. x = 64", "C. x = 36", "D. x = 128"],
            "correct": "B",
            "sol1": (
                "• Điều kiện xác định: x > 0.\n"
                "• Đưa về cùng cơ số 2: log₄x = (log₂x)/2 và log₈x = (log₂x)/3.\n"
                "• Đặt t = log₂x, phương trình trở thành: t + t/2 + t/3 = 11 ⇔ t · (11/6) = 11 ⇔ t = 6.\n"
                "• Vậy log₂x = 6 ⇔ x = 2⁶ = 64 (thỏa mãn điều kiện). Chọn đáp án B."
            ),
            "sol2": (
                "Kỹ thuật CALC thử đáp án: Nhập biểu thức log₂X + log₄X + log₈X vào máy, nhấn CALC rồi lần lượt "
                "thay X bằng 32, 64, 36, 128. Giá trị nào cho kết quả bằng 11 chính là đáp án cần tìm."
            ),
            "trap": (
                "⚠️ Bẫy đổi cơ số: Học sinh hay nhầm log₄x = 2·log₂x thay vì (log₂x)/2. Hãy nhớ công thức "
                "log_(aⁿ) x = (1/n)·log_a x — số mũ của CƠ SỐ đi xuống làm mẫu số."
            ),
        },
        {
            "content": (
                "Tìm tập nghiệm của bất phương trình 2^(x² - 3x) ≤ 16."
            ),
            "options": ["A. (-1; 4)", "B. [-1; 4]", "C. [-4; 1]", "D. (-∞; -1] ∪ [4; +∞)"],
            "correct": "B",
            "sol1": (
                "• Viết 16 = 2⁴ để đưa hai vế về cùng cơ số 2.\n"
                "• Vì cơ số 2 > 1 nên hàm số mũ đồng biến, bất phương trình tương đương: x² - 3x ≤ 4.\n"
                "• Chuyển vế: x² - 3x - 4 ≤ 0 ⇔ (x + 1)(x - 4) ≤ 0.\n"
                "• Tam thức có hai nghiệm -1 và 4, hệ số a = 1 > 0 nên biểu thức không dương giữa hai nghiệm.\n"
                "• Vậy tập nghiệm là đoạn [-1; 4]. Chọn đáp án B."
            ),
            "sol2": (
                "Kỹ thuật thử biên: Thay lần lượt x = -1 và x = 4 vào vế trái, cả hai đều cho đúng 16 nên hai "
                "đầu mút PHẢI thuộc tập nghiệm — điều này loại ngay phương án khoảng mở (-1; 4)."
            ),
            "trap": (
                "⚠️ Bẫy chiều bất đẳng thức: Nếu cơ số nằm trong khoảng (0; 1) thì hàm nghịch biến và phải ĐỔI "
                "CHIỀU bất phương trình. Ở đây cơ số 2 > 1 nên giữ nguyên chiều.\n"
                "⚠️ Bẫy đóng/mở ngoặc: dấu '≤' cho đoạn đóng [-1; 4], không phải khoảng mở."
            ),
        }
    ],
    "nguyen_ham_tich_phan": [
        {
            "content": (
                "Cho hàm số f(x) liên tục trên ℝ thỏa mãn f(x) + f(2 - x) = x² - 2x + 3 với mọi x ∈ ℝ. "
                "Tính giá trị của tích phân I = ∫[0→2] f(x)dx."
            ),
            "options": ["A. I = 4/3", "B. I = 7/3", "C. I = 14/3", "D. I = 10/3"],
            "correct": "B",
            "sol1": (
                "• Lấy tích phân hai vế trên đoạn [0; 2]:\n"
                "  ∫[0→2] f(x)dx + ∫[0→2] f(2 - x)dx = ∫[0→2] (x² - 2x + 3)dx.\n"
                "• Đổi biến t = 2 - x cho tích phân thứ hai ⇒ ∫[0→2] f(2 - x)dx = ∫[0→2] f(t)dt = I.\n"
                "• Vế phải: [x³/3 - x² + 3x] từ 0 đến 2 = 8/3 - 4 + 6 = 14/3.\n"
                "• Do đó 2I = 14/3 ⇔ I = 7/3. Chọn đáp án B."
            ),
            "sol2": (
                "Kỹ thuật chọn hàm đại diện: Giả thiết mang tính đối xứng nên có thể chọn f(x) = (x² - 2x + 3)/2. "
                "Bấm trực tiếp ∫[0→2] (x² - 2x + 3)/2 dx trên Casio fx-580VN X sẽ ra ngay 7/3 chỉ trong 5 giây."
            ),
            "trap": (
                "⚠️ Bẫy đổi biến: Khi đặt t = 2 - x thì dt = -dx, đồng thời hai cận cũng đảo chỗ "
                "(x = 0 ⇒ t = 2 và x = 2 ⇒ t = 0). Hai lần đổi dấu này triệt tiêu nhau — quên một trong hai "
                "sẽ cho kết quả sai dấu."
            ),
        },
        {
            "content": (
                "Tính diện tích hình phẳng giới hạn bởi parabol y = x² và đường thẳng y = 2x."
            ),
            "options": ["A. 2/3", "B. 8/3", "C. 4/3", "D. 2"],
            "correct": "C",
            "sol1": (
                "• Tìm hoành độ giao điểm: x² = 2x ⇔ x(x - 2) = 0 ⇔ x = 0 hoặc x = 2.\n"
                "• Trên khoảng (0; 2) ta có 2x > x², nên hàm lấy tích phân là (2x - x²).\n"
                "• S = ∫[0→2] (2x - x²)dx = [x² - x³/3] từ 0 đến 2 = 4 - 8/3 = 4/3.\n"
                "• Vậy diện tích bằng 4/3 (đơn vị diện tích). Chọn đáp án C."
            ),
            "sol2": (
                "Bấm thẳng trên Casio fx-580VN X: nhập ∫[0→2] |2X - X²| dX. Dùng dấu giá trị tuyệt đối thì "
                "không cần xét xem đồ thị nào nằm trên, máy tự cho ra kết quả dương đúng bằng diện tích."
            ),
            "trap": (
                "⚠️ Bẫy quên dấu giá trị tuyệt đối: Diện tích là ∫|f(x) - g(x)|dx. Nếu lấy sai thứ tự hiệu "
                "(x² - 2x) sẽ ra -4/3, một diện tích âm — điều vô nghĩa.\n"
                "⚠️ Bẫy cận tích phân: phải giải phương trình hoành độ giao điểm để tìm cận, không tự suy đoán."
            ),
        }
    ],
    "hinh_hoc_khong_gian": [
        {
            "content": (
                "Cho hình chóp S.ABCD có đáy ABCD là hình vuông cạnh a, cạnh bên SA vuông góc với mặt phẳng "
                "đáy và SA = a√3. Tính khoảng cách từ điểm A đến mặt phẳng (SBC)."
            ),
            "options": ["A. a√3/2", "B. a/2", "C. a√3/3", "D. a√2/2"],
            "correct": "A",
            "sol1": (
                "• Ta có BC ⊥ AB (vì đáy là hình vuông) và BC ⊥ SA (vì SA ⊥ đáy) ⇒ BC ⊥ (SAB).\n"
                "• Suy ra (SBC) ⊥ (SAB) theo giao tuyến SB.\n"
                "• Kẻ AH ⊥ SB tại H thì AH ⊥ (SBC), do đó d(A, (SBC)) = AH.\n"
                "• Trong tam giác vuông SAB: 1/AH² = 1/SA² + 1/AB² = 1/(3a²) + 1/a² = 4/(3a²).\n"
                "• Vậy AH = a√3/2. Chọn đáp án A."
            ),
            "sol2": (
                "Kỹ thuật tọa độ hóa: Gắn hệ trục với A(0;0;0), B(a;0;0), D(0;a;0), S(0;0;a√3). Viết phương trình "
                "mặt phẳng (SBC) rồi áp dụng công thức khoảng cách từ điểm đến mặt phẳng — mọi phép căn bậc hai "
                "đều bấm thẳng trên Casio."
            ),
            "trap": (
                "⚠️ Bẫy xác định chân đường vuông góc: Nhiều học sinh kẻ AH ⊥ SC thay vì AH ⊥ SB. Phải tìm đúng "
                "giao tuyến của hai mặt phẳng vuông góc (ở đây là SB) rồi mới hạ đường cao."
            ),
        },
        {
            "content": (
                "Trong không gian với hệ tọa độ Oxyz, cho ba điểm A(1; 0; 0), B(0; 2; 0) và C(0; 0; 3). "
                "Viết phương trình mặt phẳng (ABC)."
            ),
            "options": [
                "A. x + y + z - 6 = 0",
                "B. 3x + 6y + 2z - 6 = 0",
                "C. 6x + 3y + 2z + 6 = 0",
                "D. 6x + 3y + 2z - 6 = 0"
            ],
            "correct": "D",
            "sol1": (
                "• Ba điểm A, B, C lần lượt nằm trên ba trục tọa độ nên dùng được phương trình đoạn chắn.\n"
                "• Phương trình đoạn chắn: x/1 + y/2 + z/3 = 1.\n"
                "• Quy đồng với mẫu chung 6: 6x + 3y + 2z = 6.\n"
                "• Vậy (ABC): 6x + 3y + 2z - 6 = 0. Chọn đáp án D."
            ),
            "sol2": (
                "Kỹ thuật thử tọa độ: Thay lần lượt A(1;0;0), B(0;2;0), C(0;0;3) vào từng phương án. "
                "Phương án nào làm cả ba điểm cùng thỏa mãn chính là đáp án — nhanh hơn việc tính tích có hướng."
            ),
            "trap": (
                "⚠️ Bẫy dấu hạng tử tự do: Sau khi quy đồng phải chuyển vế đúng dấu, ra -6 chứ không phải +6.\n"
                "⚠️ Bẫy hoán vị hệ số: mẫu số 1, 2, 3 cho hệ số 6, 3, 2 (nghịch đảo tỉ lệ), rất dễ viết nhầm thành 3, 6, 2."
            ),
        }
    ],
    "dai_so_co_ban": [
        {
            "content": (
                "Một hộp đựng 5 viên bi xanh và 4 viên bi đỏ có kích thước đôi một khác nhau. Lấy ngẫu nhiên "
                "đồng thời 3 viên bi từ hộp. Tính xác suất để trong 3 viên bi lấy được có ít nhất một viên bi đỏ."
            ),
            "options": ["A. 37/42", "B. 5/42", "C. 10/21", "D. 5/14"],
            "correct": "A",
            "sol1": (
                "• Số phần tử của không gian mẫu: n(Ω) = C(9, 3) = 84.\n"
                "• Xét biến cố đối: 'không lấy được viên bi đỏ nào', tức cả 3 viên đều màu xanh.\n"
                "• Số cách chọn: C(5, 3) = 10 ⇒ xác suất của biến cố đối bằng 10/84 = 5/42.\n"
                "• Vậy xác suất cần tìm là 1 - 5/42 = 37/42. Chọn đáp án A."
            ),
            "sol2": (
                "Kỹ thuật biến cố đối: Khi đề bài xuất hiện cụm từ 'ít nhất một', hãy phản xạ chuyển ngay sang "
                "biến cố đối để chỉ phải đếm một trường hợp thay vì ba. Tổ hợp C(n, k) bấm bằng phím nCr trên "
                "Casio fx-580VN X."
            ),
            "trap": (
                "⚠️ Bẫy 'ít nhất một': Học sinh thường cộng dồn ba trường hợp (1 đỏ, 2 đỏ, 3 đỏ) rồi đếm thiếu "
                "hoặc đếm trùng.\n"
                "⚠️ Bẫy thứ hai: nhầm 'lấy đồng thời' (dùng tổ hợp C) thành 'lấy lần lượt có thứ tự' (chỉnh hợp A)."
            ),
        },
        {
            "content": (
                "Cho cấp số cộng (uₙ) có số hạng đầu u₁ = 3 và công sai d = 4. "
                "Tính tổng của 20 số hạng đầu tiên của cấp số cộng đó."
            ),
            "options": ["A. 410", "B. 800", "C. 820", "D. 1640"],
            "correct": "C",
            "sol1": (
                "• Công thức tổng n số hạng đầu: Sₙ = n/2 · [2u₁ + (n - 1)d].\n"
                "• Thay n = 20, u₁ = 3, d = 4: S₂₀ = 20/2 · [2·3 + 19·4] = 10 · (6 + 76).\n"
                "• Vậy S₂₀ = 10 · 82 = 820. Chọn đáp án C."
            ),
            "sol2": (
                "Kiểm tra bằng số hạng cuối: u₂₀ = u₁ + 19d = 3 + 76 = 79, sau đó S₂₀ = 20·(u₁ + u₂₀)/2 "
                "= 20·(3 + 79)/2 = 820. Hai cách cho cùng kết quả nên chắc chắn đúng."
            ),
            "trap": (
                "⚠️ Bẫy số hạng thứ n: uₙ = u₁ + (n - 1)d, KHÔNG phải u₁ + n·d. Dùng nhầm sẽ ra u₂₀ = 83 và tổng sai.\n"
                "⚠️ Bẫy quên chia đôi: công thức có hệ số n/2; bỏ quên sẽ ra 1640 (phương án D)."
            ),
        }
    ],
    "dao_dong_co": [
        {
            "content": (
                "Một vật dao động điều hòa với biên độ A = 5 cm và tần số góc ω = 10 rad/s. "
                "Tính tốc độ của vật tại thời điểm vật có li độ x = 3 cm."
            ),
            "options": ["A. 40 cm/s", "B. 30 cm/s", "C. 50 cm/s", "D. 80 cm/s"],
            "correct": "A",
            "sol1": (
                "• Áp dụng hệ thức độc lập với thời gian: x² + (v/ω)² = A².\n"
                "• Suy ra |v| = ω·√(A² - x²).\n"
                "• Thay số: |v| = 10 · √(5² - 3²) = 10 · √16 = 10 · 4 = 40 cm/s.\n"
                "• Chọn đáp án A."
            ),
            "sol2": (
                "Kỹ thuật bộ ba Pythagore: Cặp số (3; 4; 5) xuất hiện rất dày trong đề dao động điều hòa. "
                "Nhận ra ngay √(5² - 3²) = 4 giúp bỏ qua hoàn toàn bước bấm máy."
            ),
            "trap": (
                "⚠️ Bẫy đơn vị: Đề cho A theo cm thì v thu được cũng theo cm/s — đổi nhầm sang m/s sẽ sai 100 lần.\n"
                "⚠️ Bẫy thứ hai: nhầm tốc độ cực đại v_max = ωA = 50 cm/s (phương án C) với tốc độ tại li độ x."
            ),
        },
        {
            "content": (
                "Một con lắc lò xo gồm vật nhỏ khối lượng m = 100 g gắn vào lò xo nhẹ có độ cứng "
                "k = 40 N/m. Tính chu kỳ dao động điều hòa của con lắc (lấy π ≈ 3,14)."
            ),
            "options": ["A. 0,157 s", "B. 0,314 s", "C. 0,628 s", "D. 3,14 s"],
            "correct": "B",
            "sol1": (
                "• Công thức chu kỳ con lắc lò xo: T = 2π·√(m/k).\n"
                "• Đổi khối lượng về đơn vị chuẩn SI: m = 100 g = 0,1 kg.\n"
                "• Tính tỉ số: m/k = 0,1/40 = 0,0025 ⇒ √(m/k) = 0,05.\n"
                "• Vậy T = 2π · 0,05 = 0,1π ≈ 0,314 s. Chọn đáp án B."
            ),
            "sol2": (
                "Mẹo nhận dạng: khi m/k cho ra một số chính phương đẹp (ở đây 0,0025 = 0,05²) thì chu kỳ luôn "
                "có dạng bội của π. Nhận ra T = 0,1π giúp chọn đáp án mà gần như không cần bấm máy."
            ),
            "trap": (
                "⚠️ Bẫy đơn vị khối lượng: quên đổi 100 g sang 0,1 kg sẽ khiến kết quả sai lệch hơn 30 lần.\n"
                "⚠️ Bẫy nhầm công thức: T = 2π√(m/k) còn tần số góc ω = √(k/m) — hai biểu thức đảo ngược nhau."
            ),
        }
    ],
    "song_co": [
        {
            "content": (
                "Trên mặt nước có hai nguồn sóng kết hợp A, B dao động cùng pha, cách nhau AB = 20 cm. Sóng "
                "truyền trên mặt nước với bước sóng λ = 3 cm. Tìm số điểm dao động với biên độ cực đại trên "
                "đoạn thẳng nối hai nguồn."
            ),
            "options": ["A. 13", "B. 12", "C. 14", "D. 11"],
            "correct": "A",
            "sol1": (
                "• Hai nguồn cùng pha nên điểm cực đại thỏa mãn d₂ - d₁ = k·λ với k ∈ ℤ.\n"
                "• Điểm nằm trên đoạn AB nên: -AB < k·λ < AB ⇔ -AB/λ < k < AB/λ.\n"
                "• Thay số: -20/3 < k < 20/3 ⇔ -6,67 < k < 6,67.\n"
                "• Vậy k nhận các giá trị nguyên từ -6 đến 6, tức 13 giá trị ⇒ có 13 điểm cực đại.\n"
                "• Chọn đáp án A."
            ),
            "sol2": (
                "Công thức đếm nhanh: Với hai nguồn CÙNG PHA và tỉ số AB/λ không nguyên, số cực đại trên đoạn AB "
                "luôn là số lẻ và bằng 2·⌊AB/λ⌋ + 1 = 2·6 + 1 = 13."
            ),
            "trap": (
                "⚠️ Bẫy chẵn/lẻ: Hai nguồn cùng pha cho số cực đại LẺ và số cực tiểu CHẴN; hai nguồn ngược pha thì "
                "ngược lại.\n"
                "⚠️ Bẫy thứ hai: quên giá trị k = 0 (đường trung trực của AB) nên đếm thiếu mất một điểm."
            ),
        },
        {
            "content": (
                "Một sóng cơ truyền trên một sợi dây dài với tần số f = 50 Hz và tốc độ truyền sóng "
                "v = 200 cm/s. Tính khoảng cách ngắn nhất giữa hai điểm trên phương truyền sóng "
                "dao động ngược pha nhau."
            ),
            "options": ["A. 1 cm", "B. 4 cm", "C. 2 cm", "D. 8 cm"],
            "correct": "C",
            "sol1": (
                "• Bước sóng: λ = v/f = 200/50 = 4 cm.\n"
                "• Hai điểm dao động ngược pha khi độ lệch pha Δφ = (2k + 1)·π, tương ứng khoảng cách "
                "d = (2k + 1)·λ/2 với k ∈ ℕ.\n"
                "• Khoảng cách NGẮN NHẤT ứng với k = 0, tức d = λ/2 = 4/2 = 2 cm.\n"
                "• Chọn đáp án C."
            ),
            "sol2": (
                "Ghi nhớ ba mốc phản xạ: cùng pha cách nhau λ, ngược pha cách nhau λ/2, vuông pha cách nhau λ/4. "
                "Nhớ bộ ba này thì loại được phương án sai ngay mà không cần biến đổi công thức."
            ),
            "trap": (
                "⚠️ Bẫy nhầm cùng pha với ngược pha: khoảng cách λ = 4 cm (phương án B) là của hai điểm CÙNG pha.\n"
                "⚠️ Bẫy đơn vị: v cho theo cm/s nên λ cũng ra cm — nếu quy đổi nhầm sang mét sẽ sai 100 lần."
            ),
        }
    ],
    "dien_xoay_chieu": [
        {
            "content": (
                "Đặt điện áp u = 200√2·cos(100πt) V vào hai đầu đoạn mạch RLC mắc nối tiếp gồm R = 100 Ω, "
                "cuộn cảm thuần L = 1/π H và tụ điện C = 10⁻⁴/(2π) F. Tính công suất tiêu thụ của đoạn mạch."
            ),
            "options": ["A. 200 W", "B. 100 W", "C. 400 W", "D. 141 W"],
            "correct": "A",
            "sol1": (
                "• Cảm kháng: Z_L = ωL = 100π · (1/π) = 100 Ω.\n"
                "• Dung kháng: Z_C = 1/(ωC) = 1 / [100π · 10⁻⁴/(2π)] = 200 Ω.\n"
                "• Tổng trở: Z = √[R² + (Z_L - Z_C)²] = √[100² + (-100)²] = 100√2 Ω.\n"
                "• Điện áp hiệu dụng U = 200 V ⇒ I = U/Z = 200/(100√2) = √2 A.\n"
                "• Công suất: P = I²·R = 2 · 100 = 200 W. Chọn đáp án A."
            ),
            "sol2": (
                "Kỹ thuật số phức (Menu 2 trên Casio fx-580VN X): Nhập u = 200√2∠0 rồi chia cho "
                "Z = 100 + (100 - 200)i để đọc ngay biên độ và pha của dòng điện, sau đó dùng P = U·I·cos φ."
            ),
            "trap": (
                "⚠️ Bẫy giá trị hiệu dụng: u = 200√2·cos(...) nghĩa là U₀ = 200√2 V nên U = 200 V. Dùng nhầm "
                "200√2 vào công thức công suất sẽ cho kết quả gấp đôi (400 W - phương án C).\n"
                "⚠️ Bẫy đơn vị điện dung: nếu đề cho C theo μF phải đổi ra 10⁻⁶ F trước khi tính Z_C."
            ),
        },
        {
            "content": (
                "Đặt điện áp xoay chiều u = 220√2·cos(100πt) V vào hai đầu một cuộn cảm thuần "
                "có độ tự cảm L = 1/(2π) H. Tính cường độ dòng điện hiệu dụng chạy qua cuộn cảm."
            ),
            "options": ["A. 2,2 A", "B. 6,22 A", "C. 8,8 A", "D. 4,4 A"],
            "correct": "D",
            "sol1": (
                "• Tần số góc đọc từ biểu thức điện áp: ω = 100π rad/s.\n"
                "• Cảm kháng: Z_L = ωL = 100π · 1/(2π) = 50 Ω.\n"
                "• Điện áp hiệu dụng: U = U₀/√2 = 220√2/√2 = 220 V.\n"
                "• Định luật Ôm cho đoạn mạch chỉ có cuộn cảm: I = U/Z_L = 220/50 = 4,4 A.\n"
                "• Chọn đáp án D."
            ),
            "sol2": (
                "Mẹo rút gọn π: Với ω = 100π và L có mẫu số chứa π, hai chữ π luôn triệt tiêu nhau — "
                "nhẩm ngay Z_L = 100/2 = 50 Ω mà không cần chạm vào máy tính."
            ),
            "trap": (
                "⚠️ Bẫy giá trị cực đại và hiệu dụng: u = 220√2·cos(...) nghĩa là U₀ = 220√2 V và U = 220 V. "
                "Lấy nhầm 220√2 chia cho 50 sẽ ra 6,22 A (phương án B).\n"
                "⚠️ Bẫy công suất: cuộn cảm THUẦN không tiêu thụ công suất (cos φ = 0), đừng áp dụng P = UI."
            ),
        }
    ],
}

# Chuyên đề dự phòng khi tài liệu không khớp mục nào trong ngân hàng
_FALLBACK_TOPIC = {"toan": "ham_so", "vatly": "dao_dong_co"}


def create_added_question(
    idx: int,
    subject: str = "toan",
    topic_key: Optional[str] = None,
    variant: int = 0
) -> RewrittenQuestionItem:
    """
    Tạo thêm bài tập vận dụng cao ĐÚNG CHUYÊN ĐỀ của tài liệu gốc.

    Nguồn câu hỏi gồm hai phần, đều đã qua thẩm định:
      1. Ngân hàng gốc viết tay, đáp án tính lại độc lập bằng Python.
      2. Ngân hàng do AI sinh ra, nhưng CHỈ những câu đã qua đủ ba lớp kiểm
         chứng của core/question_forge (cấu trúc, giải lại độc lập, đối chiếu
         sympy). Câu nào AI sinh mà chưa thẩm định thì không bao giờ tới đây.
    """
    fallback = _FALLBACK_TOPIC.get(subject, "ham_so")
    key = topic_key if topic_key in VERIFIED_QUESTION_BANK else fallback
    bank = list(VERIFIED_QUESTION_BANK.get(key) or VERIFIED_QUESTION_BANK[fallback])

    # Bổ sung các câu AI đã sinh và đã được thẩm định cho đúng chuyên đề này
    try:
        from core.question_forge import doc_ngan_hang
        for item in doc_ngan_hang(topic_key=key, subject=subject):
            if not item.get("verified"):
                continue          # chốt chặn cuối, không bao giờ lấy câu chưa duyệt
            bank.append({
                "content": item.get("content", ""),
                "options": item.get("options", []),
                "correct": item.get("correct", ""),
                "sol1": item.get("solution", ""),
                "sol2": item.get("casio_tip", ""),
                "trap": item.get("trap_warning", ""),
            })
    except Exception as e:
        print(f"Không đọc được ngân hàng câu hỏi AI: {e}")

    q = bank[variant % len(bank)]

    return RewrittenQuestionItem(
        index=idx,
        title=f"Câu {idx} [Vận dụng cao - Phân hóa điểm 10]",
        level="Vận dụng cao",
        original_content="[Bài toán bổ sung phân hóa]",
        original_solution="",
        new_content=q["content"],
        new_options=list(q["options"]),
        correct_answer=q["correct"],
        solution_method1=q["sol1"],
        solution_method2=q["sol2"],
        trap_warning=q["trap"],
        is_added_new=True
    )


# ==========================================
# CƠ CHẾ GOOGLE GEMINI AI REWRITER
# ==========================================

# ============================================================
# CHỌN LỌC CÂU CẦN AI XỬ LÝ
# Đo trên tài liệu thật: 86% câu trong kho của người dùng ĐÃ CÓ SẴN lời giải.
# Gửi hết cho AI viết lại là trả tiền để sinh lại thứ đã có, mà đầu ra lại là
# phần đắt nhất (gấp 5 lần đầu vào). Chỉ gọi AI ở chỗ thật sự thiếu.
# ============================================================

AI_SCOPE_THIEU = "thieu"   # chỉ câu còn thiếu lời giải / đáp án  (mặc định)
AI_SCOPE_TAT_CA = "tat_ca"  # gửi toàn bộ, viết lại tất
AI_SCOPE_KHONG = "khong"    # không gọi AI, chạy hoàn toàn ngoại tuyến

MIN_SOLUTION_LEN = 40       # ngắn hơn thế thì coi như chưa có lời giải thật


def can_ai_xu_ly(q: QuestionItem) -> bool:
    """
    Câu này có thực sự cần AI không?

    Cần khi: chưa có lời giải tử tế, HOẶC là câu trắc nghiệm mà chưa biết đáp án
    đúng (lúc đó AI phải giải ra mới điền được đáp án).
    """
    thieu_loi_giai = len((q.solution or "").strip()) < MIN_SOLUTION_LEN
    la_trac_nghiem = len(q.options or []) >= 2
    thieu_dap_an = la_trac_nghiem and not (q.correct_answer or "").strip()
    return thieu_loi_giai or thieu_dap_an


def phan_loai_theo_nhu_cau(questions: List[QuestionItem], scope: str):
    """Tách danh sách thành (cần AI, tự xử lý ngoại tuyến), giữ nguyên thứ tự gốc."""
    if scope == AI_SCOPE_KHONG:
        return [], list(enumerate(questions))
    if scope == AI_SCOPE_TAT_CA:
        return list(enumerate(questions)), []

    can, khong_can = [], []
    for i, q in enumerate(questions):
        (can if can_ai_xu_ly(q) else khong_can).append((i, q))
    return can, khong_can


def rewrite_with_gemini(
    questions: List[QuestionItem],
    api_key: str,
    model_name: str = "gemini-3.6-flash",
    subject: str = "toan",
    add_count: int = 2,
    ai_scope: str = AI_SCOPE_THIEU,
    provider: str = GEMINI,
    options: Optional[Dict[str, Any]] = None,
    doc_type: str = "",
    cap_hoc: str = ""
) -> RewrittenBook:
    # Tên hàm giữ nguyên cho khỏi vỡ các lệnh gọi cũ, nhưng nay nó chạy được cả
    # Gemini lẫn Claude — chọn bên nào là do `provider`.
    tt = chuan_hoa(provider, api_key, model_name)

    # Chuẩn nghiệp vụ nạp từ tệp skill. Trước đây câu lệnh chỉ dài ~1.800 ký tự
    # và không hề biết đề thi từ 2025 có ba phần I/II/III.
    if cap_hoc not in (TIEU_HOC, THCS, THPT):
        cap_hoc = phat_hien_cap_hoc([q.content for q in questions[:30]],
                                    questions[0].source_file if questions else "")
    van_ban_skill = nap_van_ban_skill(cap_hoc, doc_type or "CHUYEN_DE")
    giong_van = huong_dan_giong_van(cap_hoc)
    total_orig = len(questions)
    new_total = total_orig + add_count

    all_texts = [q.content for q in questions]
    topic_data = detect_subject_and_topic(all_texts, subject=subject)
    theory_text = build_pedagogical_theory_section(topic_data)

    subj_label = "Toán học" if subject == "toan" else "Vật lý"

    # Chỉ gửi cho AI những câu thật sự cần. Tài liệu đã có sẵn lời giải thì chỉ
    # cần chuẩn hóa lại bằng bộ ngoại tuyến — vừa miễn phí, vừa giữ nguyên lời
    # giải gốc của tác giả thay vì để AI viết lại theo cách của nó.
    can_ai, tu_xu_ly = phan_loai_theo_nhu_cau(questions, ai_scope)
    ket_qua_theo_vi_tri: Dict[int, RewrittenQuestionItem] = {}

    for vi_tri, q in tu_xu_ly:
        ket_qua_theo_vi_tri[vi_tri] = generate_offline_enhancement(
            q, vi_tri + 1, new_total, subject, topic_key=topic_data.get("topic_key")
        )

    if not can_ai:
        # Không câu nào cần AI: vẫn lấy metadata (tên sách, lời tựa) rồi trả về
        rewritten_items = [ket_qua_theo_vi_tri[i] for i in sorted(ket_qua_theo_vi_tri)]
        for i in range(add_count):
            rewritten_items.append(create_added_question(
                len(rewritten_items) + 1, subject=subject,
                topic_key=topic_data.get("topic_key"), variant=i
            ))
        source_filename = questions[0].source_file if questions else ""
        meta = synthesize_book_metadata(
            filename=source_filename,
            sample_content="\n".join(q.content for q in questions[:6]),
            subject=subject, api_key=api_key, model_name=model_name,
            options=options, doc_type=doc_type
        )
        return RewrittenBook(
            original_title=source_filename,
            new_title=meta.get("book_title", ""),
            subtitle=meta.get("subtitle", ""),
            author_note=meta.get("author_note", ""),
            chapter_summary=topic_data.get("title", ""),
            theory_section=theory_text,
            valedictorian_secrets=meta.get("valedictorian_secrets", []),
            stem_connection=meta.get("stem_connection", ""),
            creative_options=meta.get("creative_options", []),
            questions=rewritten_items
        )

    # Mỗi lần gọi chỉ gửi một lô để không vượt giới hạn ngữ cảnh
    BATCH_SIZE = 25
    MAX_BATCHES = 12
    batches = [can_ai[i:i + BATCH_SIZE] for i in range(0, len(can_ai), BATCH_SIZE)][:MAX_BATCHES]

    rewritten_items: List[RewrittenQuestionItem] = []
    ai_processed = 0
    meta_from_ai: Dict[str, Any] = {}

    for batch_no, batch in enumerate(batches, 1):
        # batch là danh sách cặp (vị trí trong tài liệu gốc, câu hỏi)
        sample_text = ""
        for stt_lo, (_, q) in enumerate(batch):
            opts = "\n".join(q.options) if q.options else ""
            sample_text += (
                f"\n--- Câu {stt_lo} ---\nĐề: {q.content}\n{opts}\n"
                f"Đáp án: {q.correct_answer}\nGiải: {q.solution}\n"
            )

        khoi_chuan = ""
        if van_ban_skill:
            khoi_chuan = (
                "=== CHUẨN NGHIỆP VỤ BẮT BUỘC TUÂN THỦ ===\n"
                + van_ban_skill
                + "\n=== HẾT PHẦN CHUẨN ===\n\n"
            )

        # Thang mức độ phải khớp với chuẩn đang áp dụng. Từ 2025 đề thi THPT chỉ
        # còn BA mức Biết – Hiểu – Vận dụng, không còn bốn mức như trước. Để lẫn
        # hai thang trong cùng một câu lệnh là tự mâu thuẫn với phần chuẩn ở trên.
        if doc_type == DE_THI and cap_hoc in (THPT, THCS):
            muc_do = "'Biết', 'Hiểu', 'Vận dụng' (đúng ba mức của chuẩn 2025)"
        elif cap_hoc == TIEU_HOC:
            muc_do = "'Nhận biết', 'Thông hiểu', 'Vận dụng'"
        else:
            muc_do = "'Nhận biết', 'Thông hiểu', 'Vận dụng', 'Vận dụng cao'"

        # Máy tính cầm tay chỉ có nghĩa từ THCS trở lên. Tiểu học không được phép
        # dùng, nên "Cách 2" ở đó phải là cách nhẩm hoặc cách hình dung khác.
        if cap_hoc == TIEU_HOC:
            cach_hai = ("Cách 2 (cách nhẩm nhanh hoặc mẹo hình dung phù hợp với trẻ — "
                        "TUYỆT ĐỐI không nhắc tới máy tính cầm tay)")
            cach_hai_vd = "Cách nhẩm nhanh cho học sinh"
        else:
            cach_hai = "Cách 2 (mẹo Casio fx-580VN X)"
            cach_hai_vd = "Mẹo Casio / Giải nhanh"

        # Ví dụ trong khuôn JSON phải KHỚP với quy tắc ở trên. Mô hình bám theo ví
        # dụ mạnh hơn bám theo lời dặn, nên để mẫu ghi "Thông hiểu" trong khi luật
        # bảo dùng ba mức 2025 là tự phá luật của chính mình.
        muc_do_vd = "Hiểu" if (doc_type == DE_THI and cap_hoc in (THPT, THCS)) else "Thông hiểu"

        prompt = f"""{khoi_chuan}Bạn là chuyên gia biên soạn tài liệu giảng dạy môn {subj_label} cấp {TEN_CAP[cap_hoc]} theo chuẩn chương trình GDPT 2018 của Bộ Giáo dục và Đào tạo Việt Nam.

{giong_van}

Đây là LÔ {batch_no}/{len(batches)}, gồm {len(batch)} câu hỏi. Hãy biên soạn chuẩn mực:
1. GIỮ NGUYÊN 100% CẤU TRÚC VÀ ĐỀ BÀI GỐC: chỉ chuẩn hóa ngữ pháp và ký hiệu toán học cho liền mạch, tuyệt đối không thêm câu mở đầu lạ, không đổi số liệu.
2. Phân cấp độ từng câu, CHỈ dùng một trong các mức: {muc_do}.
3. Viết lời giải 2 cách: Cách 1 (tự luận chuẩn mực sư phạm) + {cach_hai}.
4. Chỉ ra cảnh báo bẫy sai lầm học sinh hay mắc.
5. TUYỆT ĐỐI KHÔNG tự sinh thêm câu hỏi mới. Trả về đúng {len(batch)} câu của lô này.
6. Trường "index" phải là SỐ THỨ TỰ TRONG LÔ như đánh dấu ở trên (0, 1, 2, ...), không phải số câu trong đề gốc.
7. Trường "correct_answer" phải là một trong các nhãn A, B, C, D và phải khớp với lời giải bạn viết.

Dữ liệu lô này:
{sample_text}

TRẢ VỀ ĐỊNH DẠNG JSON:
{{
  "new_title": "Tên sách/cẩm nang chuẩn",
  "subtitle": "Phụ đề phân hóa",
  "author_note": "Lời tựa sư phạm",
  "questions": [
    {{
      "index": 0,
      "level": "{muc_do_vd}",
      "new_content": "Đề bài đã chuẩn hóa",
      "new_options": ["A. ...", "B. ...", "C. ...", "D. ..."],
      "correct_answer": "A",
      "solution_method1": "Lời giải tự luận bài bản",
      "solution_method2": "{cach_hai_vd}",
      "trap_warning": "Bẫy sai lầm"
    }}
  ]
}}
Chỉ trả về JSON thuần túy.
"""
        try:
            data = boc_json(goi_ai(tt, prompt, json_mode=True, max_tokens=32000))
        except Exception as e:
            # Một lô lỗi không được làm hỏng cả cuốn sách: rơi về bộ xử lý ngoại
            # tuyến cho riêng lô đó rồi đi tiếp.
            print(f"Lô {batch_no} gặp lỗi {tt.ten_hien_thi} ({e}), dùng bộ xử lý ngoại tuyến cho lô này.")
            for vi_tri, q in batch:
                ket_qua_theo_vi_tri[vi_tri] = generate_offline_enhancement(
                    q, vi_tri + 1, new_total, subject, topic_key=topic_data.get("topic_key")
                )
            continue

        if batch_no == 1:
            meta_from_ai = {
                "new_title": data.get("new_title", ""),
                "subtitle": data.get("subtitle", ""),
                "author_note": data.get("author_note", "")
            }

        returned = data.get("questions", []) or []
        da_nhan = set()

        for q_json in returned:
            try:
                stt_lo = int(q_json.get("index"))
            except (TypeError, ValueError):
                continue
            if not (0 <= stt_lo < len(batch)):
                continue

            vi_tri, orig_q = batch[stt_lo]
            da_nhan.add(stt_lo)
            level = q_json.get("level", "Vận dụng")
            ket_qua_theo_vi_tri[vi_tri] = RewrittenQuestionItem(
                index=vi_tri + 1,
                title=f"Câu {vi_tri + 1} [{level}]",
                level=level,
                original_content=orig_q.content,
                original_solution=orig_q.solution,
                new_content=clean_paragraph_text(q_json.get("new_content", "")) or orig_q.content,
                new_options=[clean_paragraph_text(o) for o in q_json.get("new_options", [])] or list(orig_q.options),
                correct_answer=(q_json.get("correct_answer", "") or "").strip(),
                solution_method1=clean_paragraph_text(q_json.get("solution_method1", "")),
                solution_method2=clean_paragraph_text(q_json.get("solution_method2", "")),
                trap_warning=clean_paragraph_text(q_json.get("trap_warning", "")),
                is_added_new=False,
                source_file=orig_q.source_file
            )
            ai_processed += 1

        # Câu nào AI bỏ sót thì bù bằng bộ ngoại tuyến, không để mất bài
        for stt_lo, (vi_tri, q) in enumerate(batch):
            if stt_lo not in da_nhan:
                ket_qua_theo_vi_tri[vi_tri] = generate_offline_enhancement(
                    q, vi_tri + 1, new_total, subject, topic_key=topic_data.get("topic_key")
                )

    # Câu vượt quá giới hạn số lô cũng phải có mặt, xử lý ngoại tuyến
    da_gui = {vi_tri for lo in batches for vi_tri, _ in lo}
    for vi_tri, q in can_ai:
        if vi_tri not in da_gui and vi_tri not in ket_qua_theo_vi_tri:
            ket_qua_theo_vi_tri[vi_tri] = generate_offline_enhancement(
                q, vi_tri + 1, new_total, subject, topic_key=topic_data.get("topic_key")
            )

    # Gộp lại ĐÚNG THỨ TỰ trong tài liệu gốc rồi đánh số lại liên tục
    rewritten_items = []
    for vi_tri in sorted(ket_qua_theo_vi_tri):
        item = ket_qua_theo_vi_tri[vi_tri]
        stt = len(rewritten_items) + 1
        item.index = stt
        item.title = f"Câu {stt} [{item.level}]"
        rewritten_items.append(item)

    # Câu bổ sung lấy từ ngân hàng đã thẩm định đáp án, KHÔNG để AI tự bịa
    for i in range(add_count):
        rewritten_items.append(create_added_question(
            len(rewritten_items) + 1,
            subject=subject,
            topic_key=topic_data.get("topic_key"),
            variant=i
        ))

    # Bổ sung phần làm giàu nội dung để nhánh AI không nghèo hơn nhánh ngoại tuyến
    source_filename = questions[0].source_file if questions else ""
    meta = synthesize_book_metadata(
        filename=source_filename,
        sample_content="\n".join(q.content for q in questions[:6]),
        subject=subject,
        api_key=api_key,
        model_name=model_name,
        options=options, doc_type=doc_type
    )

    default_title = f"{new_total} Tuyệt Kỹ Chinh Phục Điểm 9+ {'Toán Học' if subject == 'toan' else 'Vật Lý'}"
    return RewrittenBook(
        original_title=source_filename or f"Tài liệu {total_orig} bài toán",
        new_title=(meta_from_ai.get("new_title") or meta.get("book_title") or default_title),
        subtitle=(meta_from_ai.get("subtitle") or meta.get("subtitle")
                  or "Hệ Thống Kiến Thức Trọng Tâm, Phân Dạng & Lời Giải Đa Chiều"),
        author_note=(meta_from_ai.get("author_note") or meta.get("author_note")
                     or "Tài liệu được biên soạn đồng bộ theo định hướng phát triển năng lực học sinh, chuẩn chương trình GDPT 2018."),
        chapter_summary=topic_data.get("title", ""),
        theory_section=theory_text,
        valedictorian_secrets=meta.get("valedictorian_secrets", []),
        stem_connection=meta.get("stem_connection", ""),
        creative_options=meta.get("creative_options", []),
        questions=rewritten_items
    )


def rewrite_offline(
    questions: List[QuestionItem],
    subject: str = "toan",
    add_count: int = 2,
    api_key: Optional[str] = None,
    model_name: str = "gemini-3.6-flash",
    options: Optional[Dict[str, Any]] = None,
    doc_type: str = ""
) -> RewrittenBook:
    source_filename = questions[0].source_file if questions else ""

    # 1. Phát hiện các chương/chủ đề trong tài liệu
    distinct_chapters: List[str] = []
    for q in questions:
        c_title = q.chapter_title.strip()
        if c_title and c_title not in distinct_chapters:
            distinct_chapters.append(c_title)

    # 2. Sinh Metadata Độc Bản (AI hoặc Ngoại Tuyến Tự Động)
    sample_content = "\n".join(q.content for q in questions[:6])
    meta = synthesize_book_metadata(
        filename=source_filename,
        chapter_titles=distinct_chapters if distinct_chapters else None,
        sample_content=sample_content,
        subject=subject,
        api_key=api_key,
        model_name=model_name,
        options=options, doc_type=doc_type
    )
    book_title = meta.get("book_title") or (Path(source_filename).stem.replace("_", " ").upper() if source_filename else "TÀI LIỆU CHUYÊN ĐỀ")
    subtitle = meta.get("subtitle", "Hệ Thống Kiến Thức Trọng Tâm & Lời Giải Chi Tiết Chuẩn BGD")
    author_note = meta.get("author_note", "Tài liệu được tái cấu trúc toàn diện theo chuẩn chương trình GDPT 2018 của Bộ GD&ĐT.")

    # 3. NẾU TÀI LIỆU CÓ TỪ 2 CHƯƠNG/CHỦ ĐỀ TRỞ LÊN: Xây dựng cấu trúc Master Chapter Book
    if len(distinct_chapters) >= 2:
        chapters: List[RewrittenChapter] = []
        for ch_idx, ch_title in enumerate(distinct_chapters, 1):
            ch_questions = [q for q in questions if q.chapter_title.strip() == ch_title]
            if not ch_questions:
                continue

            # Luôn nhận diện chuyên đề của chương, kể cả khi tài liệu gốc đã có
            # sẵn phần lý thuyết — vì còn cần khóa chuyên đề để chọn đúng mẹo
            # Casio và cảnh báo bẫy cho từng bài.
            ch_texts = [q.content for q in ch_questions]
            ch_topic_data = detect_subject_and_topic(ch_texts, subject=subject)
            ch_topic_key = ch_topic_data.get("topic_key")

            # Ưu tiên lý thuyết có sẵn trong tài liệu gốc (theory_box / Ghi nhớ)
            ch_theory = ""
            for q in ch_questions:
                if q.theory_box and len(q.theory_box.strip()) > 15:
                    ch_theory = q.theory_box.strip()
                    break

            if not ch_theory:
                ch_theory = build_pedagogical_theory_section(ch_topic_data)

            rewritten_items: List[RewrittenQuestionItem] = []
            for q_idx, q in enumerate(ch_questions, 1):
                enh = generate_offline_enhancement(q, q_idx, len(ch_questions), subject=subject,
                                                   topic_key=ch_topic_key)
                rewritten_items.append(enh)

            chapters.append(RewrittenChapter(
                index=ch_idx,
                title=ch_title.upper(),
                source_name=source_filename,
                theory_section=ch_theory,
                questions=rewritten_items
            ))

        return RewrittenBook(
            original_title=source_filename or book_title,
            new_title=book_title,
            subtitle=subtitle,
            author_note=author_note,
            chapter_summary=f"Tuyển tập {len(chapters)} chương chuyên đề trọng tâm",
            theory_section="",
            valedictorian_secrets=meta.get("valedictorian_secrets", []),
            stem_connection=meta.get("stem_connection", ""),
            creative_options=meta.get("creative_options", []),
            chapters=chapters,
            questions=[]
        )

    # 4. TÀI LIỆU ĐƠN CHỦ ĐỀ HOẶC ĐỀ THI LIÊN TỤC
    total_orig = len(questions)
    new_total = total_orig + add_count

    all_texts = [q.content for q in questions]
    topic_data = detect_subject_and_topic(all_texts, subject=subject)

    # Nếu có theory_box gốc từ file, dùng nó, ngược lại sinh từ theory_bank
    orig_theory = ""
    for q in questions:
        if q.theory_box and len(q.theory_box.strip()) > 15:
            orig_theory = q.theory_box.strip()
            break
    theory_text = orig_theory if orig_theory else build_pedagogical_theory_section(topic_data)

    rewritten_items: List[RewrittenQuestionItem] = []
    for idx, q in enumerate(questions, 1):
        enh = generate_offline_enhancement(q, idx, new_total, subject=subject,
                                           topic_key=topic_data.get("topic_key"))
        rewritten_items.append(enh)

    for i in range(1, add_count + 1):
        rewritten_items.append(create_added_question(
            total_orig + i,
            subject=subject,
            topic_key=topic_data.get("topic_key"),
            variant=i - 1
        ))

    return RewrittenBook(
        original_title=source_filename or book_title,
        new_title=book_title,
        subtitle=subtitle,
        author_note=author_note,
        chapter_summary=topic_data.get("title", ""),
        theory_section=theory_text,
        valedictorian_secrets=meta.get("valedictorian_secrets", []),
        stem_connection=meta.get("stem_connection", ""),
        creative_options=meta.get("creative_options", []),
        chapters=[],
        questions=rewritten_items
    )


def create_master_book_from_chapters(
    chapter_data_list: List[Dict[str, Any]],
    subject: str = "toan",
    master_title: Optional[str] = None,
    api_key: Optional[str] = None,
    model_name: str = "gemini-3.6-flash",
    options: Optional[Dict[str, Any]] = None,
    doc_type: str = ""
) -> RewrittenBook:
    chapters: List[RewrittenChapter] = []

    for c_idx, data in enumerate(chapter_data_list, 1):
        source_name = data.get("source_name", f"Tài liệu {c_idx}")
        questions = data.get("questions", [])
        if not questions:
            continue

        # Luôn nhận diện chuyên đề để còn chọn đúng mẹo Casio và cảnh báo bẫy
        all_texts = [q.content for q in questions]
        topic_data = detect_subject_and_topic(all_texts, subject=subject)
        ch_topic_key = topic_data.get("topic_key")

        # Lấy lý thuyết gốc hoặc sinh chuẩn
        ch_theory = ""
        for q in questions:
            if hasattr(q, "theory_box") and q.theory_box and len(q.theory_box.strip()) > 15:
                ch_theory = q.theory_box.strip()
                break

        if not ch_theory:
            ch_theory = build_pedagogical_theory_section(topic_data)

        rewritten_items: List[RewrittenQuestionItem] = []
        for q_idx, q in enumerate(questions, 1):
            enh = generate_offline_enhancement(q, q_idx, len(questions), subject=subject,
                                               topic_key=ch_topic_key)
            rewritten_items.append(enh)

        clean_chapter_name = Path(source_name).stem.replace("_", " ").replace("-", " ")
        chapters.append(RewrittenChapter(
            index=c_idx,
            title=f"CHUYÊN ĐỀ {c_idx}: {clean_chapter_name.upper()}",
            source_name=source_name,
            theory_section=ch_theory,
            questions=rewritten_items
        ))

    sub_name = "Toán Học" if subject == "toan" else "Vật Lý"

    # Đại Cẩm Nang cũng phải có lời tựa, bí kíp thủ khoa và góc STEM như sách đơn —
    # trước đây chế độ gộp thư mục bị thiếu hoàn toàn phần làm giàu nội dung này.
    chapter_titles = [ch.title for ch in chapters]
    sample_content = ""
    for ch in chapters[:2]:
        for q in ch.questions[:3]:
            sample_content += q.new_content + "\n"

    meta = synthesize_book_metadata(
        filename=chapters[0].source_name if chapters else "",
        chapter_titles=chapter_titles or None,
        sample_content=sample_content,
        subject=subject,
        api_key=api_key,
        model_name=model_name,
        options=options, doc_type=doc_type
    )

    if master_title and master_title.strip():
        final_title = master_title.strip()
    else:
        final_title = meta.get("book_title") or f"ĐẠI CẨM NANG TOÀN DIỆN MÔN {sub_name.upper()}"

    default_note = (
        f"Cuốn đại cẩm nang được tổng hợp và biên soạn đồng bộ từ toàn bộ thư mục tài liệu gốc. "
        f"Bố cục sách gồm {len(chapters)} chương chuyên đề bài bản, tích hợp đầy đủ lý thuyết nền tảng, "
        f"hệ thống bài tập phân loại theo cấp độ nhận thức và hướng dẫn giải chi tiết."
    )

    return RewrittenBook(
        original_title="Thư mục tài liệu tổng hợp",
        new_title=final_title,
        subtitle=meta.get("subtitle") or "Tuyển Tập Chuyên Đề Bồi Dưỡng — Kiến Thức Trọng Tâm & Lời Giải Chi Tiết Chuẩn BGD",
        author_note=meta.get("author_note") or default_note,
        chapter_summary=f"Tuyển tập {len(chapters)} chuyên đề trọng tâm môn {sub_name}",
        theory_section="",
        valedictorian_secrets=meta.get("valedictorian_secrets", []),
        stem_connection=meta.get("stem_connection", ""),
        creative_options=meta.get("creative_options", []),
        chapters=chapters,
        questions=[],
        doc_type=SACH          # gộp nhiều tài liệu thì kết quả luôn là một cuốn sách
    )


def process_rewrite_pipeline(
    questions: List[QuestionItem],
    subject: str = "toan",
    add_count: int = 2,
    api_key: Optional[str] = None,
    model_name: str = "gemini-3.6-flash",
    doc_type: str = CHUYEN_DE,
    exam_info: Optional[Dict[str, str]] = None,
    ai_scope: str = AI_SCOPE_THIEU,
    provider: str = GEMINI,
    options: Optional[Dict[str, Any]] = None,
    cap_hoc: str = "",
    loai_dau_ra: str = ""
) -> RewrittenBook:
    """
    Đầu vào là đề thi thì KHÔNG chèn thêm câu mới: một đề thi 50 câu mà tự dưng
    thành 52 câu là sai bản chất tài liệu. Câu bổ sung chỉ hợp lý với sách và
    tài liệu chuyên đề, nơi càng nhiều bài luyện càng tốt.
    """
    if doc_type == DE_THI:
        add_count = 0
    cap = cap_hoc if cap_hoc in (TIEU_HOC, THCS, THPT) else phat_hien_cap_hoc(
        [q.content for q in questions[:30]],
        questions[0].source_file if questions else ""
    )

    def _gan_loai(book: RewrittenBook) -> RewrittenBook:
        book.doc_type = doc_type
        book.exam_info = dict(exam_info or {})
        book.cap_hoc = cap
        book.loai_dau_ra = loai_dau_ra or ""
        book.subject = subject
        return book

    # Không dùng AI thì khỏi gọi, chạy thẳng bộ ngoại tuyến
    if ai_scope == AI_SCOPE_KHONG:
        return _gan_loai(rewrite_offline(
            questions, subject=subject, add_count=add_count, api_key=None,
            options=options, doc_type=doc_type
        ))

    if api_key and api_key.strip():
        try:
            return _gan_loai(rewrite_with_gemini(
                questions, api_key=api_key.strip(), model_name=model_name,
                subject=subject, add_count=add_count, ai_scope=ai_scope,
                provider=provider, options=options, doc_type=doc_type,
                cap_hoc=cap
            ))
        except Exception as e:
            print(f"Lỗi đường ống AI: {e}. Chuyển sang rewrite_offline.")
            return _gan_loai(rewrite_offline(
                questions, subject=subject, add_count=add_count,
                api_key=api_key, model_name=model_name,
                options=options, doc_type=doc_type
            ))
    else:
        return _gan_loai(rewrite_offline(
            questions, subject=subject, add_count=add_count,
            api_key=api_key, model_name=model_name,
            options=options, doc_type=doc_type
        ))
