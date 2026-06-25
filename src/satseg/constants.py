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

IGNORE_INDEX = 5
NUM_CLASSES = 6
