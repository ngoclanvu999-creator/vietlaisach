import os
import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# CHẾ ĐỘ CHẠY & BẢO MẬT
# ---------------------------------------------------------------------------
# LOCAL_MODE = True: ứng dụng chạy trên máy cá nhân, được phép duyệt thư mục
#   bất kỳ trên ổ đĩa và mở Explorer.
# LOCAL_MODE = False (mặc định khi deploy Linux/Cloud): chỉ được phép đọc các
#   tệp do người dùng tải lên nằm trong thư mục input/, tuyệt đối không cho
#   phép liệt kê hệ thống tệp của máy chủ.
LOCAL_MODE = os.environ.get(
    "LOCAL_MODE",
    "1" if sys.platform == "win32" else "0"
).strip() == "1"

# Nếu đặt biến môi trường APP_ACCESS_TOKEN, mọi lệnh gọi /api/... bắt buộc phải
# kèm token (header "X-Access-Token" hoặc tham số ?token=...). Để trống thì tắt.
ACCESS_TOKEN = os.environ.get("APP_ACCESS_TOKEN", "").strip()
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
CONFIG_FILE = BASE_DIR / "app_settings.json"

INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

DEFAULT_CONFIG = {
    # Khóa chỉ được lưu ở đây khi chạy trên MÁY CÁ NHÂN (LOCAL_MODE).
    # Trên Web mỗi người dán khóa của riêng mình, máy chủ không giữ.
    # Chỉ còn Claude: chủ dự án chốt bỏ hẳn Gemini ngày 19/09/2026.
    "claude_api_key": "",
    "claude_model": "claude-sonnet-5",
    "default_subject": "toan",  # 'toan' or 'vatly'
    "default_add_count": 2,
    "default_rewrite_level": "medium",  # 'light', 'medium', 'deep'
    "enable_casio": True,
    "enable_traps": True,
    "enable_summary_box": True,
    "enable_dual_solutions": True,
    "output_format": "a4"  # 'a4' or 'b5'
}

def load_settings() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                config = DEFAULT_CONFIG.copy()
                config.update(data)
                return config
        except Exception:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

def save_settings(settings: dict) -> dict:
    current = load_settings()
    current.update(settings)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(current, f, ensure_ascii=False, indent=2)
    return current
