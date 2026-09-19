/**
 * Giao diện app VIẾT LẠI SÁCH.
 *
 * Gọn nhất trong ba app: KHÔNG có bước chọn loại đầu ra nào cả, vì app này chỉ
 * làm đúng một việc — biến tài liệu gốc thành một cuốn sách.
 *
 * Khóa API nằm trong localStorage của trình duyệt, gửi kèm từng yêu cầu qua
 * header. Máy chủ không lưu.
 */
(function () {
    "use strict";

    // ======================================================================
    // KHÓA API — của riêng từng người
    // ======================================================================
    const KHO_KHOA = "claude_api_key";
    const KHO_MODEL = "claude_model";

    function doc(ten) {
        try { return localStorage.getItem(ten) || ""; } catch (e) { return ""; }
    }
    function ghi(ten, giatri) {
        try {
            if (giatri) localStorage.setItem(ten, giatri);
            else localStorage.removeItem(ten);
            return true;
        } catch (e) { return false; }   // chế độ ẩn danh hoặc trình duyệt chặn
    }

    function goi(url, opts) {
        const o = opts || {};
        const h = new Headers(o.headers || {});
        const k = doc(KHO_KHOA), m = doc(KHO_MODEL);
        if (k) h.set("X-Claude-Key", k);
        if (m) h.set("X-Claude-Model", m);
        return fetch(url, Object.assign({}, o, { headers: h }));
    }

    const $ = (id) => document.getElementById(id);
    function thoat(s) {
        if (!s) return "";
        return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;")
                        .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
    }

    // ======================================================================
    // TRẠNG THÁI
    // ======================================================================
    let tepDaNap = [];     // đường dẫn tuyệt đối các tệp đã bóc tách được
    let mayCoKhoa = false;

    // ======================================================================
    // BƯỚC 1 — NẠP LIỆU
    // ======================================================================
    const vungTha = $("vung-tha");
    const oTep = $("o-tep");
    const oThuMuc = $("o-thu-muc");

    // Bấm vào BẤT CỨ ĐÂU trong khung đều mở hộp chọn tệp. Bản cũ chỉ gắn sự
    // kiện lên hai cái nút nên bấm giữa khung không ăn gì, mà đó lại là chỗ
    // người dùng bấm nhiều nhất.
    vungTha.addEventListener("click", (e) => {
        if (e.target.closest("#btn-chon-thu-muc")) { oThuMuc.click(); return; }
        oTep.click();
    });
    $("btn-chon-tep").addEventListener("click", (e) => { e.stopPropagation(); oTep.click(); });
    $("btn-chon-thu-muc").addEventListener("click", (e) => { e.stopPropagation(); oThuMuc.click(); });

    ["dragenter", "dragover"].forEach((t) =>
        vungTha.addEventListener(t, (e) => {
            e.preventDefault(); vungTha.classList.add("dragover");
        }));
    ["dragleave", "drop"].forEach((t) =>
        vungTha.addEventListener(t, (e) => {
            e.preventDefault(); vungTha.classList.remove("dragover");
        }));
    vungTha.addEventListener("drop", (e) => {
        const ds = e.dataTransfer && e.dataTransfer.files;
        if (ds && ds.length) napTep(ds);
    });

    oTep.addEventListener("change", () => { if (oTep.files.length) napTep(oTep.files); });
    oThuMuc.addEventListener("change", () => { if (oThuMuc.files.length) napTep(oThuMuc.files); });

    function monDangChon() {
        const r = document.querySelector('input[name="mon"]:checked');
        return r ? r.value : "toan";
    }

    document.querySelectorAll(".radio-card").forEach((the) => {
        the.addEventListener("click", () => {
            document.querySelectorAll(".radio-card").forEach((x) => x.classList.remove("active"));
            the.classList.add("active");
            the.querySelector('input[type="radio"]').checked = true;
        });
    });

    async function napTep(danhSach) {
        const hop = $("ket-qua-nap");
        hop.classList.remove("hidden");
        hop.innerHTML = '<div class="ingest-loading">Đang bóc tách tài liệu…</div>';

        const fd = new FormData();
        for (const f of danhSach) fd.append("files", f, f.name);
        fd.append("subject", monDangChon());

        try {
            const res = await goi("/api/nap-lieu", { method: "POST", body: fd });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Nạp liệu thất bại");
            veKetQuaNap(data);
        } catch (err) {
            hop.innerHTML = '<div class="ingest-error">❌ ' + thoat(err.message) + "</div>";
            tepDaNap = [];
            capNhatNutBienSoan();
        }
    }

    function veKetQuaNap(data) {
        tepDaNap = data.duong_dan || [];
        const hop = $("ket-qua-nap");
        let html = '<div class="file-status-box">'
            + '<div class="file-count"><strong>' + data.tong_cau + " câu</strong> từ "
            + data.so_tep + " tệp</div>";
        if (data.tep_hong && data.tep_hong.length) {
            html += '<div class="ingest-skipped">Bỏ qua ' + data.tep_hong.length
                 + " tệp không đọc được: "
                 + data.tep_hong.map((x) => thoat(x.tep)).join(", ") + "</div>";
        }
        if (data.nhan_dien && data.nhan_dien.ten_hien_thi) {
            html += '<div class="doctype-detected">Nhận diện: <strong>'
                 + thoat(data.nhan_dien.ten_hien_thi)
                 + "</strong> — chỉ là gợi ý, bạn vẫn tự chọn loại đầu ra ở Bước 2.</div>";
        }
        html += "</div>";
        hop.innerHTML = html;

        veXemTruoc(data.xem_truoc || [], data.tong_cau);
        capNhatNutBienSoan();
    }

    function veXemTruoc(ds, tong) {
        const the = $("the-xem-truoc");
        if (!ds.length) { the.classList.add("hidden"); return; }
        the.classList.remove("hidden");
        // `ds` chỉ là phần XEM TRƯỚC, không phải số câu bóc tách được — ghi rõ
        // để không ai tưởng đã mất bài.
        $("huy-hieu-xem-truoc").textContent = tong > ds.length
            ? "Đã bóc tách " + tong + " câu — xem trước " + ds.length + " câu đầu"
            : "Đã bóc tách " + tong + " câu";

        $("danh-sach-xem-truoc").innerHTML = ds.map((q) => {
            let h = '<div class="preview-card"><div class="preview-q-head">'
                  + thoat(q.title || "Câu " + q.index) + "</div>"
                  + '<div class="preview-q-text">' + thoat(q.content) + "</div>";
            if (q.options && q.options.length) {
                h += '<div class="preview-options">'
                   + q.options.map((o) => "<span>" + thoat(o) + "</span>").join("")
                   + "</div>";
            }
            return h + "</div>";
        }).join("");
    }

    function capNhatNutBienSoan() {
        const nut = $("btn-bien-soan");
        nut.disabled = tepDaNap.length === 0;
        nut.textContent = tepDaNap.length
            ? "Biên soạn thành sách"
            : "Nạp tài liệu trước đã";
    }

    // ======================================================================
    // BƯỚC 3 — BIÊN SOẠN
    // ======================================================================
    function docGiay(s) {
        if (s == null) return "";
        const p = Math.floor(s / 60), g = s % 60;
        return p > 0 ? p + " phút " + g + " giây" : g + " giây";
    }

    $("btn-bien-soan").addEventListener("click", async () => {
        const nut = $("btn-bien-soan");
        nut.disabled = true;
        $("the-ket-qua").classList.add("hidden");
        $("the-tien-do").classList.remove("hidden");

        let phanTram = 3;
        $("thanh-tien-do").style.width = "3%";
        $("chu-tien-do").textContent = "Đang bóc tách lại tài liệu…";

        // Hỏi máy chủ tiến độ THẬT chứ không chạy đồng hồ. Thanh chạy theo đồng
        // hồ thì với tài liệu lớn nó lên 92% rồi đứng im hàng chục phút, người
        // dùng kết luận phần mềm treo.
        const dongHo = setInterval(async () => {
            try {
                const r = await fetch("/api/tien-do");
                if (!r.ok) return;
                const td = await r.json();
                if (td.tong_lo > 0) {
                    phanTram = Math.max(phanTram, td.phan_tram || 0);
                    $("thanh-tien-do").style.width = phanTram + "%";
                    let dong = "Lô " + td.lo_hien_tai + "/" + td.tong_lo
                             + " — đã xong " + td.cau_xong + "/" + td.tong_cau + " câu";
                    if (td.uoc_con_lai_giay != null) {
                        dong += " · còn khoảng " + docGiay(td.uoc_con_lai_giay);
                    }
                    dong += " · đã chạy " + docGiay(td.da_chay_giay);
                    if (td.loi) dong += " · lưu ý: " + td.loi;
                    $("chu-tien-do").textContent = dong;
                } else {
                    phanTram = Math.min(10, phanTram + 1);
                    $("thanh-tien-do").style.width = phanTram + "%";
                }
            } catch (e) { /* mất mạng chốc lát thì bỏ qua nhịp này */ }
        }, 2000);

        const fd = new FormData();
        fd.append("duong_dan", tepDaNap.join("|"));
        fd.append("subject", monDangChon());
        fd.append("cap_hoc", $("cap-hoc").value);
        fd.append("ai_scope", $("pham-vi-ai").value);
        fd.append("paper_format", $("kho-giay").value);
        fd.append("tieu_de_rieng", $("tieu-de").value.trim());
        fd.append("solution", $("co-loi-giai").checked ? "1" : "0");
        fd.append("theory", $("co-ly-thuyet").checked ? "1" : "0");
        fd.append("traps", $("co-bay").checked ? "1" : "0");
        fd.append("casio", $("co-casio").checked ? "1" : "0");
        fd.append("them_cau", $("them-cau").value);

        try {
            const res = await goi("/api/bien-soan", { method: "POST", body: fd });
            const data = await res.json();
            clearInterval(dongHo);
            $("thanh-tien-do").style.width = "100%";
            $("the-tien-do").classList.add("hidden");
            if (!res.ok) throw new Error(data.detail || "Biên soạn thất bại");
            veKetQua(data);
        } catch (err) {
            clearInterval(dongHo);
            $("the-tien-do").classList.add("hidden");
            alert("Lỗi khi biên soạn: " + err.message);
        } finally {
            nut.disabled = false;
        }
    });

    function veKetQua(data) {
        const the = $("the-ket-qua");
        the.classList.remove("hidden");
        $("ten-ket-qua").textContent = (data.book && data.book.new_title) || "Đã biên soạn xong";
        $("phu-de-ket-qua").textContent = (data.book && data.book.subtitle) || "";
        $("lien-ket-tai").href = data.download_url;

        const dau = data.nha_cung_cap || {};
        const o = $("dau-an-ai");
        o.textContent = dau.dung_ai
            ? "✅ Biên soạn bằng " + dau.ten_hien_thi + " (" + dau.model + ")"
            : "💻 Biên soạn bằng Bộ máy ngoại tuyến — chưa dán khóa Claude";
        o.className = "key-status " + (dau.dung_ai ? "key-status-on" : "key-status-local");

        const bc = data.validation_report;
        $("bao-cao-tham-dinh").innerHTML = bc
            ? '<div class="scorecard-header"><span class="score-title">Thẩm định thể thức</span>'
              + '<span class="score-badge">' + thoat(String(bc.total_score || "")) + "</span></div>"
            : "";
    }

    $("btn-mo-thu-muc-ra").addEventListener("click", () => moThuMuc());
    $("btn-thu-muc").addEventListener("click", () => moThuMuc());

    async function moThuMuc() {
        try {
            const r = await goi("/api/mo-thu-muc-ket-qua", { method: "POST" });
            if (!r.ok) {
                const d = await r.json();
                alert(d.detail || "Không mở được thư mục");
            }
        } catch (e) { alert("Không mở được thư mục: " + e.message); }
    }

    // ======================================================================
    // CÀI ĐẶT KHÓA
    // ======================================================================
    const hopCaiDat = $("hop-cai-dat");

    $("btn-cai-dat").addEventListener("click", async () => {
        $("o-khoa").value = doc(KHO_KHOA);
        $("o-model").value = doc(KHO_MODEL) || "claude-sonnet-5";
        try {
            const r = await goi("/api/settings");
            const s = await r.json();
            mayCoKhoa = !!s.server_key_available;
        } catch (e) { mayCoKhoa = false; }
        capNhatTrangThaiKhoa();
        hopCaiDat.classList.remove("hidden");
    });

    $("btn-dong-cai-dat").addEventListener("click", () => hopCaiDat.classList.add("hidden"));
    hopCaiDat.addEventListener("click", (e) => {
        if (e.target === hopCaiDat) hopCaiDat.classList.add("hidden");
    });

    $("btn-hien-khoa").addEventListener("click", () => {
        const o = $("o-khoa");
        const an = o.type === "password";
        o.type = an ? "text" : "password";
        $("btn-hien-khoa").textContent = an ? "Ẩn" : "Hiện";
    });

    function moTaKhoa(k) { return k ? "••••••••" + k.slice(-4) : ""; }

    function capNhatTrangThaiKhoa() {
        const o = $("trang-thai-khoa");
        const k = doc(KHO_KHOA);
        if (k) {
            o.textContent = "✅ Đang dùng khóa của bạn (" + moTaKhoa(k) + ") — lưu trên trình duyệt này";
            o.className = "key-status key-status-on";
        } else if (mayCoKhoa) {
            o.textContent = "💻 Đang chạy trên máy cá nhân, dùng khóa đã lưu sẵn trong máy";
            o.className = "key-status key-status-local";
        } else {
            o.textContent = "Chưa có khóa — đang dùng Bộ máy Offline (vẫn biên soạn được)";
            o.className = "key-status";
        }
    }

    // Gửi thẳng khóa đang GÕ TRONG Ô, không lấy khóa đã lưu: phải thử được
    // trước khi bấm lưu, nếu không nút này vô dụng đúng lúc cần nhất.
    $("btn-thu-khoa").addEventListener("click", async () => {
        const khoa = $("o-khoa").value.trim();
        const ra = $("ket-qua-thu-khoa");
        ra.classList.remove("hidden", "key-ok", "key-loi");
        if (!khoa) {
            ra.textContent = "Chưa dán khóa vào ô bên trên.";
            ra.classList.add("key-loi");
            return;
        }
        const nut = $("btn-thu-khoa");
        const chuCu = nut.textContent;
        nut.disabled = true;
        nut.textContent = "Đang thử…";
        ra.textContent = "Đang gọi thử một lượt rất ngắn…";
        try {
            const h = new Headers({ "X-Claude-Key": khoa, "X-Claude-Model": $("o-model").value });
            const res = await fetch("/api/thu-khoa", { method: "POST", headers: h });
            const d = await res.json();
            if (d.dung_duoc) {
                ra.textContent = "✅ " + d.thong_bao
                    + (d.dap_so_dung ? "" : " (lưu ý: mô hình trả lời sai phép nhân thử)");
                ra.classList.add("key-ok");
            } else {
                ra.textContent = "❌ " + (d.thong_bao || "Khóa không dùng được.")
                    + (d.chi_tiet ? "\n" + d.chi_tiet : "");
                ra.classList.add("key-loi");
            }
        } catch (err) {
            ra.textContent = "❌ Không gọi được máy chủ: " + err.message;
            ra.classList.add("key-loi");
        } finally {
            nut.disabled = false;
            nut.textContent = chuCu;
        }
    });

    $("btn-luu-cai-dat").addEventListener("click", () => {
        const khoa = $("o-khoa").value.trim();
        const ok1 = ghi(KHO_KHOA, khoa);
        const ok2 = ghi(KHO_MODEL, $("o-model").value);
        if (!ok1 || !ok2) {
            alert("Trình duyệt đang chặn lưu trữ cục bộ (thường gặp ở chế độ ẩn danh), "
                + "nên không giữ được khóa cho lần sau. Khóa vẫn dùng được trong phiên này.");
        }
        capNhatTrangThaiKhoa();
        hopCaiDat.classList.add("hidden");
        alert(khoa
            ? "Đã lưu khóa Claude. Khóa nằm trong trình duyệt của bạn, chỉ mình bạn dùng."
            : "Chưa có khóa Claude nên ứng dụng sẽ chạy bằng Bộ máy Offline.");
    });

    capNhatNutBienSoan();
    capNhatTrangThaiKhoa();
})();
