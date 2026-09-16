# Kiến trúc engine & driver

Mỗi lớp có **1 engine** (sinh đề) + **1 hoặc vài driver** (dựng .docx).
Tất cả nằm trong thư mục làm việc của phiên (`…\scratchpad\`). Nếu mất, dựng lại theo khuôn dưới.

## 1. Engine `genNc.py` — hàm sinh đề

```python
# helper chuẩn hoá
_NEG = re.compile(r'(?<![\w\d.])-(?=\d)')
def _fix(s):
    s = _NEG.sub('−', s)                       # -3 -> −3
    for _ in range(3):
        s = (s.replace(" + −"," − ").replace(" − −"," + ")
               .replace("+ −","− ").replace("− −","+ "))
    s = re.sub(r'·−(\d)', r'·(−\1)', s)
    s = re.sub(r'−\s*\(−(\d+)\)', r'+ \1', s)
    s = re.sub(r'\+\s*\(−(\d+)\)', r'− \1', s)
    s = re.sub(r'(?<![\w.])1([xyz])\b', r'\1', s)          # 1x -> x
    s = re.sub(r'(?<=\d)\.(?=\d)', ',', s)                 # 1.5 -> 1,5
    s = s.replace("  ", " ")
    return _sup(s)                              # ^n -> lũy thừa unicode (nếu cần)

def _r(de, giai, dap):
    de   = [de]   if isinstance(de,str)   else list(de)
    giai = [giai] if isinstance(giai,str) else list(giai)
    return {"de":[_fix(x) for x in de], "giai":[_fix(x) for x in giai], "dap":_fix(dap)}

def fs(f):                                       # Fraction -> "a/b" hoặc "n"
    f = Fraction(f)
    if f.denominator == 1: return str(f.numerator)
    s = "" if f.numerator >= 0 else "−"
    return f"{s}{abs(f.numerator)}/{f.denominator}"
```

**Mỗi dạng toán** = một hàm chấp nhận tham số cụ thể, có `assert` kiểm chứng:

```python
def nhan_trong_bang(a, b, story):
    tich = a * b
    de = [f"{story} Mỗi thùng có {b} hộp bánh. Hỏi {a} thùng có bao nhiêu hộp bánh?"]
    giai = [f"Số hộp bánh: {b} × {a} = {tich} (hộp)."]
    assert tich == a * b
    return _r(de, giai, f"{tich} hộp")
```

**Generator theo seed** — mỗi `gp_*(i)` chọn một dạng con và tham số từ `i`:

```python
_ST = ["Bài toán.", "Bài tập.", "Câu hỏi.", "Em hãy giải bài toán sau."]
def _s(i): return _ST[i % len(_ST)]

def gp_nhan(i):
    k = i % 3; jj = i // 3          # k chọn nhánh; jj quét tham số
    a = 2 + jj % 9; b = 2 + (jj // 9) % 9
    if k == 0: return nhan_trong_bang(a, b, _s(i))
    ...

L3_GENS = [gp_nhan, gp_chia, gp_2phep, gp_gapgiam, gp_motphan, gp_bieuthuc, ...]
```

Mẹo tăng `distinct` (số đề khác nhau): trộn chỉ số `j = i * <số lẻ lớn> + <hằng>` hoặc chia
`jj = i // k` để mỗi nhánh có đủ dải tham số. **Tránh sympy trong vòng lặp retry** — rất chậm.

**Tự kiểm (`if __name__ == "__main__"`):** chạy mỗi `gp_*` với `range(900)`, in `distinct` và
báo `ART` nếu có "None" / hai dấu cách / `− −` / `+ −` / `^` / `((` / `\d\.\d`. Mục tiêu `bad = 0`.

## 2. Driver `build_lN.py` — dựng .docx (dùng `kidbook`)

```python
import kidbook as _KB
from kidbook import newdoc, cover, probbox, ghinho, toc
_KB.set_grade("LỚP 3")

_PREFIXES = ("Bài toán. ","Bài tập. ","Câu hỏi. ","Bài toán.","Bài tập.","Câu hỏi.")
def _clean(pr):          # bỏ tiền tố story ở đầu de[0] (đã có tiêu đề "Bài N")
    de = list(pr["de"])
    if de:
        s = de[0]
        for p in _PREFIXES:
            if s.startswith(p): s = s[len(p):].lstrip(); break
        de[0] = (s[0].upper()+s[1:]) if s else s
    pr["de"] = de; return pr

PARTS = [
    ("PHẦN 1 — Nhân, chia trong bảng và bài toán có lời văn", [G.gp_nhan, G.gp_chia, G.gp_2phep]),
    ...                                           # 7–12 phần
]
CHUYEN_DE = [
    ("Dạng 1 — Nhân, chia trong bảng", [G.gp_nhan, G.gp_chia],
     ["Muốn tìm tích, lấy thừa số nhân với thừa số.", "Muốn chia đều: lấy tổng chia số nhóm."]),
    ...
]
```

**Các hàm builder** (giống nhau ở mọi lớp — có thể chép sang):
| Hàm | Dùng cho | Chữ ký |
|---|---|---|
| `build_collection(n_bai, parts, seed, title, sub, fname, intro)` | sách "N bài toán…" chia phần | |
| `make_de_book(n_de, n_cau, parts, title, sub, fname, intro, seed_start=0)` | sách "N đề" (mock) — cuối cuốn "HƯỚNG DẪN CHẤM VÀ ĐÁP SỐ" | |
| `make_tracnghiem_book(n_cau, parts, title, sub, fname, intro, seed_start=0)` | sách trắc nghiệm 4 lựa chọn — Phần I câu hỏi / II đáp án / III lời giải | chọn câu có `_last_int(dap) > 3` để bịa phương án |
| `build_chuyende_book(per_dang, title, sub, fname, intro, seed_start=0)` | cẩm nang / chuyên đề — dùng global `CHUYEN_DE`, mỗi dạng có `ghinho(...)` | |

Bên trong builder: `gen_collection` lặp qua parts, mỗi phần lấy `target` bài,
dùng vòng `for bump in range(0, 600, 7)` để né trùng (`seen` = set các `" ".join(de)`),
`_clean` mỗi bài trước khi thêm. Dựng doc:
`newdoc()` → `cover()` → heading "Định hướng biên soạn" + intro → heading "Mục lục" + `toc()` →
mỗi phần: `d.add_heading(pname, level=1)`; mỗi bài: `d.add_heading(f"Bài {num}", level=2)` →
`probbox(d, p["de"])` → `d.add_heading("Lời giải", level=3)` → các dòng giải →
`d.add_paragraph().add_run("Đáp số: "+p["dap"]).bold=True`. Cuối: `_KB.footerbanner(d)` → `d.save(...)`.

## 3. `__main__` của driver = danh sách công việc

```python
if __name__ == "__main__":
    build_chuyende_book(14, "CẨM NANG 12 DẠNG TOÁN LỚP 3 THEO CHỦ ĐỀ",
        "12 dạng toán — mỗi dạng có phần GHI NHỚ và bài tập lời giải",
        "Cam_Nang_12_Dang_Toan_Lop_3_Theo_Chu_De.docx", "…intro…", seed_start=90000)
    make_de_book(40, 6, PARTS, "40 ĐỀ ÔN LUYỆN HỌC SINH GIỎI TOÁN LỚP 3",
        "40 đề — mỗi đề 6 bài, có hướng dẫn chấm và đáp số",
        "40_De_On_Luyen_HSG_Toan_Lop_3.docx", "…intro…", seed_start=1000)
    build_collection(96, PARTS, 20000, "96 BÀI TẬP NÂNG CAO TOÁN LỚP 3", "…", "…docx", "…")
    ...
```
Mỗi cuốn: **seed_start khác nhau** (cách xa nhau) để không trùng đề giữa các cuốn.

## 4. Lớp 4 & một phần lớp 5: driver kiểu THỦ TỤC (Family B)

Không có `newdoc()` — dựng `doc = Document()` ở mức module rồi viết thẳng.
Chỉ cần chèn sau `Document()`:
```python
import kidbook as _KB
_KB.restyle(doc, "LỚP 4")            # áp viền + style Heading + phông
```
và đổi thân `add_problem_box(document, text_lines)` thành `_KB.probbox(document, text_lines)`.
