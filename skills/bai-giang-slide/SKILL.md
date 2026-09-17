---
name: bai-giang-slide
description: >-
  Nguyên tắc thiết kế BÀI GIẢNG POWERPOINT dạy trên lớp: bám tiến trình bốn hoạt
  động của kế hoạch bài dạy, mỗi slide một ý, tách slide đề và slide đáp án, lời
  giải dài đưa xuống ghi chú người trình bày, cỡ chữ và mức trang trí theo cấp
  học. Dùng khi dựng BÀI GIẢNG / SLIDE / TRÌNH CHIẾU cho tiết dạy. KHÔNG dùng
  cho tài liệu in ra giấy.
---

# Bài giảng PowerPoint — nguyên tắc thiết kế

> **CẢNH BÁO VỀ NGUỒN.** Khác với các skill còn lại, tệp này **không đo từ mẫu
> thật**. Kho tài liệu chỉ có 10 tệp bài giảng và chủ dự án chưa cung cấp video
> mẫu, nên toàn bộ nội dung dưới đây là **đề xuất chuyên môn của trợ lý**.
>
> Chủ dự án nên đọc kỹ tệp này hơn ba skill kia, và sửa thẳng chỗ nào thấy không
> hợp với cách dạy thực tế. Khi nào có mẫu thật thì đo lại và thay tệp này.
>
> Viết ngày 17/09/2026 theo yêu cầu *"bài giảng powerpoint thì bạn tự làm 1 skill"*.

---

## 1. Neo vào tiến trình tiết dạy, không tự bịa mạch

Bài giảng tồn tại để phục vụ **một tiết dạy**, mà tiết dạy ở Việt Nam đi theo bốn
hoạt động của kế hoạch bài dạy (xem skill `giao-an-5512`). Nên mạch slide bám
đúng bốn hoạt động đó — đây là chỗ duy nhất trong tệp này có căn cứ văn bản:

| Hoạt động | Slide làm gì | Số slide gợi ý |
|---|---|---|
| **1. Mở đầu** | Nêu tình huống, câu hỏi khơi vấn đề | 1–2 |
| **2. Hình thành kiến thức mới** | Dẫn dắt tới khái niệm, chốt kiến thức | 4–6 |
| **3. Luyện tập** | Bài tập, mỗi bài **hai slide**: đề rồi đáp án | 8–12 |
| **4. Vận dụng** | Bài gắn thực tiễn, giao về nhà | 1–2 |

Thêm slide bìa và slide kết. **Tổng 16–24 slide cho một tiết 45 phút.** Nhiều hơn
là chiếu không kịp, ít hơn là mỗi slide nhồi quá nhiều.

---

## 2. Quy tắc cứng nhất: slide để CHIẾU LÊN, không để đọc

Đây là lỗi phổ biến nhất khi chuyển tài liệu Word thành slide — bê nguyên đoạn
văn lên rồi cỡ chữ 14pt, học sinh bàn cuối không đọc được và giáo viên quay lưng
đọc màn hình.

| | Ngưỡng |
|---|---|
| Cỡ chữ tiêu đề slide | ≥ 30pt |
| Cỡ chữ nội dung | ≥ 24pt |
| Cỡ chữ nhỏ nhất được phép | 20pt |
| Số dòng chữ trên một slide | ≤ 7 |
| Số chữ trên một dòng | ≤ 12 |

**Một slide một ý.** Nếu một slide cần cuộn mắt để đọc hết thì phải tách đôi.

Dùng phông **không chân** (Arial) cho slide, khác với tài liệu in dùng Times New
Roman — chữ có chân nhòe khi chiếu qua máy chiếu độ phân giải thấp.

---

## 3. Tách slide đề và slide đáp án

Mỗi bài luyện tập chiếm **hai slide liền nhau**:

```
┌─────────────────────┐      ┌─────────────────────┐
│ BÀI 3               │      │ BÀI 3 — ĐÁP ÁN      │
│                     │  →   │                     │
│ Giải phương trình:  │      │ B. x = 5            │
│    2ˣ = 32          │      │                     │
│                     │      │ 32 = 2⁵ nên x = 5   │
│ A. 4   B. 5         │      │                     │
│ C. 6   D. 8         │      │                     │
└─────────────────────┘      └─────────────────────┘
   giáo viên dừng ở đây         bấm sang khi đã đủ thời gian
   cho học sinh nghĩ
```

Gộp đề và đáp án vào một slide là **hỏng hẳn giá trị sư phạm**: học sinh nhìn
thấy đáp án trước khi kịp nghĩ.

---

## 4. Lời giải dài đưa xuống ghi chú người trình bày

Slide đáp án chỉ hiện **kết quả và bước then chốt** (tối đa 3 dòng). Lời giải đầy
đủ đặt ở **phần ghi chú** của slide — chỉ giáo viên nhìn thấy ở chế độ trình bày,
học sinh không thấy.

Ghi chú cũng là chỗ đặt gợi ý điều hành lớp: *"Cho học sinh suy nghĩ 1–2 phút
trước khi chuyển slide"*, *"Hỏi thêm: nếu đổi cơ số thành 3 thì sao?"*.

---

## 5. Mức trang trí theo cấp học

Theo đúng quy tắc chung của dự án (xem `core/trang_tri.py`):

| Cấp | Nền | Biểu tượng | Màu nhấn |
|---|---|---|---|
| **Tiểu học** | Vàng kem ấm | Có — mỗi mục một biểu tượng | Cam đất, xanh lá |
| **THCS** | Trắng ngà | Rất ít | Xanh dương |
| **THPT** | Trắng | Không | Xanh navy |

Tiểu học được dùng biểu tượng vì trẻ cần mốc thị giác để bám theo. THPT không
dùng, vì slide đầy biểu tượng làm mất tính nghiêm túc của tiết học.

**Ràng buộc chung cho mọi cấp:** nền phải tương phản mạnh với chữ. Không dùng ảnh
nền phía sau chữ, không dùng chữ màu nhạt trên nền màu.

---

## 6. Hình ảnh — dùng khi giải thích được, không dùng để lấp chỗ

Hình chỉ đưa lên slide khi nó **giải thích điều mà lời nói khó diễn đạt**: đồ thị
hàm số, hình không gian, sơ đồ tư duy, mô hình thí nghiệm.

Không đưa ảnh minh họa chung chung (học sinh cười, sách vở, bóng đèn ý tưởng) —
nó chiếm chỗ mà không dạy gì.

Hình có chữ bên trong phải đủ to để đọc từ cuối lớp, nếu không thì bỏ.

---

## 7. Danh mục tự kiểm trước khi đưa lên lớp

Dựng xong chạy qua bảy câu này:

1. Slide nào có quá 7 dòng chữ không?
2. Có slide nào chữ dưới 20pt không?
3. Mỗi bài luyện tập đã tách đủ hai slide đề và đáp án chưa?
4. Lời giải dài đã xuống ghi chú chưa, hay còn nằm trên slide?
5. Tổng số slide có nằm trong khoảng 16–24 không?
6. Mức trang trí có đúng cấp học không?
7. Có hình nào chỉ để cho đẹp không? Bỏ đi.

---

## 8. Những điều cố tình KHÔNG đưa vào

- **Không hiệu ứng chuyển slide cầu kỳ.** Chúng làm chậm tiết dạy và phân tán
  học sinh. Nhiều nhất là hiệu ứng mờ dần.
- **Không chữ chạy, không âm thanh nền.**
- **Không đánh số câu theo kiểu tài liệu in** (`Câu T1.`, `Câu H1.`) — trên slide
  chỉ cần `BÀI 1`, `BÀI 2` cho ngắn gọn dễ nhìn.
- **Không in thang điểm** lên slide; slide là để dạy, không phải để chấm.
