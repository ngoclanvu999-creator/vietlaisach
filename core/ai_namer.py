"""
Mô-đun Đấu Nối API & Trí Tuệ Nhân Tạo Đặt Tên Sách Độc Bản (AI Book Title & Metadata Synthesizer)
Hỗ trợ cả Gemini API trực tuyến lẫn Bộ suy luận ngữ nghĩa ngoại tuyến thông minh (Smart Offline Heuristics).
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from config import load_settings

def extract_grade_and_subject(text: str, default_subject: str = "toan") -> Dict[str, str]:
    t_lower = text.lower()
    subject = "vatly" if any(k in t_lower for k in ["vật lý", "vật lí", "vat ly", "dao động", "sóng cơ", "điện xoay chiều"]) else "toan"
    grade = "Lớp 12"
    if "lớp 10" in t_lower or "lop 10" in t_lower or "toán 10" in t_lower:
        grade = "Lớp 10"
    elif "lớp 11" in t_lower or "lop 11" in t_lower or "toán 11" in t_lower:
        grade = "Lớp 11"
    elif "lớp 12" in t_lower or "lop 12" in t_lower or "toán 12" in t_lower:
        grade = "Lớp 12"
    return {"subject": subject, "grade": grade}

def synthesize_book_metadata(
    raw_title: str = "",
    raw_subtitle: str = "",
    series: str = "",
    filename: str = "",
    chapter_titles: Optional[List[str]] = None,
    sample_content: str = "",
    subject: str = "toan",
    api_key: Optional[str] = None,
    model_name: str = "gemini-2.5-flash"
) -> Dict[str, Any]:
    """
    Đặt tên sách độc bản, ấn tượng, đúng tinh thần tài liệu, không trùng lặp giữa các cuốn.
    """
    settings = load_settings()
    key = api_key or settings.get("gemini_api_key", "").strip() or os.environ.get("GEMINI_API_KEY", "").strip() or os.environ.get("GOOGLE_API_KEY", "").strip()

    combined_info = f"File: {filename}\nRaw Title: {raw_title}\nSubtitle: {raw_subtitle}\nSeries: {series}\nChapters: {chapter_titles}\nContent Sample: {sample_content[:1000]}"
    info = extract_grade_and_subject(combined_info, default_subject=subject)
    subj_name = "Toán Học" if info["subject"] == "toan" else "Vật Lý"

    # 1. THỬ DÙNG GEMINI API NẾU CÓ KEY
    if key:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=key)
            prompt = f"""
Bạn là Tổng Biên Tập Nhà Xuất Bản Giáo Dục hàng đầu Việt Nam.
Hãy đặt tên sách và bộ thông tin xuất bản ĐỘC BẢN, SANG TRỌNG, CHUẨN SƯ PHẠM GDPT 2018 cho tài liệu sau:

Thông tin tài liệu gốc:
- Tên tệp: {filename}
- Tiêu đề bóc tách: {raw_title}
- Phụ đề gốc: {raw_subtitle}
- Bộ sách / Tủ sách: {series}
- Danh sách các chương / chuyên đề: {chapter_titles}
- Trích đoạn nội dung: {sample_content[:800]}

YÊU CẦU:
1. 'book_title': Tên sách chính thức, in hoa, mang tính độc bản, thể hiện rõ chủ đề, khối lớp ({info['grade']}) và môn học ({subj_name}). Ví dụ: 'SỔ TAY CÔNG THỨC VÀ DẠNG TOÁN TRỌNG TÂM TOÁN 10' hoặc 'TUYỂN TẬP ĐỀ THI HỌC SINH GIỎI TOÁN 11 - CỤM BẮC GIANG'. Tuyệt đối không dùng tên chung chung như 'Tài liệu bài tập' hay 'Tuyệt kỹ chinh phục điểm 9+'.
2. 'subtitle': Phụ đề ấn tượng nêu bật phương pháp sư phạm (Lý thuyết cốt lõi, Phương pháp giải, Lời giải chi tiết).
3. 'series': Tên tủ sách phù hợp (ví dụ: 'TỦ SÁCH CHUYÊN TOÁN THPT').
4. 'author_note': Lời tựa sư phạm trang trọng (3-4 câu).
5. 'doc_type': 'THEMATIC_BOOK' (sổ tay/chuyên đề lý thuyết bài tập) hoặc 'EXAM_TEST' (đề thi).

Trả về định dạng JSON thuần:
{{
  "book_title": "...",
  "subtitle": "...",
  "series": "...",
  "author_note": "...",
  "doc_type": "THEMATIC_BOOK"
}}
"""
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            data = json.loads(response.text)
            if data.get("book_title"):
                return {
                    "book_title": data["book_title"].upper(),
                    "subtitle": data.get("subtitle", "Hệ Thống Hóa Lý Thuyết & Hướng Dẫn Giải Chi Tiết Chuẩn BGD"),
                    "series": data.get("series", series or f"TỦ SÁCH {subj_name.upper()} THPT — {info['grade'].upper()}"),
                    "author_note": data.get("author_note", "Tài liệu được biên soạn công phu theo định hướng phát triển phẩm chất và năng lực học sinh, bám sát cấu trúc đề thi của Bộ GD&ĐT."),
                    "doc_type": data.get("doc_type", "THEMATIC_BOOK"),
                    "grade": info["grade"],
                    "subject": info["subject"],
                    "source_api": "Gemini AI"
                }
        except Exception as e:
            print(f"Lỗi gọi Gemini Namer: {e}. Chuyển sang bộ suy luận ngoại tuyến.")

    # 2. BỘ SUY LUẬN NGOẠI TUYẾN THÔNG MINH (SMART OFFLINE HEURISTICS)
    clean_stem = Path(filename).stem.replace("_", " ").replace("-", " ")

    # Xác định loại tài liệu
    is_exam = any(k in combined_info.lower() for k in ["đề thi", "de thi", "hsg", "học sinh giỏi", "olympic", "chọn học sinh giỏi", "thpt quốc gia", "kỳ thi"])
    doc_type = "EXAM_TEST" if is_exam else "THEMATIC_BOOK"

    # Xây dựng Book Title từ tài liệu gốc
    if raw_title and len(raw_title.strip()) >= 8:
        final_title = raw_title.strip()
    elif "so-tay" in filename.lower() or "sổ tay" in combined_info.lower():
        final_title = f"SỔ TAY DẠNG TOÁN VÀ CÔNG THỨC {subj_name.upper()} {info['grade'].upper().replace('LỚP ', '')}"
    elif "tuyen-tap" in filename.lower() or "tuyển tập" in combined_info.lower():
        final_title = f"TUYỂN TẬP BÀI TOÁN CHỌN LỌC BỒI DƯỠNG HSG {subj_name.upper()} {info['grade'].upper().replace('LỚP ', '')}"
    elif is_exam:
        # Làm sạch tên từ file đề thi
        clean_exam_title = re.sub(r'\[PDF\]\s*', '', clean_stem, flags=re.IGNORECASE)
        final_title = clean_exam_title.upper()
    else:
        final_title = f"CẨM NANG PHÂN DẠNG VÀ PHƯƠNG PHÁP GIẢI {subj_name.upper()} {info['grade'].upper()}"

    # Đảm bảo in hoa chuẩn
    final_title = " ".join(final_title.split()).upper()

    # Xây dựng Subtitle
    if raw_subtitle and len(raw_subtitle.strip()) >= 10:
        final_subtitle = raw_subtitle.strip()
    elif chapter_titles and len(chapter_titles) >= 3:
        chap_preview = ", ".join(re.sub(r'^(?:chủ đề|chương|phần)\s*\d+[\s.:\-–—]*', '', c, flags=re.IGNORECASE).strip() for c in chapter_titles[:3])
        final_subtitle = f"Tuyển Tập {len(chapter_titles)} Chuyên Đề Trọng Tâm ({chap_preview}...) & Lời Giải Chi Tiết Chuẩn BGD"
    elif is_exam:
        final_subtitle = "Đề Thi Chính Thức Có Lời Giải Chi Tiết Chuẩn Mực Sư Phạm, Mẹo Casio & Cảnh Báo Bẫy"
    else:
        final_subtitle = "Tóm Tắt Lý Thuyết Cốt Lõi, Bảng Công Thức Vàng & Hệ Thống Bài Tập Mẫu Có Lời Giải Chi Tiết"

    final_series = series if series else f"TỦ SÁCH {subj_name.upper()} THPT — {info['grade'].upper()}"

    author_note = (
        f"Tài liệu này được tái cấu trúc và biên soạn đồng bộ theo định hướng phát triển năng lực của chương trình GDPT 2018. "
        f"Bố cục tài liệu phân tầng khoa học: Hệ thống hóa lý thuyết nền tảng, sơ đồ tư duy phương pháp giải và tuyển tập bài tập "
        f"có lời giải chi tiết, tích hợp kỹ thuật giải nhanh máy tính cầm tay Casio fx-580VN X."
    )

    return {
        "book_title": final_title,
        "subtitle": final_subtitle,
        "series": final_series,
        "author_note": author_note,
        "doc_type": doc_type,
        "grade": info["grade"],
        "subject": info["subject"],
        "source_api": "Offline Smart Heuristics"
    }
