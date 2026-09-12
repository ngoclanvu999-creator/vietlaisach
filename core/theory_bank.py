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
        "dai_so_co_ban": ["bất đẳng thức", "tổ hợp", "xác suất", "nhị thức", "cấp số cộng", "cấp số nhân", "nghiệm"],
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
