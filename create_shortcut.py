# -*- coding: utf-8 -*-
"""
Tạo lối tắt ra Desktop cho phần mềm, kèm icon riêng.

VÌ SAO TỆP NÀY DÀI HƠN TƯỞNG. Thư mục dự án có dấu tiếng Việt
("D:\\tool viếtt ssách") mà `WScript.Shell` — cách tạo lối tắt thông dụng nhất
trên Windows — lại là giao diện COM kiểu ANSI. Hệ quả đo được ngày 19/09/2026:

  - Gán `TargetPath` là đường dẫn tiếng Việt  -> lỗi "Value does not fall
    within the expected range", không tạo được lối tắt.
  - Gán `Arguments` / `WorkingDirectory` tiếng Việt -> KHÔNG báo lỗi, nhưng đọc
    ngược lại thì "viếtt" đã thành "vi?tt". Ký tự "ế" không có trong bảng mã
    cp1252 nên rụng mất, còn "á" thì còn. Hỏng ngầm, tệ hơn hỏng ra mặt.
  - Tên ngắn 8.3 không cứu được: ổ đĩa này tắt sinh tên ngắn.

Cách đi được: tạo một ĐIỂM NỐI (junction) tên thuần ASCII trỏ vào thư mục dự
án, rồi cho lối tắt đi qua đó. Mọi đường dẫn đưa cho Windows đều ASCII nên
không còn chỗ nào phải chuyển bảng mã.

Điểm nối không chiếm chỗ đĩa, xóa lúc nào cũng được bằng `rmdir` và không đụng
gì tới thư mục thật.
"""

import os
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
HOME = Path(os.environ.get("USERPROFILE", "C:\\Users\\Default"))
DESKTOP = HOME / "Desktop"

TEN_HIEN = "Biên Soạn Sách Pro.lnk"       # tên người dùng nhìn thấy
TEN_TAM = "_BienSoanSachPro_tam.lnk"      # tên ASCII lúc tạo, đổi lại sau
TEN_CU = "Bien_Soan_Sach_Pro.lnk"         # lối tắt bản cũ, dọn đi
NOI_ASCII = HOME / "BienSoanSachPro"      # điểm nối tên thuần ASCII


def _thuan_ascii(p: Path) -> bool:
    return str(p).isascii()


def _loi_di_ascii() -> Path:
    """
    Đường dẫn thuần ASCII tới thư mục dự án. Nếu bản thân nó đã ASCII thì dùng
    luôn, khỏi tạo thêm gì.
    """
    if _thuan_ascii(BASE_DIR):
        return BASE_DIR

    if NOI_ASCII.exists():
        if (NOI_ASCII / "Chay_Ung_Dung.bat").exists():
            return NOI_ASCII
        print(f"[!] {NOI_ASCII} đã tồn tại nhưng không trỏ đúng thư mục dự án.")
        return BASE_DIR

    subprocess.run(["cmd", "/c", "mklink", "/J", str(NOI_ASCII), str(BASE_DIR)],
                   capture_output=True, text=True, errors="replace")
    if (NOI_ASCII / "Chay_Ung_Dung.bat").exists():
        print(f"[*] Đã tạo điểm nối ASCII: {NOI_ASCII}")
        return NOI_ASCII

    print("[!] Không tạo được điểm nối; lối tắt có thể hỏng vì đường dẫn có dấu.")
    return BASE_DIR


def _bao_dam_co_icon(goc: Path) -> str:
    ico = goc / "static" / "icon_tool.ico"
    if not (BASE_DIR / "static" / "icon_tool.ico").exists():
        try:
            subprocess.run([sys.executable, str(BASE_DIR / "scripts" / "tao_icon.py")],
                           capture_output=True, text=True, timeout=120)
        except Exception as e:
            print(f"[!] Không sinh được icon riêng ({e}), dùng icon hệ thống.")
    return f"{ico},0" if ico.exists() else "shell32.dll,43"


def _chay_ps(noi_dung: str) -> str:
    """
    Chạy PowerShell qua TỆP .ps1 có BOM UTF-8, không qua -Command.

    Truyền thẳng bằng -Command thì đường dẫn tiếng Việt hỏng ngay ở dòng lệnh;
    có BOM thì PowerShell biết chắc bảng mã chứ không phải đoán.
    """
    tep = BASE_DIR / "_tao_loi_tat.ps1"
    tep.write_text(noi_dung, encoding="utf-8-sig")
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(tep)],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
        return (r.stderr or "").strip()
    finally:
        try:
            tep.unlink()
        except Exception:
            pass


def main() -> int:
    if not (BASE_DIR / "Chay_Ung_Dung.bat").exists():
        print("[!] Không thấy Chay_Ung_Dung.bat. Dừng lại.")
        return 1
    if not DESKTOP.is_dir():
        print(f"[!] Không thấy thư mục Desktop tại {DESKTOP}. Dừng lại.")
        return 1

    goc = _loi_di_ascii()
    target = goc / "Chay_Ung_Dung.bat"
    icon = _bao_dam_co_icon(goc)

    for cu in (DESKTOP / TEN_CU, DESKTOP / TEN_HIEN, DESKTOP / TEN_TAM):
        if cu.exists():
            try:
                cu.unlink()
            except Exception:
                pass

    tam = DESKTOP / TEN_TAM
    loi = _chay_ps(f"""
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut('{tam}')
$s.TargetPath = '{target}'
$s.WorkingDirectory = '{goc}'
$s.IconLocation = '{icon}'
$s.Description = 'Phan mem Bien Soan Sach Toan - Vat Ly Pro'
$s.Save()
""")

    if not tam.exists():
        print(f"[!] Lỗi tạo lối tắt: {loi[:300]}")
        return 1

    # Đổi sang tên tiếng Việt bằng Python — Python xử lý tên tệp Unicode đúng,
    # còn WScript.Shell thì không tạo nổi tệp .lnk có dấu.
    cuoi = DESKTOP / TEN_HIEN
    try:
        tam.replace(cuoi)
    except Exception as e:
        print(f"[!] Không đổi được tên hiển thị ({e}), giữ tên {TEN_TAM}.")
        cuoi = tam

    print(f"[OK] Đã tạo lối tắt: {cuoi}")
    print(f"[OK] Trỏ tới      : {target}")
    print(f"[OK] Icon         : {icon}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
