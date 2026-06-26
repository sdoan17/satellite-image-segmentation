from __future__ import annotations

from dataclasses import dataclass


CLASS_NAMES = ["building", "land", "road", "vegetation", "water", "unlabeled"]

COLOR_TO_CLASS = {
    (60, 16, 152): 0,
    (132, 41, 246): 1,
    (110, 193, 228): 2,
    (254, 221, 58): 3,
    (226, 169, 41): 4,
    (155, 155, 155): 5,
}

CLASS_TO_COLOR = {class_id: color for color, class_id in COLOR_TO_CLASS.items()}
CLASS_COLORS = CLASS_TO_COLOR

IGNORE_INDEX = 5
NUM_CLASSES = 6


@dataclass(frozen=True)
class SegmentationClass:
    id: int
    name: str
    rgb: tuple[int, int, int]
    ignored: bool = False


def class_metadata() -> list[SegmentationClass]:
    return [
        SegmentationClass(
            id=class_id,
            name=CLASS_NAMES[class_id],
            rgb=CLASS_COLORS[class_id],
            ignored=class_id == IGNORE_INDEX,
        )
        for class_id in range(NUM_CLASSES)
    ]
