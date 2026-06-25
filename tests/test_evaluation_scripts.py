import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image


class EvaluationScriptTests(unittest.TestCase):
    def test_build_metrics_from_prediction_payload_keeps_validation_and_test_separate(self):
        from scripts.evaluate_model import build_metrics_from_prediction_payload

        payload = {
            "validation": {
                "predictions": [[0, 1], [1, 1]],
                "targets": [[0, 1], [0, 1]],
            },
            "test": {
                "predictions": [[0, 0], [0, 1]],
                "targets": [[0, 1], [1, 1]],
            },
        }

        document = build_metrics_from_prediction_payload(
            payload,
            model_artifact_name="models/pytorch_model.pth",
            generated_at="2026-06-25T12:00:00Z",
        )

        self.assertNotEqual(document["validation"]["pixel_accuracy"], document["test"]["pixel_accuracy"])
        self.assertEqual(document["validation"]["valid_pixel_count"], 4)
        self.assertEqual(document["test"]["valid_pixel_count"], 4)

    def test_generate_demo_artifacts_writes_prediction_overlay_and_metadata(self):
        from scripts.generate_demo_artifacts import generate_demo_artifacts

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            image_path = tmp_path / "sample.jpg"
            Image.new("RGB", (8, 8), (90, 120, 150)).save(image_path)

            metadata_path = generate_demo_artifacts(
                sample_images=[image_path],
                output_dir=tmp_path / "samples",
                generated_at="2026-06-25T12:00:00Z",
            )

            metadata = json.loads(metadata_path.read_text())
            sample = metadata["samples"][0]

            self.assertEqual(sample["source_image"], "sample.jpg")
            self.assertTrue((tmp_path / "samples" / sample["original"]).exists())
            self.assertTrue((tmp_path / "samples" / sample["prediction"]).exists())
            self.assertTrue((tmp_path / "samples" / sample["overlay"]).exists())
            self.assertEqual(sample["prediction_source"], "generated_placeholder")


if __name__ == "__main__":
    unittest.main()
