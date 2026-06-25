import unittest


class MetricsTests(unittest.TestCase):
    def test_pixel_accuracy_ignores_unlabeled_targets(self):
        from src.satseg.metrics import pixel_accuracy

        predictions = [
            [0, 1, 2],
            [5, 4, 0],
        ]
        targets = [
            [0, 1, 5],
            [5, 3, 0],
        ]

        self.assertEqual(pixel_accuracy(predictions, targets, ignore_index=5), 0.75)

    def test_per_class_iou_uses_none_for_empty_union(self):
        from src.satseg.metrics import compute_segmentation_metrics

        metrics = compute_segmentation_metrics(
            predictions=[
                [0, 1],
                [0, 1],
            ],
            targets=[
                [0, 1],
                [1, 1],
            ],
            class_names=["building", "land", "road", "vegetation", "water", "unlabeled"],
            ignore_index=5,
        )

        self.assertEqual(metrics["per_class_iou"][2]["class_name"], "road")
        self.assertIsNone(metrics["per_class_iou"][2]["iou"])
        self.assertEqual(metrics["per_class_iou"][2]["union"], 0)
        self.assertAlmostEqual(metrics["mean_iou"], (0.5 + (2 / 3)) / 2)

    def test_metrics_document_contains_reader_contract(self):
        from src.satseg.metrics import build_metrics_document

        split_metrics = {
            "validation": {
                "pixel_accuracy": 0.5,
                "mean_iou": 0.25,
                "per_class_iou": [],
                "valid_pixel_count": 4,
                "ignored_pixel_count": 1,
                "class_distribution": {},
            },
            "test": {
                "pixel_accuracy": 0.75,
                "mean_iou": 0.4,
                "per_class_iou": [],
                "valid_pixel_count": 8,
                "ignored_pixel_count": 2,
                "class_distribution": {},
            },
        }

        document = build_metrics_document(
            split_metrics,
            model_artifact_name="models/pytorch_model.pth",
            generated_at="2026-06-25T12:00:00Z",
        )

        self.assertEqual(document["schema_version"], 1)
        self.assertEqual(document["model_artifact_name"], "models/pytorch_model.pth")
        self.assertEqual(document["generated_at"], "2026-06-25T12:00:00Z")
        self.assertEqual(document["class_names"][5], "unlabeled")
        self.assertEqual(document["validation"]["pixel_accuracy"], 0.5)
        self.assertEqual(document["test"]["pixel_accuracy"], 0.75)
        self.assertIn("per_class_iou", document["validation"])


if __name__ == "__main__":
    unittest.main()
