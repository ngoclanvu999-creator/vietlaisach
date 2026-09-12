document.addEventListener("DOMContentLoaded", () => {
    // ==========================================
    // DOM ELEMENTS
    // ==========================================
    // Tabs
    const tabBtnFile = document.getElementById("tab-btn-file");
    const tabBtnFolder = document.getElementById("tab-btn-folder");
    const tabBtnZip = document.getElementById("tab-btn-zip");
    const panelFileUpload = document.getElementById("panel-file-upload");
    const panelFolderUpload = document.getElementById("panel-folder-upload");
    const panelZipUpload = document.getElementById("panel-zip-upload");

    // Tab 1: Single File Upload
    const dropZone = document.getElementById("drop-zone");
    const fileInput = document.getElementById("file-input");
    const fileStatus = document.getElementById("file-status");
    const fileNameEl = document.getElementById("file-name");
    const fileCountEl = document.getElementById("file-count");
    const btnRemoveFile = document.getElementById("btn-remove-file");

    // Tab 2: Web Folder Upload & Server Scan
    const dropZoneFolder = document.getElementById("drop-zone-folder");
    const folderInput = document.getElementById("folder-input");
    const toggleServerScan = document.getElementById("toggle-server-scan");
    const serverPathBox = document.getElementById("server-path-box");
    const folderPathInput = document.getElementById("folder-path-input");
    const btnScanFolder = document.getElementById("btn-scan-folder");
    const folderResultsBox = document.getElementById("folder-results");
    const folderFoundCount = document.getElementById("folder-found-count");
    const folderFileList = document.getElementById("folder-file-list");
    const btnClearFolder = document.getElementById("btn-clear-folder");

    // Tab 3: ZIP Upload
    const dropZoneZip = document.getElementById("drop-zone-zip");
    const zipInput = document.getElementById("zip-input");
    const zipStatus = document.getElementById("zip-status");
    const zipNameEl = document.getElementById("zip-name");
    const zipCountEl = document.getElementById("zip-count");
    const btnRemoveZip = document.getElementById("btn-remove-zip");

    // Subject & Options
    const radioCards = document.querySelectorAll(".radio-card");
    const btnProcess = document.getElementById("btn-process");
    const customTitleInput = document.getElementById("custom-title");
    const btnSuggestTitles = document.getElementById("btn-suggest-titles");
    const aiTitlesDrawer = document.getElementById("ai-titles-drawer");
    const aiTitlesList = document.getElementById("ai-titles-list");
    const btnCloseTitles = document.getElementById("btn-close-titles");
    const addCountSelect = document.getElementById("add-count");
    const checkTheory = document.getElementById("check-theory");
    const checkCasio = document.getElementById("check-casio");
    const checkTraps = document.getElementById("check-traps");

    // Lọc HTML nhưng vẫn giữ ngắt dòng — dùng cho lời giải nhiều dòng.
    function escapeMultiline(str) {
        return escapeHtml(str).replace(/\n/g, "<br>");
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

    const modalReader = document.getElementById("modal-reader");
    const btnCloseReader = document.getElementById("btn-close-reader");
    const btnPrintReader = document.getElementById("btn-print-reader");
    const readerBookTitle = document.getElementById("reader-book-title");
    const readerBookSubtitle = document.getElementById("reader-book-subtitle");
    const readerContent = document.getElementById("reader-content");

    const btnDeployInfo = document.getElementById("btn-deploy-info");
    const modalDeploy = document.getElementById("modal-deploy");
    const btnCloseDeploy = document.getElementById("btn-close-deploy");
    const btnDismissDeploy = document.getElementById("btn-dismiss-deploy");

    // App State
    let activeTab = "file"; // "file", "folder", "zip"
    let currentUploadedFilename = null;
    let currentScannedFiles = [];
    let currentBatchFolder = null;
    let selectedSubject = "toan";
    let currentCompiledBook = null;
    let areSolutionsVisible = true;
    let activeFilterLevel = "all";

    // ==========================================
    // TABS SWITCHING
    // ==========================================
    function switchTab(tab) {
        activeTab = tab;
        tabBtnFile.classList.toggle("active", tab === "file");
        tabBtnFolder.classList.toggle("active", tab === "folder");
        tabBtnZip.classList.toggle("active", tab === "zip");

        panelFileUpload.classList.toggle("hidden", tab !== "file");
        panelFolderUpload.classList.toggle("hidden", tab !== "folder");
        panelZipUpload.classList.toggle("hidden", tab !== "zip");

        if (tab === "file") {
            btnProcess.disabled = !currentUploadedFilename;
        } else if (tab === "folder") {
            btnProcess.disabled = currentScannedFiles.length === 0;
        } else if (tab === "zip") {
            btnProcess.disabled = currentScannedFiles.length === 0;
        }
    }

    tabBtnFile.addEventListener("click", () => switchTab("file"));
    tabBtnFolder.addEventListener("click", () => switchTab("folder"));
    tabBtnZip.addEventListener("click", () => switchTab("zip"));

    // Server path toggle
    if (toggleServerScan) {
        toggleServerScan.addEventListener("click", () => {
            serverPathBox.classList.toggle("hidden");
        });
    }

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
    // TAB 1: SINGLE FILE UPLOAD
    // ==========================================
    const btnBrowseFile = document.getElementById("btn-browse-file");
    if (dropZone) {
        dropZone.addEventListener("click", (e) => {
            if (e.target !== fileInput && fileInput) fileInput.click();
        });
    }
    if (btnBrowseFile) {
        btnBrowseFile.addEventListener("click", (e) => {
            e.stopPropagation();
            if (fileInput) fileInput.click();
        });
    }

    setupDragDrop(dropZone, (files) => {
        if (files.length > 0) handleSingleFile(files[0]);
    });

    fileInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) handleSingleFile(e.target.files[0]);
    });

    btnRemoveFile.addEventListener("click", (e) => {
        e.stopPropagation();
        resetSingleFile();
    });

    function resetSingleFile() {
        currentUploadedFilename = null;
        fileInput.value = "";
        fileStatus.classList.add("hidden");
        dropZone.classList.remove("hidden");
        btnProcess.disabled = true;
        previewPlaceholder.classList.remove("hidden");
        previewList.classList.add("hidden");
        previewToolbar.classList.add("hidden");
        previewBadge.textContent = "Chưa có dữ liệu";
    }

    async function handleSingleFile(file) {
        fileNameEl.textContent = file.name;
        fileCountEl.textContent = "Đang đọc & bóc tách bài toán...";
        dropZone.classList.add("hidden");
        fileStatus.classList.remove("hidden");

        const formData = new FormData();
        formData.append("file", file);
        formData.append("subject", selectedSubject);

        try {
            const res = await fetch("/api/upload", { method: "POST", body: formData });
            const data = await res.json();
            if (data.status === "success") {
                currentUploadedFilename = data.filename;
                fileCountEl.textContent = `Đã bóc tách thành công: ${data.total_items} bài toán`;
                btnProcess.disabled = false;
                renderInitialPreview(data.preview, data.total_items);
            } else {
                alert("Lỗi khi đọc tài liệu: " + (data.detail || "Không rõ"));
                resetSingleFile();
            }
        } catch (err) {
            alert("Lỗi kết nối máy chủ: " + err.message);
            resetSingleFile();
        }
    }

    // ==========================================
    // TAB 2: WEB FOLDER UPLOAD & SCAN
    // ==========================================
    const btnBrowseFolder = document.getElementById("btn-browse-folder");
    if (dropZoneFolder) {
        dropZoneFolder.addEventListener("click", (e) => {
            if (e.target !== folderInput && folderInput) folderInput.click();
        });
    }
    if (btnBrowseFolder) {
        btnBrowseFolder.addEventListener("click", (e) => {
            e.stopPropagation();
            if (folderInput) folderInput.click();
        });
    }

    setupDragDrop(dropZoneFolder, (files) => {
        if (files.length > 0) handleBatchUpload(files);
    });

    folderInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) handleBatchUpload(e.target.files);
    });

    if (btnClearFolder) {
        btnClearFolder.addEventListener("click", () => {
            currentScannedFiles = [];
            currentBatchFolder = null;
            folderResultsBox.classList.add("hidden");
            dropZoneFolder.classList.remove("hidden");
            btnProcess.disabled = true;
            previewPlaceholder.classList.remove("hidden");
            previewList.classList.add("hidden");
            previewToolbar.classList.add("hidden");
        });
    }

    async function handleBatchUpload(fileList) {
        folderFoundCount.textContent = `Đang tải lên ${fileList.length} tệp...`;
        folderResultsBox.classList.remove("hidden");
        dropZoneFolder.classList.add("hidden");

        const formData = new FormData();
        for (let i = 0; i < fileList.length; i++) {
            formData.append("files", fileList[i]);
        }
        formData.append("subject", selectedSubject);

        try {
            const res = await fetch("/api/upload-batch", { method: "POST", body: formData });
            const data = await res.json();
            if (data.status === "success") {
                currentScannedFiles = data.files;
                currentBatchFolder = data.folder_path;
                displayFolderFiles(data.files, data.total_files);
            } else {
                alert("Lỗi tải thư mục: " + (data.detail || "Không rõ"));
                dropZoneFolder.classList.remove("hidden");
                folderResultsBox.classList.add("hidden");
            }
        } catch (err) {
            alert("Lỗi tải lên: " + err.message);
            dropZoneFolder.classList.remove("hidden");
            folderResultsBox.classList.add("hidden");
        }
    }

    // Localhost scan folder
    if (btnScanFolder) {
        btnScanFolder.addEventListener("click", async () => {
            const p = folderPathInput.value.trim();
            if (!p) {
                alert("Vui lòng nhập đường dẫn thư mục trên máy tính!");
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
                btnScanFolder.textContent = "Quét";

                if (data.status === "success") {
                    currentScannedFiles = data.files;
                    currentBatchFolder = data.folder_path;
                    displayFolderFiles(data.files, data.total_files);
                } else {
                    alert("Lỗi: " + (data.detail || "Không thể quét thư mục này"));
                }
            } catch (err) {
                btnScanFolder.disabled = false;
                btnScanFolder.textContent = "Quét";
                alert("Lỗi kết nối: " + err.message);
            }
        });
    }

    function displayFolderFiles(files, total) {
        folderFoundCount.textContent = `Đã tìm thấy: ${total} tài liệu hợp lệ`;
        folderFileList.innerHTML = "";
        files.forEach(f => {
            const item = document.createElement("div");
            item.className = "folder-file-item";
            item.innerHTML = `
                <span>📄 ${escapeHtml(f.name)}</span>
                <span style="color: var(--text-dim); font-size: 11.5px;">${f.size_kb} KB</span>
            `;
            folderFileList.appendChild(item);
        });

        folderResultsBox.classList.remove("hidden");
        dropZoneFolder.classList.add("hidden");
        btnProcess.disabled = files.length === 0;

        previewPlaceholder.classList.add("hidden");
        previewList.classList.remove("hidden");
        previewToolbar.classList.add("hidden");
        previewBadge.textContent = `Thư mục: ${total} tệp`;
        previewList.innerHTML = `
            <div class="preview-callout callout-theory">
                <span class="callout-title">📂 DANH SÁCH TÀI LIỆU TRONG THƯ MỤC SẼ ĐƯỢC BIÊN SOẠN:</span>
                <div>${files.map((f, i) => `${i+1}. <strong>${escapeHtml(f.name)}</strong> (${f.size_kb} KB)`).join('<br>')}</div>
            </div>
        `;
    }

    // ==========================================
    // TAB 3: ZIP ARCHIVE UPLOAD
    // ==========================================
    const btnBrowseZip = document.getElementById("btn-browse-zip");
    if (dropZoneZip) {
        dropZoneZip.addEventListener("click", (e) => {
            if (e.target !== zipInput && zipInput) zipInput.click();
        });
    }
    if (btnBrowseZip) {
        btnBrowseZip.addEventListener("click", (e) => {
            e.stopPropagation();
            if (zipInput) zipInput.click();
        });
    }

    setupDragDrop(dropZoneZip, (files) => {
        if (files.length > 0) handleZipUpload(files[0]);
    });

    zipInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) handleZipUpload(e.target.files[0]);
    });

    btnRemoveZip.addEventListener("click", (e) => {
        e.stopPropagation();
        zipInput.value = "";
        currentScannedFiles = [];
        currentBatchFolder = null;
        zipStatus.classList.add("hidden");
        dropZoneZip.classList.remove("hidden");
        btnProcess.disabled = true;
    });

    async function handleZipUpload(file) {
        zipNameEl.textContent = file.name;
        zipCountEl.textContent = "Đang tải lên & giải nén tài liệu...";
        dropZoneZip.classList.add("hidden");
        zipStatus.classList.remove("hidden");

        const formData = new FormData();
        formData.append("zip_file", file);
        formData.append("subject", selectedSubject);

        try {
            const res = await fetch("/api/upload-zip", { method: "POST", body: formData });
            const data = await res.json();
            if (data.status === "success") {
                currentScannedFiles = data.files;
                currentBatchFolder = data.folder_path;
                zipCountEl.textContent = `Đã giải nén & bóc tách: ${data.total_files} tài liệu`;
                btnProcess.disabled = false;
                displayFolderFiles(data.files, data.total_files);
            } else {
                alert("Lỗi giải nén ZIP: " + (data.detail || "Không rõ"));
                dropZoneZip.classList.remove("hidden");
                zipStatus.classList.add("hidden");
            }
        } catch (err) {
            alert("Lỗi: " + err.message);
            dropZoneZip.classList.remove("hidden");
            zipStatus.classList.add("hidden");
        }
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
        el.addEventListener("drop", (e) => {
            if (e.dataTransfer && e.dataTransfer.files) {
                onDrop(e.dataTransfer.files);
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
        btnSuggestTitles.addEventListener("click", async () => {
            aiTitlesDrawer.classList.remove("hidden");
            aiTitlesList.innerHTML = `<div class="ai-title-loading">⚡ Đang kích hoạt Gemini AI phân tích chuyên đề và sáng tạo 5 tựa sách độc bản...</div>`;

            let fname = currentUploadedFilename || (currentScannedFiles.length > 0 ? currentScannedFiles[0].name : "");

            try {
                const resp = await fetch("/api/suggest-titles", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        filename: fname,
                        sample_text: "",
                        subject: selectedSubject
                    })
                });
                const data = await resp.json();
                if (data.status === "success" && data.titles && data.titles.length > 0) {
                    aiTitlesList.innerHTML = "";
                    data.titles.forEach((t, idx) => {
                        const card = document.createElement("div");
                        card.className = "ai-title-card";
                        card.innerHTML = `
                            <div class="ai-card-style-badge">✨ Trường Phái ${idx + 1}: ${escapeHtml(t.style)}</div>
                            <div class="ai-card-main-title">${escapeHtml(t.title)}</div>
                            <div class="ai-card-subtitle">${escapeHtml(t.subtitle)}</div>
                            <div class="ai-card-hook">💡 ${escapeHtml(t.hook)}</div>
                            <button type="button" class="btn-apply-title" data-title="${escapeHtml(t.title)}">👉 Áp Dụng Tựa Này</button>
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
                } else {
                    aiTitlesList.innerHTML = `<div class="ai-title-loading" style="color:#F87171">Không thể tạo tựa sách. Vui lòng kiểm tra lại kết nối hoặc API Key.</div>`;
                }
            } catch (err) {
                aiTitlesList.innerHTML = `<div class="ai-title-loading" style="color:#F87171">Lỗi kết nối: ${escapeHtml(err.message)}</div>`;
            }
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

        try {
            // XỬ LÝ THEO CHẾ ĐỘ THƯ MỤC / ZIP
            if (activeTab === "folder" || activeTab === "zip") {
                const folderMode = document.querySelector("input[name='folder-mode']:checked").value;
                const formData = new FormData();
                formData.append("folder_path", currentBatchFolder || folderPathInput.value.trim());
                formData.append("mode", folderMode);
                formData.append("subject", selectedSubject);
                formData.append("add_count", addCountSelect.value);
                if (customTitleInput.value.trim()) {
                    formData.append("master_title", customTitleInput.value.trim());
                }

                const res = await fetch("/api/process-folder", { method: "POST", body: formData });
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
                formData.append("filename", currentUploadedFilename);
                formData.append("subject", selectedSubject);
                formData.append("add_count", addCountSelect.value);
                if (customTitleInput.value.trim()) {
                    formData.append("custom_title", customTitleInput.value.trim());
                }

                const res = await fetch("/api/process", { method: "POST", body: formData });
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
            const res = await fetch("/api/open-output-folder", { method: "POST" });
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
    // SETTINGS MODAL
    // ==========================================
    btnSettings.addEventListener("click", async () => {
        try {
            const res = await fetch("/api/settings");
            const settings = await res.json();
            // Máy chủ KHÔNG trả về API key nữa (tránh lộ khóa cho người mở trang).
            // Ô nhập để trống: bỏ trống khi lưu nghĩa là giữ nguyên khóa đang dùng.
            geminiApiKeyInput.value = "";
            if (settings.gemini_api_key_set) {
                geminiApiKeyInput.placeholder =
                    `Đã lưu khóa ${settings.gemini_api_key_hint || ""} — để trống nếu muốn giữ nguyên`;
            } else {
                geminiApiKeyInput.placeholder = "Dán Google Gemini API Key vào đây";
            }
            geminiModelSelect.value = settings.gemini_model || "gemini-3.6-flash";
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
        btnSaveSettings.disabled = true;
        btnSaveSettings.textContent = "Đang lưu...";
        try {
            const res = await fetch("/api/settings", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    gemini_api_key: geminiApiKeyInput.value.trim(),
                    gemini_model: geminiModelSelect.value
                })
            });
            const data = await res.json();
            btnSaveSettings.disabled = false;
            btnSaveSettings.textContent = "Lưu Cấu Hình";
            if (data.status === "success") {
                modalSettings.classList.add("hidden");
                alert("Đã lưu cấu hình Google Gemini AI thành công!");
            }
        } catch (err) {
            btnSaveSettings.disabled = false;
            btnSaveSettings.textContent = "Lưu Cấu Hình";
            alert("Lỗi khi lưu cấu hình: " + err.message);
        }
    });
});
