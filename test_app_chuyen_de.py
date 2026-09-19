# -*- coding: utf-8 -*-
"""
Kiểm thử app SOẠN CHUYÊN ĐỀ — dựng file Word thật rồi mở lại đo.

Không tin giá trị hàm trả về: hàm báo "đã in 4 phần" mà file chỉ có 3 thì báo
cáo đó chỉ là trang trí. Mọi khẳng định dưới đây đều đếm trên tệp .docx.

Phủ CẢ HAI loại đầu ra của app:
  CHUYEN_DE_BT  — đáp án phải dồn hết về Phần 4
  TAI_LIEU_HSG  — chia theo chuyên đề, phương án phải bị giấu ở phần đề
"""

import sys
from pathlib import Path

import docx

from app_chuyen_de.bo_dung.dung import dung_tai_lieu
from core.loai_dau_ra import CHUYEN_DE_BT, TAI_LIEU_HSG
from core.rewriter import RewrittenBook, RewrittenQuestionItem

RA = Path("app_chuyen_de/output")

# Câu 1-3 dễ, 4-5 trung bình, 6 khó, 7-8 truy được nguồn đề thi
CAU = [
    ("Tính giá trị của 2^3 + 3^2.", "Nhận biết", "A", "2^3 = 8, 3^2 = 9, tổng bằng 17.", ""),
    ("Tìm tập xác định của hàm số y = log(x - 1).", "Nhận biết", "B",
     "Điều kiện x - 1 > 0 nên x > 1.", ""),
    ("Rút gọn biểu thức 5^2 · 5^3.", "Nhận biết", "C",
     "Nhân cùng cơ số thì cộng số mũ: 5^5.", ""),
    ("Giải phương trình 2^x = 16.", "Thông hiểu", "A", "16 = 2^4 nên x = 4.", ""),
    ("Giải bất phương trình log2(x) < 3.", "Thông hiểu", "D", "0 < x < 8.", ""),
    ("Cho hình chóp S.ABCD có đáy là hình vuông cạnh a. Tìm m để thể tích bằng 2a^3.",
     "Vận dụng cao", "B",
     "Đặt t = 2^x > 0. Cần hai nghiệm dương phân biệt nên delta > 0, suy ra m > 2.", ""),
    ("Tập xác định của hàm số y = log2(3 - x) là gì?", "Thông hiểu", "A",
     "Điều kiện 3 - x > 0 nên x < 3.", "Đề thi tốt nghiệp THPT 2015"),
    ("Cho log2(a) = 3. Tính log2(4a).", "Thông hiểu", "C",
     "log2(4a) = log2(4) + log2(a) = 2 + 3 = 5.", "Đề thi tốt nghiệp THPT 2021"),
]


def dung_sach(loai: str) -> RewrittenBook:
    ds = []
    for i, (nd, muc, dap, lg, nguon) in enumerate(CAU, 1):
        q = RewrittenQuestionItem(index=i)
        q.new_content = nd
        q.level = muc
        q.correct_answer = dap
        q.solution_method1 = lg
        q.title = nguon
        q.new_options = ["A. 17", "B. 4", "C. 5^5", "D. 8"]
        q.trap_warning = "Bẫy hay mắc ở câu %d." % i
        ds.append(q)

    return RewrittenBook(
        original_title="Mu va logarit", new_title="Hàm số mũ và logarit",
        subtitle="", author_note="", chapter_summary="",
        theory_section="Định nghĩa hàm số mũ\nHàm số mũ có dạng y = a^x với a > 0, a khác 1.",
        questions=ds, loai_dau_ra=loai, cap_hoc="THPT",
    )


class Soat:
    def __init__(self, ten):
        self.loi = 0
        print("\n" + ten)
        print("-" * 78)

    def __call__(self, ten: str, ok: bool, them: str = ""):
        print("  %-5s %s" % ("ĐẠT" if ok else "HỎNG", ten))
        if them:
            print("        " + them)
        if not ok:
            self.loi += 1


def doc_docx(p: Path):
    d = docx.Document(str(p))
    return d, [x.text.strip() for x in d.paragraphs if x.text.strip()]


def kiem_chuyen_de() -> int:
    duong = RA / "Chuyên Đề Bài Tập" / "Test_Chuyen_De.docx"
    dung_tai_lieu(dung_sach(CHUYEN_DE_BT), duong)
    d, dong = doc_docx(duong)
    k = Soat("CHUYEN_DE_BT — khuôn bốn phần")

    mong = ["PHẦN 1. LÝ THUYẾT VÀ VÍ DỤ MINH HỌA",
            "PHẦN 2. BÀI TẬP TỰ LUYỆN",
            "PHẦN 3. CÂU HỎI TỪ ĐỀ THI",
            "PHẦN 4. HƯỚNG DẪN VÀ ĐÁP ÁN"]
    vi = [next((i for i, t in enumerate(dong) if t == m), -1) for m in mong]
    k("Có đủ bốn phần", all(v >= 0 for v in vi))
    k("Bốn phần đúng thứ tự", vi == sorted(vi), str(vi))

    # ĐIỀU QUAN TRỌNG NHẤT của loại này
    if vi[3] > 0:
        truoc = dong[:vi[3]]
        lo = [t for t in truoc if t.startswith(("Đáp án:", "Đáp án ")) or "Đáp án đúng" in t]
        k("Không lộ đáp án trước Phần 4", not lo, " | ".join(lo[:3]))
        giai = [i for i, t in enumerate(truoc) if t.startswith("Giải:")]
        k("Lời giải chỉ nằm ở ví dụ của Phần 1", all(i < vi[1] for i in giai),
          "có %d dòng 'Giải:'" % len(giai))

    cau_t = [t for t in dong if t.startswith("Câu T")]
    k("Phần 3 đánh số 'Câu T' kèm thẻ năm",
      bool(cau_t) and all("[" in t and "]" in t for t in cau_t),
      " | ".join(t[:44] for t in cau_t))
    k("Chỉ câu truy được nguồn mới vào Phần 3", len(cau_t) == 2,
      "có %d câu" % len(cau_t))

    bang3 = [b for b in d.tables if len(b.columns) == 3]
    k("Phần 4 dùng bảng ba cột", len(bang3) >= 1, "%d bảng ba cột" % len(bang3))
    if bang3:
        k("Tiêu đề bảng đúng quy cách",
          [c.text.strip() for c in bang3[0].rows[0].cells] == ["Câu", "Đáp án", "Hướng dẫn giải"])
        so = [int(r.cells[0].text.strip()[4:]) for r in bang3[0].rows[1:]
              if r.cells[0].text.strip().startswith("Câu ")
              and r.cells[0].text.strip()[4:].isdigit()]
        k("Bảng đáp án chạy đúng thứ tự tăng dần", so == sorted(so), str(so))

    print("        Tệp: %s" % duong)
    return k.loi


def kiem_hsg() -> int:
    duong = RA / "Tài Liệu HSG" / "Test_HSG.docx"
    dung_tai_lieu(dung_sach(TAI_LIEU_HSG), duong)
    d, dong = doc_docx(duong)
    k = Soat("TAI_LIEU_HSG — chia theo chuyên đề")

    tieu_de = [t for t in dong if t.startswith("CHUYÊN ĐỀ ")]
    k("Có chia theo chuyên đề", len(tieu_de) >= 2, " | ".join(t[:44] for t in tieu_de))

    muc_luc = [t for t in dong if t.startswith("Chuyên đề ")]
    k("Mục lục liệt kê đủ chuyên đề", len(muc_luc) == len(tieu_de),
      "%d mục lục / %d tiêu đề" % (len(muc_luc), len(tieu_de)))

    # Phương án PHẢI bị giấu ở phần đề — đề HSG là tự luận
    vi_hd = next((i for i, t in enumerate(dong) if t == "HƯỚNG DẪN GIẢI"), -1)
    k("Có phần hướng dẫn giải riêng", vi_hd > 0)
    if vi_hd > 0:
        lo = [t for t in dong[:vi_hd] if t.startswith(("A. ", "B. ", "C. ", "D. "))]
        k("Phần đề KHÔNG lộ phương án", not lo, " | ".join(lo[:3]))

    # Số hiệu bài phải liên tục và khớp giữa hai phần
    so = [int(t.split()[1].rstrip(".")) for t in dong
          if t.startswith("Bài ") and t.split()[1].rstrip(".").isdigit()]
    de, hd = so[:len(CAU)], so[len(CAU):]
    k("Số hiệu bài phần đề liên tục 1..%d" % len(CAU),
      de == list(range(1, len(CAU) + 1)), str(de))
    k("Số hiệu phần hướng dẫn khớp phần đề",
      hd == list(range(1, len(CAU) + 1)), str(hd))

    print("        Tệp: %s" % duong)
    return k.loi


def kiem_the_thuc() -> int:
    """Lề Nghị định 30 phải đo trên TỆP THẬT, không tin tham số truyền vào."""
    duong = RA / "Chuyên Đề Bài Tập" / "Test_Chuyen_De.docx"
    d = docx.Document(str(duong))
    s = d.sections[0]
    k = Soat("THỂ THỨC NGHỊ ĐỊNH 30 (đo trên tệp)")
    mm = lambda emu: round(emu / 36000)
    k("Lề trái 30mm để đóng gáy", mm(s.left_margin) == 30, "đo được %dmm" % mm(s.left_margin))
    k("Lề phải 15mm", mm(s.right_margin) == 15, "đo được %dmm" % mm(s.right_margin))
    k("Khổ A4 rộng 210mm", mm(s.page_width) == 210, "đo được %dmm" % mm(s.page_width))
    return k.loi


if __name__ == "__main__":
    loi = kiem_chuyen_de() + kiem_hsg() + kiem_the_thuc()
    print()
    print("=" * 78)
    print("KẾT QUẢ: %s" % ("ĐẠT" if loi == 0 else "%d LỖI" % loi))
    sys.exit(1 if loi else 0)
