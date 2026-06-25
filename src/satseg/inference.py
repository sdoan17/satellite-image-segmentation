from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from .constants import IGNORE_INDEX
from .model import load_model
from .visualization import class_mask_to_rgba, overlay_mask, png_base64


class SegmentationPredictor:
    def __init__(self, checkpoint_path: str | Path, device: str | None = None):
        self.checkpoint_path = Path(checkpoint_path)
        self.device = device
        self.model: Any | None = None
        self.resolved_device: str | None = None

    def load(self) -> None:
        try:
            import torch
        except ImportError as exc:
            raise RuntimeError("torch is required to run segmentation inference.") from exc

        self.resolved_device = self.device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = load_model(self.checkpoint_path, self.resolved_device)

    @property
    def is_loaded(self) -> bool:
        return self.model is not None

    def predict(self, image: Image.Image) -> dict[str, object]:
        if self.model is None:
            raise RuntimeError("Model is not loaded.")

        try:
            import torch
        except ImportError as exc:
            raise RuntimeError("torch is required to run segmentation inference.") from exc

        rgb_image = image.convert("RGB")
        original_size = rgb_image.size
        model_image = rgb_image.resize((256, 256), Image.Resampling.BILINEAR)
        image_array = np.asarray(model_image, dtype=np.float32) / 255.0
        tensor = torch.from_numpy(image_array).permute(2, 0, 1).unsqueeze(0).float()
        tensor = tensor.to(self.resolved_device or "cpu")

        with torch.inference_mode():
            logits = self.model(tensor)
            prediction = torch.argmax(logits, dim=1).squeeze(0).cpu().numpy().astype(np.uint8)

        mask_image = Image.fromarray(prediction, mode="L").resize(original_size, Image.Resampling.NEAREST)
        mask = np.asarray(mask_image, dtype=np.uint8)
        mask_rgba = class_mask_to_rgba(mask)
        overlay = overlay_mask(rgb_image, mask_rgba)
        present = sorted(int(value) for value in np.unique(mask) if int(value) != IGNORE_INDEX)

        return {
            "mask_png_base64": png_base64(mask_rgba),
            "overlay_png_base64": png_base64(overlay),
            "classes_present": present,
            "resized": original_size != model_image.size,
            "width": original_size[0],
            "height": original_size[1],
        }

