#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.satseg.constants import CLASS_NAMES, IGNORE_INDEX
from src.satseg.metrics import build_metrics_document, compute_segmentation_metrics


def build_metrics_from_prediction_payload(
    payload: dict[str, Any],
    model_artifact_name: str,
    generated_at: str | None = None,
) -> dict[str, Any]:
    split_metrics: dict[str, dict[str, Any]] = {}

    for split_name in ("validation", "test"):
        if split_name not in payload:
            raise ValueError(f"Missing required split: {split_name}")
        split_payload = payload[split_name]
        split_metrics[split_name] = compute_segmentation_metrics(
            split_payload["predictions"],
            split_payload["targets"],
            class_names=CLASS_NAMES,
            ignore_index=IGNORE_INDEX,
        )

    return build_metrics_document(
        split_metrics,
        model_artifact_name=model_artifact_name,
        generated_at=generated_at,
        class_names=CLASS_NAMES,
        ignore_index=IGNORE_INDEX,
    )


def placeholder_split_metrics(reason: str) -> dict[str, Any]:
    rows = [
        {
            "class_id": class_id,
            "class_name": class_name,
            "intersection": 0,
            "union": 0,
            "iou": None,
        }
        for class_id, class_name in enumerate(CLASS_NAMES)
    ]
    return {
        "status": "not_run",
        "reason": reason,
        "pixel_accuracy": None,
        "mean_iou": None,
        "per_class_iou": rows,
        "valid_pixel_count": 0,
        "ignored_pixel_count": 0,
        "class_distribution": {
            class_name: 0
            for class_id, class_name in enumerate(CLASS_NAMES)
            if class_id != IGNORE_INDEX
        },
    }


def build_placeholder_metrics_document(
    model_artifact_name: str,
    reason: str,
    generated_at: str | None = None,
) -> dict[str, Any]:
    return build_metrics_document(
        {
            "validation": placeholder_split_metrics(reason),
            "test": placeholder_split_metrics(reason),
        },
        model_artifact_name=model_artifact_name,
        generated_at=generated_at,
    )


def write_metrics_document(document: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(document, indent=2) + "\n")
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate validation/test segmentation metrics. Pass a prediction payload "
            "with separate validation and test entries, or write an explicit not-run "
            "placeholder when the dataset/model runtime is unavailable."
        )
    )
    parser.add_argument("--predictions-json", type=Path)
    parser.add_argument("--output", type=Path, default=Path("docs/evaluation/metrics.json"))
    parser.add_argument("--model-artifact-name", default="models/pytorch_model.pth")
    parser.add_argument("--generated-at")
    parser.add_argument(
        "--write-placeholder",
        action="store_true",
        help="Write a not-run metrics document instead of failing when no prediction payload is available.",
    )
    parser.add_argument(
        "--placeholder-reason",
        default="Local DubaiDataset labels and the PyTorch runtime are not available in this clone.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.predictions_json:
        payload = json.loads(args.predictions_json.read_text())
        document = build_metrics_from_prediction_payload(
            payload,
            model_artifact_name=args.model_artifact_name,
            generated_at=args.generated_at,
        )
    elif args.write_placeholder:
        document = build_placeholder_metrics_document(
            model_artifact_name=args.model_artifact_name,
            reason=args.placeholder_reason,
            generated_at=args.generated_at,
        )
    else:
        raise SystemExit("Provide --predictions-json or use --write-placeholder.")

    path = write_metrics_document(document, args.output)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
