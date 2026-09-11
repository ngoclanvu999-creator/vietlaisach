"""
Mô-đun Đấu Nối API & Trí Tuệ Nhân Tạo Đặt Tên Sách Độc Bản & Sáng Tạo Nội Dung Đắt Giá
(AI Book Title Hypnotizer & Creative Pedagogical Content Synthesizer)
Hỗ trợ cả Gemini API trực tuyến lẫn Bộ suy luận ngữ nghĩa ngoại tuyến thông minh.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from config import load_settings

def extract_grade_and_subject(text: str, default_subject: str = "toan") -> Dict[str, str]:
    t_lower = text.lower()
    subject = "vatly" if any(k in t_lower for k in ["vật lý", "vật lí", "vat ly", "dao động", "sóng cơ", "điện xoay chiều", "con lắc", "quang hình"]) else "toan"
    grade = "Lớp 12"
    if "lớp 10" in t_lower or "lop 10" in t_lower or "toán 10" in t_lower:
        grade = "Lớp 10"
    elif "lớp 11" in t_lower or "lop 11" in t_lower or "toán 11" in t_lower:
        grade = "Lớp 11"
    elif "lớp 12" in t_lower or "lop 12" in t_lower or "toán 12" in t_lower:
        grade = "Lớp 12"
    return {"subject": subject, "grade": grade}

def get_effective_api_key(explicit_key: Optional[str] = None) -> str:
    settings = load_settings()
    return (
        (explicit_key or "").strip()
        or settings.get("gemini_api_key", "").strip()
        or os.environ.get("GEMINI_API_KEY", "").strip()
        or os.environ.get("GOOGLE_API_KEY", "").strip()
    )

def generate_creative_titles_gemini(
    sample_text: str = "",
    filename: str = "",
    chapter_titles: Optional[List[str]] = None,
    subject: str = "toan",
    api_key: Optional[str] = None,
    model_name: str = "gemini-3.6-flash"
) -> List[Dict[str, Any]]:
    """
    Sử dụng Gemini API để sáng tạo ra 5 tựa sách 'THÔI MIÊN' — nhìn vào tựa đề là người đọc
    khao khát muốn mở sách và đọc hết cuốn sách ngay lập tức!
    """
    key = get_effective_api_key(api_key)
    info = extract_grade_and_subject(f"{filename} {sample_text}", default_subject=subject)
    subj_name = "Toán Học" if info["subject"] == "toan" else "Vật Lý"

    if key:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=key)
            prompt = f"""
Bạn là Tổng Biên Tập kỳ cựu của Nhà Xuất Bản Sách Bán Chạy Nhất (Best-Seller Education Publisher).
Nhiệm vụ của bạn là: SÁNG TẠO 5 TỰA SÁCH "THÔI MIÊN" CHO TÀI LIỆU {subj_name.upper()} {info['grade'].upper()}.
Mục tiêu tối thượng: Người học, giáo viên hoặc phụ huynh khi nhìn vào tựa sách là BỊ HÚT HỒN, TÒ MÒ VÀ MUỐN ĐỌC HẾT TOÀN BỘ CUỐN SÁCH NGAY LẬP TỨC!

Dữ liệu tài liệu:
- Tên tệp gốc: {filename}
- Các chương/chủ đề chính: {chapter_titles if chapter_titles else 'Chuyên đề trọng tâm'}
- Mẫu nội dung: {sample_text[:1200]}

Hãy sáng tạo đúng 5 phương án theo 5 trường phái cuốn hút tâm lý học sinh:
1. TRƯỜNG PHÁI BỨT PHÁ THỦ KHOA: Tựa sách mang tính chinh phục điểm tuyệt đối (9+ và 10), giải mã bí mật đỉnh cao.
2. TRƯỜNG PHÁI THỰC CHIẾN TỐC ĐỘ: Tựa sách nhấn mạnh vào tốc độ giải nhanh 15-30s, bảo bối Casio fx-580VN X và triệt tiêu bẫy đề thi.
3. TRƯỜNG PHÁI TƯ DUY BẢN CHẤT & ĐỜI SỐNG: Tựa sách làm nổi bật triết lý GDPT 2018, kết nối toán học với thực tiễn, biến môn học trở nên sinh động hấp dẫn.
4. TRƯỜNG PHÁI CẨM NANG BỎ TÚI / BẢO BỐI PHÒNG THI: Tựa sách mang lại cảm giác an tâm tuyệt đối, tóm gọn mọi công thức vàng không thể thiếu khi bước vào phòng thi.
5. TRƯỜNG PHÁI ĐỘC BẢN TRUYỀN CẢM HỨNG: Tựa sách văn phong nghệ thuật, kích thích niềm đam mê sâu thẳm, khơi gợi khát vọng dẫn đầu.

TRẢ VỀ ĐỊNH DẠNG JSON DUY NHẤT:
{{
  "titles": [
    {{
      "style": "Bứt Phá Thủ Khoa (Điểm 10 Tuyệt Đối)",
      "title": "TÊN SÁCH IN HOA CỰC CUỐN",
      "subtitle": "Phụ đề đắt giá kích thích hành động...",
      "hook": "Lý do vì sao người đọc không thể bỏ qua cuốn sách này trong 1 câu"
    }},
    ...
  ]
}}
"""
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            data = json.loads(response.text)
            titles = data.get("titles", [])
            if titles and len(titles) >= 3:
                return titles
        except Exception as e:
            print(f"Lỗi Gemini creative titles: {e}. Sử dụng bộ sáng tạo chuyên gia mặc định.")

    # BỘ SÁNG TẠO DỰ PHÒNG CHUẨN MỰC TÂM LÝ HỌC SINH (OFFLINE FALLBACK)
    clean_stem = Path(filename).stem.replace("_", " ").replace("-", " ")
    topic = clean_stem if len(clean_stem) > 4 else f"Chuyên Đề {subj_name}"

    return [
        {
            "style": "Bứt Phá Thủ Khoa (Chinh Phục Điểm 10)",
            "title": f"BỘ GIẢI MÃ TOÀN DIỆN {topic.upper()}: 100 TUYỆT KỸ CASIO & TƯ DUY ĐỈNH CAO CHINH PHỤC ĐIỂM 10",
            "subtitle": f"Bí Quyết Nắm Trọn Điểm 9+ {subj_name} {info['grade']} Dành Riêng Cho Học Sinh Khát Khao Dẫn Đầu",
            "hook": "Giải mã tận gốc mọi câu hỏi phân hóa đỉnh cao, biến những bài toán khó nhất thành cơ hội ghi điểm tuyệt đối."
        },
        {
            "style": "Thực Chiến Tốc Độ & Phản Xạ 15 Giây",
            "title": f"CHIẾN THUẬT THỰC CHIẾN {topic.upper()}: CÔNG THỨC VÀNG & BÍ THUẬT TRIỆT TIÊU BẪY ĐỀ THI",
            "subtitle": f"Làm Chủ Tốc Độ Giải Nhanh Với Casio fx-580VN X & Phương Pháp Loại Trừ Tối Ưu Thời Gian",
            "hook": "Trang bị phản xạ nhận diện bẫy chỉ trong 5 giây đầu tiên và công phá trắc nghiệm trong 30 giây."
        },
        {
            "style": "Bản Chất Học Thuật & Đời Sống (GDPT 2018)",
            "title": f"LÀM CHỦ {topic.upper()} TỪ BẢN CHẤT ĐẾN ỨNG DỤNG ĐỜI SỐNG THEO ĐỊNH HƯỚNG GDPT 2018",
            "subtitle": f"Sơ Đồ Tư Duy Khép Kín, Hệ Thống Bài Toán STEM Thực Tiễn & Lời Giải Đa Chiều",
            "hook": "Hiểu sâu sắc bản chất toán học để nhớ mãi không quên, tự tin ứng biến với mọi dạng câu hỏi mới lạ của Bộ GD&ĐT."
        },
        {
            "style": "Cẩm Nang Bỏ Túi Phòng Thi",
            "title": f"SỔ TAY CÔNG THỨC VÀNG & BẢO BỐI PHÒNG THI {topic.upper()} {info['grade'].upper()}",
            "subtitle": f"Cô Đọng Toàn Bộ Kiến Thức Cốt Lõi, Bảng Tra Cứu Nhanh & 50 Sai Lầm Cấm Kỵ",
            "hook": "Cứu cánh đắc lực giúp bạn hệ thống hóa toàn bộ kiến thức chỉ trong 1 tuần trước kỳ thi quan trọng."
        },
        {
            "style": "Truyền Cảm Hứng & Khát Vọng Đỉnh Cao",
            "title": f"CHÌA KHÓA VÀNG BƯỚC VÀO CỔNG TRƯỜNG ĐẠI HỌC MƠ ƯỚC: CHINH PHỤC {topic.upper()}",
            "subtitle": f"Hành Trình Bứt Phá Năng Lực Tự Học — Từ Mất Gốc Đến Làm Chủ Kiến Thức Đỉnh Cao",
            "hook": "Đánh thức tiềm năng vô hạn và ngọn lửa đam mê, giúp bạn vượt qua mọi rào cản tâm lý phòng thi."
        }
    ]

def generate_creative_enrichment_gemini(
    book_title: str,
    subject: str = "toan",
    sample_questions: Optional[List[str]] = None,
    api_key: Optional[str] = None,
    model_name: str = "gemini-3.6-flash"
) -> Dict[str, Any]:
    """
    Dùng Gemini API để sáng tạo thêm các nội dung giá trị gia tăng cực cao cho cuốn sách:
    1. Lời tựa truyền cảm hứng 'thôi miên' người đọc.
    2. Hộp bí kíp thủ khoa & phân tích tâm lý làm bài thi.
    3. Kết nối toán học với thế giới thực (STEM & Công nghệ tương lai).
    """
    key = get_effective_api_key(api_key)
    subj_name = "Toán Học" if subject == "toan" else "Vật Lý"

    if key:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=key)
            prompt = f"""
Bạn là Nhà Giáo Ưu Tú kiêm Chuyên Gia Viết Sách Sư Phạm Hàng Đầu.
Hãy sáng tạo NỘI DUNG MỞ RỘNG ĐẶC SẮC cho cuốn sách:
- Tựa sách: {book_title}
- Môn học: {subj_name}
- Mẫu bài tập trong sách: {sample_questions[:3] if sample_questions else 'Các chuyên đề trọng tâm'}

YÊU CẦU NỘI DUNG SÁNG TẠO:
1. 'inspiring_foreword': Lời Tựa Mở Đầu 'Thôi Miên' (3 đoạn văn truyền cảm hứng mãnh liệt, đánh trúng tâm lý khao khát điểm số và đam mê chinh phục của học sinh).
2. 'valedictorian_secrets': 3 Lời Khuyên Vàng Từ Thủ Khoa Toàn Quốc (Thực tế, sắc bén về chiến thuật phòng thi, quản lý thời gian và né bẫy).
3. 'stem_connection': 1 Góc Kết Nối Thực Tiễn GDPT 2018 (Chỉ ra kiến thức trong sách này đang vận hành thế giới thực ra sao: Trí tuệ nhân tạo, tối ưu kinh tế, hàng không vũ trụ...).

TRẢ VỀ ĐỊNH DẠNG JSON:
{{
  "inspiring_foreword": "...",
  "valedictorian_secrets": ["Bí quyết 1...", "Bí quyết 2...", "Bí quyết 3..."],
  "stem_connection": "..."
}}
"""
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Lỗi Gemini enrichment: {e}. Dùng nội dung chuyên gia mặc định.")

    # OFFLINE ENRICHMENT FALLBACK
    return {
        "inspiring_foreword": (
            f"Chào bạn, người đang cầm trên tay cuốn sách đặc biệt này!\n\n"
            f"Toán học không chỉ là những con số vô hồn hay những công thức khô khan trên bảng đen. "
            f"Toán học chính là ngôn ngữ của tư duy logic sắc bén, là công cụ tối thượng giúp bạn nhìn thấu trật tự của vũ trụ "
            f"và giải quyết những bài toán phức tạp nhất của cuộc sống.\n\n"
            f"Cuốn sách '{book_title}' được biên soạn với một sứ mệnh duy nhất: Đập tan nỗi sợ hãi, "
            f"trang bị cho bạn vũ khí tư duy tối tân nhất và dẫn dắt bạn từng bước vững chắc chạm tay vào điểm số mơ ước. "
            f"Hãy mở từng trang sách với sự tò mò của một nhà thám hiểm, bạn sẽ nhận ra mọi bài toán khó đều ẩn chứa một chìa khóa thanh lịch!"
        ),
        "valedictorian_secrets": [
            "🏆 Tuyệt kỹ 15 phút đầu: Quét sạch 30 câu nhận biết - thông hiểu với tốc độ tối đa và độ chính xác 100%, tích lũy năng lượng cho vùng điểm 9+.",
            "🏆 Kỹ thuật Casio kép: Luôn dùng máy tính để kiểm tra lại nghiệm tự luận của các bài toán tham số m bằng chức năng TABLE (Menu 8) hoặc CALC.",
            "🏆 Tâm lý 'Đóng băng lỗi sai': Khi gặp bài toán biến tướng lạ mắt, bình tĩnh đưa về bài toán gốc cơ bản bằng phương pháp đổi biến hoặc vẽ giản đồ tư duy."
        ],
        "stem_connection": (
            f"🌐 GÓC KẾT NỐI ĐỜI SỐNG (GDPT 2018): Các bài toán khảo sát hàm số, cực trị và tích phân trong chuyên đề này "
            f"chính là thuật toán cốt lõi đang điều khiển các mạng nơ-ron Trí tuệ Nhân tạo (Machine Learning Backpropagation), "
            f"tối ưu hóa chi phí logistic của các tập đoàn công nghệ và tính toán quỹ đạo hạ cánh của tên lửa tái sử dụng SpaceX."
        )
    }

def synthesize_book_metadata(
    raw_title: str = "",
    raw_subtitle: str = "",
    series: str = "",
    filename: str = "",
    chapter_titles: Optional[List[str]] = None,
    sample_content: str = "",
    subject: str = "toan",
    api_key: Optional[str] = None,
    model_name: str = "gemini-3.6-flash"
) -> Dict[str, Any]:
    """
    Đặt tên sách độc bản, ấn tượng, đúng tinh thần tài liệu, không trùng lặp giữa các cuốn.
    Tự động gọi danh sách các tựa sách thôi miên để chọn ra tựa sách hấp dẫn nhất!
    """
    key = get_effective_api_key(api_key)
    combined_info = f"File: {filename}\nRaw Title: {raw_title}\nSubtitle: {raw_subtitle}\nSeries: {series}\nChapters: {chapter_titles}\nContent Sample: {sample_content[:1000]}"
    info = extract_grade_and_subject(combined_info, default_subject=subject)
    subj_name = "Toán Học" if info["subject"] == "toan" else "Vật Lý"

    # Lấy tựa sách thôi miên phong cách Thủ Khoa
    creative_titles = generate_creative_titles_gemini(
        sample_text=sample_content,
        filename=filename,
        chapter_titles=chapter_titles,
        subject=subject,
        api_key=key,
        model_name=model_name
    )

    best_match = creative_titles[0] if creative_titles else {}
    book_title = best_match.get("title", f"CẨM NANG TOÀN DIỆN {subj_name.upper()} {info['grade'].upper()}")
    subtitle = best_match.get("subtitle", "Hệ Thống Kiến Thức Trọng Tâm, Mẹo Casio & Lời Giải Chi Tiết Chuẩn BGD")
    final_series = series if series else f"TỦ SÁCH {subj_name.upper()} THPT — {info['grade'].upper()}"

    # Lấy phần nội dung mở rộng truyền cảm hứng
    enrichment = generate_creative_enrichment_gemini(
        book_title=book_title,
        subject=subject,
        api_key=key,
        model_name=model_name
    )

    return {
        "book_title": book_title.upper(),
        "subtitle": subtitle,
        "series": final_series,
        "author_note": enrichment.get("inspiring_foreword", ""),
        "valedictorian_secrets": enrichment.get("valedictorian_secrets", []),
        "stem_connection": enrichment.get("stem_connection", ""),
        "doc_type": "THEMATIC_BOOK",
        "grade": info["grade"],
        "subject": info["subject"],
        "creative_options": creative_titles,
        "source_api": "Gemini AI (Creative Suite)" if key else "Expert Pedagogical Engine"
    }
