# Pipeline: dựng → omml → scan → deploy → mục lục

Mọi lệnh chạy trong thư mục driver (`…\scratchpad\lN_build\` …). Đặt biến môi trường
`PYTHONUTF8=1` (Windows/Git-Bash) để tránh lỗi encode khi in tiếng Việt.

## 1. Dựng .docx

```bash
cp <skill>/assets/kidbook.py .            # kèm omml_fix.py, analyze_fractions.py
PYTHONUTF8=1 python build_lN.py           # -> in "DONE <file> -> <n> bài"
```
Nếu một thư mục có nhiều driver (lớp 5: `build_f6.py` + `build_hsg.py` …) → chạy hết,
`rm -f *.docx` trước để không lẫn bản cũ.

## 2. omml_fix — đổi "a/b" thành phân số xếp chồng (BẮT BUỘC trước deploy)

```bash
PYTHONUTF8=1 python -c "
import glob, omml_fix
tot = 0
for f in sorted(glob.glob('*.docx')):
    ch, _ = omml_fix.process_docx(f); tot += ch
print(len(glob.glob('*.docx')), 'files', tot, 'phân số')
"
```
`omml_fix.process_docx(path, path_out=None)` quét paragraph + table, bỏ qua ngày tháng / đơn vị.

## 3. Scan artifact (không được có kết quả)

```bash
PYTHONUTF8=1 python -c "
import glob, re
from docx import Document
pat = re.compile(r'None|\bsqrt\b|\^[A-Za-z0-9(]|x\^|\*\*|log_\d'
                 r'|(?<![\d,√])\d\.\d|·−\d|\+ −|− −|Traceback|3x²x')
tot = 0
for f in sorted(glob.glob('*.docx')):
    d = Document(f); T = [p.text for p in d.paragraphs]
    for t in d.tables:
        for r in t.rows:
            for c in r.cells: T.append(c.text)
    hh = {(m.group(0), s.strip()[:90]) for s in T for m in pat.finditer(s)}
    if hh:
        print('==', f); [print('  ', repr(g), ex) for g, ex in list(hh)[:5]]; tot += len(hh)
print('HITS', tot)
"
```
Lưu ý false-positive hay gặp: `((x+y)/2)²` (đúng), `√((−8)²…)` (đúng), gap chữ do OMML để lại
(dạng `= − − 0 = −` khi hai phân số kề nhau) — trên Word thật hiện đúng phân số.

## 4. Kiểm tra hiển thị bằng MS Word (xem §6 SKILL.md) — làm cho ≥ 2 cuốn / lớp.

## 5. Deploy

### Lớp 1, 2, 3, mầm non — có sẵn script MAP
```bash
PYTHONUTF8=1 python deploy_lN.py          # copy build_file -> (kho nguồn: tên VN) + (curriculum: LopN-slug)
PYTHONUTF8=1 python mucluc_lN.py          # dựng lại MUC_LUC_LopN.xlsx (đọc số từ .docx đã deploy)
```
`deploy_lN.py` chứa `MAP = [(build_file, source_folder, "Tên Tiếng Việt.docx", "LopN-slug.docx"), …]`.
Curriculum: `D:\Tài liệu số\Tiểu học 2026-2027\Lớp N\09. Bồi dưỡng HSG - Nâng cao - Luyện thi\`.
Nguồn: `D:\Tài liệu số\Toán\Toán N\{5. Học sinh giỏi và Olympic | 6. Bài tập bổ trợ và nâng cao | 7. Toán tư duy…}\`.

### Lớp 4 — CHỈ kho nguồn
`D:\Tài liệu số\Toán\Toán 4\5. Học sinh giỏi và Olympic\<Tên Tiếng Việt>.docx`.
Không có thư mục `Tiểu học 2026-2027\Lớp 4\09…`. (Thư mục Lớp 4 hiện chỉ có tài liệu Toán+TV KNTT của bên khác — không đụng.)

### Lớp 5 — deploy tản mát (nhiều helper cũ: `add_f6_mucluc.py`, `upd_mucluc5.py` …)
Curriculum `Tiểu học 2026-2027\Lớp 5\09…\Lop5-*.docx` + nguồn `Toán 5\{5,6,7,8}\<Tên VN>.docx`
(`8. Ôn thi vào lớp 10` **không có ở tiểu học** — lớp 5 dùng `Toán 5\5,6,7` và thư mục thi vào 6).
Cách chắc chắn nhất: **dùng `assets/resync_pretty.py`** (xem §7 SKILL.md) — khớp theo tiêu đề bìa, ghi đè tại chỗ.

## 6. Đồng bộ định dạng hàng loạt (khi CHỈ đổi trình bày)

```bash
# 1) rebuild toàn bộ driver tiểu học  2) omml_fix mỗi thư mục
cp <skill>/assets/resync_pretty.py .
PYTHONUTF8=1 python resync_pretty.py -v     # xem "chưa khớp" (chỉ được còn file gốc + Tiếng Việt/Khoa học)
PYTHONUTF8=1 python resync_pretty.py        # ghi đè
```
Sửa `BUILD_DIRS` trong script cho khớp tên thư mục driver hiện tại nếu cần.
`cover_title()` trong script gom mọi run ≥ 22pt (kể cả tiêu đề 2 dòng) rồi chuẩn hoá để so khớp.

## 7. Bảng vị trí nhanh

| Lớp | Kho nguồn (Toán N\...) | Curriculum |
|---|---|---|
| MN | `Toán 1\7. Toán tư duy và chuẩn bị vào lớp 1` | `Tiểu học 2026-2027\Lớp 1\09…` (chung lớp 1) |
| 1 | `Toán 1\{5,6,7}` | `…\Lớp 1\09…` + `MUC_LUC_Lop1.xlsx` |
| 2 | `Toán 2\{5,6,7}` | `…\Lớp 2\09…` + `MUC_LUC_Lop2.xlsx` |
| 3 | `Toán 3\{5,6,7}` | `…\Lớp 3\09…` + `MUC_LUC_Lop3.xlsx` |
| 4 | `Toán 4\5. Học sinh giỏi và Olympic` | (không có) |
| 5 | `Toán 5\{5,6,7}` + thư mục thi vào 6 | `…\Lớp 5\09…` + `MUC_LUC_Lop5.xlsx` |

Tên subfolder có thể khác nhau giữa các lớp ("6. Bài tập bổ trợ và nâng cao" vs "6. Bổ trợ - Nâng cao"…)
→ luôn `ls "D:\Tài liệu số\Toán\Toán N"` để lấy tên chính xác trước khi deploy.
