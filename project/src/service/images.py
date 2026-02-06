# TODO: 
# ! - image extensions
# ! - image naming (must be unique)
# * better GUI 

from fastapi import FastAPI, Request, File, UploadFile
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

# Main form page
@app.get("/", response_class=HTMLResponse)
def form_page(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

# Image uploading handling endpoint
@app.post("/upload", response_class=HTMLResponse)
async def upload(request: Request, file: UploadFile = File(...)):
    # Fallback to "unnamed" if the uploaded file has no filename
    if not file.filename:
        file.filename = "unnamed"
        
    file_location = UPLOAD_DIR / file.filename
    
    # Open a local file in write-binary mode to save the uploaded content
    with open(file_location, "wb") as f:
        # Use shutil to stream the file content efficiently to disk
        shutil.copyfileobj(file.file, f)

    file_info = {
        "filename": file.filename,
        "content_type": file.content_type,
        "image_url": f"/static/uploads/{file.filename}"
    }
    
    return templates.TemplateResponse("result_image.html", {"request": request, "file_info": file_info})
    