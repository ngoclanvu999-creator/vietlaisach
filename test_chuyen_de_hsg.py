# -*- coding: utf-8 -*-
"""
Kiểm thử bộ phân loại chuyên đề HSG.

Mọi câu dưới đây là đề bài THẬT chép từ 13 đề HSG Toán 11 chủ dự án chỉ định,
không phải ví dụ tự nghĩ. Phân loại đúng trên ví dụ tự nghĩ là vô nghĩa: mẫu do
chính mình viết thì bao giờ cũng khớp mẫu do chính mình đặt.
"""

import sys

from core.chuyen_de_hsg import (
    DANH_MUC, MA_KHAC, NHOM_A, NHOM_B, NHOM_C, TEN,
    cham_diem, cho_vong_thi, danh_sach, gom_theo_chuyen_de, phan_loai,
)

# (đề bài thật, chuyên đề đúng, nguồn)
CA = [
    ("Cho hình chóp S.ABCD có đáy ABCD là hình thang cân (AB // CD) nội tiếp "
     "đường tròn tâm O và góc SBA = góc SCA = 90 độ. Gọi M là trung điểm của "
     "cạnh SA. Chứng minh rằng MO vuông góc (ABCD).",
     "KHONG_GIAN", "Nghệ An 2018-2019"),

    ("Cho hình hộp ABCD.A'B'C'D'. Gọi G là trọng tâm của tam giác BC'D. Xác định "
     "thiết diện của hình hộp khi cắt bởi mặt phẳng (ABG). Thiết diện đó là hình gì?",
     "KHONG_GIAN", "Quảng Bình 2017-2018"),

    ("Giải phương trình cos2x + 7cos3x - sin2x + 7sinx = 8.",
     "LUONG_GIAC", "Nghệ An 2018-2019"),

    ("Cho dãy số (un) thỏa mãn u1 = 1, u(n+1) = 2un/(un + 4) với n >= 1. "
     "Tìm công thức số hạng tổng quát un của dãy số đã cho.",
     "DAY_SO", "Quảng Ngãi 2018-2019"),

    ("Một tam giác vuông có chu vi bằng 3a, và 3 cạnh lập thành một cấp số cộng. "
     "Tính độ dài ba cạnh của tam giác theo a.",
     "DAY_SO", "Tân Yên - Bắc Giang 2019-2020"),

    ("Gọi S là tập hợp tất cả các số tự nhiên gồm 4 chữ số đôi một khác nhau được "
     "chọn từ các số 1, 2, 3, 4, 5, 6, 7, 8, 9. Lấy ngẫu nhiên một số từ S, tính "
     "xác suất để số được chọn là số chia hết cho 11.",
     "TO_HOP", "Nghệ An 2018-2019"),

    ("Mỗi lượt, ta gieo một con súc sắc (loại 6 mặt, cân đối) và một đồng xu "
     "(cân đối). Tính xác suất để trong 3 lượt gieo như vậy, có ít nhất một lượt "
     "gieo được kết quả con súc sắc xuất hiện mặt 1 chấm.",
     "TO_HOP", "Hà Tĩnh 2016-2017"),

    ("Cho ba số thực a, b, c thỏa mãn a^3 + b^3 + c^3 - 3abc = 32. Tìm giá trị "
     "nhỏ nhất của biểu thức P.",
     "BAT_DANG_THUC", "Nghệ An 2018-2019"),

    ("Giải và biện luận bất phương trình sau theo tham số m.",
     "PHUONG_TRINH", "Phú Yên 2018-2019"),

    ("Trong mặt phẳng với hệ trục tọa độ Oxy, cho hình chữ nhật ABCD có AB = 2BC. "
     "Gọi M là trung điểm của đoạn AB và G là trọng tâm tam giác ACD. Viết phương "
     "trình đường thẳng AD.",
     "OXY", "Nghệ An 2018-2019"),

    ("Tính giới hạn L = lim x tiến tới 0 của biểu thức căn bậc hai của 1 + 2x.",
     "GIOI_HAN", "Hà Tĩnh 2016-2017"),

    ("Cho khai triển nhị thức Newton (x^2 - x)^n = a0 + a1x + a2x^2 + ... + a2n "
     "x^2n. Tìm hệ số a10.",
     "NHI_THUC", "Vĩnh Phúc 2018-2019"),

    ("Tìm tất cả các số nguyên dương n sao cho 2^2n + 3^n + 7 là một số chính phương.",
     "SO_HOC", "Quảng Bình 2017-2018"),

    ("Cho hàm số y = x^3 - 3x^2 + x + m có đồ thị là (C). Tìm tất cả các giá trị "
     "của m để tiếp tuyến của đồ thị (C) tại điểm M chắn hai trục tọa độ một tam "
     "giác có diện tích bằng 2.",
     "DAO_HAM", "Lý Thái Tổ - Bắc Ninh 2017-2018"),

    ("Cho hàm số f liên tục trên R, thỏa mãn f(2020) = 2019 và f(f(f(f(x)))).f(x) "
     "= 1 với mọi x. Hãy tính f(2018).",
     "PHUONG_TRINH_HAM", "Phú Yên 2018-2019"),

    ("Trên mặt phẳng tọa độ, phép tịnh tiến theo vectơ v(3;1) biến đường thẳng d "
     "thành đường thẳng d', biết d' có phương trình 2x - y = 0. Khi đó d có "
     "phương trình là gì?",
     "BIEN_HINH", "Tân Yên - Bắc Giang 2019-2020"),

    ("Cho hình thang ABCD có hai cạnh đáy là AB và CD thỏa mãn AB = 3CD. Phép vị "
     "tự biến điểm A thành điểm C và biến điểm B thành điểm D có tỉ số k là bao nhiêu?",
     "BIEN_HINH", "Tân Yên - Bắc Giang 2019-2020"),
]

# Những câu PHẢI không bị xếp bừa — bẫy đã gặp thật khi dựng bộ phân loại
BAY = [
    ("Học sinh giỏi không được sử dụng tài liệu và máy tính cầm tay.",
     "chữ 'sinh' trong 'học sinh' không được tính là hàm sin"),
    ("Cho tứ diện ABCD. Gọi M, N là trung điểm AB và AC. Thiết diện tạo bởi mặt "
     "phẳng (MNE) và tứ diện ABCD, biết EF song song BC.",
     "chữ 'song' không được tính là tên hình chóp S.ABC"),
]


def kiem_phan_loai() -> int:
    loi = 0
    print("PHAN LOAI DE BAI THAT")
    print("-" * 92)
    for de, mong_doi, nguon in CA:
        that = phan_loai(de)
        ok = that == mong_doi
        loi += not ok
        print("  %-4s %-18s %s" % ("OK" if ok else "SAI", that, nguon))
        if not ok:
            print("       mong doi: %s" % mong_doi)
            d = {k: v for k, v in cham_diem(de).items() if v}
            print("       diem    : %s" % sorted(d.items(), key=lambda kv: -kv[1]))
    print()
    return loi


def kiem_bay() -> int:
    loi = 0
    print("BAY DA GAP THAT")
    print("-" * 92)
    for de, vi_sao in BAY:
        d = cham_diem(de)
        # Câu bẫy thứ nhất không thuộc chuyên đề nào; câu thứ hai là hình không
        # gian thật, chỉ cần KHÔNG phải nhờ chữ "song" mà ra.
        xau = d["LUONG_GIAC"] if "sinh" in de else 0
        ok = xau == 0
        loi += not ok
        print("  %-4s %s" % ("OK" if ok else "SAI", vi_sao))
    # "song song" không được kéo câu vào hình không gian qua mẫu tên hình chóp
    chi_song = cham_diem("Hai đường thẳng song song với nhau.")
    ok = chi_song["KHONG_GIAN"] == 0
    loi += not ok
    print("  %-4s 'song song' don le khong tu thanh hinh khong gian" % ("OK" if ok else "SAI"))
    print()
    return loi


def kiem_danh_muc() -> int:
    loi = 0
    print("DANH MUC VA NHOM")
    print("-" * 92)
    tong = sum(t for _, _, _, _, t in DANH_MUC)
    ok = abs(tong - 100.0) < 0.5
    loi += not ok
    print("  %-4s tong ti trong = %.1f%% (phai xap xi 100)" % ("OK" if ok else "SAI", tong))

    a, b, c = danh_sach(NHOM_A), danh_sach(NHOM_B), danh_sach(NHOM_C)
    ok = (len(a), len(b), len(c)) == (7, 2, 4)
    loi += not ok
    print("  %-4s nhom A/B/C = %d/%d/%d (do duoc: 7/2/4)"
          % ("OK" if ok else "SAI", len(a), len(b), len(c)))

    ok = cho_vong_thi("truong") == a and len(cho_vong_thi("tinh")) == 9 \
        and len(cho_vong_thi("quoc gia")) == 13
    loi += not ok
    print("  %-4s vong thi sau bao gom vong thi truoc" % ("OK" if ok else "SAI"))
    print()
    return loi


def kiem_gom() -> int:
    """Gom phải giữ đúng thứ tự đo được, chuyên đề hay ra nhất đứng trước."""
    class Q:
        def __init__(self, t):
            self.new_content = t

    ds = [Q(de) for de, _, _ in CA]
    nhom = gom_theo_chuyen_de(ds)
    thu_tu = list(nhom)
    mong_doi_dau = "KHONG_GIAN"      # 12/13 đề, 19,8% điểm
    ok = thu_tu[0] == mong_doi_dau
    print("GOM THEO CHUYEN DE")
    print("-" * 92)
    print("  %-4s chuyen de dau tien = %s" % ("OK" if ok else "SAI", thu_tu[0]))
    for ma in thu_tu:
        print("       %-18s %d cau   %s" % (ma, len(nhom[ma]), TEN[ma]))
    print()
    return 0 if ok else 1


if __name__ == "__main__":
    loi = kiem_phan_loai() + kiem_bay() + kiem_danh_muc() + kiem_gom()
    print("=" * 92)
    print("KET QUA: %s" % ("DAT" if loi == 0 else "%d LOI" % loi))
    sys.exit(1 if loi else 0)
