# Bố cục theo từng loại tài liệu

Rút ra từ ~19 video mẫu (tác giả "Hương Ly") trong `D:\Tài liệu số\video mẫu` —
đều là clip lật trang tài liệu Toán / Toán+Tiếng Việt tiểu học lớp 1–5, khổ dọc.

---

## A. PHIẾU BÀI TẬP TUẦN / BÀI TẬP CUỐI TUẦN

**Tổ chức:** theo tuần. Mỗi tuần một "phiếu", đặt tiêu đề `MÔN TOÁN – TUẦN N`.

**Bản trơn:**
- Đầu trang: `Họ và tên: ……………   Lớp: ……`
- Tiêu đề tuần căn giữa, đậm.
- `Bài 1:` `Bài 2:` … in đậm (thường nghiêng), nội dung theo sau.
- Bài đặt tính / tính nhẩm: xếp 2–3 cột.
- Bài giải toán có lời văn: chừa "BÀI GIẢI:" căn giữa + nhiều dòng kẻ chấm `………………`.
- Bài khó đánh dấu `Bài 10 *:`.

**Bản trang trí (video "Bài tập cuối tuần … Lớp 4", "Bài tập kèm đề ôn luyện Toán Lớp 1 trong hè"):**
- Viền trang kiểu vỏ sò / mây, màu pastel (hồng, xanh); có dải cờ đuôi nheo trên đỉnh.
- 4 góc: linh vật trẻ em (bé ngồi bàn, bé bên bảng) + con vật (gấu trúc, hươu cao cổ, thỏ, chim).
- `Bài N` / `Câu N` nằm trong **huy hiệu bo tròn màu** (lục / lam / cam / tím…) treo lệch trái, có ngôi sao/số nhỏ.
- Tiêu đề `MÔN TOÁN – TUẦN 2` trong **hộp bo góc nền vàng nhạt viền nét đứt**, chữ bong bóng.
- Đầu trang: `HỌ TÊN: ……   LỚP: ……`
- Ô tab góc phải trên: `1 2 3 4 5` (đánh dấu tuần).
- Section trong đề trắc nghiệm: `A. TRẮC NGHIỆM` / `B. TỰ LUẬN` căn giữa đậm.
- Bài "Đặt tính rồi tính": các **ô kẻ vuông rỗng** để học sinh viết phép tính dọc.
- Chỗ điền ẩn số dùng hình `☆` hoặc `□`: ví dụ `18 − ☆ = 10`, `35 + □ = 77`.
- Trắc nghiệm: mỗi phương án `A. …` `B. …` trong **ô bo tròn** riêng, 2–4 ô/hàng.
- Rải rác: sao, cầu vồng, con ong, cây xương rồng mặt cười, bút chì, máy tính, tàu hỏa, bóng đèn.
- Chân trang: băng-rôn ruy-băng vàng `EM LÀM BÀI THẬT TỐT NHÉ!` + hàng số lớn `8 9 ÷ 6`.

`kidbook.py` tái tạo: viền `doubleWave` màu · băng-rôn tiêu đề · `probbox` thẻ màu + emoji ·
`nameline` · `footerbanner`. Chưa có: linh vật, huy hiệu số ngoài lề, ô kẻ vuông.

---

## B. PHIẾU DẶN DÒ / BÀI TẬP HÀNG NGÀY

**Tổ chức:** theo THỨ trong tuần. Tiêu đề `PHIẾU DẶN DÒ TUẦN N` (hoặc "Phiếu bài tập hàng ngày").
- Đầu trang `Họ và tên: …   Lớp: …`.
- Khung viền mảnh (nét đôi) quanh trang, không trang trí.
- Đầu mỗi ngày: `Thứ Hai` `Thứ Ba` … (đậm, gạch chân, nghiêng).
- Item đánh `Bài 1.` `Bài 2.` (chấm, không hai chấm) hoặc chỉ `1.` `2.`.
- Trộn Toán + Tiếng Việt: mục Toán là tính toán, mục TV là câu/từ.
- Sub-part `a)` `b)` `c)` `d)` — xếp 2 cột với bài tính.
- Rất nhiều dòng kẻ chấm để làm ngay dưới đề.
- Phông Times New Roman, cỡ vừa.

`kidbook.py`: dùng `newdoc` + `restyle`; Heading 1 cho `Thứ Hai`, `probbox` cho từng bài,
hoặc để trơn với `d.add_paragraph` + `_KB.answerlines(d, 3)` chèn dòng kẻ chấm.

---

## C. ĐỀ KIỂM TRA / ĐỀ THI MINH HỌA

Bố cục **đề nhà trường chuẩn**:

```
TRƯỜNG: ………………                    KIỂM TRA CUỐI HỌC KÌ II
Lớp: ……                                MÔN: TOÁN LỚP 3  (Đề số 1)
Họ và tên: ………………                    (Thời gian làm bài: 40 phút)

┌────────┬──────────────────────────┬────────────────────┐
│ Điểm   │ Nhận xét của thầy cô     │ Giáo viên chấm     │
│        │ …………………………………           │ (kí và ghi rõ họ tên)│
│        │ …………………………………           │ 1. ………………          │
└────────┴──────────────────────────┴────────────────────┘

I. PHẦN TRẮC NGHIỆM. (4 điểm)  Khoanh vào chữ cái đặt trước câu trả lời đúng:
  Câu 1. ………………………?
     A. …………     B. …………     C. …………     D. …………
  …
II. PHẦN TỰ LUẬN. (6 điểm)
  Câu 9. (2 điểm) ………
  …
```

- `Câu N.` in đậm màu navy; nội dung câu màu xanh đậm.
- Bài xem đồng hồ: chèn 4 hình đồng hồ A/B/C/D.
- Tổng điểm cân theo cấp: TN 40% + TL 60%; mỗi câu TN thường 0,5 điểm.

**Đáp án / Hướng dẫn chấm** (bắt buộc, tách trang cuối):
- `Đáp án` → `Phần I. Trắc nghiệm`: bảng `Câu 1 (0,5đ) | Câu 2 (0,5đ) | …` + hàng chữ cái.
- `Phần II. Tự luận`: từng câu ghi lại đề + lời giải, **mỗi bước có điểm trong ngoặc nghiêng** `(0,25 điểm)`, `(0,125 điểm)`.
- Bài toán có lời văn: `Bài giải` căn giữa.

`kidbook.py`: `cover` → header đề (dùng `nameline` + banner "KIỂM TRA…"); tạo bảng
Điểm/Nhận xét bằng `doc.add_table(2,3)`; `d.add_heading("I. PHẦN TRẮC NGHIỆM. (4 điểm)", level=1)`;
`probbox` cho từng câu (kèm dòng "A. … B. …" ngay dưới).
Với sách "N đề": mỗi đề `d.add_heading(f"ĐỀ SỐ {k}", level=1)`, cuối cuốn "HƯỚNG DẪN CHẤM VÀ ĐÁP SỐ".

---

## D. ĐỀ CƯƠNG ÔN TẬP

Như C nhưng tổ chức theo chủ đề trước, đề minh họa sau; luôn "có đáp án chi tiết".
Đầu cuốn liệt kê "Nội dung ôn tập" theo mạch kiến thức của kì.

---

## E. CHUYÊN ĐỀ / CẨM NANG / BỒI DƯỠNG HSG

- Chia theo `Dạng 1`, `Dạng 2`, … hoặc `Chủ đề 1`, …
- Mỗi dạng: ô **GHI NHỚ** (💡, 2–4 gạch đầu dòng tóm phương pháp) → rồi bài tập.
- Mỗi bài: đề (thẻ màu) → `Lời giải` chi tiết → `Đáp số:` đậm.
- Sách "N đề luyện HSG": mỗi đề 5–6 bài trải đều mạch kiến thức, cuối cuốn có hướng dẫn chấm.

`kidbook.py`: dùng `build_chuyende_book` (xem `kien-truc-engine.md`), `ghinho` cho phần GHI NHỚ.

---

## F. ÔN HÈ / KHẢO SÁT CHẤT LƯỢNG ĐẦU NĂM

- "Ôn hè lớp N lên N+1": tổ chức theo tuần hè (Tuần 1…Tuần 8), mỗi tuần vài bài Toán + vài bài TV.
- "Khảo sát chất lượng đầu năm lớp N": một–hai đề như loại C, độ khó ôn lại lớp N−1.
- Kèm "đề khảo sát" cuối cuốn.

---

## Ghi chú chung về HÌNH & KÍ HIỆU

- Hình học: tam giác/tứ giác/hình thang dựng bằng đường thẳng, ghi nhãn đỉnh A B C D E F.
- "Đếm hình": lưới ô vuông có vài số điền sẵn, hỏi tổng số hình / số tam giác.
- Đồng hồ: mặt số 12 giờ, kim giờ–phút; dùng cho bài "xem giờ".
- Ẩn số cho lớp nhỏ: `☆` hoặc `□` thay cho `x`.
- Đơn vị: `m²`, `dm²`, `l` (lít) — giữ nguyên kí hiệu.
- Số lớn tách nhóm 3 chữ số bằng dấu cách: `12 356` (không dùng dấu chấm).
