from __future__ import annotations

import os
from pathlib import Path
from typing import Protocol

from PIL import Image

from src.satseg.inference import SegmentationPredictor


class Predictor(Protocol):
    def load(self) -> None:
        ...

    def predict(self, image: Image.Image) -> dict[str, object]:
        ...


class InferenceService:
    def __init__(self, checkpoint_path: str | Path | None = None, predictor: Predictor | None = None):
        project_root = Path(__file__).resolve().parents[3]
        default_model_path = project_root / "models" / "pytorch_model.pth"
        self.checkpoint_path = Path(
            checkpoint_path or os.getenv("SATSEG_MODEL_PATH", default_model_path)
        )
        self.predictor = predictor or SegmentationPredictor(self.checkpoint_path)
        self.load_error: str | None = None

    def load(self) -> None:
        if self.is_ready:
            return
        try:
            self.predictor.load()
            self.load_error = None
        except Exception as exc:  # noqa: BLE001 - health endpoint should expose load failure.
            self.load_error = str(exc)

    @property
    def is_ready(self) -> bool:
        return getattr(self.predictor, "is_loaded", False)

    def predict(self, image: Image.Image) -> dict[str, object]:
        if not self.is_ready:
            raise RuntimeError("Model is not loaded; inference is unavailable.")
        return self.predictor.predict(image)

