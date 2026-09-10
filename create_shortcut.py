import os
import sys
from pathlib import Path
import subprocess

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

base_dir = Path(__file__).resolve().parent
desktop = Path(os.environ.get("USERPROFILE", "C:\\Users\\Default")) / "Desktop"
shortcut_path = desktop / "Bien_Soan_Sach_Pro.lnk"
target_bat = base_dir / "Chay_Ung_Dung.bat"

ps_script = f"""
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut('{str(shortcut_path)}')
$s.TargetPath = '{str(target_bat)}'
$s.WorkingDirectory = '{str(base_dir)}'
$s.Description = 'Phan Mem Bien Soan Sach Toan - Vat Ly Pro'
$s.IconLocation = 'shell32.dll,43'
$s.Save()
"""

try:
    res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True, encoding="utf-8")
    if shortcut_path.exists():
        print(f"[OK] Đã cập nhật thành công shortcut tại: {shortcut_path}")
    else:
        print(f"[!] Lỗi tạo shortcut: {res.stderr}")
except Exception as e:
    print(f"[!] Lỗi: {e}")
