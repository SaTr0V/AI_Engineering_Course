# TODO: 
# ! - image extensions (after testing on models)
# * better GUI 

from fastapi import FastAPI, Request, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os
from pathlib import Path

import shutil


# Base directory for reliable pathing
BASE_DIR = Path(__file__).parent
# A directory for uploaded images
UPLOAD_DIR = BASE_DIR / "static" / "uploads/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()
# Mount the static directory to serve assets (in our case - images) directly via URL
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# HTML pages use Jinja2 templates engien
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Health-check
@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "Image Upload Service",
        "version": "0.1.0",
    }

# Main form page
@app.get("/", response_class=HTMLResponse)
def form_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "form.html")

# Image uploading handling endpoint
@app.post("/upload", response_class=HTMLResponse)
async def upload(request: Request, file: UploadFile = File(...)) -> HTMLResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is missing")

    # Check if a file with the same name already exists in the static/uploads directory
    fname = file.filename
    file_location = UPLOAD_DIR / fname
    
    if file_location.exists():
        stem = Path(fname).stem
        suffix = Path(fname).suffix
        counter = 1
        
        # Add a number next to stem
        while True:
            new_filename = f"{stem} ({counter}){suffix}"
            file_location = UPLOAD_DIR / new_filename
            if not file_location.exists():
                fname = new_filename
                file.filename = fname
                break
            counter += 1
            
    # Open a local file in write-binary mode to save the uploaded content
    with open(file_location, "wb") as f:
        # Use shutil to stream the file content efficiently to disk
        shutil.copyfileobj(file.file, f)

    file_info = {
        "filename": file.filename,
        "content_type": file.content_type,
        "image_url": f"/static/uploads/{file.filename}"
    }
    
    return templates.TemplateResponse(
        request,
        "result_image.html",
        {
            "file_info": file_info
        }
    )
