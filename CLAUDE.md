# Hướng dẫn làm việc trên dự án này

Công cụ biên soạn lại tài liệu Toán / Vật lý THPT thành sách Word chuẩn
Nghị định 30/2020/NĐ-CP và chương trình GDPT 2018.

## Kiến trúc

```
app.py            FastAPI, mỏng — chỉ điều phối, không chứa logic biên soạn
config.py         LOCAL_MODE, ACCESS_TOKEN, đọc/ghi app_settings.json
core/parser.py       Bóc tách docx / xlsx / pdf / ảnh  → QuestionItem
core/math_engine     Làm sạch ký hiệu toán, số mũ, phân số
core/theory_bank     Ngân hàng lý thuyết theo 16 chuyên đề
core/ai_provider.py  MỘT cửa gọi Claude — văn bản và ảnh
core/skill_loader.py Nạp chuẩn nghiệp vụ từ skills/ vào câu lệnh
core/loai_dau_ra.py  Chín loại đầu ra + cấu trúc & thang điểm đề
core/rewriter.py     Tái cấu trúc + gọi AI → RewrittenBook
core/validator.py    Thẩm định trước xuất bản (đo trên file Word thật)
core/exporter.py     Xuất .docx chuẩn NĐ 30, rẽ nhánh theo loại đầu ra
core/exporter_de.py  Bộ đề chuẩn 2025: ma trận + đặc tả + đề 3 phần + HD chấm
core/exporter_hsg.py Tài liệu HSG (tự luận, giấu phương án)
core/exporter_giao_an.py  Giáo án khung Công văn 5512
core/exporter_pptx.py     Bài giảng PowerPoint
skills/              Chuẩn nghiệp vụ, ĐI THEO REPO để deploy được
static/app.js        Toàn bộ giao diện, vanilla JS, không framework
```

## Chín loại đầu ra

Phân biệt hai khái niệm dễ lẫn: **nhận diện** (`doc_type.py`, đoán tài liệu đưa
vào là gì, ba loại) và **đầu ra** (`loai_dau_ra.py`, người dùng muốn nhận lại
dạng gì, chín loại). Nhận diện chỉ GỢI Ý, không quyết định thay người dùng.

Chín loại thuộc bốn nhóm chịu bốn chuẩn khác nhau, mỗi nhóm một bộ dựng riêng.
Với đề kiểm tra định kì, "hoàn chỉnh đúng chuẩn" là **bộ bốn phần**: ma trận đề,
bản đặc tả, đề ba phần I/II/III, hướng dẫn chấm.

**Thang điểm Phần II là chỗ dễ lập trình sai nhất**: lũy tiến 0,1 / 0,25 / 0,5 /
1,0 theo số ý đúng, KHÔNG phải 0,25 nhân số ý. Đúng 2 trong 4 ý chỉ được 0,25.
Mọi tổ hợp loại đề × môn đều phải cộng lại đúng 10,0 — có `kiem_tra_tong_diem()`.

## Skill chính là câu lệnh

Skill không phải tài liệu tham khảo, nó là phần đầu của câu lệnh gửi cho AI.
Skill nằm trong `skills/` của repo chứ KHÔNG đọc từ `~/.claude/skills`, vì máy
chủ triển khai không có thư mục cá nhân đó. Dùng `scripts/dong_bo_skill.py` để
giữ hai nơi không trôi khác nhau.

Khi sửa câu lệnh trong `rewriter.py`, nhớ **ví dụ trong khuôn JSON phải khớp với
quy tắc ghi ở trên**. Mô hình bám theo ví dụ mạnh hơn bám theo lời dặn — đã từng
để khuôn ghi "Thông hiểu" và "Mẹo Casio" trong khi luật ngay trên bảo dùng ba
mức 2025 và cấm nhắc Casio ở tiểu học.

## Cấp học quyết định giọng văn và trang trí

Tiểu học: câu ngắn thân thiện, ĐƯỢC thêm biểu tượng và trang trí. THPT: trang
trọng, không trang trí. **Giáo án mọi cấp đều không trang trí** vì là hồ sơ
chuyên môn nộp cho tổ và trường. Xem `skill_loader.duoc_trang_tri()`.

Mẫu nhận diện cấp học phải nhận cả dạng có dấu lẫn không dấu, và coi `_`, `-`,
`.` là dấu ngăn — tên tệp trong kho viết kiểu `BT_cuoi_tuan_lop_2.docx`.

Luồng: `ingest → parse → rewrite → export → validate`.
Thẩm định chạy **sau** khi xuất file vì nó mở lại file Word để đo lề và khổ giấy.

## Những nguyên tắc KHÔNG được vi phạm

**Nội dung học thuật là thứ quan trọng nhất.** Một bài toán sai đáp án in vào
sách cho học sinh là lỗi không thể chấp nhận. Mọi câu hỏi thêm vào
`VERIFIED_QUESTION_BANK` (core/rewriter.py) phải được **tính lại độc lập bằng
Python** trước khi đưa vào, không tin vào trí nhớ.

**Chỉ dùng Claude.** Bỏ hẳn Gemini ngày 19/09/2026. Đừng thêm lại nhà cung cấp
thứ hai nếu chưa có yêu cầu rõ: chính việc đỡ hai nhà cùng lúc đã sinh ra **bốn
chỗ rò rỉ khóa** — `ai_namer`, `question_forge`, `parser` (đọc ảnh) và
`get_effective_api_key`. Khóa Anthropic từng bị gửi thẳng sang máy chủ Google.

**Mọi lượt gọi AI phải đi qua `core/ai_provider.py`.** Mô-đun nào tự gọi SDK là
mô-đun đó có thể làm khóa đi lạc. Luật KL10 canh đúng điều này.

**Khóa API là của riêng từng người.** Khóa đi theo header `X-Claude-Key` từng
yêu cầu, máy chủ không lưu. Trên Web (`LOCAL_MODE=False`) nếu người dùng chưa
dán khóa thì chạy offline, **tuyệt đối không mượn khóa của máy chủ** — làm vậy
là tiêu tiền của người khác. Đường dễ lọt nhất là
`core/ai_namer.get_effective_api_key()`, nó tự đọc settings và biến môi trường.
Máy chủ dự án còn sót biến môi trường `GEMINI_API_KEY`; không mô-đun nào được
đọc nó nữa.

**Không tin vào bộ thẩm định tự cho điểm.** `PreFlightValidator` từng chấm cứng
20/20 cho tiêu chí thể thức mà không mở file. Mọi tiêu chí phải đo trên dữ liệu
thật, nếu không báo cáo chỉ là trang trí và che mất đúng lỗi cần thấy.

**Giữ nguyên 100% đề bài gốc.** Chỉ chuẩn hóa ký hiệu và ngữ pháp, không thêm
bối cảnh, không đổi số liệu.

## Kiểm thử — bắt buộc trước khi nói "xong"

```bash
python test_pipeline.py       # docx + xlsx → Word
python test_upgrade.py        # pdf + gộp thư mục
python test_fix_real_pdf.py   # đề HSG Toán 11 thật trong input/
```

**Sửa giao diện thì phải thử bằng trình duyệt thật**, Playwright có sẵn:

```python
from playwright.sync_api import sync_playwright   # đã cài sẵn
```

Bài học đắt giá: `node --check` và kiểm tra cú pháp **không đủ**. Đã từng có
lỗi template literal không đóng làm chết toàn bộ `app.js` mà vẫn lọt, và lỗi
vùng bấm giữa khung nạp liệu không ăn (test cũ chỉ bấm vào nút nên không lộ).
Phải bấm đúng chỗ người dùng hay bấm.

Sau khi chạy test nhớ dọn: `rm -rf input/ingest_*` và `git checkout --
input/sample_toan_de_thi.pdf` (test tự sinh lại file này).

## Chống lưu đệm

`index.html` dùng `?v=__ASSET_VERSION__`, thay khi trả trang bằng
`_asset_version()` — băm MD5 **nội dung** `app.js` + `style.css`. Không bao giờ
quay lại gắn cứng số phiên bản: đã từng làm trình duyệt giữ JS cũ chạy với HTML
mới, gây `TypeError` và chết cả trang.

`/api/health` trả `asset_version` để biết máy chủ đang phục vụ bản nào.

## Chạy ở máy — KHÔNG deploy lên đâu cả

Phần mềm chạy trên máy người dùng: bấm đúp `Chay_Ung_Dung.bat`, mở
`http://127.0.0.1:8501`.

**Đã bỏ hẳn Render ngày 19/09/2026**, cùng `render.yaml`,
`.github/workflows/deploy.yml` và `keep_alive.yml`. Đừng dựng lại chúng.

Lý do bỏ, để sau này không ai vô tình làm lại:

- **Kho tài liệu nằm ở máy người dùng.** Bản Web chặn duyệt thư mục
  (`if not LOCAL_MODE: raise HTTPException(403, ...)`) nên chức năng trỏ vào một
  thư mục rồi gộp cả thư mục — thứ được dùng nhiều nhất — không chạy được.
- **Đĩa trên máy chủ miễn phí là tạm**, mỗi lần deploy là mất sạch ngân hàng câu
  hỏi đã qua ba lớp thẩm định.
- **Gói miễn phí ngủ đông** sau 15 phút; có lần chờ 3 phút không hồi đáp, trong
  khi chạy ở máy khởi động hết 1 giây.
- Người dùng nói rõ chỉ mình và vài người nội bộ dùng, nên URL công khai là gánh
  nặng chứ không phải tiện ích.

Kiểm tra máy chạy được:

```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8899
curl -s http://127.0.0.1:8899/api/health
```

Nếu sau này thật sự cần cho người ngoài dùng: chạy ở máy rồi mở đường hầm
(Cloudflare Tunnel), và **bắt buộc đặt `APP_ACCESS_TOKEN` trước** — mở đường hầm
vào bản `LOCAL_MODE` mà không có token nghĩa là ai có địa chỉ cũng duyệt được ổ
đĩa và tiêu được khóa API đã lưu.

## Chi phí và tốc độ khi gọi Claude

Claude tính tiền ngay từ lượt đầu, không có bậc miễn phí. Một tài liệu tốn
`ceil(số_câu / 25) + 2` lượt gọi. Chạy test nhiều là tốn tiền thật — hãy thử
bằng tệp nhỏ (`input/sample_toan_goc.xlsx`, 4 câu) trước khi chạy tài liệu lớn.

Các lô gọi **song song 4 lô một lúc** (`SO_LO_SONG_SONG`, tối đa 8). Đo thật
trên 60 câu chia 3 lô: tuần tự 253 giây, song song 78 giây — nhanh gấp 3,2 lần.

Trần số lô là `SO_LO_TOI_DA` (mặc định 12, tức 300 câu). Câu vượt trần KHÔNG bị
mất — chúng chạy bằng bộ ngoại tuyến — nhưng chất lượng khác hẳn, nên hệ thống
in cảnh báo rõ số câu bị chuyển.

## Không commit

`output/`, `scratch/`, `input/ingest_*`, `app_settings.json` đều trong
`.gitignore`. Lưu ý `git add -A <đường dẫn>` vẫn thêm lại file **đang được theo
dõi** dù có trong gitignore — đã từng làm hỏng một lần.

## Ngân hàng câu hỏi do AI sinh

`core/question_forge.py` sinh câu hỏi mới bằng AI nhưng **không câu nào vào
ngân hàng nếu chưa qua đủ 3 lớp thẩm định**: cấu trúc → bắt AI giải lại độc lập
(giấu đáp án) → đối chiếu số bằng sympy.

Cảnh báo an toàn: `sympy.parse_expr` dùng `eval` bên trong. Truyền `local_dict`
là KHÔNG đủ — đã thử nghiệm và xác nhận `__import__('os').system(...)` chạy
thật. Biểu thức kiểm tra do AI sinh nên phải coi là dữ liệu không đáng tin;
`_bieu_thuc_an_toan()` chặn trước khi parse. Đừng nới lỏng hàm này.

Nơi lưu: mặc định `data/question_bank.json`, đổi được bằng biến môi trường
`QUESTION_BANK_DIR` (trỏ sang thư mục OneDrive/Google Drive để tự sao lưu).
Trên Render đĩa là tạm nên ngân hàng mất mỗi lần deploy — dùng nút xuất/nhập
trong Lò Soạn Đề, hoặc commit tệp ngân hàng vào repo.
