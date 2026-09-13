document.addEventListener("DOMContentLoaded", () => {
    // ==========================================
    // DOM ELEMENTS
    // ==========================================
    // Khu vực nạp liệu hợp nhất
    const dropZone = document.getElementById("drop-zone");
    const fileInput = document.getElementById("file-input");
    const folderInput = document.getElementById("folder-input");
    const btnBrowseFile = document.getElementById("btn-browse-file");
    const btnBrowseFolder = document.getElementById("btn-browse-folder");

    const ingestResults = document.getElementById("ingest-results");
    const ingestSummary = document.getElementById("ingest-summary");
    const ingestFileList = document.getElementById("ingest-file-list");
    const ingestSkipped = document.getElementById("ingest-skipped");
    const batchModeSelector = document.getElementById("batch-mode-selector");
    const doctypeBox = document.getElementById("doctype-box");
    const doctypeDetected = document.getElementById("doctype-detected");
    const doctypeSelect = document.getElementById("doctype-select");
    const aiScopeSelect = document.getElementById("ai-scope-select");
    const btnClearIngest = document.getElementById("btn-clear-ingest");

    // Quét thư mục có sẵn trên máy (chỉ dùng khi chạy Localhost)
    const toggleServerScan = document.getElementById("toggle-server-scan");
    const serverPathBox = document.getElementById("server-path-box");
    const folderPathInput = document.getElementById("folder-path-input");
    const btnScanFolder = document.getElementById("btn-scan-folder");

    // Subject & Options
    const radioCards = document.querySelectorAll(".radio-card");
    const btnProcess = document.getElementById("btn-process");
    const customTitleInput = document.getElementById("custom-title");
    const btnSuggestTitles = document.getElementById("btn-suggest-titles");
    const aiTitlesDrawer = document.getElementById("ai-titles-drawer");
    const aiTitlesList = document.getElementById("ai-titles-list");
    const btnCloseTitles = document.getElementById("btn-close-titles");
    const btnRefreshTitles = document.getElementById("btn-refresh-titles");
    const addCountSelect = document.getElementById("add-count");
    const checkTheory = document.getElementById("check-theory");
    const checkCasio = document.getElementById("check-casio");
    const checkTraps = document.getElementById("check-traps");
    const checkForeword = document.getElementById("check-foreword");
    const checkSecrets = document.getElementById("check-secrets");
    const checkStem = document.getElementById("check-stem");
    const checkSolution = document.getElementById("check-solution");
    const checkAnswerKey = document.getElementById("check-answer-key");
    const solutionPlace = document.getElementById("solution-place");
    const paperFormatSelect = document.getElementById("paper-format");

    // Lọc HTML nhưng vẫn giữ ngắt dòng — dùng cho lời giải nhiều dòng.
    function escapeMultiline(str) {
        return escapeHtml(str).replace(/\n/g, "<br>");
    }

    // Gom 6 ô tick thành các trường gửi kèm yêu cầu biên soạn.
    // Trước đây các ô này chỉ là trang trí: tick hay không thì file Word vẫn y hệt.
    function themTuyChonBienSoan(formData) {
        const map = {
            include_theory: checkTheory,
            include_foreword: checkForeword,
            include_secrets: checkSecrets,
            include_stem: checkStem,
            include_solution: checkSolution,
            include_casio: checkCasio,
            include_traps: checkTraps,
            include_answer_key: checkAnswerKey,
        };
        Object.keys(map).forEach((ten) => {
            const o = map[ten];
            formData.append(ten, o && o.checked ? "true" : "false");
        });
        if (solutionPlace) {
            formData.append("vi_tri_loi_giai", solutionPlace.value);
        }
    }

    // ==========================================
    // KHÓA API CỦA RIÊNG TỪNG NGƯỜI DÙNG
    // Khóa nằm trong trình duyệt của người dùng và gửi kèm từng yêu cầu qua
    // header. Máy chủ không lưu, nên nhiều người cùng vào một trang web vẫn
    // tiêu hạn mức trên tài khoản Google của riêng mỗi người.
    // ==========================================
    const KEY_STORE = "gemini_api_key";
    const MODEL_STORE = "gemini_model";

    function readStore(name) {
        try {
            return localStorage.getItem(name) || "";
        } catch (e) {
            return "";   // chế độ ẩn danh hoặc trình duyệt chặn lưu trữ
        }
    }

    function writeStore(name, value) {
        try {
            if (value) localStorage.setItem(name, value);
            else localStorage.removeItem(name);
            return true;
        } catch (e) {
            return false;
        }
    }

    // Mã truy cập nội bộ (chỉ dùng khi máy chủ đặt APP_ACCESS_TOKEN)
    const ACCESS_STORE = "app_access_token";

    // Bọc fetch để mọi lệnh gọi API đều tự mang theo khóa và mã truy cập
    function apiFetch(url, options) {
        const opts = options || {};
        const headers = new Headers(opts.headers || {});
        const key = readStore(KEY_STORE);
        const model = readStore(MODEL_STORE);
        const access = readStore(ACCESS_STORE);
        if (key) headers.set("X-Gemini-Key", key);
        if (model) headers.set("X-Gemini-Model", model);
        if (access) headers.set("X-Access-Token", access);
        return fetch(url, Object.assign({}, opts, { headers: headers }));
    }

    function escapeHtml(str) {
        if (!str) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }


    // Progress Card & Steps
    const progressCard = document.getElementById("progress-card");
    const progressBar = document.getElementById("progress-bar");
    const progressStatus = document.getElementById("progress-status");
    const pstep1 = document.getElementById("pstep-1");
    const pstep2 = document.getElementById("pstep-2");
    const pstep3 = document.getElementById("pstep-3");
    const pstep4 = document.getElementById("pstep-4");

    // Result Card
    const resultCard = document.getElementById("result-card");
    const resultTitle = document.getElementById("result-book-title");
    const resultSubtitle = document.getElementById("result-book-subtitle");
    const resultSingleActions = document.getElementById("result-single-actions");
    const resultBatchList = document.getElementById("result-batch-list");
    const btnDownload = document.getElementById("btn-download");
    const btnReadOnline = document.getElementById("btn-read-online");
    const btnOpenResultFolder = document.getElementById("btn-open-result-folder");
    const btnOpenFolder = document.getElementById("btn-open-folder");

    // Preview
    const previewPlaceholder = document.getElementById("preview-placeholder");
    const previewList = document.getElementById("preview-list");
    const previewBadge = document.getElementById("preview-badge");
    const previewToolbar = document.getElementById("preview-toolbar");
    const filterChips = document.querySelectorAll(".filter-chip");
    const btnToggleSolutions = document.getElementById("btn-toggle-solutions");

    // Modals
    const btnSettings = document.getElementById("btn-settings");
    const modalSettings = document.getElementById("modal-settings");
    const btnCloseModal = document.getElementById("btn-close-modal");
    const geminiApiKeyInput = document.getElementById("gemini-api-key");
    const btnToggleKey = document.getElementById("btn-toggle-key");
    const geminiModelSelect = document.getElementById("gemini-model");
    const btnSaveSettings = document.getElementById("btn-save-settings");
    const keyStatusEl = document.getElementById("key-status");

    const modalReader = document.getElementById("modal-reader");
    const btnCloseReader = document.getElementById("btn-close-reader");
    const btnPrintReader = document.getElementById("btn-print-reader");
    const readerBookTitle = document.getElementById("reader-book-title");
    const readerBookSubtitle = document.getElementById("reader-book-subtitle");
    const readerContent = document.getElementById("reader-content");

    const btnForge = document.getElementById("btn-forge");
    const modalForge = document.getElementById("modal-forge");
    const btnCloseForge = document.getElementById("btn-close-forge");
    const forgeStats = document.getElementById("forge-stats");
    const forgeTopic = document.getElementById("forge-topic");
    const forgeGrade = document.getElementById("forge-grade");
    const forgeLevel = document.getElementById("forge-level");
    const forgeCount = document.getElementById("forge-count");
    const btnForgeRun = document.getElementById("btn-forge-run");
    const forgeResult = document.getElementById("forge-result");
    const btnBankExport = document.getElementById("btn-bank-export");
    const btnBankImport = document.getElementById("btn-bank-import");
    const bankImportInput = document.getElementById("bank-import-input");

    const btnDeployInfo = document.getElementById("btn-deploy-info");
    const modalDeploy = document.getElementById("modal-deploy");
    const btnCloseDeploy = document.getElementById("btn-close-deploy");
    const btnDismissDeploy = document.getElementById("btn-dismiss-deploy");

    // App State
    // Chỉ còn MỘT luồng đầu vào: nạp xong thì hệ thống tự biết là một tài liệu
    // (làm thành một cuốn) hay nhiều tài liệu (cho chọn gộp chung / tách riêng).
    let ingestKind = null;          // "single" | "batch" | null
    let ingestFolderPath = null;    // thư mục phiên trên máy chủ
    let singleFilePath = null;      // đường dẫn tương đối khi chỉ có 1 tài liệu
    let currentScannedFiles = [];
    let selectedSubject = "toan";
    let currentCompiledBook = null;
    let areSolutionsVisible = true;
    let activeFilterLevel = "all";

    // ==========================================
    // SUBJECT SELECTOR
    // ==========================================
    function setSubject(subj) {
        selectedSubject = subj;
        const toanCard = document.getElementById("card-subject-toan");
        const vatlyCard = document.getElementById("card-subject-vatly");
        const toanRadio = document.getElementById("subject-toan");
        const vatlyRadio = document.getElementById("subject-vatly");

        if (subj === "toan") {
            if (toanCard) toanCard.classList.add("active");
            if (vatlyCard) vatlyCard.classList.remove("active");
            if (toanRadio) toanRadio.checked = true;
            if (customTitleInput) customTitleInput.placeholder = "Ví dụ: Sổ Tay Công Thức & Dạng Toán Trọng Tâm Toán 10";
        } else {
            if (vatlyCard) vatlyCard.classList.add("active");
            if (toanCard) toanCard.classList.remove("active");
            if (vatlyRadio) vatlyRadio.checked = true;
            if (customTitleInput) customTitleInput.placeholder = "Ví dụ: Cẩm Nang Bứt Phá Điểm 9+ Vật Lý THPT - Chuẩn BGD";
        }
    }

    const cardToan = document.getElementById("card-subject-toan");
    const cardVatly = document.getElementById("card-subject-vatly");
    if (cardToan) cardToan.addEventListener("click", () => setSubject("toan"));
    if (cardVatly) cardVatly.addEventListener("click", () => setSubject("vatly"));

    const radioToan = document.getElementById("subject-toan");
    const radioVatly = document.getElementById("subject-vatly");
    if (radioToan) radioToan.addEventListener("change", () => setSubject("toan"));
    if (radioVatly) radioVatly.addEventListener("change", () => setSubject("vatly"));

    // ==========================================
    // CỔNG NẠP LIỆU HỢP NHẤT
    // Người dùng thả gì cũng được — tệp lẻ, nhiều tệp, cả thư mục, file .ZIP,
    // hoặc trộn lẫn. Việc phân loại do máy chủ lo, giao diện không hỏi gì thêm.
    // ==========================================
    if (btnBrowseFile) {
        btnBrowseFile.addEventListener("click", (e) => {
            e.stopPropagation();
            fileInput.click();
        });
    }
    if (btnBrowseFolder) {
        btnBrowseFolder.addEventListener("click", (e) => {
            e.stopPropagation();
            folderInput.click();
        });
    }
    if (dropZone) {
        // Bấm vào BẤT KỲ chỗ nào trong khung đều mở hộp thoại chọn tệp.
        // Điều kiện cũ là `e.target.closest(".drop-content") === e.target`, chỉ
        // đúng khi bấm trúng đúng thẻ .drop-content — bấm vào biểu tượng hay dòng
        // chữ bên trong thì e.target là thẻ con nên không bao giờ khớp, khiến cả
        // vùng giữa khung bấm không ăn. Đó lại chính là chỗ người dùng hay bấm.
        dropZone.addEventListener("click", (e) => {
            // Hai nút đã có xử lý riêng, bỏ qua để không mở hộp thoại hai lần
            if (e.target.closest("#btn-browse-file") || e.target.closest("#btn-browse-folder")) {
                return;
            }
            fileInput.click();
        });
    }

    fileInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) handleIngest(Array.from(e.target.files));
    });
    folderInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) handleIngest(Array.from(e.target.files));
    });

    setupDragDrop(dropZone, (files) => {
        if (files.length > 0) handleIngest(files);
    });

    if (btnClearIngest) {
        btnClearIngest.addEventListener("click", (e) => {
            e.stopPropagation();
            resetIngest();
        });
    }

    function resetIngest() {
        ingestKind = null;
        ingestFolderPath = null;
        singleFilePath = null;
        currentScannedFiles = [];
        fileInput.value = "";
        folderInput.value = "";
        ingestResults.classList.add("hidden");
        batchModeSelector.classList.add("hidden");
        ingestSkipped.classList.add("hidden");
        doctypeBox.classList.add("hidden");
        dropZone.classList.remove("hidden");
        btnProcess.disabled = true;
        previewPlaceholder.classList.remove("hidden");
        previewList.classList.add("hidden");
        previewToolbar.classList.add("hidden");
        previewBadge.textContent = "Chưa có dữ liệu";
    }

    async function handleIngest(fileArray) {
        if (!fileArray || fileArray.length === 0) return;

        dropZone.classList.add("hidden");
        ingestResults.classList.remove("hidden");
        ingestSummary.textContent = `Đang nạp ${fileArray.length} mục...`;
        ingestFileList.innerHTML = '<div class="ingest-loading">⏳ Đang phân loại, giải nén và bóc tách...</div>';
        btnProcess.disabled = true;

        const formData = new FormData();
        fileArray.forEach(f => formData.append("files", f, f.name));
        formData.append("subject", selectedSubject);

        try {
            const res = await apiFetch("/api/ingest", { method: "POST", body: formData });
            const data = await res.json();

            if (!res.ok || data.status !== "success") {
                throw new Error(data.detail || "Không nạp được tài liệu");
            }

            ingestKind = data.kind;
            ingestFolderPath = data.folder_path;
            singleFilePath = data.single_file_path || null;
            currentScannedFiles = data.files || [];

            renderIngestResults(data);
            btnProcess.disabled = currentScannedFiles.length === 0;
        } catch (err) {
            ingestFileList.innerHTML =
                `<div class="ingest-error">❌ ${escapeHtml(err.message)}</div>`;
            ingestSummary.textContent = "Nạp thất bại";
            btnProcess.disabled = true;
        }
    }

    function renderIngestResults(data) {
        const files = data.files || [];
        const isSingle = data.kind === "single";

        // Chỉ kèm mô tả nguồn khi nó nói thêm được điều gì (ví dụ có giải nén .zip),
        // tránh hiển thị lặp kiểu "3 tài liệu (3 tài liệu)".
        const detail = data.source_summary || "";
        const plain = `${files.length} tài liệu`;
        ingestSummary.textContent = isSingle
            ? "1 tài liệu — sẽ biên soạn thành 1 cuốn sách"
            : (detail && detail !== plain ? `${plain} — ${detail}` : plain);

        ingestFileList.innerHTML = "";
        files.forEach(f => {
            const item = document.createElement("div");
            item.className = "folder-file-item";
            const icon = extIcon(f.ext);
            const where = f.rel_dir && f.rel_dir !== "." ? ` · ${escapeHtml(f.rel_dir)}` : "";
            item.innerHTML = `
                <span>${icon} ${escapeHtml(f.name)}<span style="color: var(--text-dim);">${where}</span></span>
                <span style="color: var(--text-dim); font-size: 11.5px;">${f.size_kb} KB</span>
            `;
            ingestFileList.appendChild(item);
        });

        // Bỏ qua tệp không hợp lệ thì nói rõ, không im lặng
        if (data.skipped && data.skipped.length > 0) {
            ingestSkipped.classList.remove("hidden");
            ingestSkipped.innerHTML =
                `⚠️ Đã bỏ qua ${data.skipped.length} tệp không hỗ trợ: ` +
                data.skipped.slice(0, 6).map(x => escapeHtml(x)).join(", ") +
                (data.skipped.length > 6 ? "…" : "");
        } else {
            ingestSkipped.classList.add("hidden");
        }

        // Chỉ hỏi gộp/tách khi thực sự có nhiều tài liệu
        batchModeSelector.classList.toggle("hidden", isSingle);

        // Báo loại tài liệu nhận diện được — đầu vào dạng nào thì đầu ra dạng đó
        const nd = data.nhan_dien;
        if (isSingle && nd && nd.doc_type) {
            doctypeBox.classList.remove("hidden");
            const tinCay = nd.do_tin_cay === "cao" ? "" :
                ` <span class="doctype-warn">(độ tin cậy ${escapeHtml(nd.do_tin_cay)} — chọn tay bên dưới nếu chưa đúng)</span>`;
            doctypeDetected.innerHTML =
                `🔎 Nhận diện: <strong>${escapeHtml(nd.ten_hien_thi || "")}</strong>` +
                ` · ${nd.tong_cau} câu` +
                (nd.so_chuong ? ` · ${nd.so_chuong} chương` : "") +
                tinCay +
                (nd.so_cau_can_ai !== undefined
                    ? `<div class="doctype-cost">💰 ${nd.so_cau_co_san} câu đã có sẵn lời giải (miễn phí) · ` +
                      `<strong>${nd.so_cau_can_ai} câu</strong> cần nhờ AI</div>`
                    : "");
            doctypeSelect.value = "";
        } else {
            doctypeBox.classList.add("hidden");
        }

        // Xem trước
        previewPlaceholder.classList.add("hidden");
        previewList.classList.remove("hidden");
        previewToolbar.classList.add("hidden");

        if (isSingle && data.preview && data.preview.length > 0) {
            renderInitialPreview(data.preview, data.total_items);
        } else if (isSingle) {
            previewBadge.textContent = "Đã nạp 1 tài liệu";
            previewList.innerHTML = `
                <div class="preview-callout callout-theory">
                    <span class="callout-title">📄 TÀI LIỆU ĐÃ SẴN SÀNG BIÊN SOẠN:</span>
                    <div>${escapeHtml(files[0] ? files[0].name : "")}</div>
                </div>
            `;
        } else {
            previewBadge.textContent = `${files.length} tài liệu`;
            previewList.innerHTML = `
                <div class="preview-callout callout-theory">
                    <span class="callout-title">📂 DANH SÁCH TÀI LIỆU SẼ ĐƯỢC BIÊN SOẠN:</span>
                    <div>${files.map((f, i) => `${i + 1}. <strong>${escapeHtml(f.name)}</strong> (${f.size_kb} KB)`).join("<br>")}</div>
                </div>
            `;
        }
    }

    function extIcon(ext) {
        const map = {
            ".docx": "📘", ".doc": "📘",
            ".xlsx": "📗", ".xls": "📗",
            ".pdf": "📕",
            ".png": "🖼️", ".jpg": "🖼️", ".jpeg": "🖼️"
        };
        return map[(ext || "").toLowerCase()] || "📄";
    }

    // ==========================================
    // QUÉT THƯ MỤC CÓ SẴN TRÊN MÁY (chế độ Localhost)
    // ==========================================
    if (toggleServerScan) {
        toggleServerScan.addEventListener("click", () => {
            serverPathBox.classList.toggle("hidden");
        });
    }

    if (btnScanFolder) {
        btnScanFolder.addEventListener("click", async () => {
            const path = folderPathInput.value.trim();
            if (!path) {
                alert("Vui lòng nhập đường dẫn thư mục");
                return;
            }

            btnScanFolder.disabled = true;
            btnScanFolder.textContent = "Đang quét...";
            try {
                const res = await apiFetch("/api/scan-folder", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ folder_path: path })
                });
                const data = await res.json();
                if (!res.ok || data.status !== "success") {
                    throw new Error(data.detail || "Không quét được thư mục");
                }

                ingestKind = data.total_files === 1 ? "single" : "batch";
                ingestFolderPath = data.folder_path;
                singleFilePath = null;   // tệp nằm ngoài input/ nên luôn đi đường thư mục
                currentScannedFiles = data.files || [];

                dropZone.classList.add("hidden");
                ingestResults.classList.remove("hidden");
                renderIngestResults({
                    kind: "batch",           // luôn cho chọn gộp/tách với đường dẫn máy chủ
                    files: data.files,
                    skipped: [],
                    source_summary: `từ thư mục ${data.folder_path}`
                });
                btnProcess.disabled = currentScannedFiles.length === 0;
            } catch (err) {
                alert("Lỗi: " + err.message);
            } finally {
                btnScanFolder.disabled = false;
                btnScanFolder.textContent = "Quét";
            }
        });
    }

    // Duyệt đệ quy một mục kéo thả (tệp hoặc thư mục) để gom hết tệp bên trong
    function walkEntry(entry, out, depth = 0) {
        return new Promise((resolve) => {
            if (!entry || depth > 12) return resolve();

            if (entry.isFile) {
                entry.file(
                    (file) => { out.push(file); resolve(); },
                    () => resolve()
                );
                return;
            }

            if (entry.isDirectory) {
                const reader = entry.createReader();
                const readBatch = () => {
                    reader.readEntries(async (batch) => {
                        if (!batch || batch.length === 0) return resolve();
                        for (const child of batch) {
                            await walkEntry(child, out, depth + 1);
                        }
                        readBatch();   // readEntries chỉ trả tối đa 100 mục mỗi lần
                    }, () => resolve());
                };
                readBatch();
                return;
            }

            resolve();
        });
    }

    // Generic Drag & Drop Helper
    function setupDragDrop(el, onDrop) {
        ["dragenter", "dragover"].forEach(name => {
            el.addEventListener(name, (e) => {
                e.preventDefault();
                e.stopPropagation();
                el.classList.add("dragover");
            });
        });
        ["dragleave", "drop"].forEach(name => {
            el.addEventListener(name, (e) => {
                e.preventDefault();
                e.stopPropagation();
                el.classList.remove("dragover");
            });
        });
        el.addEventListener("drop", async (e) => {
            if (!e.dataTransfer) return;

            // Kéo thả cả THƯ MỤC: trình duyệt chỉ trả về thư mục qua items[].
            // Phải duyệt đệ quy mới lấy được tệp bên trong; nếu trình duyệt không
            // hỗ trợ thì rơi về danh sách tệp phẳng như bình thường.
            const items = e.dataTransfer.items;
            if (items && items.length > 0 && typeof items[0].webkitGetAsEntry === "function") {
                const entries = [];
                for (let i = 0; i < items.length; i++) {
                    const entry = items[i].webkitGetAsEntry();
                    if (entry) entries.push(entry);
                }
                if (entries.length > 0) {
                    try {
                        const collected = [];
                        for (const entry of entries) {
                            await walkEntry(entry, collected);
                        }
                        if (collected.length > 0) {
                            onDrop(collected);
                            return;
                        }
                    } catch (err) {
                        console.warn("Không duyệt được thư mục kéo thả, dùng danh sách tệp phẳng:", err);
                    }
                }
            }

            if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                onDrop(Array.from(e.dataTransfer.files));
            }
        });
    }

    // ==========================================
    // RENDER PREVIEWS
    // ==========================================
    function renderInitialPreview(items, total) {
        previewPlaceholder.classList.add("hidden");
        previewList.classList.remove("hidden");
        previewToolbar.classList.add("hidden");
        previewBadge.textContent = `Bóc tách thành công ${items.length} / ${total} câu gốc`;
        previewList.innerHTML = "";

        items.forEach(q => {
            const card = document.createElement("div");
            card.className = "preview-item";

            let optionsHtml = "";
            if (q.options && q.options.length > 0) {
                optionsHtml = `<div class="preview-options-grid">${q.options.map(opt => `<div>${escapeHtml(opt)}</div>`).join('')}</div>`;
            }

            let solHtml = "";
            if (q.solution) {
                solHtml = `
                    <div class="preview-callout callout-sol">
                        <span class="callout-title">✎ Lời giải gốc:</span>
                        <div>${escapeMultiline(q.solution)}</div>
                    </div>
                `;
            }

            card.innerHTML = `
                <div class="preview-item-header">
                    <span class="preview-qtitle">▶ ${escapeHtml(q.title || `Câu ${q.index}`)}</span>
                    <span class="badge-level">Gốc từ tệp</span>
                </div>
                <div class="preview-qcontent">${escapeHtml(q.content)}</div>
                ${optionsHtml}
                ${solHtml}
            `;
            previewList.appendChild(card);
        });
    }

    function renderBookPreview(book) {
        currentCompiledBook = book;
        previewPlaceholder.classList.add("hidden");
        previewList.classList.remove("hidden");
        previewToolbar.classList.remove("hidden");
        previewBadge.textContent = `Tổng: ${book.total_questions} bài toán chuẩn BGD`;
        previewList.innerHTML = "";

        // Banner Tiêu đề sách
        const bookHeader = document.createElement("div");
        bookHeader.className = "preview-book-banner";
        bookHeader.innerHTML = `
            <h4>${escapeHtml(book.new_title)}</h4>
            <p class="book-sub">${escapeHtml(book.subtitle)}</p>
            <p class="book-note"><em>"${escapeMultiline(book.author_note)}"</em></p>
        `;
        previewList.appendChild(bookHeader);

        // Hiển thị Bí kíp thủ khoa
        if (book.valedictorian_secrets && book.valedictorian_secrets.length > 0) {
            const secBox = document.createElement("div");
            secBox.className = "preview-callout callout-casio";
            secBox.innerHTML = `
                <span class="callout-title">🏆 BÍ KÍP VÀNG PHÒNG THI & CHIẾN THUẬT TỪ THỦ KHOA:</span>
                <div style="font-size: 13.5px; line-height: 1.6; margin-top: 6px;">${book.valedictorian_secrets.map(s => `• ${escapeHtml(s)}`).join('<br>')}</div>
            `;
            previewList.appendChild(secBox);
        }

        // Hiển thị Góc kết nối STEM GDPT 2018
        if (book.stem_connection) {
            const stemBox = document.createElement("div");
            stemBox.className = "preview-callout callout-sol";
            stemBox.innerHTML = `
                <span class="callout-title">🌐 GÓC KẾT NỐI THỰC TIỄN ĐỜI SỐNG & CÔNG NGHỆ (GDPT 2018):</span>
                <div style="font-size: 13.5px; line-height: 1.6; margin-top: 6px;">${escapeHtml(book.stem_connection).replace(/\n/g, '<br>')}</div>
            `;
            previewList.appendChild(stemBox);
        }

        // Hiển thị Phần I nếu là Single Book
        if (book.theory_section && !book.is_master_book) {
            const theoryBox = document.createElement("div");
            theoryBox.className = "preview-callout callout-theory";
            theoryBox.innerHTML = `
                <span class="callout-title">📘 PHẦN I: KIẾN THỨC TRỌNG TÂM & LÝ THUYẾT CỐT LÕI GDPT 2018</span>
                <div style="font-size: 13.5px; line-height: 1.6; margin-top: 6px;">${book.theory_section.replace(/\n/g, '<br>')}</div>
            `;
            previewList.appendChild(theoryBox);
        }

        // Lặp qua câu hỏi hoặc chương
        if (book.is_master_book && book.chapters) {
            book.chapters.forEach(ch => {
                const chBox = document.createElement("div");
                chBox.className = "preview-chapter-header";
                chBox.innerHTML = `<h5>${escapeHtml(ch.title)} (${ch.total_questions} câu)</h5>`;
                previewList.appendChild(chBox);

                if (ch.theory_section) {
                    const th = document.createElement("div");
                    th.className = "preview-callout callout-theory";
                    th.innerHTML = `
                        <span class="callout-title">📘 LÝ THUYẾT NỀN TẢNG — ${ch.title}</span>
                        <div>${ch.theory_section.replace(/\n/g, '<br>')}</div>
                    `;
                    previewList.appendChild(th);
                }

                renderQuestionCards(ch.questions, previewList);
            });
        } else {
            renderQuestionCards(book.questions, previewList);
        }

        applyLevelFilter(activeFilterLevel);
    }

    function renderQuestionCards(questions, container) {
        questions.forEach(q => {
            const card = document.createElement("div");
            card.className = "preview-item";
            card.dataset.level = q.level || "Vận dụng";

            let optionsHtml = "";
            if (q.new_options && q.new_options.length > 0) {
                optionsHtml = `<div class="preview-options-grid">${q.new_options.map(opt => `<div>${escapeHtml(opt)}</div>`).join('')}</div>`;
            }

            let sol1Html = "";
            if (q.solution_method1) {
                sol1Html = `
                    <div class="preview-callout callout-sol">
                        <span class="callout-title">✎ Lời giải Tự luận chuẩn mực sư phạm:</span>
                        <div>${escapeMultiline(q.solution_method1)}</div>
                    </div>
                `;
            }

            let casioHtml = "";
            if (checkCasio.checked && q.solution_method2) {
                casioHtml = `
                    <div class="preview-callout callout-casio">
                        <span class="callout-title">💡 Kỹ thuật Casio fx-580VN X & Thủ thuật 15s:</span>
                        <div>${escapeMultiline(q.solution_method2)}</div>
                    </div>
                `;
            }

            let trapHtml = "";
            if (checkTraps.checked && q.trap_warning) {
                trapHtml = `
                    <div class="preview-callout callout-trap">
                        <span class="callout-title">⚠️ Bẫy đề thi & Sai lầm thường gặp:</span>
                        <div>${escapeMultiline(q.trap_warning)}</div>
                    </div>
                `;
            }

            card.innerHTML = `
                <div class="preview-item-header">
                    <span class="preview-qtitle">▶ ${escapeHtml(q.title)}</span>
                    <span class="badge-level">${escapeHtml(q.level || 'Vận dụng')}</span>
                    ${q.is_added_new ? `<span class="badge-added">MỚI BỔ SUNG</span>` : ''}
                </div>
                <div class="preview-qcontent">${escapeHtml(q.new_content)}</div>
                ${optionsHtml}
                ${sol1Html}
                ${casioHtml}
                ${trapHtml}
            `;
            container.appendChild(card);
        });
    }

    // Level Filter logic
    filterChips.forEach(chip => {
        chip.addEventListener("click", () => {
            filterChips.forEach(c => c.classList.remove("active"));
            chip.classList.add("active");
            activeFilterLevel = chip.dataset.level;
            applyLevelFilter(activeFilterLevel);
        });
    });

    function applyLevelFilter(level) {
        const items = previewList.querySelectorAll(".preview-item");
        items.forEach(item => {
            if (level === "all" || item.dataset.level === level) {
                item.style.display = "";
            } else {
                item.style.display = "none";
            }
        });
    }

    // Toggle Solutions visibility
    if (btnToggleSolutions) {
        btnToggleSolutions.addEventListener("click", () => {
            areSolutionsVisible = !areSolutionsVisible;
            const callouts = previewList.querySelectorAll(".callout-sol, .callout-casio, .callout-trap");
            callouts.forEach(c => c.style.display = areSolutionsVisible ? "" : "none");
            btnToggleSolutions.textContent = areSolutionsVisible ? "👁️ Ẩn Lời Giải" : "👁️ Hiện Lời Giải";
        });
    }

    // ==========================================
    // RENDER QA SCORECARD
    // ==========================================
    function renderQAScorecard(report) {
        const qaCard = document.getElementById("qa-scorecard");
        const qaScore = document.getElementById("qa-total-score");
        const qaList = document.getElementById("qa-checks-list");

        if (!report || !report.checks) {
            if (qaCard) qaCard.classList.add("hidden");
            return;
        }

        qaCard.classList.remove("hidden");
        qaScore.textContent = `${report.total_score} / ${report.max_score || 100} ĐIỂM (${report.status_text})`;
        qaList.innerHTML = report.checks.map(c => `
            <div class="qa-check-item">
                <span class="qa-check-icon">${c.passed ? "✔" : "⚠️"}</span>
                <div class="qa-check-content">
                    <div class="qa-check-name">
                        <span>${c.name} [${c.category}]</span>
                        <span class="qa-check-score">${c.score}/${c.max_score}đ</span>
                    </div>
                    <div class="qa-check-detail">${c.detail}</div>
                </div>
            </div>
        `).join("");
    }

    // ==========================================
    // AI GEMINI CREATIVE TITLES DRAWER
    // ==========================================
    if (btnSuggestTitles) {
        btnSuggestTitles.addEventListener("click", () => goiYTuaSach(false));
    }

    // Nhớ các tựa đã đề xuất để nút "Đổi 5 tựa khác" không lặp lại ý cũ
    let tuaDaDeXuat = [];

    async function goiYTuaSach(doiTuaKhac) {
        aiTitlesDrawer.classList.remove("hidden");
        aiTitlesList.innerHTML = `<div class="ai-title-loading">⚡ ${
            doiTuaKhac ? "Đang nghĩ 5 tựa hoàn toàn khác..." : "Đang phân tích chuyên đề và đặt tựa..."
        }</div>`;

        if (!doiTuaKhac) tuaDaDeXuat = [];

        const fname = currentScannedFiles.length > 0 ? currentScannedFiles[0].name : "";
        // Lấy vài câu đầu làm mẫu nội dung — đặt tựa theo nội dung thật sát hơn
        // nhiều so với chỉ nhìn tên tệp.
        let mauNoiDung = "";
        if (currentCompiledBook && currentCompiledBook.questions) {
            mauNoiDung = currentCompiledBook.questions.slice(0, 4)
                .map((q) => q.new_content || "").join(" ").slice(0, 900);
        }

        try {
            const resp = await apiFetch("/api/suggest-titles", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    filename: fname,
                    sample_text: mauNoiDung,
                    subject: selectedSubject,
                    exclude_titles: tuaDaDeXuat,
                    doc_type: (currentCompiledBook && currentCompiledBook.doc_type) || "",
                }),
            });
            const data = await resp.json();

            if (!(data.status === "success" && data.titles && data.titles.length)) {
                throw new Error(data.detail || "Không tạo được tựa. Kiểm tra lại API Key trong ⚙️ Cài Đặt AI.");
            }

            data.titles.forEach((t) => {
                if (t.title && !tuaDaDeXuat.includes(t.title)) tuaDaDeXuat.push(t.title);
            });

            aiTitlesList.innerHTML = "";
            data.titles.forEach((t) => {
                const card = document.createElement("div");
                card.className = "ai-title-card";
                card.innerHTML = `
                    <div class="ai-card-style-badge">${escapeHtml(t.style || "")}</div>
                    <div class="ai-card-main-title">${escapeHtml(t.title || "")}</div>
                    <div class="ai-card-subtitle">${escapeHtml(t.subtitle || "")}</div>
                    <div class="ai-card-hook">💡 ${escapeHtml(t.hook || "")}</div>
                    <button type="button" class="btn-apply-title">👉 Dùng tựa này</button>
                `;
                card.querySelector(".btn-apply-title").addEventListener("click", () => {
                    customTitleInput.value = t.title;
                    customTitleInput.style.borderColor = "#10B981";
                    customTitleInput.style.boxShadow = "0 0 10px rgba(16, 185, 129, 0.4)";
                    setTimeout(() => {
                        customTitleInput.style.borderColor = "";
                        customTitleInput.style.boxShadow = "";
                    }, 2000);
                    aiTitlesDrawer.classList.add("hidden");
                });
                aiTitlesList.appendChild(card);
            });
        } catch (err) {
            aiTitlesList.innerHTML =
                `<div class="ai-title-loading" style="color:#F87171">${escapeHtml(err.message)}</div>`;
        }
    }

    if (btnRefreshTitles) {
        btnRefreshTitles.addEventListener("click", async () => {
            btnRefreshTitles.disabled = true;
            const chuCu = btnRefreshTitles.textContent;
            btnRefreshTitles.textContent = "⏳ Đang đổi...";
            await goiYTuaSach(true);
            btnRefreshTitles.disabled = false;
            btnRefreshTitles.textContent = chuCu;
        });
    }

    if (btnCloseTitles) {
        btnCloseTitles.addEventListener("click", () => {
            aiTitlesDrawer.classList.add("hidden");
        });
    }

    // ==========================================
    // PROCESS REWRITE PIPELINE
    // ==========================================
    btnProcess.addEventListener("click", async () => {
        btnProcess.disabled = true;
        progressCard.classList.remove("hidden");
        resultCard.classList.add("hidden");

        const progressMessages = [
            "Đang quét và bóc tách độc lập các bài toán...",
            "Đang xây dựng Phần I: Lý thuyết nền tảng & Bảng công thức vàng CT GDPT 2018...",
            "Đang thiết lập lời giải kép tự luận và kỹ thuật Casio fx-580VN X...",
            "Đang bổ sung cảnh báo bẫy đề thi và lỗi sai học sinh...",
            "Đang căn lề in ấn Nghị định 30 (Trái 30mm, Phải 15mm, Trên 20mm, Dưới 20mm)..."
        ];

        let msgIdx = 0;
        let pct = 15;
        progressStatus.textContent = progressMessages[0];
        progressBar.style.width = "15%";

        const timer = setInterval(() => {
            msgIdx = (msgIdx + 1) % progressMessages.length;
            progressStatus.textContent = progressMessages[msgIdx];
            pct = Math.min(92, pct + 18);
            progressBar.style.width = `${pct}%`;

            if (pct >= 30) pstep1.classList.add("completed");
            if (pct >= 55) pstep2.classList.add("completed");
            if (pct >= 75) pstep3.classList.add("completed");
            if (pct >= 90) pstep4.classList.add("completed");
        }, 1800);

        // Khổ giấy được lưu vào cài đặt để bộ xuất bản dùng đúng kích thước trang
        if (paperFormatSelect) {
            try {
                await apiFetch("/api/settings", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ output_format: paperFormatSelect.value })
                });
            } catch (e) {
                console.warn("Không lưu được khổ giấy, dùng mặc định A4:", e);
            }
        }

        try {
            // Một tài liệu -> một cuốn sách. Nhiều tài liệu -> gộp chung hoặc tách riêng.
            if (ingestKind !== "single") {
                const folderMode = document.querySelector("input[name='folder-mode']:checked").value;
                const formData = new FormData();
                formData.append("folder_path", ingestFolderPath || folderPathInput.value.trim());
                formData.append("mode", folderMode);
                formData.append("subject", selectedSubject);
                formData.append("add_count", addCountSelect.value);
                if (customTitleInput.value.trim()) {
                    formData.append("master_title", customTitleInput.value.trim());
                }
                themTuyChonBienSoan(formData);

                const res = await apiFetch("/api/process-folder", { method: "POST", body: formData });
                const data = await res.json();
                clearInterval(timer);
                progressBar.style.width = "100%";
                progressCard.classList.add("hidden");
                btnProcess.disabled = false;

                if (data.status === "success") {
                    resultCard.classList.remove("hidden");
                    if (data.mode === "merge") {
                        resultTitle.textContent = data.book.new_title;
                        resultSubtitle.textContent = `${data.book.subtitle} (${data.book.total_chapters} chương - ${data.book.total_questions} bài toán)`;
                        btnDownload.href = data.download_url;
                        resultSingleActions.classList.remove("hidden");
                        resultBatchList.classList.add("hidden");
                        renderQAScorecard(data.validation_report);
                        renderBookPreview(data.book);
                    } else {
                        resultTitle.textContent = `Đã biên soạn thành công ${data.total_books} cuốn sách riêng lẻ`;
                        resultSubtitle.textContent = "Tất cả các tệp Word .docx đã được định dạng chuẩn Nghị định 30 và nén sẵn vào 1 file ZIP.";
                        resultSingleActions.classList.add("hidden");
                        resultBatchList.classList.remove("hidden");
                        const qaCard = document.getElementById("qa-scorecard");
                        if (qaCard) qaCard.classList.add("hidden");

                        let batchHtml = "";
                        if (data.zip_download_url) {
                            batchHtml += `
                                <div style="margin-bottom: 16px; text-align: center;">
                                    <a href="${data.zip_download_url}" class="btn btn-success btn-large" style="display: inline-flex; width: auto; padding: 12px 28px;">
                                        <span class="icon">📦</span> TẢI TRỌN BỘ SÁCH (.ZIP) — 1 CLICK
                                    </a>
                                </div>
                            `;
                        }
                        batchHtml += data.books.map(b => `
                            <div class="result-batch-item">
                                <div>
                                    <strong>${b.title}</strong>
                                    <p style="font-size: 11.5px; color: var(--text-muted);">Nguồn: ${b.source} (${b.total_questions} câu) — Đạt chuẩn: ${b.validation_report ? b.validation_report.total_score : 100}/100đ</p>
                                </div>
                                <a href="${b.download_url}" class="btn btn-outline" style="padding: 6px 14px; font-size: 12px;">📥 Tải DOCX</a>
                            </div>
                        `).join("");
                        resultBatchList.innerHTML = batchHtml;
                    }
                } else {
                    alert("Lỗi: " + (data.detail || "Không rõ nguyên nhân"));
                }
            } 
            // XỬ LÝ THEO CHẾ ĐỘ FILE ĐƠN
            else {
                const formData = new FormData();
                formData.append("filename", singleFilePath);
                formData.append("subject", selectedSubject);
                formData.append("add_count", addCountSelect.value);
                if (customTitleInput.value.trim()) {
                    formData.append("custom_title", customTitleInput.value.trim());
                }
                if (doctypeSelect && doctypeSelect.value) {
                    formData.append("doc_type", doctypeSelect.value);
                }
                if (aiScopeSelect && aiScopeSelect.value) {
                    formData.append("ai_scope", aiScopeSelect.value);
                }
                themTuyChonBienSoan(formData);

                const res = await apiFetch("/api/process", { method: "POST", body: formData });
                const data = await res.json();
                clearInterval(timer);
                progressBar.style.width = "100%";
                progressCard.classList.add("hidden");
                btnProcess.disabled = false;

                if (data.status === "success") {
                    resultCard.classList.remove("hidden");
                    resultTitle.textContent = data.book.new_title;
                    resultSubtitle.textContent = `${data.book.subtitle} (${data.book.total_questions} bài toán hoàn chỉnh)`;
                    btnDownload.href = data.download_url;
                    resultSingleActions.classList.remove("hidden");
                    resultBatchList.classList.add("hidden");
                    renderQAScorecard(data.validation_report);
                    renderBookPreview(data.book);
                } else {
                    alert("Lỗi: " + (data.detail || "Không rõ"));
                }
            }
        } catch (err) {
            clearInterval(timer);
            progressCard.classList.add("hidden");
            btnProcess.disabled = false;
            alert("Lỗi biên soạn: " + err.message);
        }
    });

    // ==========================================
    // INTERACTIVE WEB BOOK READER MODAL
    // ==========================================
    if (btnReadOnline) {
        btnReadOnline.addEventListener("click", () => {
            if (!currentCompiledBook) {
                alert("Vui lòng biên soạn sách trước khi đọc trực tuyến!");
                return;
            }
            openWebReader(currentCompiledBook);
        });
    }

    if (btnCloseReader) {
        btnCloseReader.addEventListener("click", () => modalReader.classList.add("hidden"));
    }

    if (btnPrintReader) {
        btnPrintReader.addEventListener("click", () => {
            window.print();
        });
    }

    function openWebReader(book) {
        readerBookTitle.textContent = book.new_title;
        readerBookSubtitle.textContent = book.subtitle;
        readerContent.innerHTML = "";

        // Cover / Title Page
        const cover = document.createElement("div");
        cover.className = "reader-cover";
        cover.innerHTML = `
            <div style="font-size: 13px; font-weight: bold; letter-spacing: 2px; color: #4A5568; margin-bottom: 8px;">TÀI LIỆU LƯU HÀNH NỘI BỘ — CHƯƠNG TRÌNH GDPT 2018</div>
            <h1>${escapeHtml(book.new_title)}</h1>
            <div class="reader-sub">${escapeHtml(book.subtitle)}</div>
            <div class="reader-intro">
                <strong>Lời Tựa Sư Phạm:</strong><br>
                ${escapeHtml(book.author_note)}
            </div>
        `;
        readerContent.appendChild(cover);

        // Hiển thị Bí kíp thủ khoa trong Reader
        if (book.valedictorian_secrets && book.valedictorian_secrets.length > 0) {
            const secBox = document.createElement("div");
            secBox.className = "reader-callout reader-callout-casio";
            secBox.innerHTML = `
                <strong>🏆 BÍ KÍP VÀNG PHÒNG THI & CHIẾN THUẬT TỪ THỦ KHOA:</strong>
                <div style="margin-top: 6px;">${book.valedictorian_secrets.map(s => `• ${escapeHtml(s)}`).join('<br>')}</div>
            `;
            readerContent.appendChild(secBox);
        }

        // Hiển thị Góc kết nối STEM GDPT 2018 trong Reader
        if (book.stem_connection) {
            const stemBox = document.createElement("div");
            stemBox.className = "reader-callout reader-callout-sol";
            stemBox.innerHTML = `
                <strong>🌐 GÓC KẾT NỐI THỰC TIỄN ĐỜI SỐNG & CÔNG NGHỆ (GDPT 2018):</strong>
                <div style="margin-top: 6px; white-space: pre-line;">${escapeHtml(book.stem_connection)}</div>
            `;
            readerContent.appendChild(stemBox);
        }

        // Render Single Book vs Master Book
        if (book.is_master_book && book.chapters) {
            book.chapters.forEach(ch => {
                const chHeader = document.createElement("div");
                chHeader.className = "reader-section-title";
                chHeader.textContent = ch.title;
                readerContent.appendChild(chHeader);

                if (ch.theory_section) {
                    const th = document.createElement("div");
                    th.className = "reader-callout reader-callout-sol";
                    th.innerHTML = `
                        <strong>📘 PHẦN I: KIẾN THỨC TRỌNG TÂM & LÝ THUYẾT NỀN TẢNG CHUẨN BGD</strong>
                        <div style="margin-top: 6px; white-space: pre-line;">${ch.theory_section}</div>
                    `;
                    readerContent.appendChild(th);
                }

                renderReaderQuestions(ch.questions, readerContent);
            });
        } else {
            if (book.theory_section) {
                const th = document.createElement("div");
                th.className = "reader-callout reader-callout-sol";
                th.innerHTML = `
                    <strong>📘 PHẦN I: KIẾN THỨC TRỌNG TÂM & LÝ THUYẾT NỀN TẢNG CHUẨN BGD</strong>
                    <div style="margin-top: 6px; white-space: pre-line;">${book.theory_section}</div>
                `;
                readerContent.appendChild(th);
            }

            const secTitle = document.createElement("div");
            secTitle.className = "reader-section-title";
            secTitle.textContent = "PHẦN II: HỆ THỐNG BÀI TOÁN RÈN LUYỆN THEO CẤP ĐỘ NHẬN THỨC";
            readerContent.appendChild(secTitle);

            renderReaderQuestions(book.questions, readerContent);
        }

        modalReader.classList.remove("hidden");
    }

    function renderReaderQuestions(questions, container) {
        questions.forEach(q => {
            const card = document.createElement("div");
            card.className = "reader-q-card";

            let optsHtml = "";
            if (q.new_options && q.new_options.length > 0) {
                optsHtml = `<div class="reader-options-box">${q.new_options.map(opt => {
                    const isCorrect = q.correct_answer && opt.trim().startsWith(q.correct_answer);
                    return `<div class="reader-opt-item ${isCorrect ? 'correct' : ''}">${escapeHtml(opt)}</div>`;
                }).join('')}</div>`;
            }

            let sol1Html = "";
            if (q.solution_method1) {
                sol1Html = `
                    <div class="reader-callout reader-callout-sol">
                        <strong>✎ Hướng dẫn giải chi tiết (Tự luận chuẩn mực):</strong>
                        <div style="margin-top: 4px; white-space: pre-line;">${q.solution_method1}</div>
                    </div>
                `;
            }

            let casioHtml = "";
            if (q.solution_method2) {
                casioHtml = `
                    <div class="reader-callout reader-callout-casio">
                        <strong>💡 Kỹ thuật Casio fx-580VN X & Tư duy giải nhanh:</strong>
                        <div style="margin-top: 4px; white-space: pre-line;">${q.solution_method2}</div>
                    </div>
                `;
            }

            let trapHtml = "";
            if (q.trap_warning) {
                trapHtml = `
                    <div class="reader-callout reader-callout-trap">
                        <strong>⚠️ Bẫy đề thi & Lỗi sai học sinh hay mắc phải:</strong>
                        <div style="margin-top: 4px; white-space: pre-line;">${q.trap_warning}</div>
                    </div>
                `;
            }

            card.innerHTML = `
                <div class="reader-q-head">▶ ${q.title} [${q.level || 'Vận dụng'}]</div>
                <div class="reader-q-text">${q.new_content}</div>
                ${optsHtml}
                ${sol1Html}
                ${casioHtml}
                ${trapHtml}
            `;
            container.appendChild(card);
        });
    }

    // ==========================================
    // DEPLOY GUIDE MODAL
    // ==========================================
    if (btnDeployInfo) {
        btnDeployInfo.addEventListener("click", () => modalDeploy.classList.remove("hidden"));
    }
    if (btnCloseDeploy) {
        btnCloseDeploy.addEventListener("click", () => modalDeploy.classList.add("hidden"));
    }
    if (btnDismissDeploy) {
        btnDismissDeploy.addEventListener("click", () => modalDeploy.classList.add("hidden"));
    }

    // ==========================================
    // OPEN FOLDERS
    // ==========================================
    async function triggerOpenOutputFolder() {
        try {
            const res = await apiFetch("/api/open-output-folder", { method: "POST" });
            const data = await res.json();
            if (data.status === "info") {
                alert(data.message);
            }
        } catch (e) {
            console.error(e);
        }
    }
    btnOpenFolder.addEventListener("click", triggerOpenOutputFolder);
    btnOpenResultFolder.addEventListener("click", triggerOpenOutputFolder);

    // ==========================================
    // HỘP THOẠI CÀI ĐẶT
    // Khóa API được giữ trong trình duyệt của chính người dùng. Máy chủ không
    // nhận, không lưu và không dùng chung khóa giữa những người vào trang.
    // ==========================================
    function describeKey(key) {
        if (!key) return "";
        return "••••••••" + key.slice(-4);
    }

    function refreshKeyStatus() {
        if (!keyStatusEl) return;
        const key = readStore(KEY_STORE);
        if (key) {
            keyStatusEl.textContent = `✅ Đang dùng khóa của bạn (${describeKey(key)}) — lưu trên trình duyệt này`;
            keyStatusEl.className = "key-status key-status-on";
        } else if (serverHasKey) {
            keyStatusEl.textContent = "💻 Đang chạy trên máy cá nhân, dùng khóa đã cấu hình sẵn trong máy";
            keyStatusEl.className = "key-status key-status-local";
        } else {
            keyStatusEl.textContent = "Chưa có khóa — đang dùng Bộ máy Offline (vẫn biên soạn được sách)";
            keyStatusEl.className = "key-status";
        }
    }

    let serverHasKey = false;

    btnSettings.addEventListener("click", async () => {
        // Khóa lấy từ trình duyệt, không hỏi máy chủ
        geminiApiKeyInput.value = readStore(KEY_STORE);
        geminiModelSelect.value = readStore(MODEL_STORE) || "gemini-3.6-flash";

        try {
            const res = await apiFetch("/api/settings");
            const settings = await res.json();
            serverHasKey = !!settings.server_key_available;
        } catch (e) {
            serverHasKey = false;
        }

        refreshKeyStatus();
        modalSettings.classList.remove("hidden");
    });

    btnCloseModal.addEventListener("click", () => modalSettings.classList.add("hidden"));
    modalSettings.addEventListener("click", (e) => {
        if (e.target === modalSettings) modalSettings.classList.add("hidden");
    });

    btnToggleKey.addEventListener("click", () => {
        if (geminiApiKeyInput.type === "password") {
            geminiApiKeyInput.type = "text";
            btnToggleKey.textContent = "Ẩn";
        } else {
            geminiApiKeyInput.type = "password";
            btnToggleKey.textContent = "Hiện";
        }
    });

    btnSaveSettings.addEventListener("click", () => {
        const key = geminiApiKeyInput.value.trim();
        const model = geminiModelSelect.value;

        const okKey = writeStore(KEY_STORE, key);
        const okModel = writeStore(MODEL_STORE, model);

        if (!okKey || !okModel) {
            alert(
                "Trình duyệt đang chặn lưu trữ cục bộ (thường gặp ở chế độ ẩn danh), " +
                "nên không giữ được khóa cho lần sau. Khóa vẫn dùng được trong phiên này."
            );
        }

        refreshKeyStatus();
        modalSettings.classList.add("hidden");

        if (key) {
            alert("Đã lưu khóa API vào trình duyệt của bạn. Khóa này chỉ mình bạn dùng.");
        } else {
            alert("Đã xóa khóa API khỏi trình duyệt. Ứng dụng sẽ chạy bằng Bộ máy Offline.");
        }
    });

    // ==========================================
    // LÒ SOẠN ĐỀ AI
    // AI soạn đề mới, nhưng chỉ câu qua đủ 3 lớp thẩm định mới vào ngân hàng.
    // Câu bị loại vẫn hiện kèm lý do — người dùng cần thấy AI sai ở đâu chứ
    // không phải một con số "đã tạo N câu" vô nghĩa.
    // ==========================================
    const TEN_CHUYEN_DE = {
        ham_so: "Ứng dụng đạo hàm — khảo sát hàm số",
        mu_logarit: "Hàm số mũ & logarit",
        nguyen_ham_tich_phan: "Nguyên hàm — tích phân & ứng dụng",
        hinh_hoc_khong_gian: "Hình học không gian & Oxyz",
        dai_so_co_ban: "Bất đẳng thức, tổ hợp — xác suất, dãy số",
        dao_dong_co: "Dao động cơ",
        song_co: "Sóng cơ & giao thoa",
        dien_xoay_chieu: "Dòng điện xoay chiều & mạch RLC",
    };
    const CHUYEN_DE_TOAN = ["ham_so", "mu_logarit", "nguyen_ham_tich_phan",
                            "hinh_hoc_khong_gian", "dai_so_co_ban"];
    const CHUYEN_DE_LY = ["dao_dong_co", "song_co", "dien_xoay_chieu"];

    function napDanhSachChuyenDe() {
        if (!forgeTopic) return;
        const ds = selectedSubject === "toan" ? CHUYEN_DE_TOAN : CHUYEN_DE_LY;
        forgeTopic.innerHTML = ds
            .map((k) => `<option value="${k}">${escapeHtml(TEN_CHUYEN_DE[k] || k)}</option>`)
            .join("");
    }

    function veThongKeNganHang(tk) {
        if (!forgeStats || !tk) return;
        const theoChuyenDe = Object.keys(tk.theo_chuyen_de || {})
            .map((k) => `${escapeHtml(TEN_CHUYEN_DE[k] || k)}: <strong>${tk.theo_chuyen_de[k]}</strong>`)
            .join(" · ") || "chưa có câu nào";
        forgeStats.innerHTML = `
            <div class="forge-stat-row">
                <span>📚 Đã thẩm định: <strong>${tk.tong_da_tham_dinh}</strong> câu</span>
                <span>🚫 Đã loại: <strong>${tk.tong_bi_loai}</strong> câu</span>
            </div>
            <div class="forge-stat-detail">${theoChuyenDe}</div>
        `;
    }

    async function taiNganHang() {
        try {
            const res = await apiFetch("/api/question-bank");
            const data = await res.json();
            if (data.status === "success") veThongKeNganHang(data.thong_ke);
        } catch (e) {
            if (forgeStats) forgeStats.textContent = "Không tải được ngân hàng câu hỏi.";
        }
    }

    if (btnForge) {
        btnForge.addEventListener("click", async () => {
            napDanhSachChuyenDe();
            modalForge.classList.remove("hidden");
            await taiNganHang();
        });
    }
    if (btnCloseForge) {
        btnCloseForge.addEventListener("click", () => modalForge.classList.add("hidden"));
    }
    if (modalForge) {
        modalForge.addEventListener("click", (e) => {
            if (e.target === modalForge) modalForge.classList.add("hidden");
        });
    }

    function veMotCau(q, dat) {
        const dauHieu = dat
            ? (q.checks_passed || []).map((c) => `<li class="forge-pass">✔ ${escapeHtml(c)}</li>`).join("")
            : (q.reject_reasons || []).map((c) => `<li class="forge-fail">✘ ${escapeHtml(c)}</li>`).join("");
        const phuongAn = (q.options || [])
            .map((o) => {
                const dung = o.trim().startsWith(q.correct);
                return `<div class="forge-opt ${dung ? "forge-opt-correct" : ""}">${escapeHtml(o)}</div>`;
            })
            .join("");
        return `
            <div class="forge-card ${dat ? "forge-card-ok" : "forge-card-bad"}">
                <div class="forge-card-head">
                    <span class="forge-badge">${dat ? "✅ ĐẠT" : "❌ BỊ LOẠI"}</span>
                    <span class="forge-level">${escapeHtml(q.level || "")} · ${escapeHtml(q.grade || "")}</span>
                </div>
                <div class="forge-content">${escapeHtml(q.content || "")}</div>
                <div class="forge-opts">${phuongAn}</div>
                <div class="forge-answer">Đáp án đề ghi: <strong>${escapeHtml(q.correct || "?")}</strong>${
                    q.resolve_answer ? ` · AI giải lại ra: <strong>${escapeHtml(q.resolve_answer)}</strong>` : ""
                }</div>
                <details class="forge-solution">
                    <summary>Xem lời giải</summary>
                    <div>${escapeMultiline(q.solution || "")}</div>
                </details>
                <ul class="forge-checks">${dauHieu}</ul>
            </div>
        `;
    }

    if (btnForgeRun) {
        btnForgeRun.addEventListener("click", async () => {
            btnForgeRun.disabled = true;
            btnForgeRun.textContent = "⏳ Đang soạn và thẩm định...";
            forgeResult.classList.remove("hidden");
            forgeResult.innerHTML = '<div class="forge-loading">AI đang soạn đề, sau đó sẽ tự giải lại để đối chiếu. Mất khoảng 20-60 giây...</div>';

            try {
                const res = await apiFetch("/api/generate-questions", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        topic_key: forgeTopic.value,
                        subject: selectedSubject,
                        grade: forgeGrade.value,
                        level: forgeLevel.value,
                        so_luong: parseInt(forgeCount.value, 10),
                    }),
                });
                const data = await res.json();

                if (!res.ok || data.status !== "success") {
                    throw new Error(data.detail || "Không soạn được câu hỏi");
                }

                const dat = data.dat || [];
                const truot = data.truot || [];
                veThongKeNganHang(data.thong_ke);

                forgeResult.innerHTML = `
                    <div class="forge-summary">
                        AI soạn <strong>${data.tong}</strong> câu ·
                        <span class="forge-pass">${dat.length} đạt, đã vào ngân hàng</span> ·
                        <span class="forge-fail">${truot.length} bị loại</span> ·
                        tốn ${data.so_luot_goi_api} lượt API
                    </div>
                    ${dat.map((q) => veMotCau(q, true)).join("")}
                    ${truot.map((q) => veMotCau(q, false)).join("")}
                `;
            } catch (err) {
                forgeResult.innerHTML = `<div class="forge-error">❌ ${escapeHtml(err.message)}</div>`;
            } finally {
                btnForgeRun.disabled = false;
                btnForgeRun.textContent = "⚡ Soạn đề & Thẩm định";
            }
        });
    }

    // Tải ngân hàng về / nhập lại — cần thiết vì đĩa trên Render là tạm
    if (btnBankExport) {
        btnBankExport.addEventListener("click", async () => {
            try {
                const res = await apiFetch("/api/question-bank/export");
                if (!res.ok) {
                    const d = await res.json();
                    throw new Error(d.detail || "Không tải được");
                }
                const blob = await res.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = "ngan_hang_cau_hoi.json";
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            } catch (err) {
                alert("Lỗi: " + err.message);
            }
        });
    }

    if (btnBankImport) {
        btnBankImport.addEventListener("click", () => bankImportInput.click());
        bankImportInput.addEventListener("change", async (e) => {
            if (!e.target.files.length) return;
            const fd = new FormData();
            fd.append("file", e.target.files[0]);
            try {
                const res = await apiFetch("/api/question-bank/import", { method: "POST", body: fd });
                const data = await res.json();
                if (!res.ok || data.status !== "success") {
                    throw new Error(data.detail || "Không nhập được");
                }
                veThongKeNganHang(data.thong_ke);
                alert(`Đã nhập thêm ${data.da_them} câu vào ngân hàng` +
                      (data.bo_qua ? `, bỏ qua ${data.bo_qua} câu chưa thẩm định hoặc sai định dạng.` : "."));
            } catch (err) {
                alert("Lỗi: " + err.message);
            } finally {
                bankImportInput.value = "";
            }
        });
    }

    // ==========================================
    // MÀN HÌNH KHÓA TRUY CẬP NỘI BỘ
    // Chỉ bật khi máy chủ có đặt APP_ACCESS_TOKEN. Mã nhập vào được nhớ trên
    // trình duyệt và gửi kèm mọi lệnh gọi API qua header X-Access-Token.
    // ==========================================
    const accessGate = document.getElementById("access-gate");
    const accessInput = document.getElementById("access-code-input");
    const accessError = document.getElementById("access-error");
    const btnAccessSubmit = document.getElementById("btn-access-submit");

    function showGate(saiMa) {
        if (!accessGate) return;
        accessGate.classList.remove("hidden");
        accessError.classList.toggle("hidden", !saiMa);
        if (saiMa) accessInput.value = "";
        setTimeout(() => accessInput.focus(), 60);
    }

    function hideGate() {
        if (accessGate) accessGate.classList.add("hidden");
    }

    async function thuMaTruyCap() {
        // /api/verify-access bị middleware chặn nếu mã sai, nên chỉ cần xem mã trả về
        try {
            const res = await apiFetch("/api/verify-access", { method: "POST" });
            return res.status !== 401;
        } catch (e) {
            return false;
        }
    }

    async function kiemTraQuyenTruyCap() {
        let canMa = false;
        try {
            const res = await fetch("/api/health");   // endpoint này luôn mở
            canMa = !!(await res.json()).auth_required;
        } catch (e) {
            return;   // không gọi được máy chủ thì để giao diện chạy bình thường
        }

        if (!canMa) {
            hideGate();
            return;
        }
        if (await thuMaTruyCap()) {
            hideGate();
        } else {
            showGate(false);
        }
    }

    if (btnAccessSubmit) {
        btnAccessSubmit.addEventListener("click", async () => {
            const ma = accessInput.value.trim();
            if (!ma) return;

            btnAccessSubmit.disabled = true;
            btnAccessSubmit.textContent = "Đang kiểm tra...";
            writeStore(ACCESS_STORE, ma);

            const dung = await thuMaTruyCap();
            btnAccessSubmit.disabled = false;
            btnAccessSubmit.textContent = "Vào trang";

            if (dung) {
                hideGate();
            } else {
                writeStore(ACCESS_STORE, "");
                showGate(true);
            }
        });

        accessInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter") btnAccessSubmit.click();
        });
    }

    kiemTraQuyenTruyCap();

    // Hiện trạng thái khóa ngay khi mở trang
    refreshKeyStatus();
});
