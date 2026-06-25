from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError

from src.satseg.constants import class_metadata

from .schemas import ClassMetadata, HealthResponse, InputMetadata, PredictResponse, PredictionPayload
from .services.inference_service import InferenceService


MAX_INPUT_PIXELS = 1_048_576
DEMO_DISCLAIMER = "Model prediction for demonstration only; not authoritative geospatial analysis."


def _allowed_origins() -> list[str]:
    raw = os.getenv("BACKEND_CORS_ORIGINS", "*")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def _classes() -> list[ClassMetadata]:
    return [
        ClassMetadata(
            id=item.id,
            name=item.name,
            rgb=list(item.rgb),
            ignored=item.ignored,
        )
        for item in class_metadata()
    ]


async def _read_image(file: UploadFile) -> Image.Image:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Upload must be a supported image file.")

    try:
        file.file.seek(0)
        with Image.open(file.file) as candidate:
            candidate.verify()
        file.file.seek(0)
        with Image.open(file.file) as candidate:
            image = candidate.convert("RGB")
    except (UnidentifiedImageError, OSError):
        raise HTTPException(status_code=400, detail="Upload must be a supported image file.") from None

    pixels = image.width * image.height
    if pixels > MAX_INPUT_PIXELS:
        raise HTTPException(
            status_code=413,
            detail=f"Image has {pixels} pixels and exceeds the {MAX_INPUT_PIXELS} pixel limit.",
        )
    return image


def create_app(inference_service: Any | None = None) -> FastAPI:
    service = inference_service or InferenceService()

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        if inference_service is None:
            service.load()
        yield

    app = FastAPI(
        title="Satellite Segmentation Inference API",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.state.inference_service = service
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_allowed_origins(),
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse | JSONResponse:
        if not service.is_ready:
            response = HealthResponse(
                status="unhealthy",
                model_loaded=False,
                error=service.load_error,
            )
            return JSONResponse(status_code=503, content=response.model_dump())
        return HealthResponse(status="healthy", model_loaded=True, error=None)

    @app.post("/predict", response_model=PredictResponse)
    async def predict(file: UploadFile = File(...)) -> PredictResponse:
        if not service.is_ready:
            raise HTTPException(
                status_code=503,
                detail="Model is not loaded; inference is unavailable.",
            )

        image = await _read_image(file)
        result = service.predict(image)
        return PredictResponse(
            input=InputMetadata(width=image.width, height=image.height),
            prediction=PredictionPayload(
                mask_png_base64=str(result["mask_png_base64"]),
                overlay_png_base64=str(result["overlay_png_base64"]),
                classes_present=[int(value) for value in result.get("classes_present", [])],
                resized=bool(result.get("resized", False)),
            ),
            classes=_classes(),
            disclaimer=DEMO_DISCLAIMER,
        )

    return app


app = create_app()
