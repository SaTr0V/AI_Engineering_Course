from src.service.main import app

import pytest
from httpx import AsyncClient, ASGITransport
from pathlib import Path

from typing import Generator
import io


# Client fixture
@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


# Take one image from dataset (~/data/div2k_samples)
@pytest.fixture
def image_from_dataset() -> Generator[str, bytes, str]:
    extensions = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
    
    DATA_DIR = Path(__file__).parent.parent / "data" / "div2k_samples"
    images = [f for f in DATA_DIR.iterdir() if f.suffix.lower() in extensions]

    if not images:
        pytest.skip(f"No images in {DATA_DIR}")
    
    # Sixth image from samples
    image_path = images[5]
    # (image_name, image_size, image_extension)
    yield image_path.name, image_path.read_bytes(), f"image/{image_path.suffix.lstrip('.')}"
    
    # Delete images that were uploaded during testing
    UPLOAD_DIR = Path(__file__).parent.parent / "src" / "service" / "static" / "uploads"
    for f in UPLOAD_DIR.glob(f"{image_path.stem}*{image_path.suffix}"):
        f.unlink()
    

@pytest.mark.asyncio
async def test_root_page(client):
    response = await client.get("/")
    assert response.status_code == 200
    
    print("\nMain page status: 200")


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    
    print("\nHealth-check: ok")


@pytest.mark.asyncio
async def test_image_upload(client, image_from_dataset):
    name, data, extension = image_from_dataset
    
    response = await client.post(
        "/upload",
        files={"file": (name, io.BytesIO(data), extension)}
    )
    
    assert response.status_code == 200
    assert name in response.text
    
    print("\nImage upload test successful")
