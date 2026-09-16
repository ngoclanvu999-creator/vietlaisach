---
name: toan-tieu-hoc
description: >-
  Playbook biên soạn lại và trình bày bộ sách bài tập TOÁN TIỂU HỌC (mầm non, lớp 1–5)
  thành file Word theo phong cách "bài tập cuối tuần / phiếu ôn tập" của kho
  D:\Tài liệu số. Dùng khi: tạo mới hoặc bổ sung cuốn Toán tiểu học; sửa nội dung
  hoặc sửa TRÌNH BÀY (định dạng) các cuốn đã có; cần quy ước bố cục theo từng loại
  tài liệu (phiếu bài tập tuần, đề kiểm tra, đề cương ôn tập, chuyên đề, ôn hè,
  khảo sát đầu năm); hoặc dựng lại & deploy hàng loạt. KHÔNG dùng cho THCS/THPT.
---

# Toán tiểu học — biên soạn & trình bày

Bộ sách gồm ~70 cuốn: mầm non 3, lớp 1: 11 (gồm 3 mầm non), lớp 2: 9, lớp 3: 8, lớp 4: 5, lớp 5: 37.
Mỗi cuốn là **file Word tự dựng**, thay thế/bổ sung cho sách tham khảo gốc trong kho `D:\Tài liệu số\Toán\Toán N\`.

## 1. Nguyên tắc nội dung — BẮT BUỘC

1. **Tự sinh toàn bộ đề bằng Python.** Mọi đáp số phải được **tính và kiểm chứng bằng code** (dùng `assert` trong hàm sinh; `fractions.Fraction` cho số học chính xác).
2. **KHÔNG sao chép nguyên văn** sách gốc; **KHÔNG ghi nguồn**. Số lượng bài phải KHÁC bản gốc; khác cả nội dung lẫn hình thức.
3. **KHÔNG xóa/sửa file gốc.** Chỉ *thêm* file `.docx` mới bên cạnh. File gốc thường có đuôi mô tả kiểu "(Có lời giải tham khảo)" — không đụng vào.
4. Phạm vi kiến thức bám **CT GDPT 2018** theo từng lớp — xem `references/pham-vi-theo-lop.md`.
5. Phân số phải hiển thị dạng **phân số xếp chồng chuẩn SGK** (OMML / Word Equation) → luôn chạy `assets/omml_fix.py` sau khi dựng .docx, trước khi deploy.
6. Số thập phân dùng **dấu phẩy** (`1,5` không phải `1.5`). Dấu trừ dùng `−` (U+2212), không phải `-`.
7. Không để lọt "None", `^`, `x^2`, `((`, `+ −`, `− −` trong văn bản cuối. Có bộ scan artifact ở `references/pipeline.md`.

## 2. Loại tài liệu và BỐ CỤC (theo video mẫu ở `D:\Tài liệu số\video mẫu`)

Tài liệu tiểu học chia thành các LOẠI, mỗi loại có quy ước trình bày riêng.
Chi tiết đầy đủ + mô tả từng khung hình video: `references/bo-cuc-theo-loai.md`. Tóm tắt:

| Loại | Tổ chức | Đặc điểm bắt buộc |
|---|---|---|
| **Phiếu / Bài tập cuối tuần** | theo TUẦN | "MÔN TOÁN – TUẦN N" (băng-rôn), dòng *Họ và tên / Lớp*, "Bài N:" đậm, dòng kẻ chấm để làm, lời động viên cuối trang. Bản "cao cấp" có viền trang, linh vật, huy hiệu số. |
| **Phiếu dặn dò / bài tập hàng ngày** | theo THỨ (Thứ Hai…Thứ Sáu) | "PHIẾU DẶN DÒ TUẦN N", đầu mục là "Thứ Hai" (gạch chân nghiêng), item đánh "Bài N." hoặc chỉ "N.", nhiều dòng kẻ chấm, ít trang trí. |
| **Đề kiểm tra / Đề thi minh họa** | theo ĐỀ | Header: TRƯỜNG… / "KIỂM TRA … MÔN: TOÁN LỚP N (Đề số k)" / "(Thời gian 40 phút)". Bảng **Điểm – Nhận xét của thầy cô – Giáo viên chấm**. "I. Phần trắc nghiệm (X điểm)" + "II. Phần tự luận (X điểm)". "Câu N." đậm màu navy. Đáp án: bảng chữ cái + **hướng dẫn chấm chi tiết điểm từng bước** "(0,25 điểm)". |
| **Đề cương ôn tập** | theo CHỦ ĐỀ / kỳ | Hệ thống câu hỏi kiểu đề thi, có đáp án. Kèm 1–2 "đề thi minh họa" cuối cuốn. |
| **Chuyên đề / Cẩm nang / Bồi dưỡng HSG** | theo DẠNG / CHỦ ĐỀ | Mỗi dạng mở đầu bằng ô **GHI NHỚ** (💡, tóm tắt phương pháp), rồi bài tập có lời giải chi tiết. |
| **Ôn hè / Khảo sát đầu năm** | theo TUẦN hè hoặc theo ĐỀ | Bắc cầu lớp N → N+1. Cấu trúc như phiếu tuần hoặc như đề khảo sát. |

**Phong cách hình ảnh:** có hai truyền thống trong kho mẫu —
- **Trơn (đa số phiếu/đề):** phông Times New Roman, không viền, chỉ dùng dòng kẻ chấm + bảng + hình vẽ. Sạch, giống đề nhà trường.
- **Trang trí ("bài tập cuối tuần" cao cấp):** viền trang kiểu sóng/mây màu, linh vật hoạt hình ở 4 góc, "Bài N"/"Câu N" trong huy hiệu tròn màu, ô làm bài kẻ ô vuông, hình sao/cầu vồng/con vật rải rác, chân trang "EM LÀM BÀI THẬT TỐT NHÉ!".

`assets/kidbook.py` dựng lại **phong cách trang trí** trong giới hạn của python-docx (viền trang, băng-rôn màu, thẻ bài màu, huy hiệu emoji, dòng họ tên, GHI NHỚ, chân trang động viên). Nó **chưa** làm được: ảnh linh vật clip-art, huy hiệu số nổi ngoài lề, ô kẻ vuông đặt tính. Nếu người dùng cần linh vật clip-art → phải nhúng ảnh (nêu rõ giới hạn/bản quyền trước khi làm).

## 3. Hệ thống trình bày — `assets/kidbook.py`

Thư viện dùng chung cho MỌI driver dựng sách tiểu học. Copy vào thư mục làm việc rồi:

```python
import kidbook as _KB
from kidbook import newdoc, cover, probbox, ghinho, toc
_KB.set_grade("LỚP 3")          # MẦM NON | LỚP 1..5 — quyết định màu accent
d = newdoc()                     # viền trang doubleWave + phông + style Heading
cover(d, "96 BÀI TẬP NÂNG CAO TOÁN LỚP 3", "96 bài — chia 7 phần, có lời giải chi tiết")
d.add_heading("PHẦN 1 — Nhân, chia trong bảng", level=1)   # -> băng-rôn màu
d.add_heading("Bài 1", level=2)                             # -> tiêu đề màu gạch chân
probbox(d, ["Một cửa hàng có 5 thùng, mỗi thùng 8 hộp bánh. Hỏi có bao nhiêu hộp?"])  # thẻ màu + emoji
d.add_heading("Lời giải", level=3)
d.add_paragraph("Số hộp bánh: 5 × 8 = 40 (hộp).")
d.add_paragraph().add_run("Đáp số: 40 hộp.").bold = True
ghinho(d, "Nhân chia trong bảng", ["Gấp n lần: nhân với n.", "Tìm 1/n: chia cho n."])
_KB.footerbanner(d)              # "EM ĐÃ CỐ GẮNG RẤT NHIỀU — GIỎI QUÁ!"
d.save("...docx")
```

Quy tắc quan trọng khi mở rộng `kidbook.py`:
- Ô có nền + viền → **dùng một đoạn văn** (`_boxpara`) với `_para_shade_border`, KHÔNG dùng table 1-cell (Word vẽ viền lệch trái/dưới).
- `probbox` giữ chữ ký `probbox(doc, lines)` để mọi driver cũ chạy được không cần sửa.
- `ghinho` nhận cả `ghinho(doc, title, lines)` lẫn `ghinho(doc, noi_dung)`.
- Màu accent theo lớp: MN hồng · L1 cam · L2 lục · L3 lam · L4 tím · L5 xanh mòng két.

## 4. Kho code & vị trí deploy

- **Engine sinh đề + driver dựng .docx** nằm trong thư mục làm việc của phiên
  (`…\scratchpad\lopN_common\genNc.py`, `…\scratchpad\lN_build\build_lN.py`, v.v.).
  Nếu bắt đầu phiên mới mà không còn → xem `references/kien-truc-engine.md` để dựng lại
  theo đúng khuôn (hàm `gp_xxx(seed)` trả `{"de":[...], "giai":[...], "dap":"..."}`).
- **Deploy 2 nơi** (chi tiết lệnh: `references/pipeline.md`):
  1. Kho nguồn: `D:\Tài liệu số\Toán\Toán N\{5,6,7,8}\<Tên Tiếng Việt Đẹp>.docx`
  2. Chương trình: `D:\Tài liệu số\Tiểu học 2026-2027\Lớp N\09. Bồi dưỡng HSG - Nâng cao - Luyện thi\LopN-<slug>.docx` + cập nhật `MUC_LUC_LopN.xlsx`
  - **Lớp 4 KHÔNG có thư mục chương trình** → chỉ deploy vào kho nguồn `Toán 4\5. Học sinh giỏi và Olympic\`.

## 5. Quy trình dựng / sửa một cuốn

1. **Khảo sát** file gốc trong kho (đọc mục lục, ước lượng số bài, xác định loại tài liệu ở §2).
2. **Thiết kế bản thay thế**: tên mới hấp dẫn, số bài khác gốc, cấu trúc lại theo PARTS/CHUYEN_DE.
3. **Mở rộng engine** nếu thiếu dạng (thêm hàm `gp_*`; test `python genNc.py` → `bad = 0`, `distinct` đủ lớn).
4. **Dựng .docx** qua driver (dùng `kidbook`).
5. **`python -c "import omml_fix; ..."`** trên toàn bộ .docx vừa dựng (lệnh ở `references/pipeline.md`).
6. **Scan artifact** (không None/`^`/`((`/`+ −`/`.` giữa số).
7. **Kiểm tra hiển thị thật** bằng Word COM → PDF → ảnh (§6).
8. **Deploy** + cập nhật mục lục.

## 6. Kiểm tra hiển thị (không có LibreOffice → dùng MS Word COM)

```bash
# .ps1 PHẢI ghi bằng utf-8-sig, nếu không PowerShell đọc sai đường dẫn tiếng Việt
python - <<'PY'
import subprocess
lines = ['$w=New-Object -ComObject Word.Application','$w.Visible=$false',
  '$d=$w.Documents.Open("D:\\...\\file.docx"); $d.SaveAs([ref]"D:\\...\\out.pdf",[ref]17); $d.Close($false)',
  '$w.Quit()']
open('c.ps1','w',encoding='utf-8-sig').write("\n".join(lines))
subprocess.run(['powershell.exe','-NoProfile','-File','c.ps1'],check=True)
PY
python -c "import pymupdf; d=pymupdf.open('out.pdf'); [d[i].get_pixmap(dpi=110).save(f'p{i}.png') for i in (0,3)]"
# rồi Read các p*.png
```
Gói cần: `pymupdf`, `imageio-ffmpeg` (trích khung video mẫu) — cài bằng `pip install pymupdf imageio-ffmpeg`.
Lưu ý: emoji trong bản raster pymupdf hiện đen trắng; trên MS Word thật sẽ là emoji màu → không cần lo.

## 7. Dựng lại & đồng bộ ĐỊNH DẠNG hàng loạt cho cuốn đã deploy

Khi chỉ đổi trình bày (không đổi nội dung): rebuild toàn bộ → omml → chạy `assets/resync_pretty.py`.
Script khớp từng file đã deploy với file vừa dựng **theo tiêu đề bìa** (run ≥22pt, gộp mọi mảnh)
rồi ghi đè tại chỗ, không đổi tên/vị trí. Tự bỏ qua file gốc và file Tiếng Việt/Khoa học.
Kiểm tra trước bằng `python resync_pretty.py -v` (in danh sách "chưa khớp").

## Tài liệu tham khảo trong skill
- `references/bo-cuc-theo-loai.md` — bố cục chi tiết từng loại + ghi chú các khung hình video mẫu
- `references/pham-vi-theo-lop.md` — phạm vi kiến thức CT2018 lớp 1–5 + mầm non
- `references/kien-truc-engine.md` — khuôn engine `gp_*` / driver / các hàm builder
- `references/pipeline.md` — lệnh omml, scan artifact, deploy, mục lục
- `assets/kidbook.py`, `assets/omml_fix.py`, `assets/analyze_fractions.py`, `assets/resync_pretty.py`
