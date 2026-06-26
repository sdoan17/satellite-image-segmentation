from __future__ import annotations

import base64
import io

import numpy as np
from PIL import Image

from .constants import CLASS_COLORS, IGNORE_INDEX


def class_mask_to_rgba(mask: np.ndarray, alpha: int = 180) -> Image.Image:
    rgba = np.zeros((*mask.shape, 4), dtype=np.uint8)
    for class_id, rgb in CLASS_COLORS.items():
        selected = mask == class_id
        rgba[selected, :3] = rgb
        rgba[selected, 3] = 0 if class_id == IGNORE_INDEX else alpha
    return Image.fromarray(rgba, mode="RGBA")


def overlay_mask(image: Image.Image, mask_rgba: Image.Image) -> Image.Image:
    base = image.convert("RGBA")
    if mask_rgba.size != base.size:
        mask_rgba = mask_rgba.resize(base.size, Image.Resampling.NEAREST)
    return Image.alpha_composite(base, mask_rgba)


def png_base64(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")

