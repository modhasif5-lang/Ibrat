"""
Image Storage Service Abstraction & Optimization Engine.
Provides local filesystem storage with Pillow image optimization, thumbnail generation,
format conversion to WebP, and interface ready to be swapped with S3/R2.
"""

import io
import os
import uuid
import logging
from abc import ABC, abstractmethod
from typing import Optional, Tuple
from fastapi import HTTPException, UploadFile, status
from PIL import Image, ImageOps

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger("product-service.storage")


class BaseStorageService(ABC):
    """Abstract file storage interface."""

    @abstractmethod
    async def upload_image(self, file: UploadFile, subfolder: str = "products") -> Tuple[str, str]:
        """Upload image, optimize, generate thumbnail, and return (relative_url, absolute_path)."""
        pass

    @abstractmethod
    async def save_image(self, file: UploadFile, subfolder: str = "products") -> str:
        """Upload image and return relative URL directly."""
        pass

    @abstractmethod
    async def delete_image(self, relative_path: str) -> bool:
        """Delete image and associated thumbnail from storage."""
        pass


class LocalStorageService(BaseStorageService):
    """Local filesystem storage implementation with Pillow WebP optimization."""

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = base_dir or settings.UPLOAD_DIR
        os.makedirs(self.base_dir, exist_ok=True)
        self.allowed_types = [t.strip().lower() for t in settings.ALLOWED_IMAGE_TYPES.split(",")]
        self.max_bytes = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
        self.min_dimension = 100
        self.max_dimension = 4000

    def _validate_and_optimize(
        self, contents: bytes
    ) -> Tuple[bytes, bytes, Tuple[int, int]]:
        """
        Validate image integrity using Pillow, auto-orient, optimize to WebP,
        and generate a 400x500 thumbnail.
        Returns: (optimized_webp_bytes, thumbnail_webp_bytes, (width, height))
        """
        if len(contents) > self.max_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File exceeds maximum allowed size of {settings.MAX_IMAGE_SIZE_MB}MB.",
            )

        # 1. Verify integrity
        try:
            probe = Image.open(io.BytesIO(contents))
            probe.verify()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Corrupt or invalid image file. Header verification failed.",
            )

        # 2. Re-open for actual processing
        img = Image.open(io.BytesIO(contents))
        img = ImageOps.exif_transpose(img)

        # 3. Check dimensions
        w, h = img.size
        if w < self.min_dimension or h < self.min_dimension:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Image dimensions ({w}x{h}) are too small. Minimum is {self.min_dimension}x{self.min_dimension}px.",
            )
        if w > self.max_dimension or h > self.max_dimension:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Image dimensions ({w}x{h}) exceed maximum allowed {self.max_dimension}x{self.max_dimension}px.",
            )

        # 4. Color mode conversion for WebP
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            optimized_img = img.copy()
        else:
            optimized_img = img.convert("RGB")

        # Downsample large images if > 1600px width/height while preserving aspect ratio
        if optimized_img.size[0] > 1600 or optimized_img.size[1] > 1600:
            optimized_img.thumbnail((1600, 1600), Image.Resampling.LANCZOS)

        # Encode main image to WebP
        main_buffer = io.BytesIO()
        optimized_img.save(main_buffer, format="WEBP", quality=85, method=4)
        optimized_bytes = main_buffer.getvalue()

        # 5. Generate 400x500 product thumbnail
        thumb_img = ImageOps.fit(optimized_img, (400, 500), method=Image.Resampling.LANCZOS)
        thumb_buffer = io.BytesIO()
        thumb_img.save(thumb_buffer, format="WEBP", quality=80)
        thumb_bytes = thumb_buffer.getvalue()

        return optimized_bytes, thumb_bytes, optimized_img.size

    async def upload_image(
        self, file: UploadFile, subfolder: str = "products"
    ) -> Tuple[str, str]:
        # Validate content-type
        content_type = file.content_type.lower() if file.content_type else ""
        if content_type not in self.allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type '{content_type}'. Allowed types: {', '.join(self.allowed_types)}",
            )

        contents = await file.read()
        await file.seek(0)

        # Process and optimize
        opt_bytes, thumb_bytes, (w, h) = self._validate_and_optimize(contents)

        file_id = uuid.uuid4().hex
        main_filename = f"{file_id}.webp"
        thumb_filename = f"{file_id}_thumb.webp"

        folder_path = os.path.join(self.base_dir, subfolder)
        os.makedirs(folder_path, exist_ok=True)

        main_path = os.path.join(folder_path, main_filename)
        thumb_path = os.path.join(folder_path, thumb_filename)

        with open(main_path, "wb") as f:
            f.write(opt_bytes)

        with open(thumb_path, "wb") as f:
            f.write(thumb_bytes)

        relative_url = f"/api/uploads/{subfolder}/{main_filename}"
        logger.info(
            f"Image saved & optimized: {relative_url} ({w}x{h}, {len(opt_bytes)} bytes, thumb: {len(thumb_bytes)} bytes)"
        )
        return relative_url, main_path

    async def save_image(self, file: UploadFile, subfolder: str = "products") -> str:
        """Alias returning relative URL directly."""
        rel_url, _ = await self.upload_image(file, subfolder=subfolder)
        return rel_url

    async def delete_image(self, relative_path: str) -> bool:
        """Delete image and thumbnail if present."""
        try:
            clean_path = relative_path.replace("/api/uploads/", "").replace("/uploads/", "").lstrip("/")
            full_path = os.path.join(self.base_dir, clean_path)

            deleted_any = False
            if os.path.exists(full_path):
                os.remove(full_path)
                deleted_any = True

            # Also delete thumbnail if exists
            base, ext = os.path.splitext(full_path)
            thumb_path = f"{base}_thumb{ext}"
            if os.path.exists(thumb_path):
                os.remove(thumb_path)
                deleted_any = True

            return deleted_any
        except Exception as e:
            logger.error(f"Error deleting image {relative_path}: {e}")
            return False


# Singleton storage instance
storage_service = LocalStorageService()
