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
from core.exporter import DocxBookExporter

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

@app.post("/api/scan-folder")
async def api_scan_folder(req: ScanFolderRequest):
    p = Path(req.folder_path.strip().strip('"').strip("'"))
    if not p.exists() or not p.is_dir():
        raise HTTPException(status_code=400, detail=f"Đường dẫn thư mục không tồn tại trên máy: {req.folder_path}")

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

@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    subject: str = Form("toan")
):
    ext = Path(file.filename).suffix.lower()
    allowed = [".docx", ".doc", ".xlsx", ".xls", ".pdf", ".png", ".jpg", ".jpeg"]
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Định dạng không được hỗ trợ. Vui lòng tải lên file: Word, Excel, PDF hoặc Ảnh.")

    save_path = INPUT_DIR / file.filename
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    settings = load_settings()
    api_key = settings.get("gemini_api_key", "").strip()

    try:
        parsed_items = parse_input_file(save_path, subject=subject, api_key=api_key)
        preview = [item.to_dict() for item in parsed_items[:10]]
        return {
            "status": "success",
            "filename": file.filename,
            "total_items": len(parsed_items),
            "preview": preview
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi đọc file: {str(e)}")

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
    model_name = settings.get("gemini_model", "gemini-2.5-flash")

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

        # 3. Xuất Word chuẩn Nghị định 30
        stem = Path(filename).stem
        clean_title_slug = "".join(c for c in book.new_title[:30] if c.isalnum() or c in (" ", "-", "_")).strip().replace(" ", "_")
        out_filename = f"Sach_Bien_Soan_{stem}_{clean_title_slug}.docx"
        out_path = OUTPUT_DIR / out_filename
        DocxBookExporter.export(book, out_path)

        return {
            "status": "success",
            "book": book.to_dict(),
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
    model_name = settings.get("gemini_model", "gemini-2.5-flash")

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

            clean_folder_name = p.name.replace(" ", "_")
            out_filename = f"Dai_Cam_Nang_{clean_folder_name}_Chuan_BGD.docx"
            out_path = OUTPUT_DIR / out_filename
            DocxBookExporter.export(master_book, out_path)

            return {
                "status": "success",
                "mode": "merge",
                "book": master_book.to_dict(),
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
                    clean_slug = "".join(c for c in single_book.new_title[:25] if c.isalnum() or c in (" ", "-", "_")).strip().replace(" ", "_")
                    out_name = f"Sach_{f_path.stem}_{clean_slug}.docx"
                    out_path = OUTPUT_DIR / out_name
                    DocxBookExporter.export(single_book, out_path)

                    processed_books.append({
                        "source": f_path.name,
                        "output_filename": out_name,
                        "download_url": f"/api/download/{out_name}",
                        "title": single_book.new_title,
                        "total_questions": len(single_book.questions)
                    })
                except Exception as e:
                    print(f"Lỗi khi xử lý {f_path.name}: {e}")

            if not processed_books:
                raise HTTPException(status_code=400, detail="Không thể biên soạn tài liệu nào từ thư mục này")

            return {
                "status": "success",
                "mode": "split",
                "total_books": len(processed_books),
                "books": processed_books
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
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

@app.post("/api/open-output-folder")
async def open_output_folder():
    try:
        if sys.platform == "win32":
            os.startfile(str(OUTPUT_DIR))
        return {"status": "success", "folder": str(OUTPUT_DIR)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading

    def open_browser():
        import time
        time.sleep(1.2)
        try:
            webbrowser.open("http://127.0.0.1:8501")
        except Exception:
            pass

    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=8501, log_level="info")
