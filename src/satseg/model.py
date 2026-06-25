from __future__ import annotations

from pathlib import Path
from typing import Any

from .constants import NUM_CLASSES


def build_model(num_classes: int = NUM_CLASSES) -> Any:
    """Build the notebook-compatible SMP UNet model."""
    try:
        import segmentation_models_pytorch as smp
    except ImportError as exc:
        raise RuntimeError(
            "segmentation-models-pytorch is required to build the segmentation model."
        ) from exc

    return smp.Unet(
        encoder_name="resnet34",
        encoder_weights=None,
        in_channels=3,
        classes=num_classes,
    )


def load_model(checkpoint_path: str | Path, device: str | None = None) -> Any:
    """Load the trained checkpoint once for inference."""
    try:
        import torch
    except ImportError as exc:
        raise RuntimeError("torch is required to load the segmentation model.") from exc

    resolved_device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    model = build_model()
    state_dict = torch.load(checkpoint_path, map_location=resolved_device)
    model.load_state_dict(state_dict)
    model.to(resolved_device)
    model.eval()
    return model

