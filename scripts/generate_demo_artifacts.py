#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.satseg.constants import CLASS_NAMES, CLASS_TO_COLOR
from src.satseg.metrics import current_timestamp


def _safe_stem(path: Path) -> str:
    return "".join(char if char.isalnum() or char in ("-", "_") else "_" for char in path.stem)


def _placeholder_prediction(image: Image.Image) -> Image.Image:
    rgb = image.convert("RGB")
    width, height = rgb.size
    prediction = Image.new("RGB", (width, height))
    pixels = prediction.load()
    source = rgb.load()

    for y in range(height):
        for x in range(width):
            r, g, b = source[x, y]
            brightness = (r + g + b) // 3
            if b > r + 20:
                class_id = 4
            elif g > r + 25:
                class_id = 3
            elif brightness < 75:
                class_id = 2
            elif brightness > 170:
                class_id = 1
            else:
                class_id = 0
            pixels[x, y] = CLASS_TO_COLOR[class_id]

    return prediction


def _overlay(original: Image.Image, prediction: Image.Image) -> Image.Image:
    return Image.blend(original.convert("RGB"), prediction.convert("RGB"), alpha=0.45)


def generate_demo_artifacts(
    sample_images: list[Path],
    output_dir: Path,
    generated_at: str | None = None,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "schema_version": 1,
        "generated_at": generated_at or current_timestamp(),
        "class_names": CLASS_NAMES,
        "samples": [],
    }

    for index, image_path in enumerate(sample_images, start=1):
        stem = f"{index:02d}-{_safe_stem(image_path)}"
        original_name = f"{stem}-original{image_path.suffix.lower() or '.jpg'}"
        prediction_name = f"{stem}-prediction.png"
        overlay_name = f"{stem}-overlay.png"

        original_path = output_dir / original_name
        prediction_path = output_dir / prediction_name
        overlay_path = output_dir / overlay_name

        shutil.copyfile(image_path, original_path)
        with Image.open(image_path) as image:
            prediction = _placeholder_prediction(image)
            prediction.save(prediction_path)
            _overlay(image, prediction).save(overlay_path)

        metadata["samples"].append(
            {
                "id": stem,
                "source_image": image_path.name,
                "original": original_name,
                "prediction": prediction_name,
                "overlay": overlay_name,
                "prediction_source": "generated_placeholder",
                "notes": (
                    "Placeholder prediction generated without the PyTorch runtime. "
                    "Regenerate with model-backed predictions when the DubaiDataset is available."
                ),
            }
        )

    metadata_path = output_dir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n")
    return metadata_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate curated demo sample artifacts.")
    parser.add_argument("sample_images", nargs="*", type=Path, default=[Path("images/image1.jpg"), Path("images/image2.jpg")])
    parser.add_argument("--output-dir", type=Path, default=Path("docs/evaluation/samples"))
    parser.add_argument("--generated-at")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sample_images = [path for path in args.sample_images if path.exists()]
    if not sample_images:
        raise SystemExit("No sample images found.")
    metadata_path = generate_demo_artifacts(
        sample_images=sample_images,
        output_dir=args.output_dir,
        generated_at=args.generated_at,
    )
    print(f"Wrote {metadata_path}")


if __name__ == "__main__":
    main()
