# -*- coding: utf-8 -*-
"""
Chuyển hàng loạt tệp .doc (Word cũ) sang .docx bằng LibreOffice.

Vì sao cần: thư viện python-docx chỉ đọc được .docx. Kho tài liệu thật có rất
nhiều tệp .doc từ thời Word 2003, chiếm tới 30% và nằm ngoài tầm với của mọi
công cụ trong dự án này.

Vì sao dùng LibreOffice chứ không dùng Word: đã thử điều khiển Word qua COM —
chuyển được tệp lẻ nhưng chạy hàng loạt thì treo, rất chậm và hay bật hộp thoại
ẩn. LibreOffice chạy chế độ headless, nhận nhiều tệp một lượt, không hỏi gì.

Điểm mấu chốt về tốc độ: gọi LibreOffice MỘT LẦN cho mỗi lô nhiều tệp thay vì
mỗi tệp một lần. Khởi động LibreOffice mất ~9 giây, nên gọi lẻ tốn 10s/tệp còn
gọi theo lô chỉ tốn 0,8s/tệp — nhanh gấp 12 lần.

Cách dùng:
    python scripts/chuyen_doi_doc.py <thư mục nguồn> [--ra <thư mục đích>]
                                     [--soffice <đường dẫn soffice.exe>]
                                     [--lo <số tệp mỗi lô>] [--thu <số tệp thử>]

Không có --ra thì tệp .docx được đặt cạnh tệp .doc gốc. Tệp gốc KHÔNG bị xóa
hay sửa; đã chuyển rồi thì lần chạy sau tự bỏ qua.
"""

import argparse
import os
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Những nơi LibreOffice thường nằm. Bản giải nén bằng `msiexec /a` không cần
# quyền Admin nên hay được đặt ở ổ khác.
NOI_TIM_SOFFICE = [
    r"E:\LibreOffice\program\soffice.exe",
    r"D:\LibreOffice\program\soffice.exe",
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
]


def tim_soffice(chi_dinh: str = "") -> str:
    if chi_dinh:
        if Path(chi_dinh).exists():
            return chi_dinh
        raise SystemExit(f"Không thấy LibreOffice tại: {chi_dinh}")
    for p in NOI_TIM_SOFFICE:
        if Path(p).exists():
            return p
    raise SystemExit(
        "Không tìm thấy LibreOffice. Tải bản .msi từ libreoffice.org rồi giải nén bằng:\n"
        "    msiexec /a <tệp.msi> /qn TARGETDIR=E:\\LibreOffice\n"
        "(cách này KHÔNG cần quyền Administrator)"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nguon", help="Thư mục chứa tệp .doc cần chuyển")
    ap.add_argument("--ra", default="", help="Thư mục đích (mặc định: đặt cạnh tệp gốc)")
    ap.add_argument("--soffice", default="", help="Đường dẫn soffice.exe")
    ap.add_argument("--lo", type=int, default=40, help="Số tệp mỗi lô")
    ap.add_argument("--thu", type=int, default=0, help="Chỉ chạy thử N tệp đầu")
    args = ap.parse_args()

    soffice = tim_soffice(args.soffice)
    nguon = Path(args.nguon)
    if not nguon.is_dir():
        raise SystemExit(f"Không thấy thư mục: {nguon}")

    print(f"LibreOffice: {soffice}")
    print(f"Nguồn      : {nguon}")

    # Gom theo thư mục cha: LibreOffice chỉ nhận MỘT --outdir cho mỗi lần gọi,
    # nên gom như vậy vừa giữ được cấu trúc thư mục vừa gọi được theo lô.
    theo_thu_muc = defaultdict(list)
    tong = 0
    bo_qua = 0
    for goc, _, tep in os.walk(str(nguon)):
        for ten in tep:
            if not ten.lower().endswith(".doc") or ten.startswith("~$"):
                continue
            p = Path(goc) / ten
            dich_dir = Path(args.ra) / p.parent.relative_to(nguon) if args.ra else p.parent
            if (dich_dir / (p.stem + ".docx")).exists():
                bo_qua += 1
                continue
            theo_thu_muc[dich_dir].append(p)
            tong += 1
            if args.thu and tong >= args.thu:
                break
        if args.thu and tong >= args.thu:
            break

    print(f"Cần chuyển : {tong} tệp trong {len(theo_thu_muc)} thư mục")
    if bo_qua:
        print(f"Bỏ qua     : {bo_qua} tệp (đã có bản .docx)")
    if not tong:
        print("Không có gì để làm.")
        return

    t0 = time.time()
    xong = 0
    loi = 0

    for dich_dir, ds_tep in theo_thu_muc.items():
        dich_dir.mkdir(parents=True, exist_ok=True)
        for i in range(0, len(ds_tep), args.lo):
            lo = ds_tep[i:i + args.lo]
            lenh = [soffice, "--headless", "--norestore", "--convert-to", "docx",
                    "--outdir", str(dich_dir)] + [str(p) for p in lo]
            try:
                subprocess.run(lenh, capture_output=True, timeout=60 * 30)
            except Exception as e:
                print(f"  Lô lỗi ({e}) — bỏ qua, đi tiếp")

            for p in lo:
                if (dich_dir / (p.stem + ".docx")).exists():
                    xong += 1
                else:
                    loi += 1

            troi = time.time() - t0
            da = xong + loi
            con = (tong - da) * (troi / max(1, da)) / 60
            print(f"  {da}/{tong}  (thành công {xong}, lỗi {loi})  còn ~{con:.0f} phút", flush=True)

    troi = time.time() - t0
    print("=" * 46)
    print(f"Chuyển thành công : {xong}")
    print(f"Thất bại          : {loi}")
    print(f"Thời gian         : {troi/60:.1f} phút ({troi/max(1,xong):.2f} giây/tệp)")
    print("\nTệp .doc gốc vẫn còn nguyên, không bị xóa hay sửa.")


if __name__ == "__main__":
    main()
