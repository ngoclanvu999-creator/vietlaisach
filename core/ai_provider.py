# -*- coding: utf-8 -*-
"""
Đấu nối AI: một cửa duy nhất để gọi Claude.

Vì sao có mô-đun này: trước đây mã gọi thẳng SDK rải rác trong rewriter,
ai_namer và question_forge, nên khóa đi lạc sang nhà cung cấp khác mà không ai
biết — khóa Anthropic từng bị gửi thẳng sang máy chủ Google. Gom về một hàm
`goi_ai()` thì phần còn lại của hệ thống không cần biết cách gọi, và chỉ có một
chỗ duy nhất phải canh.

Ngày 19/09/2026 chủ dự án chốt **bỏ hẳn Gemini**, chỉ dùng Claude. Vì vậy mô-đun
này không còn khái niệm "nhà cung cấp" nữa. Đừng thêm lại nhánh thứ hai nếu chưa
có yêu cầu rõ: chính việc đỡ hai nhà cung cấp cùng lúc đã sinh ra ba chỗ rò rỉ
khóa.

Nguyên tắc giữ nguyên: khóa là tài sản riêng của từng người, đi theo từng lượt
gọi, mô-đun này không lưu và không đọc khóa của ai khác.
"""

import json
import re
from dataclasses import dataclass

TEN_HIEN_THI = "Anthropic Claude"

MODEL_CLAUDE_MAC_DINH = "claude-sonnet-5"

MODEL_CLAUDE_CHO_PHEP = {
    "claude-sonnet-5",    # cân bằng giá và chất lượng, khuyên dùng
    "claude-haiku-4-5",   # rẻ nhất, hợp việc đơn giản
    "claude-opus-5",      # mạnh nhất, đắt gấp hơn hai lần Sonnet
}

# Những mô hình Claude nhận tham số suy luận thích ứng và mức công sức.
# Haiku 4.5 KHÔNG nhận hai tham số này, gửi lên là lỗi 400.
MODEL_CLAUDE_CO_SUY_LUAN = {"claude-sonnet-5", "claude-opus-5"}


class LoiHanMuc(Exception):
    """Hết hạn mức hoặc hết tín dụng — khác hẳn lỗi mạng, cần báo người dùng rõ."""


class LoiDauRaThieu(Exception):
    """
    Gọi thành công nhưng đầu ra không dùng được: rỗng hẳn, hoặc bị cắt giữa chừng.

    Đây là kiểu hỏng NGUY HIỂM NHẤT vì nó không tự báo — không ngoại lệ, không mã
    lỗi, chỉ là một chuỗi rỗng hoặc một đoạn JSON cụt đi tiếp xuống dưới rồi biến
    thành tài liệu thiếu bài mà không ai biết vì sao.

    Cả hai đều đã gặp thật ngày 18–19/09/2026 khi thử khóa Claude: cùng một câu
    lệnh với max_tokens hẹp, lần thì trả rỗng với stop_reason "max_tokens" (suy
    luận thích ứng ăn hết ngân sách), lần thì trả về nửa câu rồi dừng. Không lần
    nào sinh ra lỗi.

    Nơi gọi duy nhất (`rewriter`) luôn yêu cầu JSON trọn vẹn, nên đầu ra cụt là
    vô dụng hoàn toàn. Nay biến nó thành ngoại lệ có nêu lý do, để hệ thống rơi
    về ngoại tuyến một cách CÓ Ý THỨC thay vì âm thầm nuốt mất nội dung.
    """


@dataclass
class ThongTinAI:
    """Thông tin đăng nhập cho đúng một lượt gọi."""
    api_key: str = ""
    model: str = MODEL_CLAUDE_MAC_DINH

    def co_khoa(self) -> bool:
        return bool((self.api_key or "").strip())

    @property
    def ten_hien_thi(self) -> str:
        return TEN_HIEN_THI


def chuan_hoa(api_key: str = "", model: str = "") -> ThongTinAI:
    """Ép về bộ giá trị hợp lệ; mô hình lạ thì rơi về mặc định."""
    m = (model or "").strip()
    if m not in MODEL_CLAUDE_CHO_PHEP:
        m = MODEL_CLAUDE_MAC_DINH
    return ThongTinAI(api_key=(api_key or "").strip(), model=m)


# ---------------------------------------------------------------------------
# Bóc JSON
# ---------------------------------------------------------------------------
_RAO_MA = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$", re.IGNORECASE)


def boc_json(van_ban: str):
    """
    Lấy JSON ra khỏi câu trả lời.

    Claude hay bọc câu trả lời trong rào ```json. Gỡ rào trước, nếu vẫn không
    phân tích được thì cắt từ dấu ngoặc đầu tới dấu ngoặc cuối — mô hình đôi khi
    thêm một câu dẫn trước JSON.

    `strict=False` là chỗ quan trọng nhất. Claude không có chế độ ép JSON nên
    hay để nguyên dấu xuống dòng thật bên trong chuỗi — về mặt chuẩn JSON là
    sai, `json.loads` mặc định báo "Invalid control character". Đã gặp thật ngày
    19/09/2026: một lô 25 câu hỏng nguyên vì đúng lỗi này, rơi hết về bộ xử lý
    ngoại tuyến. Nội dung thì hoàn toàn dùng được, chỉ vướng đúng một ký tự.
    """
    t = (van_ban or "").strip()
    if not t:
        raise ValueError("Câu trả lời rỗng")

    t = _RAO_MA.sub("", t).strip()
    for doan in (t, None):
        if doan is None:
            dau = min((i for i in (t.find("{"), t.find("[")) if i >= 0), default=-1)
            cuoi = max(t.rfind("}"), t.rfind("]"))
            if not (dau >= 0 and cuoi > dau):
                break
            doan = t[dau:cuoi + 1]
        try:
            return json.loads(doan, strict=False)
        except json.JSONDecodeError:
            continue

    raise ValueError("Không tìm thấy JSON hợp lệ trong câu trả lời")


def la_loi_han_muc(err: Exception) -> bool:
    """Nhận diện lỗi hết hạn mức / hết tiền để báo đúng bệnh."""
    t = f"{type(err).__name__} {err}".lower()
    dau_hieu = (
        "resource_exhausted", "quota", "rate_limit", "ratelimit",
        "429", "insufficient", "credit balance", "billing",
    )
    return any(d in t for d in dau_hieu)


# ---------------------------------------------------------------------------
# Gọi thật
# ---------------------------------------------------------------------------
def goi_ai(
    tt: ThongTinAI,
    prompt: str,
    json_mode: bool = False,
    max_tokens: int = 16000,
) -> str:
    """
    Gửi một câu lệnh, nhận về văn bản thô.

    `json_mode` giữ lại trong chữ ký cho nơi gọi khỏi phải sửa, nhưng Claude
    KHÔNG có chế độ ép JSON — việc gỡ rào ```json và chịu ký tự điều khiển do
    `boc_json()` lo ở phía nhận.

    Không bắt lỗi ở đây: nơi gọi cần biết lô nào hỏng để rơi về chế độ ngoại
    tuyến cho riêng lô đó, nên lỗi phải nổi lên. Riêng lỗi hết hạn mức thì đổi
    thành LoiHanMuc cho dễ phân biệt.
    """
    if not tt.co_khoa():
        raise ValueError("Chưa có khóa API cho lượt gọi này")

    try:
        return _goi_claude(tt, prompt, max_tokens)
    except Exception as e:
        if la_loi_han_muc(e):
            raise LoiHanMuc(
                f"{tt.ten_hien_thi} báo hết hạn mức hoặc hết tín dụng: {e}"
            ) from e
        raise


def _goi_claude(tt: ThongTinAI, prompt: str, max_tokens: int) -> str:
    """
    Dùng truyền phát (streaming) vì đầu ra của ta thường dài — cả lô 25 câu kèm
    lời giải — và yêu cầu không truyền phát với max_tokens lớn dễ hết giờ.
    """
    import anthropic

    client = anthropic.Anthropic(api_key=tt.api_key)

    tham_so = {
        "model": tt.model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if tt.model in MODEL_CLAUDE_CO_SUY_LUAN:
        # Suy luận thích ứng giúp giảm sai số ở bài toán nhiều bước. Mức công
        # sức để "medium" vì đây là việc chạy hàng loạt, ưu tiên chi phí.
        tham_so["thinking"] = {"type": "adaptive"}
        tham_so["output_config"] = {"effort": "medium"}

    with client.messages.stream(**tham_so) as luong:
        tin = luong.get_final_message()

    if getattr(tin, "stop_reason", "") == "refusal":
        chi_tiet = getattr(tin, "stop_details", None)
        raise RuntimeError(
            f"Claude từ chối xử lý nội dung này"
            f"{f' ({chi_tiet.category})' if chi_tiet else ''}"
        )

    van_ban = "".join(b.text for b in tin.content if getattr(b, "type", "") == "text")
    ly_do = getattr(tin, "stop_reason", "") or "không rõ"

    if not van_ban.strip():
        if ly_do == "max_tokens":
            raise LoiDauRaThieu(
                f"Claude dùng hết {max_tokens} token mà chưa viết được chữ nào. "
                f"Model {tt.model} bật suy luận thích ứng nên phần suy luận đã ăn "
                f"hết ngân sách. Cần tăng max_tokens, hoặc chia lô nhỏ hơn."
            )
        raise LoiDauRaThieu(f"Claude trả về rỗng (dừng vì: {ly_do}).")

    if ly_do == "max_tokens":
        raise LoiDauRaThieu(
            f"Claude bị cắt giữa chừng ở {len(van_ban)} ký tự vì chạm trần "
            f"{max_tokens} token. JSON cụt không bóc được, phải chia lô nhỏ hơn."
        )

    return van_ban


# Kiểu ảnh Claude nhận. Đuôi tệp lạ thì coi là PNG — thà gửi sai kiểu còn hơn
# đoán bừa rồi bỏ qua cả ảnh.
_KIEU_ANH = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp",
}


def goi_ai_kem_anh(tt: ThongTinAI, prompt: str, duong_dan_anh,
                   max_tokens: int = 8000) -> str:
    """
    Gửi một câu lệnh KÈM ẢNH, dùng cho ảnh chụp đề thi.

    Để ở đây chứ không để trong `parser.py` vì cùng một lý do như mọi lượt gọi
    khác: mô-đun nào tự gọi SDK là mô-đun đó có thể làm khóa đi lạc. `parser.py`
    từng gọi thẳng `genai.Client` để đọc ảnh, nên khóa nào truyền vào cũng bay
    sang máy chủ Google — kể cả khóa Anthropic.
    """
    import base64
    from pathlib import Path

    if not tt.co_khoa():
        raise ValueError("Chưa có khóa API cho lượt gọi này")

    import anthropic

    p = Path(duong_dan_anh)
    kieu = _KIEU_ANH.get(p.suffix.lower(), "image/png")
    du_lieu = base64.standard_b64encode(p.read_bytes()).decode("ascii")

    client = anthropic.Anthropic(api_key=tt.api_key)
    tham_so = {
        "model": tt.model,
        "max_tokens": max_tokens,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image",
                 "source": {"type": "base64", "media_type": kieu, "data": du_lieu}},
                {"type": "text", "text": prompt},
            ],
        }],
    }
    if tt.model in MODEL_CLAUDE_CO_SUY_LUAN:
        tham_so["thinking"] = {"type": "adaptive"}
        tham_so["output_config"] = {"effort": "medium"}

    try:
        with client.messages.stream(**tham_so) as luong:
            tin = luong.get_final_message()
    except Exception as e:
        if la_loi_han_muc(e):
            raise LoiHanMuc(f"{tt.ten_hien_thi} báo hết hạn mức hoặc hết tín dụng: {e}") from e
        raise

    van_ban = "".join(b.text for b in tin.content if getattr(b, "type", "") == "text")
    if not van_ban.strip():
        raise LoiDauRaThieu(
            f"Claude đọc ảnh nhưng không trả về chữ nào "
            f"(dừng vì: {getattr(tin, 'stop_reason', '') or 'không rõ'})."
        )
    return van_ban
