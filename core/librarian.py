"""
Thủ thư: quét cả kho tài liệu, phân loại, phát hiện trùng lặp và đề xuất dọn dẹp.

Bối cảnh: kho thật có hàng nghìn tệp gom từ nhiều nguồn, tên đặt lộn xộn, nhiều
bản trùng nhau, lẫn cả tệp hỏng không đọc được. Muốn biên soạn ra tài liệu sạch
thì phải biết mình đang có gì trước đã.

Hai lớp quét, vì đọc hết vài nghìn tệp mất hàng giờ:

  Lớp 1 — QUÉT NHANH (tức thì, không mở tệp)
      Phân loại bằng tên tệp và đường dẫn. Tên tài liệu giáo dục Việt Nam thường
      rất giàu thông tin: "Đề thi học kì 1 môn Toán lớp 9 năm 2018 - 2019 huyện
      Hải Hậu" đã đủ biết môn, lớp, loại, năm, đơn vị. Đủ để dựng bức tranh tổng
      thể và chọn ra phần đáng đọc sâu.

  Lớp 2 — ĐỌC SÂU (chậm, có nhớ đệm, chạy nền được)
      Mở từng tệp, bóc tách câu hỏi, chấm chất lượng, lấy vân tay để dò trùng.
      Kết quả lưu lại theo (đường dẫn, thời gian sửa, kích thước) nên chạy lần
      hai chỉ xử lý tệp mới hoặc tệp đã thay đổi.

Toàn bộ việc phân loại KHÔNG tốn một lượt gọi API nào.
"""

import hashlib
import json
import os
import re
import time
import unicodedata
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from config import BASE_DIR

CACHE_DIR = BASE_DIR / "data"
CACHE_FILE = CACHE_DIR / "thu_vien_cache.json"

DUOI_HO_TRO = {".docx", ".pdf", ".xlsx"}
DUOI_CAN_CHUYEN = {".doc", ".xls"}     # định dạng cũ, thư viện Python không đọc được


# ---------------------------------------------------------------------------
# LỚP 1: PHÂN LOẠI TỪ TÊN TỆP
# ---------------------------------------------------------------------------

def _bo_dau(s: str) -> str:
    """Bỏ dấu tiếng Việt để so khớp từ khóa cho chắc."""
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("đ", "d").replace("Đ", "D").lower()


MON_HOC = [
    ("toan", ["toan", "math"]),
    ("vatly", ["vat ly", "vat li", "vatly", "ly ", " ly", "physic"]),
    ("hoahoc", ["hoa hoc", "hoa ", " hoa", "chemis"]),
    ("sinhhoc", ["sinh hoc", "sinh ", "biolog"]),
    ("nguvan", ["ngu van", "van ", " van", "literat"]),
    ("tienganh", ["tieng anh", "anh van", "english"]),
    ("tinhoc", ["tin hoc", "informat"]),
    ("lichsu", ["lich su", "history"]),
    ("dialy", ["dia ly", "dia li", "geograph"]),
    ("gdcd", ["gdcd", "giao duc cong dan"]),
]

# Thu tu quan trong: loai nao DAC TRUNG hon thi xet truoc.
# "dap_an" cố tình để CUỐI vì rất nhiều tài liệu có cụm "có đáp án" trong tên
# nhưng bản chất là chuyên đề hay đề thi — chỉ khi không khớp loại nào khác thì
# mới thực sự là tệp đáp án rời.
LOAI_TAI_LIEU = [
    ("giao_an", ["giao an", "ke hoach bai day", "kpbd", "ppct", "phan phoi chuong trinh"]),
    ("so_tay", ["so tay", "cam nang", "tom tat ly thuyet", "cong thuc", "kien thuc can nho"]),
    ("chuyen_de", ["chuyen de", "phan dang", "dang bai", "phuong phap giai",
                   "cac dang toan", "bai tap"]),
    ("de_thi", ["de thi", "de kiem tra", "de ks", "de khao sat", "kiem tra",
                "thi thu", "de on", "de so", "de minh hoa", "de tham khao",
                "hoc ki", "hoc ky", "giua ki", "cuoi ki", "hsg", "hoc sinh gioi",
                "tuyen sinh", "tot nghiep", "khao sat chat luong"]),
    ("sach", ["sach", "giao trinh", "tuyen tap", "tuyen chon", "boi duong"]),
    ("dap_an", ["dap an", "huong dan giai", "loi giai", "giai chi tiet", "bai giai"]),
]

_RE_LOP = re.compile(r"\b(?:lop|khoi|k)\s*(\d{1,2})\b")
_RE_LOP2 = re.compile(r"\b(?:toan|ly|hoa|sinh|van|anh)\s*(\d{1,2})\b")
# Dấu gạch nối đã bị thay bằng khoảng trắng khi chuẩn hóa, nên mẫu năm học phải
# chấp nhận cả "2020-2021" lẫn "2020 2021".
_RE_NAM = re.compile(r"\b(20\d{2})\s*[-–]?\s*(20\d{2})\b")
_RE_NAM1 = re.compile(r"\b(20\d{2})\b")


def phan_loai_tu_ten(duong_dan: Path, goc: Optional[Path] = None) -> Dict[str, Any]:
    """Đoán môn / lớp / loại / năm chỉ từ tên tệp và đường dẫn thư mục."""
    phan_duong = str(duong_dan.relative_to(goc)) if goc else str(duong_dan)
    van_ban = _bo_dau(phan_duong.replace("_", " ").replace("-", " "))
    # Tên tệp luôn cụ thể hơn tên thư mục cha, nên xét riêng để ưu tiên
    ten_tep = _bo_dau(duong_dan.stem.replace("_", " ").replace("-", " "))

    mon = ""
    for nguon in (ten_tep, van_ban):
        for ma, tu_khoa in MON_HOC:
            if any(tk in nguon for tk in tu_khoa):
                mon = ma
                break
        if mon:
            break

    lop = 0
    m = _RE_LOP.search(van_ban) or _RE_LOP2.search(van_ban)
    if m:
        gt = int(m.group(1))
        if 1 <= gt <= 12:
            lop = gt

    loai = ""
    for nguon in (ten_tep, van_ban):
        for ma, tu_khoa in LOAI_TAI_LIEU:
            if any(tk in nguon for tk in tu_khoa):
                loai = ma
                break
        if loai:
            break

    # Năm học: ưu tiên lấy từ TÊN TỆP. Thư mục cha thường mang năm của cả kho
    # ("THCS 2026-2027") và sẽ đè lên năm thật của tài liệu ("... năm 2019-2020").
    nam = ""
    for nguon in (ten_tep, van_ban):
        m = _RE_NAM.search(nguon)
        if m:
            nam = f"{m.group(1)}-{m.group(2)}"
            break
        m = _RE_NAM1.search(nguon)
        if m and 2000 <= int(m.group(1)) <= 2035:
            nam = m.group(1)
            break

    return {"mon": mon, "lop": lop, "loai": loai, "nam": nam}


def _cap_hoc(lop: int) -> str:
    if 1 <= lop <= 5:
        return "tieu_hoc"
    if 6 <= lop <= 9:
        return "thcs"
    if 10 <= lop <= 12:
        return "thpt"
    return "khong_ro"


def quet_nhanh(thu_muc: Path, gioi_han: int = 0) -> Dict[str, Any]:
    """
    Quét toàn kho bằng tên tệp — chạy trong vài giây kể cả với hàng nghìn tệp.
    Cho bức tranh tổng thể để biết nên đọc sâu phần nào.
    """
    thu_muc = Path(thu_muc)
    ds: List[Dict[str, Any]] = []
    trung_ten: Dict[str, List[str]] = {}

    for goc, _, tep in os.walk(str(thu_muc)):
        for ten in tep:
            if ten.startswith("~$"):
                continue
            p = Path(goc) / ten
            duoi = p.suffix.lower()
            if duoi not in DUOI_HO_TRO and duoi not in DUOI_CAN_CHUYEN:
                continue
            try:
                st = p.stat()
            except OSError:
                continue

            info = phan_loai_tu_ten(p, thu_muc)
            info.update({
                "duong_dan": str(p),
                "ten": ten,
                "duoi": duoi,
                "kb": round(st.st_size / 1024, 1),
                "cap_hoc": _cap_hoc(info["lop"]),
                "doc_duoc": duoi in DUOI_HO_TRO,
            })
            ds.append(info)

            # Gom theo tên đã chuẩn hóa để phát hiện bản trùng tên
            khoa = re.sub(r"[\s_\-().]+", "", _bo_dau(p.stem))
            trung_ten.setdefault(khoa, []).append(str(p))

            if gioi_han and len(ds) >= gioi_han:
                break
        if gioi_han and len(ds) >= gioi_han:
            break

    nhom_trung = {k: v for k, v in trung_ten.items() if len(v) > 1}

    return {
        "thu_muc": str(thu_muc),
        "tong_tep": len(ds),
        "danh_sach": ds,
        "thong_ke": _thong_ke(ds),
        "trung_ten": nhom_trung,
        "so_nhom_trung_ten": len(nhom_trung),
        "so_tep_trung_ten": sum(len(v) for v in nhom_trung.values()),
    }


def _thong_ke(ds: List[Dict[str, Any]]) -> Dict[str, Any]:
    def dem(khoa):
        out: Dict[str, int] = {}
        for d in ds:
            gt = str(d.get(khoa) or "khong_ro")
            out[gt] = out.get(gt, 0) + 1
        return dict(sorted(out.items(), key=lambda x: -x[1]))

    can_chuyen = sum(1 for d in ds if not d["doc_duoc"])
    return {
        "theo_mon": dem("mon"),
        "theo_cap_hoc": dem("cap_hoc"),
        "theo_lop": dem("lop"),
        "theo_loai": dem("loai"),
        "theo_duoi": dem("duoi"),
        "so_tep_can_chuyen_doi": can_chuyen,
        "tong_dung_luong_mb": round(sum(d["kb"] for d in ds) / 1024, 1),
    }


# ---------------------------------------------------------------------------
# LỚP 2: ĐỌC SÂU
# ---------------------------------------------------------------------------

def _van_tay_cau(noi_dung: str) -> str:
    """Vân tay một câu hỏi để dò trùng giữa các tệp, bỏ qua khác biệt vụn vặt."""
    s = _bo_dau(noi_dung)
    s = re.sub(r"[^a-z0-9]+", "", s)
    return hashlib.md5(s[:180].encode()).hexdigest()[:16] if len(s) >= 30 else ""


def _doc_cache() -> Dict[str, Any]:
    if not CACHE_FILE.exists():
        return {}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _ghi_cache(data: Dict[str, Any]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = CACHE_FILE.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    tmp.replace(CACHE_FILE)


def _khoa_cache(p: Path) -> str:
    try:
        st = p.stat()
        return f"{p}|{int(st.st_mtime)}|{st.st_size}"
    except OSError:
        return str(p)


def doc_sau_mot_tep(p: Path, mon_mac_dinh: str = "toan") -> Dict[str, Any]:
    """Mở một tệp, bóc tách và chấm chất lượng."""
    from core.parser import parse_input_file, lay_dau_hieu_tai_lieu
    from core.doc_type import detect_document_type
    from core.theory_bank import detect_subject_and_topic

    kq: Dict[str, Any] = {"duong_dan": str(p), "loi": ""}
    t0 = time.time()
    try:
        qs = parse_input_file(p, subject=mon_mac_dinh)
    except Exception as e:
        kq.update(loi=str(e)[:160], so_cau=0, chat_luong=0)
        return kq

    n = len(qs)
    co_giai = sum(1 for q in qs if len((q.solution or "").strip()) > 40)
    co_pa = sum(1 for q in qs if len(q.options or []) >= 4)
    do_dai_tb = sum(len(q.content) for q in qs) / max(1, n)

    nd = detect_document_type(qs, lay_dau_hieu_tai_lieu(), p.name)
    chu_de = detect_subject_and_topic([q.content for q in qs[:40]], subject=mon_mac_dinh)

    # Chấm chất lượng bóc tách 0-100: tệp nào điểm thấp thì dùng lại rất mệt
    diem = 0
    if n >= 5:
        diem += 35
    elif n >= 2:
        diem += 20
    if 40 <= do_dai_tb <= 1200:
        diem += 25          # độ dài đề hợp lý, không bị dồn cục hay vụn vặt
    if co_giai or co_pa:
        diem += 25
    if n and (co_giai + co_pa) / n > 0.5:
        diem += 15

    kq.update({
        "so_cau": n,
        "so_co_loi_giai": co_giai,
        "so_du_phuong_an": co_pa,
        "do_dai_de_tb": round(do_dai_tb),
        "loai_tai_lieu": nd["doc_type"],
        "ten_loai": nd["ten_hien_thi"],
        "chuyen_de": chu_de.get("topic_key", ""),
        "chat_luong": min(100, diem),
        "van_tay": [v for v in (_van_tay_cau(q.content) for q in qs) if v],
        "giay": round(time.time() - t0, 2),
    })
    return kq


def quet_sau(
    danh_sach_tep: List[str],
    mon_mac_dinh: str = "toan",
    dung_cache: bool = True,
    bao_tien_do=None,
) -> List[Dict[str, Any]]:
    """
    Đọc sâu một danh sách tệp, có nhớ đệm nên chạy lại rất nhanh.
    bao_tien_do: hàm nhận (đã_xong, tổng, tên_tệp) để báo tiến độ ra ngoài.
    """
    cache = _doc_cache() if dung_cache else {}
    ket_qua: List[Dict[str, Any]] = []
    moi = 0

    for i, duong_dan in enumerate(danh_sach_tep, 1):
        p = Path(duong_dan)
        khoa = _khoa_cache(p)

        if dung_cache and khoa in cache:
            ket_qua.append(cache[khoa])
        else:
            r = doc_sau_mot_tep(p, mon_mac_dinh)
            cache[khoa] = r
            ket_qua.append(r)
            moi += 1
            if moi % 25 == 0:
                _ghi_cache(cache)      # lưu dần để mất điện không mất hết công

        if bao_tien_do:
            bao_tien_do(i, len(danh_sach_tep), p.name)

    if dung_cache and moi:
        _ghi_cache(cache)
    return ket_qua


# ---------------------------------------------------------------------------
# DÒ TRÙNG LẶP NỘI DUNG
# ---------------------------------------------------------------------------

def do_trung_lap(ket_qua_sau: List[Dict[str, Any]], nguong: float = 0.6) -> Dict[str, Any]:
    """
    Tìm các tệp có nội dung chồng lấn nhau.

    So bằng vân tay từng câu hỏi chứ không so tên tệp: hai tệp tên khác hẳn nhau
    vẫn có thể là cùng một bộ đề đã đổi tên.
    """
    hop_le = [r for r in ket_qua_sau if r.get("van_tay")]
    cap_trung: List[Dict[str, Any]] = []

    # Lập bảng tra: vân tay -> các tệp chứa nó
    bang: Dict[str, List[int]] = {}
    for i, r in enumerate(hop_le):
        for v in set(r["van_tay"]):
            bang.setdefault(v, []).append(i)

    # Đếm số câu chung giữa từng cặp tệp
    chung: Dict[Tuple[int, int], int] = {}
    for ds_tep in bang.values():
        if len(ds_tep) < 2 or len(ds_tep) > 40:
            continue                    # câu xuất hiện ở quá nhiều tệp là câu phổ thông
        for a in range(len(ds_tep)):
            for b in range(a + 1, len(ds_tep)):
                khoa = (ds_tep[a], ds_tep[b])
                chung[khoa] = chung.get(khoa, 0) + 1

    for (a, b), so_chung in chung.items():
        na = len(set(hop_le[a]["van_tay"]))
        nb = len(set(hop_le[b]["van_tay"]))
        ti_le = so_chung / max(1, min(na, nb))
        if ti_le >= nguong and so_chung >= 3:
            cap_trung.append({
                "tep_a": hop_le[a]["duong_dan"],
                "tep_b": hop_le[b]["duong_dan"],
                "so_cau_chung": so_chung,
                "ti_le": round(ti_le, 2),
                "cau_a": na,
                "cau_b": nb,
            })

    cap_trung.sort(key=lambda x: -x["ti_le"])
    return {
        "so_cap_trung": len(cap_trung),
        "cap_trung": cap_trung[:200],
        "so_tep_lien_quan": len({c["tep_a"] for c in cap_trung} | {c["tep_b"] for c in cap_trung}),
    }


# ---------------------------------------------------------------------------
# ĐỀ XUẤT DỌN DẸP
# ---------------------------------------------------------------------------

def de_xuat_don_dep(quet: Dict[str, Any], sau: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Gom tài liệu thành các nhóm có thể biên soạn thành một cuốn sạch."""
    ds = quet["danh_sach"]
    theo_duong_dan = {r["duong_dan"]: r for r in (sau or [])}

    nhom: Dict[str, Dict[str, Any]] = {}
    for d in ds:
        if not d["doc_duoc"]:
            continue
        r = theo_duong_dan.get(d["duong_dan"])
        if r and (r.get("chat_luong", 0) < 40 or r.get("so_cau", 0) < 2):
            continue          # tệp bóc tách kém thì không đưa vào sách

        mon = d["mon"] or "chua_ro_mon"
        lop = d["lop"] or 0
        loai = d["loai"] or "khac"
        khoa = f"{mon}|{lop}|{loai}"

        g = nhom.setdefault(khoa, {
            "mon": mon, "lop": lop, "loai": loai,
            "cap_hoc": d["cap_hoc"], "so_tep": 0, "so_cau": 0, "tep": [],
        })
        g["so_tep"] += 1
        g["so_cau"] += (r or {}).get("so_cau", 0)
        if len(g["tep"]) < 60:
            g["tep"].append(d["duong_dan"])

    ds_nhom = sorted(nhom.values(), key=lambda g: -g["so_tep"])

    can_chuyen = [d["duong_dan"] for d in ds if not d["doc_duoc"]]
    kem = [r["duong_dan"] for r in (sau or [])
           if r.get("chat_luong", 100) < 40 or r.get("loi")]

    return {
        "so_nhom": len(ds_nhom),
        "nhom": ds_nhom,
        "can_chuyen_doi": can_chuyen[:400],
        "so_can_chuyen_doi": len(can_chuyen),
        "boc_tach_kem": kem[:200],
        "so_boc_tach_kem": len(kem),
    }
