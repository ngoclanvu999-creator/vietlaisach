# -*- coding: utf-8 -*-
"""
Đấu nối AI: một cửa duy nhất cho cả Gemini lẫn Claude.

Vì sao có mô-đun này: trước đây mã gọi thẳng `genai.Client` rải rác trong
rewriter và ai_namer, nên muốn thêm nhà cung cấp thứ hai là phải sửa từng chỗ.
Gom về một hàm `goi_ai()` thì phần còn lại của hệ thống không cần biết đang nói
chuyện với ai.

Nguyên tắc giữ nguyên như cũ: khóa là tài sản riêng của từng người, đi theo
từng lượt gọi, mô-đun này không lưu và không đọc khóa của ai khác.
"""

import json
import re
from dataclasses import dataclass
from typing import Optional

GEMINI = "gemini"
CLAUDE = "claude"
NHA_CUNG_CAP = (GEMINI, CLAUDE)

TEN_HIEN_THI = {
    GEMINI: "Google Gemini",
    CLAUDE: "Anthropic Claude",
}

MODEL_GEMINI_MAC_DINH = "gemini-3.6-flash"
MODEL_CLAUDE_MAC_DINH = "claude-sonnet-5"

MODEL_GEMINI_CHO_PHEP = {
    "gemini-3.6-flash", "gemini-3.6-pro",
    "gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash",
}

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
    provider: str = GEMINI
    api_key: str = ""
    model: str = ""

    def co_khoa(self) -> bool:
        return bool((self.api_key or "").strip())

    @property
    def ten_hien_thi(self) -> str:
        return TEN_HIEN_THI.get(self.provider, self.provider)


def chuan_hoa(provider: str = "", api_key: str = "", model: str = "") -> ThongTinAI:
    """Ép về bộ giá trị hợp lệ; mô hình lạ thì rơi về mặc định của nhà đó."""
    p = (provider or "").strip().lower()
    if p not in NHA_CUNG_CAP:
        p = GEMINI

    m = (model or "").strip()
    if p == CLAUDE:
        if m not in MODEL_CLAUDE_CHO_PHEP:
            m = MODEL_CLAUDE_MAC_DINH
    else:
        if m not in MODEL_GEMINI_CHO_PHEP:
            m = MODEL_GEMINI_MAC_DINH

    return ThongTinAI(provider=p, api_key=(api_key or "").strip(), model=m)


# ---------------------------------------------------------------------------
# Bóc JSON
# ---------------------------------------------------------------------------
_RAO_MA = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$", re.IGNORECASE)


def boc_json(van_ban: str):
    """
    Lấy JSON ra khỏi câu trả lời.

    Gemini có chế độ trả JSON thuần, còn Claude thì hay bọc trong rào ```json.
    Gỡ rào trước, nếu vẫn không phân tích được thì cắt từ dấu ngoặc đầu tới dấu
    ngoặc cuối — mô hình đôi khi thêm một câu dẫn trước JSON.
    """
    t = (van_ban or "").strip()
    if not t:
        raise ValueError("Câu trả lời rỗng")

    t = _RAO_MA.sub("", t).strip()
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        pass

    dau = min((i for i in (t.find("{"), t.find("[")) if i >= 0), default=-1)
    cuoi = max(t.rfind("}"), t.rfind("]"))
    if dau >= 0 and cuoi > dau:
        return json.loads(t[dau:cuoi + 1])

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

    Không bắt lỗi ở đây: nơi gọi cần biết lô nào hỏng để rơi về chế độ ngoại
    tuyến cho riêng lô đó, nên lỗi phải nổi lên. Riêng lỗi hết hạn mức thì đổi
    thành LoiHanMuc cho dễ phân biệt.
    """
    if not tt.co_khoa():
        raise ValueError("Chưa có khóa API cho lượt gọi này")

    try:
        if tt.provider == CLAUDE:
            return _goi_claude(tt, prompt, max_tokens)
        return _goi_gemini(tt, prompt, json_mode)
    except Exception as e:
        if la_loi_han_muc(e):
            raise LoiHanMuc(
                f"{tt.ten_hien_thi} báo hết hạn mức hoặc hết tín dụng: {e}"
            ) from e
        raise


def _goi_gemini(tt: ThongTinAI, prompt: str, json_mode: bool) -> str:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=tt.api_key)
    cau_hinh = (
        types.GenerateContentConfig(response_mime_type="application/json")
        if json_mode else None
    )
    response = client.models.generate_content(
        model=tt.model, contents=prompt, config=cau_hinh
    )
    van_ban = response.text or ""
    ly_do = ""
    try:
        ly_do = str(response.candidates[0].finish_reason or "")
    except Exception:
        pass

    if not van_ban.strip():
        raise LoiDauRaThieu(
            "Gemini trả về rỗng"
            + (f" (dừng vì: {ly_do})" if ly_do else "")
            + ". Lô này không dùng được."
        )
    if "MAX_TOKENS" in ly_do.upper():
        raise LoiDauRaThieu(
            f"Gemini bị cắt giữa chừng ở {len(van_ban)} ký tự vì chạm trần token. "
            f"JSON cụt không bóc được, phải chia lô nhỏ hơn."
        )
    return van_ban


def _goi_claude(tt: ThongTinAI, prompt: str, max_tokens: int) -> str:
    """
    Dùng truyền phát (streaming) vì đầu ra của ta thường dài — cả lô 25 câu kèm
    lời giải — và yêu cầu không truyền phát với max_tokens lớn dễ hết giờ.

    Claude không có chế độ ép JSON như Gemini; ta để `boc_json()` gỡ rào ```json
    ở phía nhận.
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
