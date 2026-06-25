from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any, Iterable

from .constants import CLASS_NAMES, IGNORE_INDEX


def _tolist(values: Any) -> Any:
    if hasattr(values, "detach"):
        values = values.detach()
    if hasattr(values, "cpu"):
        values = values.cpu()
    if hasattr(values, "tolist"):
        return values.tolist()
    return values


def _flatten(values: Any) -> list[int]:
    values = _tolist(values)
    flattened: list[int] = []

    def visit(item: Any) -> None:
        if isinstance(item, (str, bytes)):
            raise TypeError("Segmentation labels must be numeric, not strings.")
        if isinstance(item, Iterable):
            for child in item:
                visit(child)
            return
        flattened.append(int(item))

    visit(values)
    return flattened


def _paired_labels(predictions: Any, targets: Any) -> list[tuple[int, int]]:
    pred_labels = _flatten(predictions)
    target_labels = _flatten(targets)
    if len(pred_labels) != len(target_labels):
        raise ValueError(
            f"Predictions and targets must contain the same number of pixels: "
            f"{len(pred_labels)} != {len(target_labels)}."
        )
    return list(zip(pred_labels, target_labels))


def pixel_accuracy(predictions: Any, targets: Any, ignore_index: int = IGNORE_INDEX) -> float | None:
    valid_pairs = [(pred, target) for pred, target in _paired_labels(predictions, targets) if target != ignore_index]
    if not valid_pairs:
        return None
    correct = sum(1 for pred, target in valid_pairs if pred == target)
    return correct / len(valid_pairs)


def per_class_iou(
    predictions: Any,
    targets: Any,
    class_names: list[str] | None = None,
    ignore_index: int = IGNORE_INDEX,
) -> list[dict[str, Any]]:
    class_names = class_names or CLASS_NAMES
    pairs = [(pred, target) for pred, target in _paired_labels(predictions, targets) if target != ignore_index]
    intersections = Counter()
    unions = Counter()

    for class_id in range(len(class_names)):
        if class_id == ignore_index:
            continue
        for pred, target in pairs:
            pred_matches = pred == class_id
            target_matches = target == class_id
            if pred_matches and target_matches:
                intersections[class_id] += 1
            if pred_matches or target_matches:
                unions[class_id] += 1

    rows: list[dict[str, Any]] = []

    for class_id, class_name in enumerate(class_names):
        intersection = intersections[class_id]
        union = unions[class_id]
        iou = None if union == 0 or class_id == ignore_index else intersection / union
        rows.append(
            {
                "class_id": class_id,
                "class_name": class_name,
                "intersection": intersection,
                "union": union,
                "iou": iou,
            }
        )

    return rows


def compute_segmentation_metrics(
    predictions: Any,
    targets: Any,
    class_names: list[str] | None = None,
    ignore_index: int = IGNORE_INDEX,
) -> dict[str, Any]:
    class_names = class_names or CLASS_NAMES
    pairs = _paired_labels(predictions, targets)
    valid_pairs = [(pred, target) for pred, target in pairs if target != ignore_index]
    ignored_pixel_count = len(pairs) - len(valid_pairs)
    iou_rows = per_class_iou(predictions, targets, class_names, ignore_index)
    included_ious = [
        row["iou"]
        for row in iou_rows
        if row["class_id"] != ignore_index and row["iou"] is not None
    ]
    target_counts = Counter(target for _pred, target in valid_pairs)

    return {
        "pixel_accuracy": pixel_accuracy(predictions, targets, ignore_index),
        "mean_iou": (sum(included_ious) / len(included_ious)) if included_ious else None,
        "per_class_iou": iou_rows,
        "valid_pixel_count": len(valid_pairs),
        "ignored_pixel_count": ignored_pixel_count,
        "class_distribution": {
            class_names[class_id]: target_counts.get(class_id, 0)
            for class_id in range(len(class_names))
            if class_id != ignore_index
        },
    }


def current_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_metrics_document(
    split_metrics: dict[str, dict[str, Any]],
    model_artifact_name: str,
    generated_at: str | None = None,
    class_names: list[str] | None = None,
    ignore_index: int = IGNORE_INDEX,
) -> dict[str, Any]:
    class_names = class_names or CLASS_NAMES
    return {
        "schema_version": 1,
        "generated_at": generated_at or current_timestamp(),
        "model_artifact_name": model_artifact_name,
        "class_names": class_names,
        "ignore_index": ignore_index,
        "validation": split_metrics.get("validation"),
        "test": split_metrics.get("test"),
    }
