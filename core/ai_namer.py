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
from config import load_settings, LOCAL_MODE

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

# Bộ nhớ đệm trong tiến trình: cùng một tài liệu không gọi lại Gemini nhiều lần.
# Chế độ biên soạn cả thư mục trước đây gọi API 2 lần cho MỖI tệp, rất tốn hạn mức.
_METADATA_CACHE: Dict[str, Any] = {}
_CACHE_LIMIT = 128


def _cache_get(key: str):
    return _METADATA_CACHE.get(key)


def _cache_put(key: str, value):
    if len(_METADATA_CACHE) >= _CACHE_LIMIT:
        _METADATA_CACHE.clear()
    _METADATA_CACHE[key] = value
    return value


def get_effective_api_key(explicit_key: Optional[str] = None) -> str:
    """
    Khóa dùng cho lần gọi này.

    Trên bản Web/Cloud chỉ chấp nhận khóa do chính người dùng gửi lên. Nếu họ
    chưa dán khóa thì trả về rỗng để hệ thống chạy chế độ ngoại tuyến — tuyệt
    đối không lặng lẽ mượn khóa của chủ máy chủ, vì làm vậy là tiêu hạn mức của
    người khác mà họ không hề biết.

    Khi chạy trên máy cá nhân thì mới lấy tiếp khóa đã lưu hoặc biến môi trường.
    """
    explicit = (explicit_key or "").strip()
    if explicit:
        return explicit

    if not LOCAL_MODE:
        return ""

    settings = load_settings()
    return (
        settings.get("gemini_api_key", "").strip()
        or os.environ.get("GEMINI_API_KEY", "").strip()
        or os.environ.get("GOOGLE_API_KEY", "").strip()
    )

# Tên gọi NGẮN của từng chuyên đề, dùng khi đặt tựa.
# Lấy tên tệp làm tựa cho ra kết quả xấu: "Lop10-So-Tay-Dang-Toan-va-Cong-Thuc"
# biến thành tựa 7 chữ vô nghĩa. Nhận diện chuyên đề rồi dùng tên gọn hơn nhiều.
TEN_NGAN_CHUYEN_DE = {
    "ham_so": "Hàm Số",
    "mu_logarit": "Mũ & Logarit",
    "nguyen_ham_tich_phan": "Tích Phân",
    "hinh_hoc_khong_gian": "Hình Không Gian",
    "dai_so_co_ban": "Tổ Hợp & Xác Suất",
    "dao_dong_co": "Dao Động Cơ",
    "song_co": "Sóng Cơ",
    "dien_xoay_chieu": "Điện Xoay Chiều",
}


def _ten_chu_de_ngan(sample_text: str, filename: str, subject: str, subj_name: str) -> str:
    """Tên chủ đề gọn để ghép vào tựa sách."""
    try:
        from core.theory_bank import detect_subject_and_topic
        kq = detect_subject_and_topic([sample_text or "", filename or ""], subject=subject)
        if kq.get("match_score", 0) > 0:
            ten = TEN_NGAN_CHUYEN_DE.get(kq.get("topic_key", ""))
            if ten:
                return ten
    except Exception:
        pass

    # Không nhận ra chuyên đề thì thử rút gọn tên tệp, bỏ các tiền tố kỹ thuật
    stem = Path(filename).stem.replace("_", " ").replace("-", " ")
    stem = re.sub(r"(lop|lớp)\s*\d{1,2}", "", stem, flags=re.I)
    stem = re.sub(r"(bai|bài|de|đề|tai lieu|tài liệu|chuyen de|chuyên đề|pdf|docx|xlsx)",
                  "", stem, flags=re.I)
    stem = " ".join(stem.split())
    tu = stem.split()
    if 1 <= len(tu) <= 3 and len(stem) >= 4:
        return stem.title()
    return subj_name


def _gon_tua(t: Dict[str, Any]) -> Dict[str, Any]:
    """
    Chốt chặn cuối cho quy tắc "ngắn gọn": mô hình vẫn hay viết dài dù đã dặn.
    Cắt phần sau dấu hai chấm và giới hạn số từ.
    """
    out = dict(t)
    tieu_de = (out.get("title") or "").strip()
    # Bỏ phần đuôi sau dấu hai chấm — đó thường là chỗ mô hình nhồi thêm chữ
    if ":" in tieu_de:
        dau, sau = tieu_de.split(":", 1)
        if len(dau.split()) >= 3:
            tieu_de = dau.strip()
        else:
            tieu_de = f"{dau.strip()}: {sau.strip()}"
    tu = tieu_de.split()
    if len(tu) > 8:
        tieu_de = " ".join(tu[:8])
    out["title"] = tieu_de.strip(" -—,;")

    hook = (out.get("hook") or "").strip()
    tu_hook = hook.split()
    if len(tu_hook) > 30:
        hook = " ".join(tu_hook[:30]).rstrip(",;") + "..."
    out["hook"] = hook
    return out


def generate_creative_titles_gemini(
    sample_text: str = "",
    filename: str = "",
    chapter_titles: Optional[List[str]] = None,
    subject: str = "toan",
    api_key: Optional[str] = None,
    model_name: str = "gemini-3.6-flash",
    exclude_titles: Optional[List[str]] = None,
    doc_type: str = ""
) -> List[Dict[str, Any]]:
    """
    Sáng tạo 5 tựa NGẮN GỌN kèm hook đủ mạnh để người đọc muốn xem từ đầu đến cuối.

    Tựa dài lê thê kiểu "BỘ GIẢI MÃ TOÀN DIỆN ... 100 TUYỆT KỸ CASIO & TƯ DUY
    ĐỈNH CAO CHINH PHỤC ĐIỂM 10" nghe thì kêu nhưng không ai nhớ nổi, in lên bìa
    cũng không vừa. Sức hút nằm ở hook chứ không nằm ở độ dài tựa.

    exclude_titles: các tựa đã đề xuất lần trước, để nút "Đổi 5 tựa khác" cho ra
    phương án thực sự mới chứ không lặp lại.
    """
    key = get_effective_api_key(api_key)
    info = extract_grade_and_subject(f"{filename} {sample_text}", default_subject=subject)
    subj_name = "Toán Học" if info["subject"] == "toan" else "Vật Lý"
    loai_tl = "đề thi" if doc_type == "DE_THI" else "cuốn sách"

    tranh = [t.strip() for t in (exclude_titles or []) if t and t.strip()]
    # Đã loại trừ thì không dùng lại kết quả cũ trong bộ nhớ đệm
    cache_key = f"titles|{filename}|{subject}|{chapter_titles}|{hash(sample_text[:1200])}|{doc_type}"
    if not tranh:
        cached = _cache_get(cache_key)
        if cached is not None:
            return cached

    if key:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=key)
            phan_tranh = ""
            if tranh:
                phan_tranh = (
                    "\n\nTUYỆT ĐỐI TRÁNH các tựa đã đề xuất lần trước (phải khác hẳn về ý tưởng, "
                    "không chỉ đổi vài chữ):\n- " + "\n- ".join(tranh[:15])
                )

            prompt = f"""
Bạn là Tổng Biên Tập một nhà xuất bản sách giáo dục bán chạy.
Hãy đặt 5 TỰA cho {loai_tl} {subj_name} {info['grade']} dưới đây.

QUY TẮC VỀ TỰA — quan trọng nhất:
- NGẮN GỌN: tối đa 6 từ. Tựa hay là tựa người ta đọc một lần là nhớ.
- Không nhồi nhét: không liệt kê "toàn diện, chi tiết, đầy đủ, chuyên sâu" cùng lúc.
- Không dùng dấu hai chấm để nối hai vế dài. Một ý sắc gọn là đủ.
- Không bịa con số không có thật (đừng ghi "100 tuyệt kỹ" nếu tài liệu không có 100 mục).

QUY TẮC VỀ HOOK:
- Mỗi tựa kèm một câu hook DUY NHẤT, tối đa 25 từ.
- Hook phải chạm vào một nỗi đau hoặc khát khao có thật của người học: sợ mất gốc,
  làm bài chậm, học mãi không nhớ, muốn điểm cao, sắp thi mà chưa ôn kịp.
- Hook nói ĐIỀU NGƯỜI ĐỌC NHẬN ĐƯỢC, không khoe cuốn sách hay thế nào.
- Viết như đang nói chuyện với một học sinh thật, không sáo rỗng.

Dữ liệu tài liệu:
- Tên tệp gốc: {filename}
- Các chương/chủ đề: {chapter_titles if chapter_titles else 'Chuyên đề trọng tâm'}
- Mẫu nội dung: {sample_text[:1200]}{phan_tranh}

Năm tựa theo 5 hướng khác nhau:
1. Hướng KẾT QUẢ: nói thẳng thứ người học đạt được.
2. Hướng TỐC ĐỘ: nhấn vào giải nhanh, tiết kiệm thời gian.
3. Hướng BẢN CHẤT: hiểu gốc rễ thay vì học vẹt.
4. Hướng CẨM NANG: gọn, tra cứu nhanh, mang theo được.
5. Hướng CẢM HỨNG: chạm vào khát vọng, giàu hình ảnh.

TRẢ VỀ JSON DUY NHẤT:
{{
  "titles": [
    {{
      "style": "Kết quả",
      "title": "Tựa ngắn tối đa 6 từ",
      "subtitle": "Phụ đề một dòng, tối đa 12 từ",
      "hook": "Một câu chạm đúng điều người học đang lo, tối đa 25 từ."
    }}
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
                titles = [_gon_tua(t) for t in titles]
                return titles if tranh else _cache_put(cache_key, titles)
        except Exception as e:
            print(f"Lỗi Gemini creative titles: {e}. Sử dụng bộ sáng tạo chuyên gia mặc định.")

    # BỘ DỰ PHÒNG NGOẠI TUYẾN — cũng phải ngắn gọn và có hook thật.
    # Có nhiều bộ khác nhau để nút "Đổi 5 tựa khác" vẫn cho ra phương án mới
    # ngay cả khi không gọi được API (hết hạn mức hoặc chưa dán khóa).
    chu_de = _ten_chu_de_ngan(sample_text, filename, info["subject"], subj_name)
    lop = info["grade"]

    cac_bo = [
        [
            ("Kết quả", f"Bứt Phá {chu_de}", f"Lộ trình chắc điểm 9+ {subj_name} {lop}",
             "Học đúng thứ cần học, bỏ hẳn phần không bao giờ ra thi."),
            ("Tốc độ", f"{chu_de} Trong 30 Giây", "Mẹo Casio và phản xạ loại trừ nhanh",
             "Hết cảnh còn 10 phút mà chưa làm xong 15 câu cuối."),
            ("Bản chất", f"Hiểu Gốc {chu_de}", "Từ bản chất tới mọi biến thể của đề",
             "Nhớ được lâu vì hiểu tại sao, không phải vì học thuộc."),
            ("Cẩm nang", f"Sổ Tay {chu_de}", f"Công thức cốt lõi {subj_name} {lop} bỏ túi",
             "Mỏng, tra nhanh, ôn trọn kiến thức trong tuần cuối trước thi."),
            ("Cảm hứng", f"Chinh Phục {chu_de}", "Hành trình từ mất gốc đến tự tin",
             "Dành cho người từng nghĩ mình không có khiếu môn này."),
        ],
        [
            ("Kết quả", f"{chu_de} Không Còn Khó", "Mỗi dạng một cách làm cố định",
             "Gặp dạng nào cũng biết bắt đầu từ đâu, không còn ngồi nhìn đề."),
            ("Tốc độ", f"Giải Nhanh {chu_de}", "Rút ngắn mỗi câu còn một phần ba thời gian",
             "Làm xong sớm, còn thời gian soát lại những câu dễ mất điểm oan."),
            ("Bản chất", f"Đọc Vị {chu_de}", "Nhận ra dạng bài chỉ sau một dòng đề",
             "Đề đổi số, đổi cách hỏi vẫn làm được vì đã hiểu đúng bản chất."),
            ("Cẩm nang", f"{chu_de} Bỏ Túi", "Toàn bộ công thức trong vài trang",
             "Mở ra là thấy ngay công thức cần, không phải lật cả quyển."),
            ("Cảm hứng", f"Ngày Mai Giỏi {chu_de}", "Mỗi ngày một bước tiến nhỏ",
             "Bắt đầu từ con số không cũng theo kịp, miễn là bắt đầu hôm nay."),
        ],
        [
            ("Kết quả", f"Chắc Điểm {chu_de}", "Không bỏ sót dạng nào hay ra thi",
             "Những câu chắc chắn có trong đề, chắc chắn bạn làm được."),
            ("Tốc độ", f"{chu_de} Tức Thì", "Phản xạ loại trừ và bấm máy",
             "Nhìn đề là biết chọn hướng nào, không thử hết bốn phương án."),
            ("Bản chất", f"Gốc Rễ {chu_de}", "Hiểu một lần, dùng được mãi",
             "Học một công thức nhưng giải được cả chục dạng khác nhau."),
            ("Cẩm nang", f"Tra Cứu {chu_de}", f"Sổ tay {subj_name} {lop} gọn nhẹ",
             "Đặt cạnh vở nháp, cần gì tra nấy, không mất mạch làm bài."),
            ("Cảm hứng", f"Thắp Lửa {chu_de}", "Từ ngại học đến thấy thú vị",
             "Khi hiểu rồi, môn khó nhất lại thành môn bạn thích làm nhất."),
        ],
    ]

    # Đã loại trừ bao nhiêu tựa thì chuyển sang bộ tiếp theo
    chi_so_bo = (len(tranh) // 5) % len(cac_bo) if tranh else 0
    bo_chon = cac_bo[chi_so_bo]

    ket_qua = []
    for style, title, subtitle, hook in bo_chon:
        if title in tranh:
            continue
        ket_qua.append(_gon_tua({
            "style": style, "title": title, "subtitle": subtitle, "hook": hook
        }))

    # Nếu bộ này trùng hết thì lấy tạm bộ khác cho có phương án
    if not ket_qua:
        bo_khac = cac_bo[(chi_so_bo + 1) % len(cac_bo)]
        ket_qua = [_gon_tua({"style": st, "title": ti, "subtitle": su, "hook": ho})
                   for st, ti, su, ho in bo_khac]
    return ket_qua


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

    cache_key = f"enrich|{book_title}|{subject}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

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
            return _cache_put(cache_key, json.loads(response.text))
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
    model_name: str = "gemini-3.6-flash",
    options: Optional[Dict[str, Any]] = None,
    doc_type: str = ""
) -> Dict[str, Any]:
    """
    Đặt tên sách độc bản, ấn tượng, đúng tinh thần tài liệu, không trùng lặp giữa các cuốn.
    Tự động gọi danh sách các tựa sách thôi miên để chọn ra tựa sách hấp dẫn nhất!

    Hai lượt gọi AI ở đây (đặt tựa + sáng tạo nội dung) trước kia chạy vô điều
    kiện, kể cả khi người dùng đã bỏ tích hết các mục tương ứng — tức mỗi tài
    liệu tiêu oan tới 2 lượt, bằng 10% hạn mức miễn phí một ngày. Nay chỉ gọi
    khi thật sự có thứ để in ra:
      - Tựa sách sáng tạo: đề thi không cần, vì đề thi có tiêu đề hành chính riêng.
      - Nội dung sáng tạo: chỉ gọi khi còn ít nhất một trong lời tựa, bí kíp,
        góc STEM được bật.
    """
    key = get_effective_api_key(api_key)
    opts = options or {}
    can_tua_sang_tao = str(doc_type or "").upper() != "DE_THI"
    can_noi_dung = any(
        opts.get(k, True) for k in ("foreword", "secrets", "stem")
    )
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
    ) if can_tua_sang_tao else []

    best_match = creative_titles[0] if creative_titles else {}
    # Đề thi không đặt tựa kiểu sách: tiêu đề của nó là tiêu đề hành chính.
    tua_du_phong = (
        f"ĐỀ KIỂM TRA {subj_name.upper()} {info['grade'].upper()}"
        if not can_tua_sang_tao
        else f"CẨM NANG TOÀN DIỆN {subj_name.upper()} {info['grade'].upper()}"
    )
    book_title = best_match.get("title", tua_du_phong)
    subtitle = best_match.get("subtitle", "Hệ Thống Kiến Thức Trọng Tâm, Mẹo Casio & Lời Giải Chi Tiết Chuẩn BGD")
    final_series = series if series else f"TỦ SÁCH {subj_name.upper()} THPT — {info['grade'].upper()}"

    # Lấy phần nội dung mở rộng truyền cảm hứng
    enrichment = generate_creative_enrichment_gemini(
        book_title=book_title,
        subject=subject,
        api_key=key,
        model_name=model_name
    ) if can_noi_dung else {}

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
