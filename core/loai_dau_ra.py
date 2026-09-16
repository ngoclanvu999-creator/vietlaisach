# -*- coding: utf-8 -*-
"""
Chín loại đầu ra, ứng với chín thư mục người dùng đang dùng thật.

Phân biệt hai khái niệm dễ lẫn:
  - NHẬN DIỆN (core/doc_type.py): đoán tài liệu ĐƯA VÀO là gì. Ba loại.
  - ĐẦU RA (mô-đun này): người dùng muốn NHẬN LẠI tài liệu dạng gì. Chín loại.

Chín loại không phải chín biến thể của một thứ. Chúng thuộc bốn nhóm chịu bốn
chuẩn khác nhau, nên mỗi nhóm có một bộ dựng riêng.

Một điểm dễ làm sai: với đề kiểm tra định kì, "hoàn chỉnh đúng chuẩn" theo Bộ
KHÔNG phải một tệp đề, mà là bộ bốn phần — ma trận đề, bản đặc tả, đề kiểm tra,
hướng dẫn chấm. Hai phần đầu là thứ giáo viên tốn công nhất mà máy suy ra được,
vì mỗi câu đã có sẵn mức độ và chuyên đề.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

# --- Bốn nhóm, quyết định dùng bộ dựng nào ---
NHOM_DE = "DE"              # đề kiểm tra, đề thi
NHOM_ON_LUYEN = "ON_LUYEN"  # chuyên đề bài tập, tài liệu HSG
NHOM_GIAO_AN = "GIAO_AN"    # giáo án theo Công văn 5512
NHOM_BAI_GIANG = "BAI_GIANG"  # bài giảng PowerPoint

# --- Chín loại ---
DE_CHUONG_BAI = "DE_CHUONG_BAI"
DE_GIUA_KI_1 = "DE_GIUA_KI_1"
DE_GIUA_KI_2 = "DE_GIUA_KI_2"
DE_HOC_KI_1 = "DE_HOC_KI_1"
DE_HOC_KI_2 = "DE_HOC_KI_2"
CHUYEN_DE_BT = "CHUYEN_DE_BT"
TAI_LIEU_HSG = "TAI_LIEU_HSG"
GIAO_AN = "GIAO_AN"
BAI_GIANG = "BAI_GIANG"


@dataclass
class QuyCachDauRa:
    ma: str
    ten: str
    nhom: str
    thu_muc: str                 # tên thư mục kết quả, khớp thư mục người dùng đang dùng
    thoi_gian: int = 0           # phút; 0 nghĩa là không áp dụng
    can_ma_tran: bool = False    # có cần ma trận + bản đặc tả không
    pham_vi: str = ""            # phạm vi kiến thức, ghi vào ma trận
    ty_le_cau: float = 1.0       # so với đề cuối kì đầy đủ (dùng để suy số câu)
    ghi_chu: str = ""


QUY_CACH: Dict[str, QuyCachDauRa] = {
    DE_CHUONG_BAI: QuyCachDauRa(
        ma=DE_CHUONG_BAI, ten="Đề kiểm tra theo chương bài", nhom=NHOM_DE,
        thu_muc="Đề kiểm tra theo chương bài", thoi_gian=45,
        can_ma_tran=True, ty_le_cau=0.45,
        pham_vi="Một chương hoặc một số bài đã học",
        ghi_chu="Kiểm tra thường xuyên, ma trận gọn.",
    ),
    DE_GIUA_KI_1: QuyCachDauRa(
        ma=DE_GIUA_KI_1, ten="Đề kiểm tra giữa học kì 1", nhom=NHOM_DE,
        thu_muc="Đề kiểm tra giữa học kì 1", thoi_gian=60,
        can_ma_tran=True, ty_le_cau=0.6,
        pham_vi="Từ đầu học kì 1 đến thời điểm kiểm tra giữa kì",
    ),
    DE_GIUA_KI_2: QuyCachDauRa(
        ma=DE_GIUA_KI_2, ten="Đề kiểm tra giữa học kì 2", nhom=NHOM_DE,
        thu_muc="Đề kiểm tra giữa học kì 2", thoi_gian=60,
        can_ma_tran=True, ty_le_cau=0.6,
        pham_vi="Từ đầu học kì 2 đến thời điểm kiểm tra giữa kì",
    ),
    DE_HOC_KI_1: QuyCachDauRa(
        ma=DE_HOC_KI_1, ten="Đề thi học kì 1", nhom=NHOM_DE,
        thu_muc="Đề thi học kì 1", thoi_gian=90,
        can_ma_tran=True, ty_le_cau=1.0,
        pham_vi="Toàn bộ chương trình học kì 1",
    ),
    DE_HOC_KI_2: QuyCachDauRa(
        ma=DE_HOC_KI_2, ten="Đề thi học kì 2", nhom=NHOM_DE,
        thu_muc="Đề thi học kì 2", thoi_gian=90,
        can_ma_tran=True, ty_le_cau=1.0,
        pham_vi="Toàn bộ chương trình học kì 2 (có thể kèm học kì 1)",
    ),
    CHUYEN_DE_BT: QuyCachDauRa(
        ma=CHUYEN_DE_BT, ten="Chuyên đề bài tập", nhom=NHOM_ON_LUYEN,
        thu_muc="Chuyên Đề Bài Tập",
        pham_vi="Một chuyên đề, đi từ lý thuyết tới hệ thống bài tập",
    ),
    TAI_LIEU_HSG: QuyCachDauRa(
        ma=TAI_LIEU_HSG, ten="Tài liệu học sinh giỏi", nhom=NHOM_ON_LUYEN,
        thu_muc="Tài Liệu HSG",
        pham_vi="Chuyên sâu, chủ yếu tự luận, độ khó dồn về vận dụng cao",
    ),
    GIAO_AN: QuyCachDauRa(
        ma=GIAO_AN, ten="Giáo án Word", nhom=NHOM_GIAO_AN,
        thu_muc="Giáo Án Word",
        pham_vi="Một bài học trong sách giáo khoa",
        ghi_chu="Khung Công văn 5512. Hồ sơ chuyên môn — không trang trí.",
    ),
    BAI_GIANG: QuyCachDauRa(
        ma=BAI_GIANG, ten="Bài giảng PowerPoint", nhom=NHOM_BAI_GIANG,
        thu_muc="Bài Giảng Power Point",
        pham_vi="Một bài học, trình chiếu trên lớp",
    ),
}

DANH_SACH = list(QUY_CACH.keys())


def quy_cach(ma: str) -> Optional[QuyCachDauRa]:
    return QUY_CACH.get(str(ma or "").upper())


def la_de(ma: str) -> bool:
    q = quy_cach(ma)
    return bool(q and q.nhom == NHOM_DE)


def thu_muc_cua(ma: str) -> str:
    """Tên thư mục để xếp kết quả vào. Không khớp loại nào thì để thư mục chung."""
    q = quy_cach(ma)
    return q.thu_muc if q else "Khác"


# ---------------------------------------------------------------------------
# Cấu trúc đề chuẩn 2025 và cách suy ra đề ngắn hơn
# ---------------------------------------------------------------------------
# Đề tốt nghiệp đầy đủ, lấy thẳng từ công bố của Bộ (xem skills/de-thi-thpt-2025).
#   Toán   : 12 + 4 + 6 = 22 câu / 34 lệnh hỏi / 90 phút
#   Vật lí : 18 + 4 + 6 = 28 câu / 40 lệnh hỏi / 50 phút
# Tỉ trọng điểm từng phần suy ra từ chính thang điểm đó, và được GIỮ NGUYÊN khi
# rút gọn đề, để đề ngắn vẫn cùng một triết lý đánh giá.
CHUAN_DAY_DU = {
    "toan": {
        "so_cau": (12, 4, 6),
        "ty_trong": (0.30, 0.40, 0.30),   # 3,0 + 4,0 + 3,0 = 10,0
        "thoi_gian": 90,
    },
    "vatly": {
        "so_cau": (18, 4, 6),
        "ty_trong": (0.45, 0.40, 0.15),   # 4,5 + 4,0 + 1,5 = 10,0
        "thoi_gian": 50,
    },
}

# Thang điểm lũy tiến Phần II của đề tốt nghiệp, ứng với câu tối đa 1,0 điểm.
# ĐÂY LÀ CHỖ DỄ LẬP TRÌNH SAI NHẤT: không phải 0,25 nhân số ý đúng.
# Đúng 2 trong 4 ý chỉ được 0,25 chứ không phải 0,5.
LUY_TIEN_CHUAN = (0.10, 0.25, 0.50, 1.00)


@dataclass
class CauTrucDe:
    """Số câu và thang điểm cụ thể của một đề."""
    so_cau_p1: int
    so_cau_p2: int
    so_cau_p3: int
    diem_moi_cau_p1: float
    diem_toi_da_p2: float          # điểm tối đa MỘT câu Phần II
    diem_moi_cau_p3: float
    luy_tien_p2: List[float] = field(default_factory=list)
    thoi_gian: int = 90

    @property
    def tong_cau(self) -> int:
        return self.so_cau_p1 + self.so_cau_p2 + self.so_cau_p3

    @property
    def tong_lenh_hoi(self) -> int:
        """Một câu Đúng/Sai tính là 1 câu nhưng 4 lệnh hỏi."""
        return self.so_cau_p1 + self.so_cau_p2 * 4 + self.so_cau_p3

    @property
    def tong_diem(self) -> float:
        return round(
            self.so_cau_p1 * self.diem_moi_cau_p1
            + self.so_cau_p2 * self.diem_toi_da_p2
            + self.so_cau_p3 * self.diem_moi_cau_p3,
            2,
        )


def _lam_tron(x: float) -> float:
    return round(x + 1e-9, 3)


def tinh_cau_truc(ma_loai: str, subject: str = "toan") -> CauTrucDe:
    """
    Suy ra số câu và thang điểm cho một loại đề.

    Đề cuối kì dùng đúng cấu trúc tốt nghiệp. Đề ngắn hơn (giữa kì, theo chương)
    giảm số câu theo tỉ lệ nhưng GIỮ NGUYÊN tỉ trọng điểm giữa ba phần, rồi chia
    lại điểm mỗi câu sao cho tổng vẫn đúng 10,0.

    Lưu ý trung thực: Bộ chỉ công bố thang điểm cho đề tốt nghiệp. Với bài kiểm
    tra định kì trong trường, số câu và thời gian do nhà trường quyết định theo
    Thông tư 22/2021, nên điểm mỗi câu ở đề ngắn KHÁC đề tốt nghiệp — điều này
    được ghi rõ trong ma trận để giáo viên biết mà điều chỉnh.
    """
    chuan = CHUAN_DAY_DU.get(subject, CHUAN_DAY_DU["toan"])
    q = quy_cach(ma_loai)
    ty_le = q.ty_le_cau if q else 1.0

    c1, c2, c3 = chuan["so_cau"]
    if ty_le < 1.0:
        c1 = max(4, round(c1 * ty_le))
        c3 = max(2, round(c3 * ty_le))
        # Phần II GIỮ NGUYÊN 4 câu ở đề định kì. Đây không phải chỗ để rút gọn:
        # Phần II chiếm 40% tổng điểm, cắt bớt câu thì mỗi câu đội lên quá 1,0
        # điểm — lệch hẳn thang của Bộ và rất khó chấm. Chỉ bài kiểm tra ngắn
        # theo chương mới hạ xuống 2 câu.
        c2 = 2 if ty_le <= 0.5 else 4

    t1, t2, t3 = chuan["ty_trong"]

    # Một câu Phần II không bao giờ được vượt 1,0 điểm — đó là trần Bộ đặt ra và
    # cũng là mốc để thang lũy tiến 0,1/0,25/0,5/1,0 còn nguyên nghĩa. Đề ngắn có
    # ít câu Phần II thì phần điểm dôi ra được chia lại cho Phần I và Phần III
    # theo đúng tỉ lệ gốc giữa hai phần đó, chứ không dồn hết vào một câu.
    diem_p2 = min(1.0, 10.0 * t2 / c2)
    con_lai = 10.0 - diem_p2 * c2
    tong_t13 = t1 + t3
    phan_p1 = con_lai * (t1 / tong_t13)
    phan_p3 = con_lai - phan_p1

    ct = CauTrucDe(
        so_cau_p1=c1, so_cau_p2=c2, so_cau_p3=c3,
        diem_moi_cau_p1=_lam_tron(phan_p1 / c1),
        diem_toi_da_p2=_lam_tron(diem_p2),
        diem_moi_cau_p3=_lam_tron(phan_p3 / c3),
        thoi_gian=(q.thoi_gian if q and q.thoi_gian else chuan["thoi_gian"]),
    )
    # Thang lũy tiến co giãn theo điểm tối đa một câu Phần II
    he_so = ct.diem_toi_da_p2 / 1.0
    ct.luy_tien_p2 = [_lam_tron(x * he_so) for x in LUY_TIEN_CHUAN]
    return ct


def kiem_tra_tong_diem(ct: CauTrucDe) -> bool:
    """Ma trận dựng xong LUÔN phải cộng lại bằng 10,0. Không khớp là sai."""
    return abs(ct.tong_diem - 10.0) < 0.05


# ---------------------------------------------------------------------------
# Ma trận mức độ tư duy
# ---------------------------------------------------------------------------
# Từ 2025 chỉ còn BA mức theo GDPT 2018, không còn bốn mức như trước.
MUC_DO = ("Biết", "Hiểu", "Vận dụng")
TY_LE_MUC_DO = (0.40, 0.30, 0.30)   # tỉ lệ tham khảo của Bộ


def phan_bo_muc_do(tong: int) -> Dict[str, int]:
    """Chia số lệnh hỏi theo ba mức, phần dư dồn vào mức Biết."""
    biet = round(tong * TY_LE_MUC_DO[0])
    hieu = round(tong * TY_LE_MUC_DO[1])
    van_dung = tong - biet - hieu
    if van_dung < 0:
        biet += van_dung
        van_dung = 0
    return {"Biết": biet, "Hiểu": hieu, "Vận dụng": van_dung}
