from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    error: str | None = None


class ClassMetadata(BaseModel):
    id: int
    name: str
    rgb: list[int]
    ignored: bool


class InputMetadata(BaseModel):
    width: int
    height: int


class PredictionPayload(BaseModel):
    format: str = "png_base64"
    mask_png_base64: str
    overlay_png_base64: str
    classes_present: list[int]
    resized: bool


class PredictResponse(BaseModel):
    input: InputMetadata
    prediction: PredictionPayload
    classes: list[ClassMetadata]
    disclaimer: str

