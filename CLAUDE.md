# Hướng dẫn làm việc trên dự án này

Công cụ biên soạn lại tài liệu Toán / Vật lý THPT thành sách Word chuẩn
Nghị định 30/2020/NĐ-CP và chương trình GDPT 2018.

## Kiến trúc

```
app.py            FastAPI, mỏng — chỉ điều phối, không chứa logic biên soạn
config.py         LOCAL_MODE, ACCESS_TOKEN, đọc/ghi app_settings.json
core/parser.py    Bóc tách docx / xlsx / pdf / ảnh  → QuestionItem
core/math_engine  Làm sạch ký hiệu toán, số mũ, phân số
core/theory_bank  Ngân hàng lý thuyết theo 8 chuyên đề
core/rewriter.py  Tái cấu trúc + gọi Gemini → RewrittenBook
core/validator.py Thẩm định trước xuất bản (đo trên file Word thật)
core/exporter.py  Xuất .docx chuẩn NĐ 30
static/app.js     Toàn bộ giao diện, vanilla JS, không framework
```

Luồng: `ingest → parse → rewrite → export → validate`.
Thẩm định chạy **sau** khi xuất file vì nó mở lại file Word để đo lề và khổ giấy.

## Những nguyên tắc KHÔNG được vi phạm

**Nội dung học thuật là thứ quan trọng nhất.** Một bài toán sai đáp án in vào
sách cho học sinh là lỗi không thể chấp nhận. Mọi câu hỏi thêm vào
`VERIFIED_QUESTION_BANK` (core/rewriter.py) phải được **tính lại độc lập bằng
Python** trước khi đưa vào, không tin vào trí nhớ.

**Khóa API là của riêng từng người.** Khóa đi theo header `X-Gemini-Key` từng
yêu cầu, máy chủ không lưu. Trên Web (`LOCAL_MODE=False`) nếu người dùng chưa
dán khóa thì chạy offline, **tuyệt đối không mượn khóa của máy chủ** — làm vậy
là tiêu hạn mức của người khác. Đường dễ lọt nhất là
`core/ai_namer.get_effective_api_key()`, nó tự đọc settings và biến môi trường.

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

## Deploy

Nhánh `main` → Render (`vietlaisach-pro.onrender.com`).

`autoDeploy: true` trong `render.yaml` **không có tác dụng** vì service được tạo
thủ công trên dashboard chứ không qua Blueprint. Deploy đi qua
`.github/workflows/deploy.yml`, cần secret `RENDER_DEPLOY_HOOK` trong GitHub.

Kiểm tra bản đã lên chưa:

```bash
curl -s https://vietlaisach-pro.onrender.com/api/health
# so asset_version với _asset_version() ở máy
```

## Hạn mức Gemini

Gói free `gemini-3.6-flash` chỉ **20 request/ngày**. Một tài liệu tốn
`ceil(số_câu / 25) + 2` lượt. Tài liệu 240 câu ăn 12 lượt — hơn nửa hạn mức.
Chạy test nhiều sẽ cháy hạn mức; khi đó hệ thống tự rơi về chế độ offline,
đó là hành vi đúng chứ không phải lỗi.

## Không commit

`output/`, `scratch/`, `input/ingest_*`, `app_settings.json` đều trong
`.gitignore`. Lưu ý `git add -A <đường dẫn>` vẫn thêm lại file **đang được theo
dõi** dù có trong gitignore — đã từng làm hỏng một lần.
