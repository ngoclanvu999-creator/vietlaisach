import re
from typing import Dict, Any, Optional, List

# ==========================================================
# HỆ THỐNG NGÂN HÀNG KIẾN THỨC LÝ THUYẾT CHUẨN CT GDPT 2018
# ==========================================================

MATH_THEORY_DATABASE: Dict[str, Dict[str, Any]] = {
    "ham_so": {
        "title": "CHUYÊN ĐỀ: ỨNG DỤNG ĐẠO HÀM ĐỂ KHẢO SÁT VÀ VẼ ĐỒ THỊ HÀM SỐ",
        "grade": "Lớp 12",
        "concepts": [
            "1. Tính đơn điệu: Cho hàm số y = f(x) có đạo hàm trên K. Nếu f'(x) ≥ 0 (f'(x) ≤ 0) với mọi x ∈ K và dấu bằng chỉ xảy ra tại hữu hạn điểm thì f(x) đồng biến (nghịch biến) trên K.",
            "2. Cực trị hàm số: Nếu f'(x₀) = 0 (hoặc không xác định) và f'(x) đổi dấu từ dương sang âm khi qua x₀ thì x₀ là điểm cực đại; đổi dấu từ âm sang dương thì x₀ là điểm cực tiểu.",
            "3. Quy tắc 2 tìm cực trị: Nếu f'(x₀) = 0 và f''(x₀) < 0 thì x₀ là điểm cực đại; nếu f''(x₀) > 0 thì x₀ là điểm cực tiểu.",
            "4. Đường tiệm cận: lim[x→±∞] f(x) = y₀ ⇒ y = y₀ là tiệm cận ngang; lim[x→x₀⁺/x₀⁻] f(x) = ±∞ ⇒ x = x₀ là tiệm cận đứng."
        ],
        "formulas": [
            "• Đạo hàm hàm hợp: [f(u)]' = u' · f'(u)",
            "• Hàm bậc ba y = ax³ + bx² + cx + d (a ≠ 0): Có 2 cực trị ⇔ y' = 0 có 2 nghiệm phân biệt ⇔ Δ' = b² - 3ac > 0.",
            "• Khoảng cách giữa 2 điểm cực trị: d = √[(x₁ - x₂)² + (y₁ - y₂)²].",
            "• Bất đẳng thức tiếp tuyến: Tiếp tuyến tại điểm uốn phân chia mặt phẳng thành hai miền lồi lõm."
        ],
        "methods": [
            "• Dạng 1: Tìm khoảng đơn điệu và cực trị dựa vào bảng biến thiên hoặc đồ thị f(x) / f'(x).",
            "• Dạng 2: Tìm tham số m để hàm số đơn điệu trên khoảng (a; b) [Phương pháp cô lập m kết hợp bảng biến thiên].",
            "• Dạng 3: Bài toán cực trị chứa dấu giá trị tuyệt đối y = |f(x)| và y = f(|x|)."
        ]
    },
    "mu_logarit": {
        "title": "CHUYÊN ĐỀ: HÀM SỐ LŨY THỪA, HÀM SỐ MŨ VÀ HÀM SỐ LOGARIT",
        "grade": "Lớp 12",
        "concepts": [
            "1. Điều kiện xác định: Với log_a(b), điều kiện là cơ số 0 < a ≠ 1 và biểu thức dưới logarit b > 0.",
            "2. Tính chất đồng biến/nghịch biến: Hàm số y = a^x và y = log_a(x) đồng biến khi a > 1; nghịch biến khi 0 < a < 1.",
            "3. Đạo hàm hàm số mũ: (a^x)' = a^x · ln a; (e^x)' = e^x; [a^u]' = u' · a^u · ln a.",
            "4. Đạo hàm logarit: (log_a x)' = 1 / (x · ln a); (ln x)' = 1 / x; [ln u]' = u' / u."
        ],
        "formulas": [
            "• Đổi cơ số: log_a b = (log_c b) / (log_c a); log_a b · log_b c = log_a c.",
            "• Công thức lũy thừa logarit: log_a (x^α) = α · log_a |x|; a^(log_a b) = b.",
            "• Phương trình a^f(x) = a^g(x) ⇔ f(x) = g(x) (với 0 < a ≠ 1).",
            "• Bất phương trình log_a f(x) < log_a g(x): Nếu a > 1 ⇔ 0 < f(x) < g(x); Nếu 0 < a < 1 ⇔ f(x) > g(x) > 0."
        ],
        "methods": [
            "• Dạng 1: Đưa về cùng cơ số hoặc đặt ẩn phụ t = a^x (t > 0).",
            "• Dạng 2: Phương pháp logarit hóa hai vế khi cơ số và số mũ khác nhau.",
            "• Dạng 3: Ứng dụng tính đơn điệu hàm số (Hàm đặc trưng f(u) = f(v) ⇒ u = v)."
        ]
    },
    "nguyen_ham_tich_phan": {
        "title": "CHUYÊN ĐỀ: NGUYÊN HÀM, TÍCH PHÂN VÀ ỨNG DỤNG HÌNH HỌC",
        "grade": "Lớp 12",
        "concepts": [
            "1. Định nghĩa nguyên hàm: Hàm số F(x) là nguyên hàm của f(x) trên K nếu F'(x) = f(x) với mọi x ∈ K. Họ nguyên hàm: ∫ f(x)dx = F(x) + C.",
            "2. Định nghĩa tích phân: ∫[a→b] f(x)dx = F(b) - F(a) với F(x) là một nguyên hàm bất kỳ của f(x).",
            "3. Ý nghĩa hình học: Diện tích hình phẳng giới hạn bởi đồ thị y = f(x), trục hoành và hai đường thẳng x = a, x = b là S = ∫[a→b] |f(x)|dx."
        ],
        "formulas": [
            "• Bảng nguyên hàm mở rộng: ∫ (ax + b)^α dx = 1/a · (ax + b)^(α+1) / (α + 1) + C (α ≠ -1).",
            "• Tích phân từng phần: ∫ u dv = u·v - ∫ v du (Thứ tự ưu tiên đặt u: 'Nhất lô - Nhì đa - Tam lượng - Tứ mũ').",
            "• Thể tích khối tròn xoay quanh trục Ox: V = π · ∫[a→b] [f(x)]² dx."
        ],
        "methods": [
            "• Dạng 1: Phương pháp đổi biến số loại 1 (đặt t = u(x)) và loại 2 (đặt x = φ(t)).",
            "• Dạng 2: Kỹ thuật múa cột (nguyên hàm từng phần liên tiếp) cho dạng đa thức nhân lượng giác/mũ.",
            "• Dạng 3: Ứng dụng tích phân tính diện tích, thể tích và giải bài toán thực tế STEM."
        ]
    },
    "hinh_hoc_khong_gian": {
        "title": "CHUYÊN ĐỀ: HÌNH HỌC KHÔNG GIAN & HỆ TỌA ĐỘ TRONG KHÔNG GIAN OXYZ",
        "grade": "Lớp 11 - Lớp 12",
        "concepts": [
            "1. Quan hệ vuông góc: Đường thẳng d ⊥ (P) ⇔ d vuông góc với hai đường thẳng cắt nhau nằm trong (P).",
            "2. Góc giữa đường thẳng và mặt phẳng: Là góc giữa đường thẳng và hình chiếu vuông góc của nó trên mặt phẳng đó (0° ≤ φ ≤ 90°).",
            "3. Khoảng cách: Khoảng cách từ điểm M đến mặt phẳng (P): d(M, (P)) = |Ax₀ + By₀ + Cz₀ + D| / √(A² + B² + C²)."
        ],
        "formulas": [
            "• Thể tích khối chóp: V = 1/3 · S_đáy · h.",
            "• Thể tích khối lăng trụ / khối hộp: V = S_đáy · h.",
            "• Bán kính mặt cầu ngoại tiếp hình chóp có cạnh bên vuông góc đáy: R = √[R_đáy² + (h/2)²].",
            "• Tích có hướng của 2 vectơ: [u⃗, v⃗] vuông góc với cả u⃗ và v⃗; Diện tích tam giác S = 1/2 · |[AB⃗, AC⃗]|."
        ],
        "methods": [
            "• Dạng 1: Xác định góc và khoảng cách bằng phương pháp hình học thuần túy (kẻ đường phụ).",
            "• Dạng 2: Phương pháp tọa độ hóa (gắn hệ trục Oxyz vào khối đa diện vuông vức để đại số hóa bài toán).",
            "• Dạng 3: Viết phương trình mặt phẳng, đường thẳng và mặt cầu thỏa mãn điều kiện tiếp xúc / cắt nhau."
        ]
    },
    # ======================= LỚP 10 =======================
    "menh_de_tap_hop": {
        "title": "CHUYÊN ĐỀ: MỆNH ĐỀ VÀ TẬP HỢP",
        "grade": "Lớp 10",
        "concepts": [
            "1. Mệnh đề: câu khẳng định hoặc đúng hoặc sai, không thể vừa đúng vừa sai. Câu cảm thán, câu hỏi không phải mệnh đề.",
            "2. Mệnh đề chứa biến P(x): chỉ xác định được tính đúng sai khi gán giá trị cụ thể cho biến.",
            "3. Mệnh đề kéo theo P ⇒ Q: chỉ SAI duy nhất khi P đúng mà Q sai. P là giả thiết, Q là kết luận.",
            "4. Mệnh đề tương đương P ⇔ Q: đúng khi P và Q cùng đúng hoặc cùng sai; đọc là 'P khi và chỉ khi Q'.",
            "5. Tập hợp: A ⊂ B ⇔ mọi phần tử của A đều thuộc B. Hai tập bằng nhau khi A ⊂ B và B ⊂ A.",
        ],
        "formulas": [
            "• Phủ định: ¬(∀x ∈ X, P(x)) = ∃x ∈ X, ¬P(x);  ¬(∃x ∈ X, P(x)) = ∀x ∈ X, ¬P(x).",
            "• Phủ định các quan hệ: ¬(a = b) là a ≠ b; ¬(a > b) là a ≤ b; ¬(a ≥ b) là a < b.",
            "• Mệnh đề đảo của P ⇒ Q là Q ⇒ P. Mệnh đề phản đảo là ¬Q ⇒ ¬P (luôn tương đương với P ⇒ Q).",
            "• Phép toán tập hợp: A ∪ B (hợp), A ∩ B (giao), A \\ B (hiệu), C_X A = X \\ A (phần bù).",
            "• Số phần tử: n(A ∪ B) = n(A) + n(B) − n(A ∩ B).",
            "• Các tập con của ℝ: (a; b), [a; b], (a; b], [a; b), (−∞; b), (a; +∞).",
        ],
        "methods": [
            "• Dạng 1: Xét tính đúng sai của mệnh đề và lập mệnh đề phủ định (chú ý đổi ∀ thành ∃ và ngược lại).",
            "• Dạng 2: Xác định quan hệ bao hàm giữa các tập hợp, liệt kê tập con.",
            "• Dạng 3: Thực hiện phép toán trên các khoảng, đoạn — nên vẽ trục số để tránh sai sót ở đầu mút.",
            "• Dạng 4: Tìm tham số m để hai tập hợp giao nhau khác rỗng hoặc tập này chứa tập kia.",
        ],
    },
    "ham_so_bac_hai": {
        "title": "CHUYÊN ĐỀ: HÀM SỐ BẬC HAI VÀ ĐỒ THỊ PARABOL",
        "grade": "Lớp 10",
        "concepts": [
            "1. Hàm số bậc hai: y = ax² + bx + c (a ≠ 0), tập xác định D = ℝ.",
            "2. Đồ thị là parabol có đỉnh I(−b/2a; −Δ/4a), trục đối xứng x = −b/2a.",
            "3. Bề lõm: a > 0 quay lên (hàm có giá trị nhỏ nhất tại đỉnh); a < 0 quay xuống (có giá trị lớn nhất).",
            "4. Tính đơn điệu: với a > 0 hàm nghịch biến trên (−∞; −b/2a) và đồng biến trên (−b/2a; +∞); a < 0 thì ngược lại.",
        ],
        "formulas": [
            "• Tọa độ đỉnh: x_I = −b/(2a), y_I = −Δ/(4a) với Δ = b² − 4ac.",
            "• Giao với trục Oy tại điểm (0; c); giao với Ox là nghiệm của ax² + bx + c = 0.",
            "• Định lý Vi-ét: x₁ + x₂ = −b/a, x₁·x₂ = c/a.",
            "• Dấu tam thức bậc hai: Δ < 0 thì f(x) cùng dấu a với mọi x; Δ = 0 thì cùng dấu a trừ tại x = −b/2a; Δ > 0 thì trái dấu a giữa hai nghiệm.",
        ],
        "methods": [
            "• Dạng 1: Lập bảng biến thiên và vẽ parabol từ đỉnh, trục đối xứng và một vài điểm.",
            "• Dạng 2: Xác định a, b, c khi biết các điều kiện về đỉnh hoặc điểm đi qua.",
            "• Dạng 3: Tìm giá trị lớn nhất, nhỏ nhất trên một đoạn — phải so sánh giá trị tại đỉnh với hai đầu mút.",
            "• Dạng 4: Biện luận số nghiệm phương trình bằng tương giao đồ thị.",
        ],
    },
    "bat_phuong_trinh": {
        "title": "CHUYÊN ĐỀ: BẤT PHƯƠNG TRÌNH VÀ HỆ BẤT PHƯƠNG TRÌNH",
        "grade": "Lớp 10",
        "concepts": [
            "1. Bất phương trình bậc nhất hai ẩn ax + by + c ≤ 0: miền nghiệm là một nửa mặt phẳng có bờ là đường thẳng ax + by + c = 0.",
            "2. Miền nghiệm của hệ bất phương trình là giao của các miền nghiệm thành phần, thường là một miền đa giác.",
            "3. Bất phương trình bậc hai một ẩn: đưa về xét dấu tam thức f(x) = ax² + bx + c.",
            "4. Bất phương trình chứa căn và chứa trị tuyệt đối phải đặt điều kiện xác định trước khi biến đổi.",
        ],
        "formulas": [
            "• Xét dấu tam thức: 'trong trái ngoài cùng' — giữa hai nghiệm thì trái dấu a, ngoài hai nghiệm thì cùng dấu a.",
            "• √A ≥ B ⇔ (B < 0 và A ≥ 0) hoặc (B ≥ 0 và A ≥ B²).",
            "• √A ≤ B ⇔ B ≥ 0 và 0 ≤ A ≤ B².",
            "• |A| ≤ B ⇔ −B ≤ A ≤ B (với B ≥ 0);  |A| ≥ B ⇔ A ≥ B hoặc A ≤ −B.",
        ],
        "methods": [
            "• Dạng 1: Biểu diễn miền nghiệm trên mặt phẳng tọa độ, dùng điểm thử (thường lấy gốc O) để chọn nửa mặt phẳng.",
            "• Dạng 2: Bài toán tối ưu — giá trị lớn nhất, nhỏ nhất của biểu thức đạt tại ĐỈNH của miền đa giác nghiệm.",
            "• Dạng 3: Giải bất phương trình bậc hai bằng bảng xét dấu.",
            "• Dạng 4: Tìm m để bất phương trình nghiệm đúng với mọi x — quy về điều kiện của Δ và dấu hệ số a.",
        ],
    },
    "he_thuc_luong_vecto": {
        "title": "CHUYÊN ĐỀ: VECTƠ VÀ HỆ THỨC LƯỢNG TRONG TAM GIÁC",
        "grade": "Lớp 10",
        "concepts": [
            "1. Vectơ là đoạn thẳng có hướng. Hai vectơ bằng nhau khi cùng hướng và cùng độ dài.",
            "2. Quy tắc ba điểm: AB⃗ + BC⃗ = AC⃗. Quy tắc hình bình hành: AB⃗ + AD⃗ = AC⃗ (ABCD là hình bình hành).",
            "3. Tích vô hướng: a⃗·b⃗ = |a⃗|·|b⃗|·cos(a⃗, b⃗). Hai vectơ vuông góc ⇔ tích vô hướng bằng 0.",
            "4. Ba điểm A, B, C thẳng hàng ⇔ AB⃗ và AC⃗ cùng phương ⇔ tồn tại k để AB⃗ = k·AC⃗.",
        ],
        "formulas": [
            "• Định lý cosin: a² = b² + c² − 2bc·cos A. Suy ra cos A = (b² + c² − a²)/(2bc).",
            "• Định lý sin: a/sin A = b/sin B = c/sin C = 2R (R là bán kính đường tròn ngoại tiếp).",
            "• Diện tích tam giác: S = ½ab·sin C = abc/(4R) = p·r = √[p(p−a)(p−b)(p−c)] với p là nửa chu vi.",
            "• Độ dài trung tuyến: m_a² = (2b² + 2c² − a²)/4.",
            "• Tọa độ: a⃗·b⃗ = x₁x₂ + y₁y₂; |a⃗| = √(x² + y²); I là trung điểm AB thì x_I = (x_A + x_B)/2.",
        ],
        "methods": [
            "• Dạng 1: Chứng minh đẳng thức vectơ bằng quy tắc ba điểm và phép chèn điểm.",
            "• Dạng 2: Phân tích một vectơ theo hai vectơ không cùng phương.",
            "• Dạng 3: Giải tam giác — biết ba yếu tố, tìm các yếu tố còn lại bằng định lý sin và cosin.",
            "• Dạng 4: Dùng tích vô hướng để chứng minh vuông góc hoặc tính góc giữa hai đường thẳng.",
        ],
    },
    "toa_do_mat_phang": {
        "title": "CHUYÊN ĐỀ: PHƯƠNG PHÁP TỌA ĐỘ TRONG MẶT PHẲNG",
        "grade": "Lớp 10",
        "concepts": [
            "1. Đường thẳng có vectơ pháp tuyến n⃗ = (A; B) và vectơ chỉ phương u⃗ = (−B; A); hai vectơ này vuông góc nhau.",
            "2. Phương trình tổng quát: Ax + By + C = 0. Phương trình tham số: x = x₀ + at, y = y₀ + bt.",
            "3. Đường tròn tâm I(a; b) bán kính R: (x − a)² + (y − b)² = R².",
            "4. Elip: x²/a² + y²/b² = 1 với a > b > 0, tiêu cự 2c và c² = a² − b².",
        ],
        "formulas": [
            "• Khoảng cách từ điểm M(x₀; y₀) đến đường thẳng: d = |Ax₀ + By₀ + C| / √(A² + B²).",
            "• Góc giữa hai đường thẳng: cos φ = |n₁⃗·n₂⃗| / (|n₁⃗|·|n₂⃗|), luôn lấy giá trị tuyệt đối vì 0° ≤ φ ≤ 90°.",
            "• Dạng khai triển đường tròn: x² + y² − 2ax − 2by + c = 0 với tâm I(a; b), R = √(a² + b² − c) (cần a² + b² − c > 0).",
            "• Đường thẳng tiếp xúc đường tròn ⇔ d(I, Δ) = R.",
        ],
        "methods": [
            "• Dạng 1: Viết phương trình đường thẳng khi biết điểm và phương (hoặc song song, vuông góc với đường cho trước).",
            "• Dạng 2: Xét vị trí tương đối và tính khoảng cách, tính góc.",
            "• Dạng 3: Viết phương trình đường tròn đi qua ba điểm hoặc tiếp xúc đường thẳng.",
            "• Dạng 4: Bài toán về tiếp tuyến của đường tròn — dùng điều kiện khoảng cách bằng bán kính.",
        ],
    },
    # ======================= LỚP 11 =======================
    "luong_giac": {
        "title": "CHUYÊN ĐỀ: HÀM SỐ LƯỢNG GIÁC VÀ PHƯƠNG TRÌNH LƯỢNG GIÁC",
        "grade": "Lớp 11",
        "concepts": [
            "1. Hàm y = sin x và y = cos x tuần hoàn chu kỳ 2π, tập giá trị [−1; 1]. Hàm y = tan x, y = cot x tuần hoàn chu kỳ π.",
            "2. Điều kiện xác định: tan x cần x ≠ π/2 + kπ; cot x cần x ≠ kπ.",
            "3. Phương trình lượng giác cơ bản luôn có vô số nghiệm, viết dưới dạng họ nghiệm kèm k ∈ ℤ.",
            "4. Phương trình a·sin x + b·cos x = c có nghiệm ⇔ a² + b² ≥ c².",
        ],
        "formulas": [
            "• sin x = sin α ⇔ x = α + k2π hoặc x = π − α + k2π.",
            "• cos x = cos α ⇔ x = ±α + k2π.  tan x = tan α ⇔ x = α + kπ.",
            "• Công thức cộng: sin(a ± b) = sin a·cos b ± cos a·sin b; cos(a ± b) = cos a·cos b ∓ sin a·sin b.",
            "• Nhân đôi: sin 2a = 2sin a·cos a; cos 2a = cos²a − sin²a = 2cos²a − 1 = 1 − 2sin²a.",
            "• Hạ bậc: sin²a = (1 − cos 2a)/2;  cos²a = (1 + cos 2a)/2.",
            "• Biến đổi tổng thành tích: sin a + sin b = 2·sin[(a+b)/2]·cos[(a−b)/2].",
            "• a·sin x + b·cos x = √(a² + b²)·sin(x + φ) với tan φ = b/a.",
        ],
        "methods": [
            "• Dạng 1: Tìm tập xác định và tập giá trị của hàm số lượng giác.",
            "• Dạng 2: Giải phương trình cơ bản, nhớ viết đủ HAI họ nghiệm với sin và cos.",
            "• Dạng 3: Đưa về phương trình bậc hai theo một hàm lượng giác bằng công thức hạ bậc hoặc nhân đôi.",
            "• Dạng 4: Phương trình bậc nhất với sin và cos — chia hai vế cho √(a² + b²).",
            "• Dạng 5: Tìm số nghiệm trên một khoảng cho trước — thay k nguyên rồi đối chiếu điều kiện.",
        ],
    },
    "day_so_cap_so": {
        "title": "CHUYÊN ĐỀ: DÃY SỐ, CẤP SỐ CỘNG VÀ CẤP SỐ NHÂN",
        "grade": "Lớp 11",
        "concepts": [
            "1. Dãy số tăng khi u_(n+1) > u_n với mọi n; giảm khi u_(n+1) < u_n. Dãy bị chặn trên, chặn dưới, hoặc bị chặn.",
            "2. Cấp số cộng: mỗi số hạng bằng số hạng trước cộng công sai d không đổi.",
            "3. Cấp số nhân: mỗi số hạng bằng số hạng trước nhân công bội q không đổi.",
            "4. Ba số a, b, c lập cấp số cộng ⇔ a + c = 2b; lập cấp số nhân ⇔ a·c = b².",
        ],
        "formulas": [
            "• Cấp số cộng: u_n = u₁ + (n − 1)d;  S_n = n/2·(u₁ + u_n) = n/2·[2u₁ + (n − 1)d].",
            "• Cấp số nhân: u_n = u₁·q^(n−1);  S_n = u₁·(1 − qⁿ)/(1 − q) với q ≠ 1.",
            "• Tổng cấp số nhân lùi vô hạn (|q| < 1): S = u₁/(1 − q).",
            "• Chứng minh quy nạp: kiểm tra n = 1 đúng, giả sử đúng với n = k rồi chứng minh đúng với n = k + 1.",
        ],
        "methods": [
            "• Dạng 1: Xét tính tăng giảm và tính bị chặn của dãy số.",
            "• Dạng 2: Tìm u₁ và d (hoặc q) từ hệ điều kiện cho trước — đưa hết về u₁ và d rồi giải hệ.",
            "• Dạng 3: Tính tổng n số hạng đầu; chú ý phân biệt công thức của cấp số cộng và cấp số nhân.",
            "• Dạng 4: Bài toán thực tế về lãi kép, tăng trưởng dân số — dùng cấp số nhân.",
        ],
    },
    "gioi_han_dao_ham": {
        "title": "CHUYÊN ĐỀ: GIỚI HẠN, HÀM SỐ LIÊN TỤC VÀ ĐẠO HÀM",
        "grade": "Lớp 11",
        "concepts": [
            "1. Hàm số f(x) liên tục tại x₀ ⇔ f xác định tại x₀ và lim[x→x₀] f(x) = f(x₀).",
            "2. Nếu f liên tục trên [a; b] và f(a)·f(b) < 0 thì phương trình f(x) = 0 có ít nhất một nghiệm trong (a; b).",
            "3. Đạo hàm tại x₀: f'(x₀) = lim[h→0] [f(x₀ + h) − f(x₀)]/h, chính là hệ số góc tiếp tuyến tại điểm đó.",
            "4. Hàm có đạo hàm tại một điểm thì liên tục tại điểm đó; điều ngược lại KHÔNG đúng.",
        ],
        "formulas": [
            "• Giới hạn đặc biệt: lim[x→0] (sin x)/x = 1;  lim[x→∞] (1 + 1/x)^x = e.",
            "• Khử dạng 0/0: phân tích thành nhân tử rồi rút gọn, hoặc nhân liên hợp với biểu thức chứa căn.",
            "• (xⁿ)' = n·x^(n−1);  (√x)' = 1/(2√x);  (sin x)' = cos x;  (cos x)' = −sin x;  (tan x)' = 1/cos²x.",
            "• (u·v)' = u'v + uv';  (u/v)' = (u'v − uv')/v²;  [f(u)]' = u'·f'(u).",
            "• Phương trình tiếp tuyến tại M(x₀; y₀): y = f'(x₀)(x − x₀) + y₀.",
        ],
        "methods": [
            "• Dạng 1: Tính giới hạn dạng vô định 0/0, ∞/∞, ∞ − ∞ bằng phân tích nhân tử hoặc nhân liên hợp.",
            "• Dạng 2: Xét tính liên tục và tìm tham số m để hàm liên tục tại một điểm.",
            "• Dạng 3: Chứng minh phương trình có nghiệm bằng định lý giá trị trung gian.",
            "• Dạng 4: Viết phương trình tiếp tuyến khi biết tiếp điểm, hệ số góc, hoặc điểm đi qua.",
        ],
    },
    "quan_he_khong_gian": {
        "title": "CHUYÊN ĐỀ: QUAN HỆ SONG SONG VÀ VUÔNG GÓC TRONG KHÔNG GIAN",
        "grade": "Lớp 11",
        "concepts": [
            "1. Hai đường thẳng trong không gian có thể cắt nhau, song song, trùng nhau hoặc CHÉO NHAU (không đồng phẳng).",
            "2. Đường thẳng d song song mặt phẳng (P) ⇔ d không nằm trong (P) và song song với một đường thẳng nào đó trong (P).",
            "3. Đường thẳng d ⊥ (P) ⇔ d vuông góc với HAI đường thẳng CẮT NHAU nằm trong (P).",
            "4. Định lý ba đường vuông góc: nếu a ⊂ (P), b không nằm trong (P) có hình chiếu b' trên (P), thì a ⊥ b ⇔ a ⊥ b'.",
        ],
        "formulas": [
            "• Giao tuyến hai mặt phẳng: tìm hai điểm chung, nối lại.",
            "• Thiết diện: xác định giao tuyến của mặt phẳng cắt với từng mặt của khối đa diện.",
            "• Góc giữa đường thẳng và mặt phẳng là góc giữa đường thẳng đó và hình chiếu của nó, thuộc [0°; 90°].",
            "• Khoảng cách từ điểm đến mặt phẳng: dựng hình chiếu vuông góc, hoặc dùng thể tích d = 3V/S_đáy.",
        ],
        "methods": [
            "• Dạng 1: Tìm giao tuyến, giao điểm và dựng thiết diện.",
            "• Dạng 2: Chứng minh song song hoặc vuông góc — luôn quy về điều kiện hai đường cắt nhau.",
            "• Dạng 3: Tính góc giữa hai đường chéo nhau bằng cách tịnh tiến về cùng một điểm.",
            "• Dạng 4: Tính khoảng cách bằng phương pháp thể tích khi dựng hình chiếu quá khó.",
        ],
    },
    # ======================= LỚP 12 bổ sung =======================
    "so_phuc": {
        "title": "CHUYÊN ĐỀ: SỐ PHỨC",
        "grade": "Lớp 12",
        "concepts": [
            "1. Số phức z = a + bi với a là phần thực, b là phần ảo, i² = −1.",
            "2. Số phức liên hợp z̄ = a − bi. Môđun |z| = √(a² + b²) chính là khoảng cách từ điểm biểu diễn tới gốc O.",
            "3. Điểm M(a; b) trong mặt phẳng Oxy biểu diễn số phức z = a + bi.",
            "4. Phương trình bậc hai hệ số thực với Δ < 0 có hai nghiệm phức liên hợp nhau.",
        ],
        "formulas": [
            "• (a + bi)(c + di) = (ac − bd) + (ad + bc)i.",
            "• z/z' = (z·z̄')/|z'|² — nhân cả tử và mẫu với liên hợp của mẫu.",
            "• |z₁·z₂| = |z₁|·|z₂|;  |z₁/z₂| = |z₁|/|z₂|;  z·z̄ = |z|².",
            "• Tập hợp điểm |z − z₀| = R là đường tròn tâm z₀ bán kính R; |z − z₁| = |z − z₂| là trung trực đoạn nối hai điểm.",
        ],
        "methods": [
            "• Dạng 1: Thực hiện phép toán và tìm phần thực, phần ảo, môđun.",
            "• Dạng 2: Giải phương trình trên tập số phức, kể cả phương trình bậc hai có Δ âm.",
            "• Dạng 3: Tìm tập hợp điểm biểu diễn — đưa về phương trình đường thẳng, đường tròn quen thuộc.",
            "• Dạng 4: Bài toán cực trị môđun — dùng ý nghĩa hình học về khoảng cách.",
        ],
    },
    "khoi_da_dien_tron_xoay": {
        "title": "CHUYÊN ĐỀ: KHỐI ĐA DIỆN VÀ KHỐI TRÒN XOAY",
        "grade": "Lớp 12",
        "concepts": [
            "1. Khối đa diện đều có 5 loại: tứ diện đều, lập phương, bát diện đều, mười hai mặt đều, hai mươi mặt đều.",
            "2. Khối nón sinh bởi tam giác vuông quay quanh một cạnh góc vuông; khối trụ sinh bởi hình chữ nhật quay quanh một cạnh.",
            "3. Mặt cầu ngoại tiếp đa diện đi qua mọi đỉnh; tâm cách đều tất cả các đỉnh.",
            "4. Tỉ số thể tích hai khối chóp có chung đỉnh và đáy đồng dạng bằng tỉ số các kích thước tương ứng.",
        ],
        "formulas": [
            "• Khối chóp: V = ⅓·S_đáy·h.  Khối lăng trụ: V = S_đáy·h.",
            "• Khối nón: V = ⅓πr²h; diện tích xung quanh S_xq = πrl với l là đường sinh.",
            "• Khối trụ: V = πr²h; S_xq = 2πrh.",
            "• Khối cầu: V = (4/3)πR³; diện tích mặt cầu S = 4πR².",
            "• Tỉ số thể tích khối chóp tam giác: V(S.A'B'C')/V(S.ABC) = (SA'/SA)·(SB'/SB)·(SC'/SC).",
        ],
        "methods": [
            "• Dạng 1: Tính thể tích khi biết đường cao và diện tích đáy — khó nhất thường là xác định chân đường cao.",
            "• Dạng 2: Dùng tỉ số thể tích cho các khối chóp chung đỉnh.",
            "• Dạng 3: Xác định tâm và bán kính mặt cầu ngoại tiếp.",
            "• Dạng 4: Bài toán cực trị thể tích — đưa về khảo sát hàm một biến.",
        ],
    },
    "dai_so_co_ban": {
        "title": "CHUYÊN ĐỀ: BẤT ĐẲNG THỨC, TỔ HỢP - XÁC SUẤT VÀ DÃY SỐ",
        "grade": "Lớp 10 - Lớp 11",
        "concepts": [
            "1. Bất đẳng thức AM-GM (Cauchy): Với a, b ≥ 0: (a + b)/2 ≥ √(ab). Dấu bằng xảy ra ⇔ a = b.",
            "2. Bất đẳng thức Cauchy-Schwarz: (a₁b₁ + a₂b₂)² ≤ (a₁² + a₂²)(b₁² + b₂²).",
            "3. Quy tắc đếm: Quy tắc cộng (các phương án độc lập); Quy tắc nhân (các công đoạn liên tiếp).",
            "4. Định nghĩa xác suất cổ điển: P(A) = n(A) / n(Ω), với n(A) là số kết quả thuận lợi, n(Ω) là số phần tử không gian mẫu."
        ],
        "formulas": [
            "• Hoán vị: P_n = n!; Chỉnh hợp: A_n^k = n! / (n - k)!; Tổ hợp: C_n^k = n! / [k! · (n - k)!].",
            "• Nhị thức Newton: (a + b)^n = ∑[k=0→n] C_n^k · a^(n-k) · b^k.",
            "• Cấp số cộng: u_n = u₁ + (n - 1)d; Tổng S_n = n/2 · (u₁ + u_n).",
            "• Cấp số nhân: u_n = u₁ · q^(n - 1); Tổng S_n = u₁ · (1 - q^n) / (1 - q) (q ≠ 1)."
        ],
        "methods": [
            "• Dạng 1: Chứng minh bất đẳng thức và tìm giá trị lớn nhất, nhỏ nhất (GTLN, GTNN).",
            "• Dạng 2: Bài toán đếm số tự nhiên, sắp xếp vị trí và chọn đồ vật.",
            "• Dạng 3: Tính xác suất bằng biến cố đối hoặc quy tắc cộng, nhân xác suất."
        ]
    }
}

PHYSICS_THEORY_DATABASE: Dict[str, Dict[str, Any]] = {
    "dao_dong_co": {
        "title": "CHUYÊN ĐỀ: DAO ĐỘNG ĐIỀU HÒA VÀ CÁC HỆ DAO ĐỘNG CƠ HỌC",
        "grade": "Lớp 12",
        "concepts": [
            "1. Phương trình dao động điều hòa: x = A·cos(ωt + φ), trong đó x là li độ (cm, m), A là biên độ (A > 0), ω là tần số góc (rad/s), φ là pha ban đầu.",
            "2. Vận tốc và gia tốc: v = x' = -ωA·sin(ωt + φ) = ωA·cos(ωt + φ + π/2) (v sớm pha π/2 so với x); a = v' = x'' = -ω²x = ω²A·cos(ωt + φ + π) (a ngược pha với x).",
            "3. Năng lượng: Động năng W_d = 1/2 m v²; Thế năng W_t = 1/2 k x²; Cơ năng W = W_d + W_t = 1/2 m ω² A² = const."
        ],
        "formulas": [
            "• Hệ thức độc lập thời gian: x² + (v/ω)² = A²; (v/v_max)² + (a/a_max)² = 1.",
            "• Chu kỳ con lắc lò xo: T = 2π·√(m/k); Tần số góc ω = √(k/m).",
            "• Chu kỳ con lắc đơn: T = 2π·√(l/g); Tần số góc ω = √(g/l).",
            "• Hiện tượng cộng hưởng: Biên độ dao động cưỡng bức đạt cực đại khi tần số lực cưỡng bức f ≈ f₀ (tần số riêng)."
        ],
        "methods": [
            "• Dạng 1: Sử dụng Vòng tròn lượng giác đa trục để tìm khoảng thời gian, quãng đường lớn nhất/nhỏ nhất.",
            "• Dạng 2: Bài toán con lắc lò xo treo thẳng đứng: Độ giãn tại VTCB Δl₀ = mg/k; Lực đàn hồi và lực phục hồi.",
            "• Dạng 3: Tổng hợp hai dao động điều hòa cùng phương, cùng tần số bằng phương pháp số phức trên Casio (Menu 2)."
        ]
    },
    "song_co": {
        "title": "CHUYÊN ĐỀ: SÓNG CƠ, SỰ TRUYỀN SÓNG VÀ GIAO THOA SÓNG",
        "grade": "Lớp 12",
        "concepts": [
            "1. Sóng cơ: Sự lan truyền dao động cơ trong môi trường vật chất theo thời gian. Sóng ngang truyền trong chất rắn và bề mặt chất lỏng; sóng dọc truyền trong chất rắn, lỏng, khí.",
            "2. Bước sóng λ: Khoảng cách giữa hai điểm gần nhau nhất trên cùng một phương truyền sóng dao động cùng pha: λ = v · T = v / f.",
            "3. Giao thoa sóng: Hiện tượng hai sóng kết hợp gặp nhau tạo nên các vân cực đại xen kẽ các vân cực tiểu."
        ],
        "formulas": [
            "• Độ lệch pha giữa 2 điểm cách nhau khoảng d: Δφ = 2πd / λ.",
            "• Điều kiện cực đại giao thoa (2 nguồn cùng pha): d₂ - d₁ = k·λ (k ∈ ℤ).",
            "• Điều kiện cực tiểu giao thoa: d₂ - d₁ = (k + 0.5)·λ.",
            "• Sóng dừng: Đầu cố định - đầu cố định: l = k · (λ/2); Một đầu cố định - một đầu tự do: l = (2k + 1) · (λ/4)."
        ],
        "methods": [
            "• Dạng 1: Viết phương trình sóng tại điểm M cách nguồn một khoảng d; xét độ lệch pha giữa hai thời điểm.",
            "• Dạng 2: Tìm số điểm cực đại, cực tiểu trên đoạn thẳng nối hai nguồn hoặc trên một đoạn bất kỳ.",
            "• Dạng 3: Bài toán đồ thị sóng cơ: Xác định chiều truyền sóng và trạng thái chuyển động của các phần tử môi trường."
        ]
    },
    "dien_xoay_chieu": {
        "title": "CHUYÊN ĐỀ: DÒNG ĐIỆN XOAY CHIỀU VÀ MẠCH RLC MẮC NỐI TIẾP",
        "grade": "Lớp 12",
        "concepts": [
            "1. Dòng điện xoay chiều: Cường độ dòng điện biến thiên điều hòa theo thời gian i = I₀·cos(ωt + φ_i).",
            "2. Giá trị hiệu dụng: I = I₀ / √2; U = U₀ / √2.",
            "3. Trở kháng của các phần tử: Điện trở thuần R; Cảm kháng Z_L = ωL; Dung kháng Z_C = 1 / (ωC)."
        ],
        "formulas": [
            "• Tổng trở đoạn mạch RLC: Z = √[R² + (Z_L - Z_C)²].",
            "• Định luật Ôm: I = U / Z; I₀ = U₀ / Z.",
            "• Độ lệch pha giữa u và i: tan φ = (Z_L - Z_C) / R.",
            "• Công suất tiêu thụ: P = U·I·cos φ = I²·R; Hệ số công suất cos φ = R / Z.",
            "• Điều kiện cộng hưởng điện: Z_L = Z_C ⇔ ω²LC = 1 ⇒ Z_min = R; I_max = U / R; cos φ = 1."
        ],
        "methods": [
            "• Dạng 1: Sử dụng Giản đồ vectơ Fresnel và phương pháp chuẩn hóa số liệu.",
            "• Dạng 2: Bài toán cực trị điện xoay chiều: R thay đổi để P_max; L thay đổi để U_L_max; C thay đổi để U_C_max.",
            "• Dạng 3: Bấm máy tính Casio số phức: Nhập u = U₀∠φ_u, chia cho Z = R + (Z_L - Z_C)i để tìm ngay biểu thức i."
        ]
    }
}

def detect_subject_and_topic(text_samples: List[str], subject: str = "toan") -> Dict[str, Any]:
    """Phân tích nội dung tài liệu để tự động nhận diện chuyên đề kiến thức tương ứng"""
    combined_text = " ".join(text_samples).lower()

    db = MATH_THEORY_DATABASE if subject == "toan" else PHYSICS_THEORY_DATABASE

    best_topic = None
    max_matches = -1

    keyword_map = {
        # Toán
        "ham_so": ["hàm số", "đạo hàm", "cực trị", "đồng biến", "nghịch biến", "tiệm cận", "bảng biến thiên", "đồ thị"],
        "mu_logarit": ["log", "logarit", "mũ", "lũy thừa", "e^", "ln"],
        "nguyen_ham_tich_phan": ["tích phân", "nguyên hàm", "diện tích hình phẳng", "thể tích khối tròn xoay", "∫"],
        "hinh_hoc_khong_gian": ["hình chóp", "lăng trụ", "oxyz", "mặt phẳng", "thể tích", "khoảng cách", "góc giữa"],
        "dai_so_co_ban": ["bất đẳng thức", "tổ hợp", "xác suất", "nhị thức", "chỉnh hợp",
                          "hoán vị", "biến cố", "không gian mẫu"],
        # --- Lớp 10 ---
        "menh_de_tap_hop": ["mệnh đề", "tập hợp", "phủ định", "tập con", "phần bù",
                            "giao của hai tập", "hợp của hai tập", "mệnh đề chứa biến"],
        "ham_so_bac_hai": ["hàm số bậc hai", "parabol", "bảng biến thiên", "đỉnh của parabol",
                           "trục đối xứng", "tam thức bậc hai"],
        "bat_phuong_trinh": ["bất phương trình", "hệ bất phương trình", "miền nghiệm",
                             "xét dấu", "dấu của tam thức", "bất phương trình bậc nhất hai ẩn"],
        "he_thuc_luong_vecto": ["vectơ", "vecto", "hệ thức lượng", "định lý cosin", "định lí cosin",
                                "định lý sin", "định lí sin", "tích vô hướng", "trung tuyến",
                                "giải tam giác"],
        "toa_do_mat_phang": ["tọa độ trong mặt phẳng", "phương trình đường thẳng", "đường tròn",
                             "elip", "vectơ pháp tuyến", "vectơ chỉ phương", "tiếp tuyến của đường tròn"],
        # --- Lớp 11 ---
        # Không để "sin", "cos" trần: chúng khớp nhầm vào "định lý cosin" của chuyên đề
        # hệ thức lượng, và vào "cosinus" hay "tangent" trong văn bản khác.
        "luong_giac": ["lượng giác", "sin x", "cos x", "tan x", "cot x", "sinx", "cosx",
                       "phương trình lượng giác", "công thức cộng", "hạ bậc", "nhân đôi",
                       "cung liên kết", "biến đổi tổng thành tích"],
        "day_so_cap_so": ["dãy số", "cấp số cộng", "cấp số nhân", "công sai", "công bội",
                          "số hạng tổng quát", "quy nạp", "lãi kép"],
        "gioi_han_dao_ham": ["giới hạn", "liên tục", "đạo hàm", "tiếp tuyến", "vô định",
                             "lim", "hệ số góc"],
        "quan_he_khong_gian": ["quan hệ song song", "quan hệ vuông góc", "thiết diện", "giao tuyến",
                               "chéo nhau", "đường thẳng và mặt phẳng", "hai mặt phẳng vuông góc"],
        # --- Lớp 12 ---
        "so_phuc": ["số phức", "phần thực", "phần ảo", "môđun", "liên hợp", "số ảo"],
        "khoi_da_dien_tron_xoay": ["khối đa diện", "khối nón", "khối trụ", "mặt cầu", "mặt nón",
                                   "mặt trụ", "khối tròn xoay", "đường sinh", "thể tích khối chóp",
                                   "mặt cầu ngoại tiếp"],
        # Vật lý
        "dao_dong_co": ["dao động", "con lắc", "biên độ", "chu kỳ", "tần số góc", "vận tốc", "gia tốc", "li độ"],
        "song_co": ["bước sóng", "sóng cơ", "giao thoa", "sóng dừng", "nguồn sóng", "cực đại", "cực tiểu"],
        "dien_xoay_chieu": ["xoay chiều", "cuộn cảm", "tụ điện", "điện áp", "công suất", "tổng trở", "cộng hưởng", "rlc"]
    }

    for topic_key, keywords in keyword_map.items():
        if topic_key in db:
            score = sum(1 for kw in keywords if kw in combined_text)
            if score > max_matches:
                max_matches = score
                best_topic = topic_key

    # Nếu không khớp từ khóa rõ ràng, lấy chuyên đề đầu tiên làm mặc định
    if not best_topic or max_matches == 0:
        best_topic = list(db.keys())[0]

    # Trả về bản sao kèm khóa chuyên đề để các mô-đun khác chọn đúng ngân hàng bài tập.
    # match_score = 0 nghĩa là KHÔNG khớp từ khóa nào, chỉ đang lấy mặc định —
    # nơi gọi cần biết điều này để còn quyết định có tin kết quả hay không.
    result = dict(db[best_topic])
    result["topic_key"] = best_topic
    result["match_score"] = max(0, max_matches)
    return result

def build_pedagogical_theory_section(topic_data: Dict[str, Any]) -> str:
    """Tạo nội dung văn bản phần Lý thuyết nền tảng & Bảng công thức theo chuẩn sư phạm Bộ GD&ĐT"""
    text = f"{topic_data['title'].upper()}\n"
    text += f"Khung kiến thức chuẩn CT GDPT 2018 - {topic_data.get('grade', 'THPT')}\n\n"

    text += "1. KHÁI NIỆM & ĐỊNH NGHĨA TRỌNG TÂM:\n"
    for c in topic_data.get("concepts", []):
        text += f"  {c}\n"

    text += "\n2. HỆ THỐNG BẢNG CÔNG THỨC VÀNG CỐT LÕI:\n"
    for f in topic_data.get("formulas", []):
        text += f"  {f}\n"

    text += "\n3. PHÂN DẠNG BÀI TẬP VÀ PHƯƠNG PHÁP TƯ DUY:\n"
    for m in topic_data.get("methods", []):
        text += f"  {m}\n"

    return text


# ==========================================================
# MẸO CASIO & CẢNH BÁO BẪY THEO TỪNG CHUYÊN ĐỀ
# Trước đây hai mục này được bốc NGẪU NHIÊN từ một danh sách chung, nên một bài
# xác suất tổ hợp có thể bị gắn mẹo "chuyển sang mode số phức để cộng biên độ
# dao động" — sai hoàn toàn ngữ cảnh và phản tác dụng sư phạm.
# ==========================================================

TOPIC_CASIO_TIPS: Dict[str, List[str]] = {
    "ham_so": [
        "Dùng TABLE (Menu 8 trên Casio fx-580VN X): nhập f(X), chọn Start/End đúng miền cần xét, "
        "Step = (End − Start)/29 để quét nhanh khoảng đồng biến, nghịch biến và điểm cực trị.",
        "Tính đạo hàm tại một điểm bằng phím d/dx: so sánh dấu của f'(x) ở hai bên điểm nghi ngờ "
        "là biết ngay đó là cực đại hay cực tiểu, khỏi lập bảng biến thiên.",
        "Tìm tiệm cận đứng: dùng CALC thay x bằng giá trị rất gần nghiệm của mẫu (ví dụ x = 2 + 10⁻⁹) "
        "để xem hàm tiến ra vô cực hay không.",
    ],
    "mu_logarit": [
        "Dùng CALC thử trực tiếp từng phương án vào phương trình mũ/logarit — nhanh hơn nhiều so với "
        "biến đổi đại số, và tránh được sai sót khi đổi cơ số.",
        "SHIFT SOLVE cho phương trình mũ-logarit: gán giá trị x ban đầu gần đáp án để máy hội tụ nhanh, "
        "sau đó nhớ ĐỐI CHIẾU với điều kiện xác định.",
        "Khi đề có log cơ số lạ, dùng công thức đổi cơ số log_a b = ln b / ln a rồi bấm thẳng bằng phím ln.",
    ],
    "nguyen_ham_tich_phan": [
        "Bấm thẳng phím tích phân ∫ với cận đã cho rồi so kết quả với từng phương án — "
        "đây là dạng câu Casio giải nhanh nhất trong đề thi.",
        "Tính diện tích hình phẳng: nhập ∫|f(x) − g(x)|dx với dấu giá trị tuyệt đối thì không cần "
        "xét đồ thị nào nằm trên, máy tự cho kết quả dương.",
        "Kiểm tra một nguyên hàm F(x) có đúng không: dùng d/dx tại vài điểm bất kỳ, nếu bằng f(x) tại "
        "mọi điểm thử thì đáp án đó đúng.",
    ],
    "hinh_hoc_khong_gian": [
        "Tọa độ hóa khối đa diện vuông vức rồi dùng Menu 5 (VECTOR): tính tích có hướng để ra vectơ pháp "
        "tuyến, từ đó tính góc và khoảng cách mà không cần vẽ hình phụ.",
        "Khoảng cách từ điểm đến mặt phẳng: sau khi có phương trình (P), bấm thẳng "
        "|Ax₀ + By₀ + Cz₀ + D| ÷ √(A² + B² + C²) trên máy.",
        "Góc giữa hai mặt phẳng: dùng tích vô hướng hai vectơ pháp tuyến rồi lấy SHIFT cos⁻¹ của giá trị "
        "tuyệt đối thương số.",
    ],
    "dai_so_co_ban": [
        "Dùng phím nCr và nPr để tính tổ hợp, chỉnh hợp ngay trên máy — nhớ phân biệt 'lấy đồng thời' "
        "(tổ hợp C) với 'lấy có thứ tự' (chỉnh hợp A).",
        "Tính tổng cấp số bằng phím Σ (SHIFT log): nhập trực tiếp công thức số hạng tổng quát với biến X "
        "chạy từ 1 đến n, không cần nhớ công thức tổng.",
        "Bài toán xác suất có cụm từ 'ít nhất một': tính xác suất biến cố đối rồi lấy 1 trừ đi — "
        "chỉ một phép tính thay vì cộng nhiều trường hợp.",
    ],
    "dao_dong_co": [
        "Tổng hợp hai dao động cùng phương cùng tần số: chuyển sang Menu 2 (COMPLEX), nhập "
        "A₁∠φ₁ + A₂∠φ₂ rồi SHIFT 2 3 để đọc ngay biên độ và pha tổng hợp.",
        "Hệ thức độc lập thời gian x² + (v/ω)² = A²: bấm trực tiếp để tìm đại lượng còn thiếu, "
        "không cần giải phương trình lượng giác.",
        "Chu kỳ con lắc: T = 2π√(m/k) hoặc 2π√(l/g) — bấm thẳng, nhưng nhớ đổi khối lượng về kg và "
        "chiều dài về mét trước.",
    ],
    "song_co": [
        "Bước sóng λ = v/f bấm một phép chia là xong; nhớ ba mốc phản xạ: cùng pha cách λ, "
        "ngược pha cách λ/2, vuông pha cách λ/4.",
        "Đếm số cực đại giao thoa: tính AB/λ rồi dùng phần nguyên — hai nguồn cùng pha cho "
        "2⌊AB/λ⌋ + 1 điểm khi tỉ số không nguyên.",
        "Độ lệch pha Δφ = 2πd/λ: bấm ra rồi chia cho π để biết ngay là bội chẵn (cùng pha) hay "
        "bội lẻ (ngược pha) của π.",
    ],
    "menh_de_tap_hop": [
        "Với bài toán giao và hợp các khoảng, hãy VẼ TRỤC SỐ ra nháp rồi tô đậm từng tập — "
        "nhanh và chắc hơn nhẩm trong đầu, nhất là ở các đầu mút đóng/mở.",
        "Kiểm tra mệnh đề chứa biến bằng CALC: nhập biểu thức rồi thử vài giá trị đặc biệt "
        "(x = 0, x = 1, x = −1) để tìm phản ví dụ bác bỏ mệnh đề sai.",
        "Đếm số phần tử tập hợp con: một tập có n phần tử thì có 2ⁿ tập con — bấm 2^n trên máy.",
    ],
    "ham_so_bac_hai": [
        "Dùng MODE Equation (Menu A) giải phương trình bậc hai để lấy nghiệm chính xác, "
        "nhanh hơn nhẩm Vi-ét khi hệ số lẻ.",
        "Tính nhanh tọa độ đỉnh: nhập −b/(2a) rồi CALC vào hàm để lấy tung độ, "
        "khỏi phải nhớ công thức −Δ/(4a).",
        "Dùng TABLE (Menu 8) với Start/End là hai đầu đoạn để dò giá trị lớn nhất, nhỏ nhất "
        "trên đoạn — nhìn cột kết quả là thấy ngay xu hướng.",
    ],
    "bat_phuong_trinh": [
        "Giải bất phương trình bằng MODE Inequality (Menu B trên fx-580VN X): máy cho ngay "
        "tập nghiệm, dùng để đối chiếu với kết quả tự làm.",
        "Với bài miền nghiệm, lấy điểm thử O(0; 0) thay vào bất phương trình — đúng thì miền "
        "chứa gốc tọa độ, sai thì lấy nửa mặt phẳng còn lại.",
        "Bất phương trình chứa căn: sau khi giải xong, CALC thử một giá trị trong tập nghiệm "
        "để chắc chắn không nhận nhầm nghiệm ngoại lai.",
    ],
    "he_thuc_luong_vecto": [
        "Chuyển sang Menu 5 (VECTOR) để tính tích vô hướng và độ dài vectơ, tránh nhầm dấu "
        "khi tính tay.",
        "Giải tam giác: nhập định lý cosin cos A = (b² + c² − a²)/(2bc) rồi SHIFT cos⁻¹ ra góc ngay. "
        "Nhớ kiểm tra máy đang ở chế độ DEG hay RAD.",
        "Tính diện tích bằng công thức Heron S = √[p(p−a)(p−b)(p−c)] — bấm một lượt, "
        "không cần tìm đường cao.",
    ],
    "toa_do_mat_phang": [
        "Khoảng cách từ điểm đến đường thẳng: bấm thẳng |Ax₀ + By₀ + C| ÷ √(A² + B²), "
        "nhớ dấu giá trị tuyệt đối ở tử.",
        "Tìm tâm và bán kính đường tròn từ dạng khai triển: tâm là (a; b) với a, b lấy từ "
        "hệ số chia đôi và ĐỔI DẤU, rồi R = √(a² + b² − c).",
        "Góc giữa hai đường thẳng: dùng Menu 5 (VECTOR) tính tích vô hướng hai vectơ pháp tuyến "
        "rồi lấy SHIFT cos⁻¹ của giá trị tuyệt đối thương số.",
    ],
    "luong_giac": [
        "Kiểm tra nghiệm phương trình lượng giác bằng CALC: thay k = 0, 1, −1 vào họ nghiệm "
        "rồi tính lại vế trái xem có bằng vế phải không.",
        "Dùng SHIFT SOLVE tìm một nghiệm gần đúng, rồi chia cho π để nhận ra nghiệm đó "
        "tương ứng với họ nghiệm nào.",
        "Luôn kiểm tra máy đang ở chế độ RAD hay DEG trước khi bấm — sai chế độ là sai toàn bộ bài. "
        "Phương trình lượng giác trong đề thi hầu hết dùng RAD.",
    ],
    "day_so_cap_so": [
        "Dùng phím Σ (SHIFT log) tính tổng trực tiếp: nhập số hạng tổng quát theo X, "
        "cho X chạy từ 1 đến n — không cần nhớ công thức tổng.",
        "Kiểm tra một dãy có phải cấp số cộng không: tính u₂ − u₁ và u₃ − u₂, bằng nhau thì đúng. "
        "Cấp số nhân thì so u₂/u₁ với u₃/u₂.",
        "Bài lãi kép dùng cấp số nhân: số tiền sau n kỳ là A·(1 + r)ⁿ, bấm thẳng bằng phím lũy thừa.",
    ],
    "gioi_han_dao_ham": [
        "Tính giới hạn bằng CALC: thay x bằng giá trị rất gần điểm cần xét (ví dụ x = 2 + 10⁻⁹) "
        "để đoán kết quả, rồi mới biến đổi đại số cho chặt chẽ.",
        "Dùng phím d/dx tính đạo hàm tại một điểm để lấy hệ số góc tiếp tuyến — "
        "nhanh hơn nhiều so với đạo hàm tay rồi thế số.",
        "Giới hạn ở vô cực: thay x = 10⁹ và x = −10⁹ để thấy ngay hàm tiến tới đâu.",
    ],
    "quan_he_khong_gian": [
        "Tọa độ hóa: gắn hệ trục vào khối có sẵn góc vuông rồi dùng Menu 5 (VECTOR) — "
        "biến bài hình không gian thành bài tính toán thuần túy.",
        "Tính khoảng cách bằng thể tích: d = 3V/S_đáy, dùng khi việc dựng hình chiếu vuông góc "
        "quá phức tạp.",
        "Góc giữa hai đường chéo nhau: tịnh tiến một đường về cắt đường kia, rồi dùng định lý "
        "cosin trong tam giác vừa tạo.",
    ],
    "so_phuc": [
        "Chuyển sang Menu 2 (COMPLEX) để cộng, trừ, nhân, chia số phức trực tiếp — "
        "máy tự xử lý i² = −1, không sợ nhầm dấu.",
        "Lấy môđun bằng SHIFT Abs, lấy liên hợp bằng SHIFT 2 2 (Conjg) ngay trong Menu 2.",
        "Giải phương trình bậc hai có Δ < 0: dùng MODE Equation, máy vẫn cho hai nghiệm phức "
        "liên hợp mà không cần biến đổi tay.",
    ],
    "khoi_da_dien_tron_xoay": [
        "Nhớ hệ số: khối chóp và khối nón đều có ⅓, khối lăng trụ và khối trụ thì không. "
        "Nhầm hệ số này là sai gấp ba lần.",
        "Bài tỉ số thể tích: dùng công thức V₁/V₂ = (SA'/SA)·(SB'/SB)·(SC'/SC), "
        "chỉ cần nhân ba tỉ số, không phải tính từng thể tích.",
        "Mặt cầu ngoại tiếp hình chóp có cạnh bên vuông góc đáy: R = √(R_đáy² + h²/4), "
        "bấm một lượt trên máy.",
    ],
    "dien_xoay_chieu": [
        "Menu 2 (COMPLEX) là vũ khí mạnh nhất cho điện xoay chiều: nhập u = U₀∠φᵤ chia cho "
        "Z = R + (Z_L − Z_C)i là ra ngay biểu thức dòng điện cả biên độ lẫn pha.",
        "Với ω = 100π và L, C có chứa π ở mẫu, hai chữ π luôn triệt tiêu — nhẩm được Z_L, Z_C "
        "mà không cần chạm vào máy.",
        "Bài toán cực trị (R thay đổi để P_max): dùng TABLE quét R trên một khoảng rồi nhìn cột "
        "công suất để đoán điểm cực đại trước khi giải chính xác.",
    ],
}

TOPIC_TRAPS: Dict[str, List[str]] = {
    "ham_so": [
        "⚠️ Bẫy phân biệt khái niệm: điểm cực trị của HÀM SỐ là giá trị x, giá trị cực trị là y, "
        "còn điểm cực trị của ĐỒ THỊ là cả tọa độ (x; y). Đọc kỹ câu hỏi hỏi cái nào.",
        "⚠️ Bẫy đầu mút: giá trị lớn nhất, nhỏ nhất trên một ĐOẠN có thể rơi vào hai đầu mút chứ "
        "không chỉ tại điểm cực trị bên trong.",
        "⚠️ Bẫy điều kiện tồn tại cực trị: với hàm bậc ba phải kiểm tra y' = 0 có hai nghiệm phân biệt "
        "(Δ > 0) trước khi áp dụng Vi-ét.",
    ],
    "mu_logarit": [
        "⚠️ Bẫy điều kiện xác định: log_a(b) đòi hỏi 0 < a ≠ 1 và b > 0. Quên đặt điều kiện là nhận "
        "nghiệm ngoại lai.",
        "⚠️ Bẫy chiều bất phương trình: cơ số trong khoảng (0; 1) làm hàm NGHỊCH BIẾN nên phải ĐỔI CHIỀU "
        "bất phương trình; cơ số lớn hơn 1 thì giữ nguyên.",
        "⚠️ Bẫy đổi cơ số: log_(aⁿ) x = (1/n)·log_a x — số mũ của CƠ SỐ đi xuống làm mẫu, rất hay bị "
        "nhầm thành nhân lên.",
    ],
    "nguyen_ham_tich_phan": [
        "⚠️ Bẫy đổi biến: khi đặt t = φ(x) phải đổi CẢ vi phân dt lẫn hai cận tích phân. "
        "Quên một trong hai là sai dấu hoặc sai kết quả.",
        "⚠️ Bẫy diện tích âm: diện tích là ∫|f(x) − g(x)|dx. Lấy sai thứ tự hiệu sẽ ra số âm — "
        "một diện tích âm là vô nghĩa.",
        "⚠️ Bẫy hằng số C: với nguyên hàm phải viết + C; với tích phân xác định thì không có C.",
    ],
    "hinh_hoc_khong_gian": [
        "⚠️ Bẫy xác định chân đường vuông góc: phải tìm đúng giao tuyến của hai mặt phẳng vuông góc "
        "rồi mới hạ đường cao xuống giao tuyến đó.",
        "⚠️ Bẫy góc: góc giữa đường thẳng và mặt phẳng luôn thuộc [0°; 90°]; nếu tính ra góc tù phải "
        "lấy góc bù.",
        "⚠️ Bẫy công thức thể tích: khối chóp có hệ số 1/3 (V = ⅓·S·h), khối lăng trụ thì không "
        "(V = S·h). Nhầm hệ số này sai gấp ba lần.",
    ],
    "dai_so_co_ban": [
        "⚠️ Bẫy 'ít nhất một': nên dùng biến cố đối thay vì cộng dồn nhiều trường hợp — cộng dồn rất "
        "dễ đếm thiếu hoặc đếm trùng.",
        "⚠️ Bẫy tổ hợp và chỉnh hợp: 'lấy đồng thời' dùng tổ hợp C (không phân biệt thứ tự), "
        "'xếp thành hàng' hay 'lấy lần lượt' dùng chỉnh hợp A.",
        "⚠️ Bẫy số hạng tổng quát: uₙ = u₁ + (n − 1)d, KHÔNG phải u₁ + n·d. Sai một bước này là sai "
        "toàn bộ phần sau.",
    ],
    "dao_dong_co": [
        "⚠️ Bẫy pha ban đầu: vật qua vị trí cân bằng theo chiều dương thì φ = −π/2; theo chiều âm thì "
        "φ = +π/2. Nhầm dấu là sai cả bài.",
        "⚠️ Bẫy đơn vị: biên độ cho theo cm thì vận tốc ra cm/s; đổi nhầm sang m/s là sai 100 lần. "
        "Khối lượng phải đổi về kg trước khi tính chu kỳ.",
        "⚠️ Bẫy tốc độ cực đại: v_max = ωA chỉ đạt tại vị trí cân bằng, đừng nhầm với tốc độ tại "
        "một li độ x bất kỳ.",
    ],
    "song_co": [
        "⚠️ Bẫy cùng pha và ngược pha: hai điểm cùng pha cách nhau λ, ngược pha cách nhau λ/2. "
        "Câu hỏi 'gần nhau nhất' thường nhắm vào chỗ nhầm này.",
        "⚠️ Bẫy chẵn lẻ: hai nguồn CÙNG pha cho số cực đại LẺ và số cực tiểu CHẴN; hai nguồn ngược pha "
        "thì ngược lại. Cũng đừng quên giá trị k = 0.",
        "⚠️ Bẫy đơn vị: v cho theo cm/s thì λ ra cm; trộn lẫn mét và centimét trong cùng một bài là "
        "nguồn sai phổ biến nhất.",
    ],
    "menh_de_tap_hop": [
        "⚠️ Bẫy phủ định lượng từ: phủ định của 'với mọi' là 'tồn tại' và ngược lại. "
        "Đồng thời phải phủ định cả phần mệnh đề bên trong, rất nhiều học sinh chỉ đổi lượng từ.",
        "⚠️ Bẫy đầu mút đóng/mở: [a; b] khác hẳn (a; b) khi lấy giao và hợp. "
        "Một dấu ngoặc sai là sai cả đáp án.",
        "⚠️ Bẫy tập rỗng: tập rỗng là tập con của MỌI tập hợp, và cũng là một tập con — "
        "đừng quên nó khi đếm số tập con.",
    ],
    "ham_so_bac_hai": [
        "⚠️ Bẫy dấu của hệ số a: a > 0 thì parabol quay lên và đỉnh là điểm THẤP NHẤT (giá trị nhỏ nhất); "
        "a < 0 thì ngược lại. Nhầm chỗ này là đảo lộn toàn bộ kết luận.",
        "⚠️ Bẫy giá trị lớn nhất trên đoạn: nếu đỉnh nằm NGOÀI đoạn đang xét thì giá trị lớn nhất, "
        "nhỏ nhất rơi vào hai đầu mút, không phải tại đỉnh.",
        "⚠️ Bẫy công thức đỉnh: hoành độ đỉnh là −b/(2a), rất hay bị viết nhầm thành b/(2a) hoặc −b/a.",
    ],
    "bat_phuong_trinh": [
        "⚠️ Bẫy nhân chia số âm: nhân hoặc chia hai vế bất phương trình cho số ÂM thì phải ĐỔI CHIỀU. "
        "Khi biểu thức chứa tham số, bắt buộc xét cả hai trường hợp dấu.",
        "⚠️ Bẫy điều kiện xác định: bất phương trình chứa căn hoặc mẫu phải đặt điều kiện TRƯỚC, "
        "rồi mới giao với tập nghiệm tìm được.",
        "⚠️ Bẫy bình phương hai vế: chỉ được bình phương khi cả hai vế KHÔNG ÂM, "
        "nếu không sẽ sinh ra nghiệm ngoại lai.",
    ],
    "he_thuc_luong_vecto": [
        "⚠️ Bẫy độ dài và vectơ: AB⃗ = −BA⃗ nhưng |AB⃗| = |BA⃗|. Nhầm dấu vectơ là sai cả bài.",
        "⚠️ Bẫy chế độ máy tính: định lý cosin cho ra góc, nếu máy đang ở RAD mà đề hỏi độ "
        "thì kết quả sai hoàn toàn.",
        "⚠️ Bẫy tích vô hướng: a⃗·b⃗ = 0 nghĩa là hai vectơ VUÔNG GÓC, không phải bằng vectơ-không. "
        "Hai khái niệm này hoàn toàn khác nhau.",
    ],
    "toa_do_mat_phang": [
        "⚠️ Bẫy pháp tuyến và chỉ phương: đường thẳng Ax + By + C = 0 có pháp tuyến (A; B) "
        "và chỉ phương (−B; A). Rất hay bị dùng nhầm cái nọ thành cái kia.",
        "⚠️ Bẫy tâm đường tròn: từ dạng x² + y² − 2ax − 2by + c = 0, tâm là (a; b) — "
        "hệ số đã mang sẵn dấu trừ nên phải ĐỔI DẤU khi lấy tọa độ tâm.",
        "⚠️ Bẫy bán kính âm: phải kiểm tra a² + b² − c > 0, nếu không thì đó không phải đường tròn.",
    ],
    "luong_giac": [
        "⚠️ Bẫy thiếu họ nghiệm: sin x = m cho HAI họ nghiệm (x = α + k2π và x = π − α + k2π). "
        "Chỉ viết một họ là mất nửa số nghiệm.",
        "⚠️ Bẫy điều kiện xác định: phương trình chứa tan x hoặc cot x phải loại các giá trị "
        "làm mẫu bằng 0 trước khi kết luận.",
        "⚠️ Bẫy chu kỳ: cos x = cos α cho x = ±α + k2π (chu kỳ 2π), còn tan x = tan α "
        "chỉ có x = α + kπ (chu kỳ π). Dùng nhầm chu kỳ là thừa hoặc thiếu nghiệm.",
    ],
    "day_so_cap_so": [
        "⚠️ Bẫy số hạng tổng quát: uₙ = u₁ + (n − 1)d, KHÔNG phải u₁ + n·d. "
        "Sai một bước này kéo theo sai toàn bộ phần sau.",
        "⚠️ Bẫy công bội âm: cấp số nhân có q < 0 thì các số hạng đan dấu — "
        "đừng vội kết luận dãy tăng hay giảm.",
        "⚠️ Bẫy tổng lùi vô hạn: công thức S = u₁/(1 − q) CHỈ dùng được khi |q| < 1.",
    ],
    "gioi_han_dao_ham": [
        "⚠️ Bẫy giới hạn một bên: hàm có giới hạn tại x₀ khi và chỉ khi giới hạn trái BẰNG giới hạn phải. "
        "Chỉ tính một bên là chưa đủ kết luận.",
        "⚠️ Bẫy liên tục và có đạo hàm: có đạo hàm thì chắc chắn liên tục, nhưng liên tục CHƯA CHẮC "
        "có đạo hàm (ví dụ y = |x| tại x = 0).",
        "⚠️ Bẫy tiếp tuyến: 'tiếp tuyến TẠI điểm M' khác 'tiếp tuyến ĐI QUA điểm M'. "
        "Trường hợp thứ hai M có thể không nằm trên đồ thị và cho nhiều tiếp tuyến.",
    ],
    "quan_he_khong_gian": [
        "⚠️ Bẫy chéo nhau: hai đường thẳng không cắt nhau trong không gian CHƯA CHẮC song song — "
        "chúng có thể chéo nhau. Phải kiểm tra có đồng phẳng hay không.",
        "⚠️ Bẫy điều kiện vuông góc: d ⊥ (P) đòi hỏi d vuông góc với hai đường CẮT NHAU trong (P). "
        "Vuông góc với hai đường song song thì chưa kết luận được gì.",
        "⚠️ Bẫy góc: góc giữa đường thẳng và mặt phẳng luôn thuộc [0°; 90°]. "
        "Tính ra góc tù thì phải lấy góc bù.",
    ],
    "so_phuc": [
        "⚠️ Bẫy phần ảo: phần ảo của z = a + bi là số b, KHÔNG phải bi. Đây là lỗi kinh điển.",
        "⚠️ Bẫy môđun: |z| = √(a² + b²) luôn là số thực không âm, không bao giờ là số phức.",
        "⚠️ Bẫy so sánh: trên tập số phức KHÔNG có quan hệ lớn bé. "
        "Chỉ so sánh được môđun của chúng.",
    ],
    "khoi_da_dien_tron_xoay": [
        "⚠️ Bẫy hệ số ⅓: khối chóp và khối nón có ⅓, khối lăng trụ và khối trụ thì không. "
        "Nhầm là sai gấp ba lần.",
        "⚠️ Bẫy đường sinh và chiều cao: với khối nón, đường sinh l và chiều cao h khác nhau, "
        "liên hệ bởi l² = h² + r². Diện tích xung quanh dùng l chứ không dùng h.",
        "⚠️ Bẫy bán kính đáy: đề thường cho ĐƯỜNG KÍNH đáy — phải chia đôi trước khi thay vào công thức.",
    ],
    "dien_xoay_chieu": [
        "⚠️ Bẫy giá trị hiệu dụng và cực đại: u = U₀·cos(ωt) nghĩa là U = U₀/√2. Dùng nhầm U₀ vào công "
        "thức công suất sẽ cho kết quả gấp đôi.",
        "⚠️ Bẫy cuộn cảm thuần và tụ điện: hai phần tử này KHÔNG tiêu thụ công suất (cos φ = 0), "
        "chỉ điện trở R mới sinh nhiệt.",
        "⚠️ Bẫy đơn vị điện dung: C thường cho theo μF (10⁻⁶) hoặc nF (10⁻⁹). Quên đổi là sai hàng "
        "nghìn lần khi tính Z_C.",
    ],
}


def get_casio_tip(topic_key: str, index: int = 0) -> str:
    """Mẹo Casio đúng chuyên đề. Xoay vòng theo index để các câu không lặp lời."""
    tips = TOPIC_CASIO_TIPS.get(topic_key or "")
    if not tips:
        tips = TOPIC_CASIO_TIPS["ham_so"]
    return tips[index % len(tips)]


def get_trap_warning(topic_key: str, index: int = 0) -> str:
    """Cảnh báo bẫy đúng chuyên đề. Xoay vòng theo index để các câu không lặp lời."""
    traps = TOPIC_TRAPS.get(topic_key or "")
    if not traps:
        traps = TOPIC_TRAPS["ham_so"]
    return traps[index % len(traps)]
