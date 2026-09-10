import os
import sys
from pathlib import Path
from typing import Optional

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
from starlette.requests import Request

from config import BASE_DIR, INPUT_DIR, OUTPUT_DIR, TEMPLATES_DIR, STATIC_DIR, load_settings, save_settings
from core.parser import parse_input_file
from core.rewriter import process_rewrite_pipeline
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

@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    subject: str = Form("toan")
):
    ext = Path(file.filename).suffix.lower()
    if ext not in [".docx", ".doc", ".xlsx", ".xls"]:
        raise HTTPException(status_code=400, detail="Vui lòng tải lên file Word (.docx) hoặc Excel (.xlsx)")

    save_path = INPUT_DIR / file.filename
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        parsed_items = parse_input_file(save_path, subject=subject)
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
async def process_document(
    filename: str = Form(...),
    subject: str = Form("toan"),
    add_count: int = Form(2),
    custom_title: Optional[str] = Form(None),
    paper_format: str = Form("a4")
):
    input_path = INPUT_DIR / filename
    if not input_path.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy file nguồn đã tải lên")

    settings = load_settings()
    api_key = settings.get("gemini_api_key", "").strip()
    model_name = settings.get("gemini_model", "gemini-2.5-flash")

    try:
        # 1. Bóc tách câu hỏi
        questions = parse_input_file(input_path, subject=subject)
        if not questions:
            raise HTTPException(status_code=400, detail="Không trích xuất được bài toán nào từ file này")

        # 2. Tái cấu trúc & Biên soạn lại
        book = process_rewrite_pipeline(
            questions=questions,
            subject=subject,
            add_count=int(add_count),
            api_key=api_key,
            model_name=model_name
        )

        if custom_title and custom_title.strip():
            book.new_title = custom_title.strip()

        # 3. Xuất bản ra Word .docx
        stem = Path(filename).stem
        out_filename = f"Sach_Bien_Soan_{stem}_{book.new_title[:25].strip().replace(' ', '_')}.docx"
        # Làm sạch tên file Windows
        clean_out_name = "".join(c for c in out_filename if c.isalnum() or c in ("-", "_", ".")).strip()
        if not clean_out_name.endswith(".docx"):
            clean_out_name += ".docx"

        out_path = OUTPUT_DIR / clean_out_name
        DocxBookExporter.export(book, out_path, paper_format=paper_format)

        return {
            "status": "success",
            "book": book.to_dict(),
            "output_filename": clean_out_name,
            "download_url": f"/api/download/{clean_out_name}"
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Lỗi khi biên soạn: {str(e)}")

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
