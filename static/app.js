document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const tabBtnFile = document.getElementById("tab-btn-file");
    const tabBtnFolder = document.getElementById("tab-btn-folder");
    const panelFileUpload = document.getElementById("panel-file-upload");
    const panelFolderScan = document.getElementById("panel-folder-scan");

    const dropZone = document.getElementById("drop-zone");
    const fileInput = document.getElementById("file-input");
    const fileStatus = document.getElementById("file-status");
    const fileNameEl = document.getElementById("file-name");
    const fileCountEl = document.getElementById("file-count");
    const btnRemoveFile = document.getElementById("btn-remove-file");

    const folderPathInput = document.getElementById("folder-path-input");
    const btnScanFolder = document.getElementById("btn-scan-folder");
    const folderResultsBox = document.getElementById("folder-results");
    const folderFoundCount = document.getElementById("folder-found-count");
    const folderFileList = document.getElementById("folder-file-list");

    const radioCards = document.querySelectorAll(".radio-card");
    const btnProcess = document.getElementById("btn-process");

    const customTitleInput = document.getElementById("custom-title");
    const addCountSelect = document.getElementById("add-count");
    const checkTheory = document.getElementById("check-theory");
    const checkCasio = document.getElementById("check-casio");
    const checkTraps = document.getElementById("check-traps");

    const progressCard = document.getElementById("progress-card");
    const progressBar = document.getElementById("progress-bar");
    const progressStatus = document.getElementById("progress-status");

    const resultCard = document.getElementById("result-card");
    const resultTitle = document.getElementById("result-book-title");
    const resultSubtitle = document.getElementById("result-book-subtitle");
    const resultSingleActions = document.getElementById("result-single-actions");
    const resultBatchList = document.getElementById("result-batch-list");
    const btnDownload = document.getElementById("btn-download");
    const btnOpenResultFolder = document.getElementById("btn-open-result-folder");
    const btnOpenFolder = document.getElementById("btn-open-folder");

    const previewPlaceholder = document.getElementById("preview-placeholder");
    const previewList = document.getElementById("preview-list");
    const previewBadge = document.getElementById("preview-badge");

    // Modal Settings Elements
    const btnSettings = document.getElementById("btn-settings");
    const modalSettings = document.getElementById("modal-settings");
    const btnCloseModal = document.getElementById("btn-close-modal");
    const geminiApiKeyInput = document.getElementById("gemini-api-key");
    const btnToggleKey = document.getElementById("btn-toggle-key");
    const geminiModelSelect = document.getElementById("gemini-model");
    const btnSaveSettings = document.getElementById("btn-save-settings");

    let activeTab = "file"; // "file" or "folder"
    let currentUploadedFilename = null;
    let currentScannedFiles = [];
    let selectedSubject = "toan";

    // ==========================================
    // TABS SWITCHING
    // ==========================================
    tabBtnFile.addEventListener("click", () => {
        activeTab = "file";
        tabBtnFile.classList.add("active");
        tabBtnFolder.classList.remove("active");
        panelFileUpload.classList.remove("hidden");
        panelFolderScan.classList.add("hidden");
        btnProcess.disabled = !currentUploadedFilename;
    });

    tabBtnFolder.addEventListener("click", () => {
        activeTab = "folder";
        tabBtnFolder.classList.add("active");
        tabBtnFile.classList.remove("active");
        panelFolderScan.classList.remove("hidden");
        panelFileUpload.classList.add("hidden");
        btnProcess.disabled = currentScannedFiles.length === 0;
    });

    // ==========================================
    // SUBJECT SELECTOR
    // ==========================================
    radioCards.forEach(card => {
        card.addEventListener("click", () => {
            radioCards.forEach(c => c.classList.remove("active"));
            card.classList.add("active");
            selectedSubject = card.dataset.subject;
            const radio = card.querySelector("input[type=radio]");
            if (radio) radio.checked = true;

            if (selectedSubject === "toan") {
                customTitleInput.placeholder = "Ví dụ: Cẩm Nang Bứt Phá Điểm 9+ Toán Học THPT - Chuẩn BGD";
            } else {
                customTitleInput.placeholder = "Ví dụ: Đại Cẩm Nang Chinh Phục Điểm 9+ Vật Lý - Chuẩn BGD";
            }
        });
    });

    // ==========================================
    // TAB 1: FILE UPLOAD (WORD, EXCEL, PDF, ANH)
    // ==========================================
    dropZone.addEventListener("click", () => fileInput.click());

    ["dragenter", "dragover"].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add("dragover");
        });
    });

    ["dragleave", "drop"].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove("dragover");
        });
    });

    dropZone.addEventListener("drop", (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) handleFileSelect(files[0]);
    });

    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) handleFileSelect(fileInput.files[0]);
    });

    btnRemoveFile.addEventListener("click", resetFileSelection);

    function resetFileSelection() {
        currentUploadedFilename = null;
        fileInput.value = "";
        fileStatus.classList.add("hidden");
        dropZone.classList.remove("hidden");
        btnProcess.disabled = true;
        previewList.classList.add("hidden");
        previewPlaceholder.classList.remove("hidden");
        previewBadge.textContent = "Chưa có dữ liệu";
    }

    async function handleFileSelect(file) {
        fileNameEl.textContent = file.name;
        fileCountEl.textContent = "Đang bóc tách và nhận diện cấu trúc bài học...";
        fileStatus.classList.remove("hidden");
        dropZone.classList.add("hidden");

        const formData = new FormData();
        formData.append("file", file);
        formData.append("subject", selectedSubject);

        try {
            const res = await fetch("/api/upload", {
                method: "POST",
                body: formData
            });
            const data = await res.json();
            if (data.status === "success") {
                currentUploadedFilename = data.filename;
                fileCountEl.textContent = `Đã tìm thấy: ${data.total_items} bài toán`;
                btnProcess.disabled = false;
                renderInitialPreview(data.preview, data.total_items);
            } else {
                alert("Lỗi khi tải file: " + (data.detail || "Không rõ"));
                resetFileSelection();
            }
        } catch (err) {
            alert("Lỗi kết nối máy chủ: " + err.message);
            resetFileSelection();
        }
    }

    // ==========================================
    // TAB 2: FOLDER SCANNING
    // ==========================================
    btnScanFolder.addEventListener("click", async () => {
        const p = folderPathInput.value.trim();
        if (!p) {
            alert("Vui lòng nhập đường dẫn thư mục cần quét (Ví dụ: D:\\Tài liệu số\\Toán\\Toán 12)!");
            return;
        }

        btnScanFolder.disabled = true;
        btnScanFolder.textContent = "Đang quét...";

        try {
            const res = await fetch("/api/scan-folder", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ folder_path: p })
            });
            const data = await res.json();
            btnScanFolder.disabled = false;
            btnScanFolder.textContent = "Quét Thư Mục";

            if (data.status === "success") {
                currentScannedFiles = data.files;
                folderFoundCount.textContent = `Đã tìm thấy: ${data.total_files} tài liệu (Word, Excel, PDF, Ảnh)`;
                folderFileList.innerHTML = "";

                data.files.forEach(f => {
                    const item = document.createElement("div");
                    item.className = "folder-file-item";
                    item.innerHTML = `
                        <span>📄 ${f.name}</span>
                        <span style="color: var(--text-dim); font-size: 11.5px;">${f.size_kb} KB</span>
                    `;
                    folderFileList.appendChild(item);
                });

                folderResultsBox.classList.remove("hidden");
                btnProcess.disabled = data.total_files === 0;

                previewPlaceholder.classList.add("hidden");
                previewList.classList.remove("hidden");
                previewBadge.textContent = `Thư mục: ${data.total_files} tệp`;
                previewList.innerHTML = `
                    <div class="preview-callout callout-theory">
                        <span class="callout-title">📂 DANH MỤC TÀI LIỆU TRONG THƯ MỤC SẼ ĐƯỢC BIÊN SOẠN:</span>
                        <div>${data.files.map((f, i) => `${i+1}. ${f.name} (${f.ext})`).join('<br>')}</div>
                    </div>
                `;
            } else {
                alert("Lỗi: " + (data.detail || "Không thể quét thư mục này"));
            }
        } catch (err) {
            btnScanFolder.disabled = false;
            btnScanFolder.textContent = "Quét Thư Mục";
            alert("Lỗi: " + err.message);
        }
    });

    // ==========================================
    // RENDER PREVIEWS
    // ==========================================
    function renderInitialPreview(items, total) {
        previewPlaceholder.classList.add("hidden");
        previewList.classList.remove("hidden");
        previewBadge.textContent = `Xem trước ${items.length} / ${total} bài gốc`;
        previewList.innerHTML = "";

        items.forEach(q => {
            const card = document.createElement("div");
            card.className = "preview-item";

            let optionsHtml = "";
            if (q.options && q.options.length > 0) {
                optionsHtml = `<div class="preview-options-grid">${q.options.map(opt => `<div>${opt}</div>`).join('')}</div>`;
            }

            let solHtml = "";
            if (q.solution) {
                solHtml = `
                    <div class="preview-callout callout-sol">
                        <span class="callout-title">✎ Lời giải gốc:</span>
                        <div>${q.solution.replace(/\n/g, '<br>')}</div>
                    </div>
                `;
            }

            card.innerHTML = `
                <div class="preview-item-header">
                    <span class="preview-qtitle">${q.title}</span>
                    ${q.correct_answer ? `<span class="badge-tag">Đáp án: ${q.correct_answer}</span>` : ''}
                </div>
                <div class="preview-qcontent">${q.content}</div>
                ${optionsHtml}
                ${solHtml}
            `;
            previewList.appendChild(card);
        });
    }

    function renderBookPreview(book) {
        previewPlaceholder.classList.add("hidden");
        previewList.classList.remove("hidden");
        previewBadge.textContent = `Tổng cộng: ${book.total_questions} bài toán chuẩn BGD`;
        previewList.innerHTML = "";

        // Hiển thị PHẦN I: LÝ THUYẾT NỀN TẢNG NẾU CÓ
        if (checkTheory.checked && book.theory_section) {
            const theoryCard = document.createElement("div");
            theoryCard.className = "preview-callout callout-theory";
            theoryCard.innerHTML = `
                <span class="callout-title" style="font-size: 13px; color: #93C5FD;">📖 PHẦN I: KIẾN THỨC TRỌNG TÂM & LÝ THUYẾT NỀN TẢNG (CHUẨN CT GDPT 2018)</span>
                <div style="margin-top: 8px; font-size: 13.5px; white-space: pre-wrap;">${book.theory_section}</div>
            `;
            previewList.appendChild(theoryCard);
        }

        const questionsToRender = book.is_master_book 
            ? (book.chapters.length > 0 ? book.chapters[0].questions : []) 
            : book.questions;

        questionsToRender.forEach(q => {
            const card = document.createElement("div");
            card.className = "preview-item";

            let optionsHtml = "";
            if (q.new_options && q.new_options.length > 0) {
                optionsHtml = `<div class="preview-options-grid">${q.new_options.map(opt => `<div>${opt}</div>`).join('')}</div>`;
            }

            let sol1Html = "";
            if (q.solution_method1) {
                sol1Html = `
                    <div class="preview-callout callout-sol">
                        <span class="callout-title">✎ Lời giải Tự luận chuẩn mực sư phạm:</span>
                        <div>${q.solution_method1.replace(/\n/g, '<br>')}</div>
                    </div>
                `;
            }

            let casioHtml = "";
            if (checkCasio.checked && q.solution_method2) {
                casioHtml = `
                    <div class="preview-callout callout-casio">
                        <span class="callout-title">💡 Kỹ thuật Casio fx-580VN X & Mẹo nhanh:</span>
                        <div>${q.solution_method2.replace(/\n/g, '<br>')}</div>
                    </div>
                `;
            }

            let trapHtml = "";
            if (checkTraps.checked && q.trap_warning) {
                trapHtml = `
                    <div class="preview-callout callout-trap">
                        <span class="callout-title">⚠️ Bẫy đề thi & Sai lầm thường gặp:</span>
                        <div>${q.trap_warning.replace(/\n/g, '<br>')}</div>
                    </div>
                `;
            }

            card.innerHTML = `
                <div class="preview-item-header">
                    <span class="preview-qtitle">▶ ${q.title}</span>
                    <span class="badge-level">${q.level || 'Vận dụng'}</span>
                    ${q.is_added_new ? `<span class="badge-added">MỚI BỔ SUNG</span>` : ''}
                </div>
                <div class="preview-qcontent">${q.new_content}</div>
                ${optionsHtml}
                ${sol1Html}
                ${casioHtml}
                ${trapHtml}
            `;
            previewList.appendChild(card);
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
            "Đang quét và bóc tách tài liệu gốc...",
            "Đang xây dựng Phần I: Lý thuyết nền tảng & Bảng công thức CT GDPT 2018...",
            "Đang nâng cấp câu từ, phân loại 4 cấp độ nhận thức...",
            "Đang thiết lập lời giải kép tự luận và kỹ thuật bấm máy Casio...",
            "Đang bổ sung cảnh báo bẫy đề thi và lỗi sai học sinh...",
            "Đang căn chỉnh trang chuẩn Nghị định 30 (Times New Roman, lề 30-15-20-20mm)..."
        ];

        let msgIdx = 0;
        progressStatus.textContent = progressMessages[0];
        const timer = setInterval(() => {
            msgIdx = (msgIdx + 1) % progressMessages.length;
            progressStatus.textContent = progressMessages[msgIdx];
        }, 2200);

        try {
            // XỬ LÝ THEO CHẾ ĐỘ THƯ MỤC
            if (activeTab === "folder") {
                const folderMode = document.querySelector("input[name='folder-mode']:checked").value;
                const formData = new FormData();
                formData.append("folder_path", folderPathInput.value.trim());
                formData.append("mode", folderMode);
                formData.append("subject", selectedSubject);
                formData.append("add_count", addCountSelect.value);
                if (customTitleInput.value.trim()) {
                    formData.append("master_title", customTitleInput.value.trim());
                }

                const res = await fetch("/api/process-folder", {
                    method: "POST",
                    body: formData
                });
                const data = await res.json();
                clearInterval(timer);
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
                        renderBookPreview(data.book);
                    } else {
                        resultTitle.textContent = `Đã biên soạn thành công ${data.total_books} cuốn sách riêng lẻ`;
                        resultSubtitle.textContent = "Toàn bộ file Word .docx đã được lưu vào thư mục output chuẩn thể thức Nghị định 30.";
                        resultSingleActions.classList.add("hidden");
                        resultBatchList.classList.remove("hidden");
                        resultBatchList.innerHTML = data.books.map(b => `
                            <div class="result-batch-item">
                                <div>
                                    <strong>${b.title}</strong>
                                    <p style="font-size: 11.5px; color: var(--text-muted);">Nguồn: ${b.source} (${b.total_questions} câu)</p>
                                </div>
                                <a href="${b.download_url}" class="btn btn-outline" style="padding: 6px 12px; font-size: 12px;">📥 Tải về</a>
                            </div>
                        `).join("");
                    }
                } else {
                    alert("Lỗi: " + (data.detail || "Không rõ nguyên nhân"));
                }
            } 
            // XỬ LÝ THEO CHẾ ĐỘ FILE ĐƠN
            else {
                const formData = new FormData();
                formData.append("filename", currentUploadedFilename);
                formData.append("subject", selectedSubject);
                formData.append("add_count", addCountSelect.value);
                if (customTitleInput.value.trim()) {
                    formData.append("custom_title", customTitleInput.value.trim());
                }

                const res = await fetch("/api/process", {
                    method: "POST",
                    body: formData
                });
                const data = await res.json();
                clearInterval(timer);
                progressCard.classList.add("hidden");
                btnProcess.disabled = false;

                if (data.status === "success") {
                    resultCard.classList.remove("hidden");
                    resultTitle.textContent = data.book.new_title;
                    resultSubtitle.textContent = `${data.book.subtitle} (${data.book.total_questions} bài toán hoàn chỉnh)`;
                    btnDownload.href = data.download_url;
                    resultSingleActions.classList.remove("hidden");
                    resultBatchList.classList.add("hidden");
                    renderBookPreview(data.book);
                } else {
                    alert("Lỗi: " + (data.detail || "Không rõ"));
                }
            }
        } catch (err) {
            clearInterval(timer);
            progressCard.classList.add("hidden");
            btnProcess.disabled = false;
            alert("Lỗi: " + err.message);
        }
    });

    // ==========================================
    // OPEN FOLDERS
    // ==========================================
    async function triggerOpenOutputFolder() {
        try {
            await fetch("/api/open-output-folder", { method: "POST" });
        } catch (e) {
            console.error(e);
        }
    }
    btnOpenFolder.addEventListener("click", triggerOpenOutputFolder);
    btnOpenResultFolder.addEventListener("click", triggerOpenOutputFolder);

    // ==========================================
    // SETTINGS MODAL
    // ==========================================
    btnSettings.addEventListener("click", async () => {
        try {
            const res = await fetch("/api/settings");
            const data = await res.json();
            if (data.gemini_api_key) geminiApiKeyInput.value = data.gemini_api_key;
            if (data.gemini_model) geminiModelSelect.value = data.gemini_model;
        } catch (e) {
            console.error(e);
        }
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

    btnSaveSettings.addEventListener("click", async () => {
        const payload = {
            gemini_api_key: geminiApiKeyInput.value.trim(),
            gemini_model: geminiModelSelect.value
        };
        try {
            await fetch("/api/settings", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            modalSettings.classList.add("hidden");
            alert("Đã lưu cấu hình AI thành công!");
        } catch (err) {
            alert("Lỗi khi lưu cấu hình: " + err.message);
        }
    });
});
