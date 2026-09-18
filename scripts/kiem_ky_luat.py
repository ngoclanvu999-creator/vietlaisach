# -*- coding: utf-8 -*-
"""
Kiểm kỷ luật nội bộ của dự án — chạy được, không phải điều lệ treo tường.

VÌ SAO CÓ TỆP NÀY. Dự án gộp chín loại đầu ra vào một công cụ. Gộp thì tiết
kiệm được bốn phần năm công sức (8.319 dòng dùng chung / 1.950 dòng riêng),
nhưng đổi lại một lỗi có thể giết cả chín loại cùng lúc — đã xảy ra thật: một
dấu backtick không đóng trong app.js làm chết toàn bộ giao diện.

Gộp mà mỗi loại có lưới an toàn riêng thì AN TOÀN HƠN tách. Gộp mà không có
lưới thì mỗi lần sửa là một lần đánh cược. Tệp này là lưới đó.

    python scripts/kiem_ky_luat.py

Mỗi luật in ra ĐẠT / HỎNG kèm số đo thật. Thoát khác 0 khi có luật hỏng, để
cắm được vào việc kiểm trước khi đẩy mã.
"""

import os
import re
import sys
from pathlib import Path
from typing import Callable, List, Tuple

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

# Mô-đun lõi PHẢI MÙ về loại đầu ra: chúng chỉ biết bóc tách, làm sạch, gọi AI.
# Ngày nào chữ "GIAO_AN" lọt vào parser.py là ngày ranh giới bắt đầu nhòe, và
# từ đó sửa loại này sẽ làm hỏng loại kia.
LOI_MU = [
    "core/parser.py",
    "core/math_engine.py",
    "core/ai_provider.py",
    "core/ai_namer.py",
    "core/theory_bank.py",
]

# Những mô-đun ĐƯỢC PHÉP biết tên loại đầu ra, vì việc của chúng đúng là điều
# phối theo loại. Ghi ra đây để danh sách trên không bị nới lỏng dần.
DUOC_BIET_LOAI = [
    "core/loai_dau_ra.py",    # chính là sổ đăng ký
    "core/skill_loader.py",   # bảng tra loại -> skill
    "core/exporter.py",       # chỗ rẽ nhánh
    "core/trang_tri.py",      # giáo án mọi cấp đều không trang trí
    "app.py",
]


class KetQua:
    def __init__(self):
        self.dat = 0
        self.hong: List[str] = []

    def ghi(self, ten: str, ok: bool, chi_tiet: str = ""):
        print("  %-5s %s" % ("ĐẠT" if ok else "HỎNG", ten))
        if chi_tiet:
            for d in chi_tiet.splitlines():
                print("        " + d)
        if ok:
            self.dat += 1
        else:
            self.hong.append(ten)


def doc(p: str) -> str:
    f = GOC / p
    return f.read_text(encoding="utf-8", errors="ignore") if f.exists() else ""


# ---------------------------------------------------------------------------
# NHÓM 1 — Lõi dùng chung phải mù về loại đầu ra
# ---------------------------------------------------------------------------

def kl1(kq: KetQua):
    from core.loai_dau_ra import DANH_SACH

    pham = []
    for tep in LOI_MU:
        nd = doc(tep)
        for ma in DANH_SACH:
            for m in re.finditer(r"\b%s\b" % re.escape(ma), nd):
                dong = nd[: m.start()].count("\n") + 1
                pham.append("%s:%d nhắc %s" % (tep, dong, ma))
    kq.ghi("KL1 · Lõi dùng chung không biết tên loại đầu ra nào",
           not pham,
           "\n".join(pham) if pham else
           "%d mô-đun lõi sạch: %s" % (len(LOI_MU), ", ".join(Path(t).name for t in LOI_MU)))


def kl2(kq: KetQua):
    pham = []
    for tep in LOI_MU:
        for m in re.finditer(r"(?:^|\n)\s*(?:from|import)\s+\S*exporter\S*", doc(tep)):
            pham.append("%s nhập bộ dựng: %s" % (tep, m.group(0).strip()))
    kq.ghi("KL2 · Lõi dùng chung không nhập bộ dựng nào",
           not pham,
           "\n".join(pham) if pham else "Không mô-đun lõi nào nhập exporter_*")


# ---------------------------------------------------------------------------
# NHÓM 2 — Mỗi loại đầu ra phải đủ BA CHÂN: skill, bộ dựng, kiểm thử
# ---------------------------------------------------------------------------

def kl3(kq: KetQua):
    from core.loai_dau_ra import DANH_SACH
    from core.skill_loader import SKILL_THEO_LOAI, thu_muc_skill

    thieu = []
    for ma in DANH_SACH:
        chon = SKILL_THEO_LOAI.get(ma)
        if not chon:
            thieu.append("%s chưa có skill" % ma)
            continue
        if not (thu_muc_skill() / chon[0] / "SKILL.md").exists():
            thieu.append("%s trỏ tới skill không tồn tại: %s" % (ma, chon[0]))
        for ref in chon[1]:
            if not (thu_muc_skill() / chon[0] / ref).exists():
                thieu.append("%s thiếu tệp tham chiếu %s" % (ma, ref))
    kq.ghi("KL3 · Chín loại đầu ra đều có skill nạp được",
           not thieu,
           "\n".join(thieu) if thieu else "%d/%d loại có skill và đủ tệp tham chiếu"
           % (len(DANH_SACH), len(DANH_SACH)))


def kl4(kq: KetQua):
    """Mỗi loại phải có đường rẽ tới một bộ dựng, không rơi vào nhánh mặc định."""
    from core.loai_dau_ra import DANH_SACH, la_de

    dieu_phoi = doc("core/exporter.py") + doc("app.py")
    thieu = []
    for ma in DANH_SACH:
        if la_de(ma):
            continue          # năm loại đề đi chung nhánh la_loai_de()
        if not re.search(r"[\"']%s[\"']" % re.escape(ma), dieu_phoi):
            thieu.append("%s không có nhánh rẽ riêng trong exporter.py/app.py" % ma)
    co_nhanh_de = "la_loai_de" in dieu_phoi
    if not co_nhanh_de:
        thieu.append("Thiếu nhánh chung cho năm loại đề (la_loai_de)")
    kq.ghi("KL4 · Mỗi loại đầu ra rẽ tới đúng bộ dựng của nó",
           not thieu,
           "\n".join(thieu) if thieu else
           "5 loại đề đi nhánh chung; 4 loại còn lại có nhánh riêng")


def kl5(kq: KetQua):
    """Luật đang hỏng nhiều nhất — ghi rõ để không quên."""
    from core.loai_dau_ra import DANH_SACH, QUY_CACH

    cac_test = "\n".join(doc(p.name) for p in GOC.glob("test_*.py"))
    thieu = [ma for ma in DANH_SACH
             if not re.search(r"[\"']%s[\"']" % re.escape(ma), cac_test)]
    co = len(DANH_SACH) - len(thieu)
    kq.ghi("KL5 · Mỗi loại đầu ra có kiểm thử riêng",
           not thieu,
           ("%d/%d loại CHƯA có kiểm thử nào chạm tới:\n" % (len(thieu), len(DANH_SACH))
            + "\n".join("  - %s" % QUY_CACH[m].ten for m in thieu))
           if thieu else "%d/%d loại đã có kiểm thử" % (co, len(DANH_SACH)))


# ---------------------------------------------------------------------------
# NHÓM 3 — Skill và mã nguồn không được trôi khác nhau
# ---------------------------------------------------------------------------

def kl6(kq: KetQua):
    from core.skill_loader import CAP_AP_DUNG, SKILL_THEO_LOAI

    thieu = sorted({ten for ten, _ in SKILL_THEO_LOAI.values()
                    if ten and ten not in CAP_AP_DUNG})
    kq.ghi("KL6 · Mỗi skill khai báo rõ dùng cho cấp học nào",
           not thieu,
           "Skill thiếu CAP_AP_DUNG: %s" % ", ".join(thieu) if thieu else
           "%d skill đều có CAP_AP_DUNG" % len(CAP_AP_DUNG))


def kl7(kq: KetQua):
    """
    Nhãn mức độ trong bộ dựng phải có mặt trong skill tương ứng.

    Đây KHÔNG phải luật giả định: đã gãy thật một lần — exporter_hsg ghi bốn mức
    "Khởi động / Cơ bản / Vận dụng / Vận dụng cao" trong khi skill tai-lieu-hsg
    quy định ba mức "Vận dụng / Vận dụng cao / Olympic". Mô hình được dặn một
    đằng, tệp dựng ra một nẻo.
    """
    from core.skill_loader import thu_muc_skill

    cap = [
        ("core/exporter_hsg.py", "tai-lieu-hsg"),
    ]
    lech = []
    for tep, skill in cap:
        nd = doc(tep)
        m = re.search(r"_nhan_do_kho.*?return \((.*?)\)", nd, re.S)
        if not m:
            lech.append("%s: không tìm thấy bảng nhãn mức độ" % tep)
            continue
        nhan = {x.strip() for x in re.findall(r'"([^"]+)"', m.group(1))}
        vb = (thu_muc_skill() / skill / "SKILL.md").read_text(encoding="utf-8")
        thieu = sorted(n for n in nhan if n not in vb)
        if thieu:
            lech.append("%s dùng nhãn không có trong skill %s: %s"
                        % (tep, skill, ", ".join(thieu)))
    kq.ghi("KL7 · Nhãn mức độ trong bộ dựng khớp chữ trong skill",
           not lech,
           "\n".join(lech) if lech else
           "Đã đối chiếu %d cặp bộ dựng ↔ skill" % len(cap))


def kl8(kq: KetQua):
    """skills/ trong repo và ~/.claude/skills không được trôi khác nhau."""
    ca_nhan = Path(os.path.expanduser("~")) / ".claude" / "skills"
    trong_repo = GOC / "skills"
    if not ca_nhan.is_dir():
        kq.ghi("KL8 · skills/ repo và ~/.claude/skills giống nhau", True,
               "Máy này không có ~/.claude/skills — bỏ qua (máy chủ triển khai cũng vậy)")
        return

    def bang(goc: Path):
        return {str(p.relative_to(goc)).replace("\\", "/"):
                p.read_bytes().replace(b"\r\n", b"\n")
                for p in goc.rglob("*.md")}

    a, b = bang(trong_repo), bang(ca_nhan)
    lech = ["chỉ có trong repo: %s" % k for k in sorted(set(a) - set(b))]
    lech += ["chỉ có trên máy: %s" % k for k in sorted(set(b) - set(a))]
    lech += ["khác nội dung: %s" % k for k in sorted(set(a) & set(b)) if a[k] != b[k]]
    kq.ghi("KL8 · skills/ repo và ~/.claude/skills giống nhau",
           not lech,
           "\n".join(lech) + "\n→ chạy: python scripts/dong_bo_skill.py --ra-may"
           if lech else "%d tệp skill trùng khớp" % len(a))


# ---------------------------------------------------------------------------
# NHÓM 4 — Thẩm định phải đo trên dữ liệu thật
# ---------------------------------------------------------------------------

def kl9(kq: KetQua):
    """
    Kiểm thử phải MỞ LẠI tệp kết quả để đếm, không tin giá trị hàm trả về.

    Bộ thẩm định từng chấm cứng 20/20 cho tiêu chí thể thức mà không mở file.
    Báo cáo kiểu đó chỉ là trang trí và che mất đúng lỗi cần thấy.
    """
    # Luật chỉ áp cho kiểm thử CÓ DỰNG RA TỆP. Kiểm thử thuần lô-gic (ví dụ bộ
    # phân loại chuyên đề) không dựng tệp nào thì không có gì để mở lại — bắt nó
    # mở tệp là luật sai, không phải mã sai.
    tot, kem, khong_dung = [], [], []
    for p in sorted(GOC.glob("test_*.py")):
        nd = p.read_text(encoding="utf-8", errors="ignore")
        co_dung = bool(re.search(r"\.save\(|export\(|xuat_[a-z_]+\(", nd))
        mo_lai = bool(re.search(r"docx\.Document\(|Document\(str\(|Presentation\(", nd))
        if not co_dung:
            khong_dung.append(p.name)
        elif mo_lai:
            tot.append(p.name)
        else:
            kem.append(p.name)
    kq.ghi("KL9 · Kiểm thử nào dựng ra tệp thì phải mở lại tệp đó để đo",
           not kem,
           ("Dựng tệp nhưng không mở lại để đo: %s" % ", ".join(kem)) if kem else
           "%d tệp dựng tệp và đều mở lại để đo; %d tệp thuần lô-gic không áp luật này"
           % (len(tot), len(khong_dung)))


# ---------------------------------------------------------------------------
# NHÓM 5 — Khóa API là của riêng từng người
# ---------------------------------------------------------------------------

def kl10(kq: KetQua):
    """
    Chọn Claude mà chỉ dán khóa Gemini thì phải chạy ngoại tuyến, KHÔNG mượn.

    Kiểm bằng hành vi thật: dựng yêu cầu giả rồi gọi thẳng request_credentials,
    chứ không đọc mã đoán ý.
    """
    try:
        import app as ung_dung
    except Exception as e:                      # pragma: no cover
        kq.ghi("KL10 · Hai nhà cung cấp không mượn khóa của nhau", False,
               "Không nạp được app.py: %s" % e)
        return

    class YeuCauGia:
        def __init__(self, h):
            self.headers = h

    that_bai = []
    goc_local = getattr(ung_dung, "LOCAL_MODE", False)
    try:
        ung_dung.LOCAL_MODE = False            # giả lập bản Web
        key, _, nha = ung_dung.request_credentials(
            YeuCauGia({"X-AI-Provider": "claude", "X-Gemini-Key": "KHOA-GEMINI-CUA-NGUOI-KHAC"}))
        if key:
            that_bai.append("Chọn Claude, chỉ có khóa Gemini → vẫn lấy được khóa %r" % key[:12])

        key2, _, _ = ung_dung.request_credentials(
            YeuCauGia({"X-AI-Provider": "gemini", "X-Claude-Key": "KHOA-CLAUDE-CUA-NGUOI-KHAC"}))
        if key2:
            that_bai.append("Chọn Gemini, chỉ có khóa Claude → vẫn lấy được khóa %r" % key2[:12])

        key3, _, _ = ung_dung.request_credentials(YeuCauGia({"X-AI-Provider": "gemini"}))
        if key3:
            that_bai.append("Không dán khóa nào → vẫn mượn được khóa của máy chủ")
    finally:
        ung_dung.LOCAL_MODE = goc_local

    kq.ghi("KL10 · Hai nhà cung cấp không mượn khóa của nhau",
           not that_bai,
           "\n".join(that_bai) if that_bai else
           "Thử 3 tình huống trên bản Web: đều trả về khóa rỗng, chạy ngoại tuyến")


# ---------------------------------------------------------------------------
# NHÓM 6 — Chống lưu đệm và an toàn
# ---------------------------------------------------------------------------

def kl11(kq: KetQua):
    nd = doc("app.py")
    html = doc("templates/index.html")
    loi = []
    if "__ASSET_VERSION__" not in html:
        loi.append("index.html không dùng ?v=__ASSET_VERSION__")
    m = re.search(r"def _asset_version\(.*?\n(.*?)\ndef ", nd, re.S)
    than = m.group(1) if m else ""
    if not than:
        loi.append("Không tìm thấy _asset_version()")
    else:
        if "md5" not in than:
            loi.append("_asset_version() không băm nội dung")
        if "app.js" not in than or "style.css" not in than:
            loi.append("_asset_version() không băm đủ app.js và style.css")
        if re.search(r"return\s+[\"'][0-9a-f]{6,}[\"']", than):
            loi.append("_asset_version() gắn cứng số phiên bản")
    kq.ghi("KL11 · Phiên bản tài nguyên băm từ nội dung, không gắn cứng",
           not loi,
           "\n".join(loi) if loi else "index.html + _asset_version() băm MD5 app.js và style.css")


def kl12(kq: KetQua):
    """
    sympy.parse_expr dùng eval bên trong. Truyền local_dict là KHÔNG đủ —
    đã thử nghiệm và xác nhận __import__('os').system(...) chạy thật.
    """
    nd = doc("core/question_forge.py")
    loi = []
    if "_bieu_thuc_an_toan" not in nd:
        loi.append("Mất hàm chặn _bieu_thuc_an_toan")
    else:
        vi_chan = nd.find("an_toan, vi_pham = _bieu_thuc_an_toan")
        vi_parse = min([m.start() for m in re.finditer(r"= parse_expr\(", nd)] or [-1])
        if vi_parse < 0:
            loi.append("Không tìm thấy lời gọi parse_expr để đối chiếu thứ tự")
        elif vi_chan < 0 or vi_chan > vi_parse:
            loi.append("parse_expr chạy TRƯỚC khi chặn — biểu thức do AI sinh vào thẳng eval")
    kq.ghi("KL12 · Chặn biểu thức trước khi đưa vào sympy.parse_expr",
           not loi,
           "\n".join(loi) if loi else "_bieu_thuc_an_toan() chặn trước mọi parse_expr")


# ---------------------------------------------------------------------------

LUAT: List[Tuple[str, Callable]] = [
    ("NHÓM 1 — Lõi dùng chung phải mù về loại đầu ra", None),
    ("", kl1), ("", kl2),
    ("NHÓM 2 — Mỗi loại đầu ra đủ ba chân: skill · bộ dựng · kiểm thử", None),
    ("", kl3), ("", kl4), ("", kl5),
    ("NHÓM 3 — Skill và mã nguồn không trôi khác nhau", None),
    ("", kl6), ("", kl7), ("", kl8),
    ("NHÓM 4 — Thẩm định đo trên dữ liệu thật", None),
    ("", kl9),
    ("NHÓM 5 — Khóa API là của riêng từng người", None),
    ("", kl10),
    ("NHÓM 6 — Chống lưu đệm và an toàn", None),
    ("", kl11), ("", kl12),
]


def main() -> int:
    print("KIỂM KỶ LUẬT NỘI BỘ — %s" % GOC)
    kq = KetQua()
    for ten, ham in LUAT:
        if ham is None:
            print("\n" + ten)
            print("-" * 78)
        else:
            ham(kq)

    tong = kq.dat + len(kq.hong)
    print("\n" + "=" * 78)
    print("KẾT QUẢ: %d/%d luật đạt" % (kq.dat, tong))
    for t in kq.hong:
        print("   HỎNG  %s" % t)
    return 1 if kq.hong else 0


if __name__ == "__main__":
    sys.exit(main())
