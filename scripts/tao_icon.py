# -*- coding: utf-8 -*-
"""
Tạo tệp icon cho phần mềm.

Trước đây lối tắt ngoài Desktop dùng icon mặc định của Windows
(`shell32.dll,43`) nên nhìn không khác gì mọi thư mục khác.

Nguyên tắc vẽ: icon phải ĐỌC ĐƯỢC Ở 16 PIXEL. Cỡ đó chỉ còn nhận ra hình khối
lớn và độ tương phản, mọi chi tiết nhỏ đều nát. Vì vậy chỉ dùng ba mảng: nền
xanh đậm, quyển sách trắng mở, và một dấu căn vàng — bỏ hết râu ria.

Vẽ ở 1024px rồi thu nhỏ để cạnh mượt, nhúng đủ các cỡ Windows cần.
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw

GOC = Path(__file__).resolve().parent.parent
RA_ICO = GOC / "static" / "icon_tool.ico"
RA_PNG = GOC / "static" / "icon_tool.png"

N = 1024
XANH = (26, 54, 93)          # COLOR_PRIMARY của tài liệu Word, cho đồng bộ
XANH_NHAT = (44, 82, 130)
TRANG = (252, 252, 250)
XAM = (203, 213, 224)
VANG = (214, 158, 46)


def _bo_tron(d: ImageDraw.ImageDraw):
    """
    Nền bo góc, MỘT MÀU.

    Bản đầu có dải sáng hai tông cho đỡ phẳng, nhưng thu xuống 48px thì chỗ
    giao nhau thành một đường cong kỳ quặc. Icon nhỏ cần tương phản, không cần
    hiệu ứng.
    """
    d.rounded_rectangle([0, 0, N, N], radius=int(N * 0.22), fill=XANH)


def _quyen_sach(d: ImageDraw.ImageDraw):
    """
    Quyển sách mở: hai trang hình thang chụm vào gáy vàng ở giữa.

    Bản đầu có thêm mấy dòng kẻ giả làm chữ trên trang phải. Thu xuống 16px
    chúng nhoè thành một mảng xám khiến cả icon thành cục mờ, nên bỏ hẳn —
    hình khối lớn và tương phản mạnh mới sống sót ở cỡ nhỏ.

    Sách cũng được phóng to hơn bản đầu để chiếm gần hết khung.
    """
    tren, duoi = int(N * 0.30), int(N * 0.76)
    giua = N // 2
    trai, phai = int(N * 0.10), int(N * 0.90)
    vong = int(N * 0.06)      # mép ngoài võng xuống cho ra dáng sách mở

    d.polygon([(trai, tren + vong), (giua - int(N * 0.025), tren),
               (giua - int(N * 0.025), duoi), (trai, duoi - vong)], fill=TRANG)
    d.polygon([(phai, tren + vong), (giua + int(N * 0.025), tren),
               (giua + int(N * 0.025), duoi), (phai, duoi - vong)], fill=XAM)
    d.rectangle([giua - int(N * 0.030), tren, giua + int(N * 0.030), duoi], fill=VANG)


def _dau_can(d: ImageDraw.ImageDraw):
    """
    Dấu căn trên trang trái — thứ nói ngay đây là phần mềm Toán.

    Nét dày hẳn lên so với bản đầu: nét mảnh thu xuống 32px là mất tăm.
    """
    day = int(N * 0.052)
    x, y = int(N * 0.155, ) , int(N * 0.575)
    d.line([(x, y), (x + int(N * 0.055), y + int(N * 0.095))], fill=XANH, width=day)
    d.line([(x + int(N * 0.055), y + int(N * 0.095)),
            (x + int(N * 0.135), y - int(N * 0.135))], fill=XANH, width=day)
    d.line([(x + int(N * 0.135), y - int(N * 0.135)),
            (x + int(N * 0.30), y - int(N * 0.135))], fill=XANH, width=day)


def main() -> int:
    anh = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(anh)
    _bo_tron(d)
    _quyen_sach(d)
    _dau_can(d)

    RA_ICO.parent.mkdir(parents=True, exist_ok=True)
    anh.resize((512, 512), Image.LANCZOS).save(RA_PNG)

    co = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    anh.save(RA_ICO, format="ICO", sizes=co)

    print("Đã tạo:", RA_ICO)
    print("        ", RA_PNG)
    print("Cỡ nhúng:", ", ".join("%dx%d" % c for c in co))
    return 0


if __name__ == "__main__":
    sys.exit(main())
