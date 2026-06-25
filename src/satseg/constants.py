from __future__ import annotations

from dataclasses import dataclass


IGNORE_INDEX = 5
NUM_CLASSES = 6
CLASS_NAMES = ["building", "land", "road", "vegetation", "water", "unlabeled"]
CLASS_COLORS = {
    0: (60, 16, 152),
    1: (132, 41, 246),
    2: (110, 193, 228),
    3: (254, 221, 58),
    4: (226, 169, 41),
    5: (155, 155, 155),
}


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

