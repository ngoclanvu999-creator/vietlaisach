# -*- coding: utf-8 -*-
"""
Đồng bộ skill giữa repo và thư mục cá nhân của Claude Code.

Vì sao cần: skill phải nằm TRONG repo thì mới theo lên máy chủ triển khai
(`~/.claude/skills` không tồn tại ở đó). Nhưng khi làm việc trong chat thì
Claude Code lại chỉ đọc `~/.claude/skills`. Hai nơi dễ trôi khác nhau, mà skill
chính là chuẩn nghiệp vụ nên lệch nhau là ra hai kết quả khác nhau.

    python scripts/dong_bo_skill.py            # xem chỗ nào lệch
    python scripts/dong_bo_skill.py --ve-repo  # lấy bản cá nhân làm chuẩn
    python scripts/dong_bo_skill.py --ra-may   # lấy bản trong repo làm chuẩn
"""
import hashlib
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent / "skills"
CA_NHAN = Path.home() / ".claude" / "skills"


def bam(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()[:10]


def liet_ke(goc: Path) -> dict:
    if not goc.is_dir():
        return {}
    return {p.relative_to(goc).as_posix(): p
            for p in goc.rglob("*") if p.is_file()}


def so_sanh():
    a, b = liet_ke(REPO), liet_ke(CA_NHAN)
    chi_repo = sorted(set(a) - set(b))
    chi_ca_nhan = sorted(set(b) - set(a))
    khac = sorted(k for k in set(a) & set(b) if bam(a[k]) != bam(b[k]))
    return chi_repo, chi_ca_nhan, khac


def sao_chep(tu: Path, den: Path):
    n = 0
    for p in tu.rglob("*"):
        if not p.is_file():
            continue
        dich = den / p.relative_to(tu)
        dich.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dich)
        n += 1
    return n


def main():
    cd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cd == "--ve-repo":
        print(f"Đã chép {sao_chep(CA_NHAN, REPO)} tệp từ máy cá nhân vào repo.")
        return
    if cd == "--ra-may":
        print(f"Đã chép {sao_chep(REPO, CA_NHAN)} tệp từ repo ra máy cá nhân.")
        return

    chi_repo, chi_ca_nhan, khac = so_sanh()
    if not (chi_repo or chi_ca_nhan or khac):
        print("Hai nơi khớp nhau hoàn toàn.")
        return
    for nhan, ds in (("Chỉ có trong repo", chi_repo),
                     ("Chỉ có trên máy cá nhân", chi_ca_nhan),
                     ("Khác nội dung", khac)):
        if ds:
            print(f"\n{nhan} ({len(ds)}):")
            for k in ds:
                print("   ", k)
    print("\nDùng --ve-repo hoặc --ra-may để đồng bộ.")


if __name__ == "__main__":
    main()
