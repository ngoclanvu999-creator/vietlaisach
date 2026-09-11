import os
import sys
from pathlib import Path
from typing import Optional, List

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config import BASE_DIR, INPUT_DIR, OUTPUT_DIR, TEMPLATES_DIR, STATIC_DIR, load_settings, save_settings
from core.parser import parse_input_file, scan_directory
from core.rewriter import process_rewrite_pipeline, create_master_book_from_chapters
from core.ai_namer import generate_creative_titles_gemini
from core.exporter import DocxBookExporter
from core.validator import PreFlightValidator

app = FastAPI(title="Biên Soạn Sách Toán - Vật Lý Pro")

STATIC_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_home():
    index_file = TEMPLATES_DIR / "index.html"
    with open(index_file, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/api/settings")
async def get_settings():
    return load_settings()

@app.post("/api/settings")
async def update_settings(settings: dict):
    saved = save_settings(settings)
    return {"status": "success", "settings": saved}

class ScanFolderRequest(BaseModel):
    folder_path: str

@app.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "service": "Bien Soan Sach Pro",
        "version": "2.5",
        "web_deploy_ready": True
    }

@app.post("/api/scan-folder")
async def api_scan_folder(req: ScanFolderRequest):
    p = Path(req.folder_path.strip().strip('"').strip("'"))
    if not p.exists() or not p.is_dir():
        raise HTTPException(status_code=400, detail=f"Đường dẫn thư mục không tồn tại: {req.folder_path}")

    try:
        files = scan_directory(p)
        return {
            "status": "success",
            "folder_path": str(p),
            "total_files": len(files),
            "files": files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi quét thư mục: {str(e)}")

class SuggestTitlesRequest(BaseModel):
    filename: str = ""
    sample_text: str = ""
    subject: str = "toan"

@app.post("/api/suggest-titles")
async def api_suggest_titles(req: SuggestTitlesRequest):
    settings = load_settings()
    api_key = settings.get("gemini_api_key", "").strip()
    model_name = settings.get("gemini_model", "gemini-3.6-flash")

    titles = generate_creative_titles_gemini(
        sample_text=req.sample_text,
        filename=req.filename,
        subject=req.subject,
        api_key=api_key,
        model_name=model_name
    )
    return {
        "status": "success",
        "total": len(titles),
        "titles": titles
    }

@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    subject: str = Form("toan")
):
    ext = Path(file.filename).suffix.lower()
    allowed = [".docx", ".doc", ".xlsx", ".xls", ".pdf", ".png", ".jpg", ".jpeg"]
    if ext not in allowed:
        raise HTTPException(status_code=400, detail="Định dạng không được hỗ trợ. Vui lòng tải lên file: Word, Excel, PDF hoặc Ảnh.")

    save_path = INPUT_DIR / file.filename
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    settings = load_settings()
    api_key = settings.get("gemini_api_key", "").strip()

    try:
        parsed_items = parse_input_file(save_path, subject=subject, api_key=api_key)
        preview = [item.to_dict() for item in parsed_items[:15]]
        return {
            "status": "success",
            "filename": file.filename,
            "total_items": len(parsed_items),
            "preview": preview
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi đọc file: {str(e)}")

@app.post("/api/upload-batch")
async def upload_batch(
    files: List[UploadFile] = File(...),
    subject: str = Form("toan")
):
    """Tải lên nhiều tệp hoặc tải lên cả thư mục tài liệu từ trình duyệt Web (Web Folder Upload)"""
    if not files:
        raise HTTPException(status_code=400, detail="Không có tệp nào được chọn")

    batch_dir = INPUT_DIR / "web_upload_batch"
    batch_dir.mkdir(parents=True, exist_ok=True)

    saved_files = []
    allowed = {".docx", ".doc", ".xlsx", ".xls", ".pdf", ".png", ".jpg", ".jpeg"}

    for f in files:
        fname = Path(f.filename).name
        ext = Path(fname).suffix.lower()
        if ext in allowed and not fname.startswith("~$"):
            save_p = batch_dir / fname
            with open(save_p, "wb") as buf:
                shutil.copyfileobj(f.file, buf)
            try:
                size_kb = round(save_p.stat().st_size / 1024, 1)
            except Exception:
                size_kb = 0
            saved_files.append({
                "name": fname,
                "path": str(save_p),
                "ext": ext,
                "size_kb": size_kb
            })

    if not saved_files:
        raise HTTPException(status_code=400, detail="Không có tệp Word, Excel, PDF hoặc Ảnh nào hợp lệ")

    return {
        "status": "success",
        "folder_path": str(batch_dir),
        "total_files": len(saved_files),
        "files": saved_files
    }

@app.post("/api/upload-zip")
async def upload_zip(
    zip_file: UploadFile = File(...),
    subject: str = Form("toan")
):
    """Tải lên file nén .zip chứa thư mục tài liệu từ bất kỳ máy tính/thiết bị nào lên web"""
    import zipfile
    if not zip_file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ tải lên file nén định dạng .zip")

    zip_path = INPUT_DIR / zip_file.filename
    with open(zip_path, "wb") as buf:
        shutil.copyfileobj(zip_file.file, buf)

    extract_dir = INPUT_DIR / f"unzipped_{Path(zip_file.filename).stem}"
    extract_dir.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(str(zip_path), "r") as z:
            z.extractall(str(extract_dir))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Không thể giải nén file zip: {str(e)}")

    files = scan_directory(extract_dir)
    return {
        "status": "success",
        "folder_path": str(extract_dir),
        "total_files": len(files),
        "files": files
    }

@app.post("/api/process")
async def process_single_document(
    filename: str = Form(...),
    subject: str = Form("toan"),
    add_count: int = Form(2),
    custom_title: Optional[str] = Form(None)
):
    input_path = INPUT_DIR / filename
    if not input_path.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy file nguồn đã tải lên")

    settings = load_settings()
    api_key = settings.get("gemini_api_key", "").strip()
    model_name = settings.get("gemini_model", "gemini-3.6-flash")

    try:
        # 1. Bóc tách
        questions = parse_input_file(input_path, subject=subject, api_key=api_key)
        if not questions:
            raise HTTPException(status_code=400, detail="Không trích xuất được bài toán nào từ file này")

        # 2. Tái cấu trúc & Bổ sung lý thuyết chuẩn BGD
        book = process_rewrite_pipeline(
            questions=questions,
            subject=subject,
            add_count=int(add_count),
            api_key=api_key,
            model_name=model_name
        )

        if custom_title and custom_title.strip():
            book.new_title = custom_title.strip()

        # 3. Thẩm định cấu trúc và thể thức văn bản trước xuất bản (QA Pre-flight Validator)
        val_report = PreFlightValidator.validate(
            book_title=book.new_title,
            subtitle=book.subtitle,
            chapters=book.chapters,
            questions=book.questions,
            doc_type="THEMATIC_BOOK" if book.chapters else "SINGLE_BOOK",
            subject=subject
        )

        # 4. Xuất Word chuẩn Nghị định 30
        stem = Path(filename).stem
        clean_title_slug = "".join(c for c in book.new_title[:30] if c.isalnum() or c in (" ", "-", "_")).strip().replace(" ", "_")
        out_filename = f"Sach_Bien_Soan_{stem}_{clean_title_slug}.docx"
        out_path = OUTPUT_DIR / out_filename
        DocxBookExporter.export(book, out_path)

        return {
            "status": "success",
            "book": book.to_dict(),
            "validation_report": val_report.to_dict(),
            "output_filename": out_filename,
            "download_url": f"/api/download/{out_filename}"
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Lỗi khi biên soạn: {str(e)}")

@app.post("/api/process-folder")
async def process_folder(
    folder_path: str = Form(...),
    mode: str = Form("merge"),  # "merge" (1 cuốn) hoặc "split" (từng cuốn riêng)
    subject: str = Form("toan"),
    add_count: int = Form(2),
    master_title: Optional[str] = Form(None)
):
    p = Path(folder_path.strip().strip('"').strip("'"))
    if not p.exists() or not p.is_dir():
        raise HTTPException(status_code=400, detail="Thư mục không tồn tại trên máy")

    settings = load_settings()
    api_key = settings.get("gemini_api_key", "").strip()
    model_name = settings.get("gemini_model", "gemini-3.6-flash")

    files = scan_directory(p)
    if not files:
        raise HTTPException(status_code=400, detail="Thư mục không chứa tệp Word, Excel, PDF hoặc Ảnh nào hợp lệ")

    try:
        # CHẾ ĐỘ 1: GỘP TOÀN BỘ THÀNH 1 CUỐN ĐẠI CẨM NANG
        if mode == "merge":
            chapter_data_list = []
            for item in files:
                f_path = Path(item["path"])
                try:
                    q_list = parse_input_file(f_path, subject=subject, api_key=api_key)
                    if q_list:
                        chapter_data_list.append({
                            "source_name": f_path.name,
                            "questions": q_list
                        })
                except Exception as e:
                    print(f"Bỏ qua file {f_path.name} do lỗi đọc: {e}")

            if not chapter_data_list:
                raise HTTPException(status_code=400, detail="Không bóc tách được bài tập nào từ các tệp trong thư mục")

            master_book = create_master_book_from_chapters(
                chapter_data_list=chapter_data_list,
                subject=subject,
                master_title=master_title
            )

            val_report = PreFlightValidator.validate(
                book_title=master_book.new_title,
                subtitle=master_book.subtitle,
                chapters=master_book.chapters,
                questions=master_book.questions,
                doc_type="MASTER_BOOK",
                subject=subject
            )

            clean_folder_name = p.name.replace(" ", "_")
            out_filename = f"Dai_Cam_Nang_{clean_folder_name}_Chuan_BGD.docx"
            out_path = OUTPUT_DIR / out_filename
            DocxBookExporter.export(master_book, out_path)

            return {
                "status": "success",
                "mode": "merge",
                "book": master_book.to_dict(),
                "validation_report": val_report.to_dict(),
                "output_filename": out_filename,
                "download_url": f"/api/download/{out_filename}"
            }

        # CHẾ ĐỘ 2: BIÊN SOẠN TỪNG TÀI LIỆU THÀNH TỪNG CUỐN SÁCH RIÊNG LẺ
        else:
            processed_books = []
            for item in files:
                f_path = Path(item["path"])
                try:
                    q_list = parse_input_file(f_path, subject=subject, api_key=api_key)
                    if not q_list:
                        continue
                    single_book = process_rewrite_pipeline(
                        questions=q_list,
                        subject=subject,
                        add_count=int(add_count),
                        api_key=api_key,
                        model_name=model_name
                    )

                    val_report = PreFlightValidator.validate(
                        book_title=single_book.new_title,
                        subtitle=single_book.subtitle,
                        chapters=single_book.chapters,
                        questions=single_book.questions,
                        doc_type="THEMATIC_BOOK" if single_book.chapters else "SINGLE_BOOK",
                        subject=subject
                    )

                    clean_slug = "".join(c for c in single_book.new_title[:25] if c.isalnum() or c in (" ", "-", "_")).strip().replace(" ", "_")
                    out_name = f"Sach_{f_path.stem}_{clean_slug}.docx"
                    out_path = OUTPUT_DIR / out_name
                    DocxBookExporter.export(single_book, out_path)

                    processed_books.append({
                        "source": f_path.name,
                        "output_filename": out_name,
                        "download_url": f"/api/download/{out_name}",
                        "title": single_book.new_title,
                        "total_questions": sum(len(c.questions) for c in single_book.chapters) if single_book.chapters else len(single_book.questions),
                        "validation_report": val_report.to_dict()
                    })
                except Exception as e:
                    print(f"Lỗi khi xử lý {f_path.name}: {e}")

            if not processed_books:
                raise HTTPException(status_code=400, detail="Không thể biên soạn tài liệu nào từ thư mục này")

            # Tự động nén toàn bộ sách thành 1 file ZIP để tải về 1-click trên Web
            import zipfile
            import time
            clean_zip_stem = "".join(c for c in p.name if c.isalnum() or c in (" ", "-", "_")).strip().replace(" ", "_") or "Sach"
            zip_filename = f"Tron_Bo_Sach_{clean_zip_stem}_{int(time.time())}.zip"
            zip_path = OUTPUT_DIR / zip_filename
            with zipfile.ZipFile(str(zip_path), "w", zipfile.ZIP_DEFLATED) as zf:
                for b in processed_books:
                    b_path = OUTPUT_DIR / b["output_filename"]
                    if b_path.exists():
                        zf.write(str(b_path), arcname=b["output_filename"])

            return {
                "status": "success",
                "mode": "split",
                "total_books": len(processed_books),
                "books": processed_books,
                "zip_filename": zip_filename,
                "zip_download_url": f"/api/download/{zip_filename}"
            }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý thư mục: {str(e)}")

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File không tồn tại hoặc đã bị xóa")
    ext = file_path.suffix.lower()
    media_type = "application/zip" if ext == ".zip" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type=media_type
    )

@app.post("/api/open-output-folder")
async def open_output_folder():
    try:
        if sys.platform == "win32":
            os.startfile(str(OUTPUT_DIR))
            return {"status": "success", "folder": str(OUTPUT_DIR)}
        else:
            return {"status": "info", "message": "Đang chạy trên môi trường Web/Cloud Server. Vui lòng tải file trực tiếp qua trình duyệt."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading

    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8501))

    if os.environ.get("AUTO_OPEN_BROWSER", "1") == "1" and sys.platform == "win32":
        def open_browser():
            import time
            time.sleep(1.2)
            try:
                webbrowser.open(f"http://127.0.0.1:{port}")
            except Exception:
                pass
        threading.Thread(target=open_browser, daemon=True).start()

    print(f"[*] Bien Soan Sach Pro dang chay tai: http://{host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")
