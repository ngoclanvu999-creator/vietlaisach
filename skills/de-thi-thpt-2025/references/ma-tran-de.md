# Bảng tra nhanh — ma trận đề thi THPT từ 2025

Tra khi cần dựng ma trận đề hoặc kiểm tra một đề có đúng chuẩn không.

## Toán — 22 câu / 34 lệnh hỏi / 90 phút

| Phần | Dạng | Số câu | Điểm/câu | Tổng điểm | Mức độ chính |
|---|---|---|---|---|---|
| I | Trắc nghiệm 4 lựa chọn | 12 | 0,25 | 3,0 | Biết, Hiểu |
| II | Đúng/Sai (4 ý mỗi câu) | 4 | tối đa 1,0 | 4,0 | Hiểu, Vận dụng |
| III | Trả lời ngắn | 6 | 0,50 | 3,0 | Vận dụng |
| | | **22** | | **10,0** | |

## Vật lí — 28 câu / 40 lệnh hỏi / 50 phút

| Phần | Dạng | Số câu | Điểm/câu | Tổng điểm |
|---|---|---|---|---|
| I | Trắc nghiệm 4 lựa chọn | 18 | 0,25 | 4,5 |
| II | Đúng/Sai (4 ý mỗi câu) | 4 | tối đa 1,0 | 4,0 |
| III | Trả lời ngắn | 6 | 0,25 | 1,5 |
| | | **28** | | **10,0** |

Hóa học và Sinh học dùng chung cấu trúc với Vật lí.

## Thang điểm Phần II (lũy tiến, KHÔNG chia đều)

| Số ý đúng | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| Điểm | 0 | **0,10** | **0,25** | **0,50** | **1,00** |

Công thức Python:

```python
def diem_dung_sai(so_y_dung: int) -> float:
    """Điểm một câu Đúng/Sai theo số ý trả lời đúng (thang lũy tiến của Bộ)."""
    return {0: 0.0, 1: 0.1, 2: 0.25, 3: 0.5, 4: 1.0}[so_y_dung]
```

Sai lầm hay gặp: tính `0.25 * so_y_dung`. Đúng 2 ý ra 0,5 trong khi thực tế
chỉ được 0,25.

## Tính điểm toàn bài

```python
def tong_diem(mon: str, dung_phan1: int, so_y_dung_moi_cau: list, dung_phan3: int) -> float:
    diem_p3 = 0.5 if mon == "toan" else 0.25
    return (dung_phan1 * 0.25
            + sum(diem_dung_sai(n) for n in so_y_dung_moi_cau)
            + dung_phan3 * diem_p3)
```

## Mức độ tư duy

Ba mức của GDPT 2018 — **Biết / Hiểu / Vận dụng**, tỉ lệ tham khảo 40/30/30.

Lưu ý: từ 2025 KHÔNG còn dùng bốn mức "Nhận biết – Thông hiểu – Vận dụng –
Vận dụng cao". Tài liệu nào vẫn ghi bốn mức là theo chuẩn cũ trước 2025.

## Lời dẫn chuẩn từng phần

Chép nguyên văn vào đề, không tự diễn đạt lại:

> **PHẦN I.** Thí sinh trả lời từ câu 1 đến câu {n}. Mỗi câu hỏi thí sinh chỉ
> chọn một phương án.

> **PHẦN II.** Thí sinh trả lời từ câu 1 đến câu 4. Trong mỗi ý a), b), c), d)
> ở mỗi câu, thí sinh chọn đúng hoặc sai.

> **PHẦN III.** Thí sinh trả lời từ câu 1 đến câu 6.

Cuối đề:

> ---------- HẾT ----------
>
> Thí sinh không được sử dụng tài liệu. Cán bộ coi thi không giải thích gì thêm.
