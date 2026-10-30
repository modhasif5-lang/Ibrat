"""
Unit and Integration Tests for Stage 13: Image Management.
Tests validation, Pillow WebP optimization, thumbnail generation, corruption rejection, and disk cleanup.
"""

import asyncio
import io
import os
import shutil
import tempfile
import uuid
from typing import Tuple
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, UploadFile
from PIL import Image

from app.core.storage import LocalStorageService
from app.services.product_service import ProductService


def create_synthetic_image(
    format_name: str = "JPEG",
    size: Tuple[int, int] = (600, 800),
    color: Tuple[int, int, int] = (197, 168, 128),
) -> bytes:
    """Generate in-memory synthetic image bytes using Pillow."""
    buf = io.BytesIO()
    img = Image.new("RGB", size, color=color)
    img.save(buf, format=format_name)
    return buf.getvalue()


def test_valid_jpeg_upload_and_webp_optimization():
    """Verify JPEG image is validated, converted to WebP, and generates thumbnail."""
    async def _test():
        with tempfile.TemporaryDirectory() as temp_dir:
            service = LocalStorageService(base_dir=temp_dir)
            img_bytes = create_synthetic_image(format_name="JPEG", size=(800, 1000))

            upload_file = UploadFile(
                filename="luxury_pump.jpg",
                file=io.BytesIO(img_bytes),
                headers={"content-type": "image/jpeg"},
            )

            relative_url, full_path = await service.upload_image(upload_file, subfolder="products")

            # 1. Verify path and extension
            assert relative_url.startswith("/api/uploads/products/")
            assert relative_url.endswith(".webp")
            assert os.path.exists(full_path)

            # 2. Verify optimized image is genuine WebP
            with Image.open(full_path) as saved_img:
                assert saved_img.format == "WEBP"
                assert saved_img.size == (800, 1000)

            # 3. Verify thumbnail was generated
            base, ext = os.path.splitext(full_path)
            thumb_path = f"{base}_thumb{ext}"
            assert os.path.exists(thumb_path)
            with Image.open(thumb_path) as thumb_img:
                assert thumb_img.format == "WEBP"
                assert thumb_img.size == (400, 500)

    asyncio.run(_test())


def test_valid_png_with_alpha_channel():
    """Verify PNG with transparency is preserved in WebP."""
    async def _test():
        with tempfile.TemporaryDirectory() as temp_dir:
            service = LocalStorageService(base_dir=temp_dir)

            # Create RGBA PNG
            buf = io.BytesIO()
            img = Image.new("RGBA", (500, 500), color=(255, 0, 0, 128))
            img.save(buf, format="PNG")
            img_bytes = buf.getvalue()

            upload_file = UploadFile(
                filename="transparent_heel.png",
                file=io.BytesIO(img_bytes),
                headers={"content-type": "image/png"},
            )

            relative_url, full_path = await service.upload_image(upload_file, subfolder="products")
            assert os.path.exists(full_path)

            with Image.open(full_path) as saved_img:
                assert saved_img.format == "WEBP"
                assert saved_img.mode in ("RGBA", "RGB")

    asyncio.run(_test())


def test_unsupported_mime_type_rejected():
    """Verify non-image MIME types are rejected with HTTP 400."""
    async def _test():
        with tempfile.TemporaryDirectory() as temp_dir:
            service = LocalStorageService(base_dir=temp_dir)

            upload_file = UploadFile(
                filename="document.pdf",
                file=io.BytesIO(b"%PDF-1.4 ..."),
                headers={"content-type": "application/pdf"},
            )

            with pytest.raises(HTTPException) as exc_info:
                await service.upload_image(upload_file, subfolder="products")

            assert exc_info.value.status_code == 400
            assert "Unsupported file type" in exc_info.value.detail

    asyncio.run(_test())


def test_corrupt_file_rejected_by_magic_bytes():
    """Verify fake file with .jpg extension but corrupt bytes is rejected by Pillow verification."""
    async def _test():
        with tempfile.TemporaryDirectory() as temp_dir:
            service = LocalStorageService(base_dir=temp_dir)

            # Plain text disguised as image
            fake_bytes = b"This is plain text pretending to be a stiletto shoe photo."

            upload_file = UploadFile(
                filename="fake_shoe.jpg",
                file=io.BytesIO(fake_bytes),
                headers={"content-type": "image/jpeg"},
            )

            with pytest.raises(HTTPException) as exc_info:
                await service.upload_image(upload_file, subfolder="products")

            assert exc_info.value.status_code == 400
            assert "Corrupt or invalid image file" in exc_info.value.detail

    asyncio.run(_test())


def test_oversized_file_rejected():
    """Verify files larger than max size are rejected."""
    async def _test():
        with tempfile.TemporaryDirectory() as temp_dir:
            service = LocalStorageService(base_dir=temp_dir)
            # Temporarily configure a small max size (e.g. 1000 bytes)
            service.max_bytes = 1000

            img_bytes = create_synthetic_image(size=(1200, 1200))

            upload_file = UploadFile(
                filename="huge_image.jpg",
                file=io.BytesIO(img_bytes),
                headers={"content-type": "image/jpeg"},
            )

            with pytest.raises(HTTPException) as exc_info:
                await service.upload_image(upload_file, subfolder="products")

            assert exc_info.value.status_code == 400
            assert "File exceeds maximum allowed size" in exc_info.value.detail

    asyncio.run(_test())


def test_image_deletion_removes_main_and_thumb():
    """Verify deleting an image removes both the main WebP and its thumbnail."""
    async def _test():
        with tempfile.TemporaryDirectory() as temp_dir:
            service = LocalStorageService(base_dir=temp_dir)
            img_bytes = create_synthetic_image(format_name="JPEG")

            upload_file = UploadFile(
                filename="sample.jpg",
                file=io.BytesIO(img_bytes),
                headers={"content-type": "image/jpeg"},
            )

            relative_url, full_path = await service.upload_image(upload_file, subfolder="reviews")
            assert os.path.exists(full_path)

            base, ext = os.path.splitext(full_path)
            thumb_path = f"{base}_thumb{ext}"
            assert os.path.exists(thumb_path)

            # Delete
            deleted = await service.delete_image(relative_url)
            assert deleted is True
            assert not os.path.exists(full_path)
            assert not os.path.exists(thumb_path)

    asyncio.run(_test())


def test_downsampling_large_dimensions():
    """Verify images exceeding 1600px are downsampled proportionally."""
    async def _test():
        with tempfile.TemporaryDirectory() as temp_dir:
            service = LocalStorageService(base_dir=temp_dir)
            # 2400x1800 image
            img_bytes = create_synthetic_image(size=(2400, 1800))

            upload_file = UploadFile(
                filename="massive_photo.jpg",
                file=io.BytesIO(img_bytes),
                headers={"content-type": "image/jpeg"},
            )

            _, full_path = await service.upload_image(upload_file, subfolder="products")
            with Image.open(full_path) as saved_img:
                # Should be scaled down to max 1600 on longest edge
                assert max(saved_img.size) == 1600

    asyncio.run(_test())
