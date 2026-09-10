document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const dropZone = document.getElementById("drop-zone");
    const fileInput = document.getElementById("file-input");
    const fileStatus = document.getElementById("file-status");
    const fileNameEl = document.getElementById("file-name");
    const fileCountEl = document.getElementById("file-count");
    const btnRemoveFile = document.getElementById("btn-remove-file");

    const radioCards = document.querySelectorAll(".radio-card");
    const btnProcess = document.getElementById("btn-process");

    const customTitleInput = document.getElementById("custom-title");
    const addCountSelect = document.getElementById("add-count");
    const paperFormatSelect = document.getElementById("paper-format");
    const checkCasio = document.getElementById("check-casio");
    const checkTraps = document.getElementById("check-traps");
    const checkSummary = document.getElementById("check-summary");

    const progressCard = document.getElementById("progress-card");
    const progressBar = document.getElementById("progress-bar");
    const progressStatus = document.getElementById("progress-status");

    const resultCard = document.getElementById("result-card");
    const resultTitle = document.getElementById("result-book-title");
    const resultSubtitle = document.getElementById("result-book-subtitle");
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

    let currentFile = null;
    let currentUploadedFilename = null;
    let selectedSubject = "toan";

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

            // Cập nhật placeholder tựa đề sách
            if (selectedSubject === "toan") {
                customTitleInput.placeholder = "Ví dụ: 102 Tuyệt Kỹ Giải Toán Thực Chiến - Bứt Phá Điểm 9+";
            } else {
                customTitleInput.placeholder = "Ví dụ: 102 Chuyên Đề Bứt Phá Vật Lý 12 - Bí Kíp Đạt Điểm 9+";
            }
        });
    });

    // ==========================================
    // DRAG & DROP / FILE SELECTION
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
        currentFile = null;
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
        const ext = file.name.split('.').pop().toLowerCase();
        if (!['docx', 'xlsx', 'doc', 'xls'].includes(ext)) {
            alert("Vui lòng chỉ tải lên file Word (.docx) hoặc Excel (.xlsx)!");
            return;
        }

        currentFile = file;
        fileNameEl.textContent = file.name;
        fileCountEl.textContent = "Đang phân tích cấu trúc tài liệu...";
        fileStatus.classList.remove("hidden");
        dropZone.classList.add("hidden");

        // Gửi lên server để bóc tách xem trước
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
                alert("Lỗi khi tải file: " + (data.detail || "Không rõ nguyên nhân"));
                resetFileSelection();
            }
        } catch (err) {
            console.error(err);
            alert("Không thể kết nối đến máy chủ: " + err.message);
            resetFileSelection();
        }
    }

    // ==========================================
    // RENDER PREVIEW LIST
    // ==========================================
    function renderInitialPreview(items, total) {
        previewPlaceholder.classList.add("hidden");
        previewList.classList.remove("hidden");
        previewBadge.textContent = `Xem trước ${items.length} / ${total} câu gốc`;
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
                        <span class="callout-title">✎ Hướng dẫn giải gốc:</span>
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

    function renderRewrittenPreview(book) {
        previewPlaceholder.classList.add("hidden");
        previewList.classList.remove("hidden");
        previewBadge.textContent = `Thành phẩm: ${book.questions.length} bài toán hoàn chỉnh`;
        previewList.innerHTML = "";

        book.questions.forEach(q => {
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
                        <span class="callout-title">✎ Lời giải Tự Luận Chuẩn Mực:</span>
                        <div>${q.solution_method1.replace(/\n/g, '<br>')}</div>
                    </div>
                `;
            }

            let casioHtml = "";
            if (checkCasio.checked && q.solution_method2) {
                casioHtml = `
                    <div class="preview-callout callout-casio">
                        <span class="callout-title">💡 Kỹ Thuật Bấm Máy Casio & Mẹo Nhanh:</span>
                        <div>${q.solution_method2.replace(/\n/g, '<br>')}</div>
                    </div>
                `;
            }

            let trapHtml = "";
            if (checkTraps.checked && q.trap_warning) {
                trapHtml = `
                    <div class="preview-callout callout-trap">
                        <span class="callout-title">⚠️ Bẫy Đề Thi Cần Tránh:</span>
                        <div>${q.trap_warning.replace(/\n/g, '<br>')}</div>
                    </div>
                `;
            }

            card.innerHTML = `
                <div class="preview-item-header">
                    <span class="preview-qtitle">▶ ${q.title}</span>
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
    // PROCESS REWRITE & EXPORT
    // ==========================================
    btnProcess.addEventListener("click", async () => {
        if (!currentUploadedFilename) {
            alert("Vui lòng chọn file trước khi bấm biên soạn!");
            return;
        }

        btnProcess.disabled = true;
        progressCard.classList.remove("hidden");
        resultCard.classList.add("hidden");

        const progressMessages = [
            "Đang chuẩn bị mô hình bóc tách và phân tích ngữ cảnh...",
            "Đang làm mới câu từ và đổi thông số số liệu...",
            "Đang kiểm tra nghiệm số đẹp bằng bộ giải SymPy...",
            "Đang xây dựng lời giải tự luận chi tiết và kỹ thuật Casio...",
            "Đang tạo bảng công thức vàng & cảnh báo bẫy sai lầm...",
            "Đang thiết lập khung Callout viền màu chuẩn sách in ấn Word .docx..."
        ];

        let msgIdx = 0;
        progressStatus.textContent = progressMessages[0];
        const timer = setInterval(() => {
            msgIdx = (msgIdx + 1) % progressMessages.length;
            progressStatus.textContent = progressMessages[msgIdx];
        }, 2200);

        const formData = new FormData();
        formData.append("filename", currentUploadedFilename);
        formData.append("subject", selectedSubject);
        formData.append("add_count", addCountSelect.value);
        formData.append("paper_format", paperFormatSelect.value);
        if (customTitleInput.value.trim()) {
            formData.append("custom_title", customTitleInput.value.trim());
        }

        try {
            const res = await fetch("/api/process", {
                method: "POST",
                body: formData
            });

            clearInterval(timer);
            progressCard.classList.add("hidden");
            btnProcess.disabled = false;

            const data = await res.json();
            if (data.status === "success") {
                resultTitle.textContent = data.book.new_title;
                resultSubtitle.textContent = `${data.book.subtitle} (${data.book.total_questions} bài toán hoàn chỉnh)`;
                btnDownload.href = data.download_url;
                resultCard.classList.remove("hidden");

                renderRewrittenPreview(data.book);
            } else {
                alert("Lỗi khi xử lý: " + (data.detail || "Không rõ nguyên nhân"));
            }
        } catch (err) {
            clearInterval(timer);
            progressCard.classList.add("hidden");
            btnProcess.disabled = false;
            console.error(err);
            alert("Lỗi kết nối máy chủ: " + err.message);
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
