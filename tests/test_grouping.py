import unittest
from app.services.grouping_services import group_and_save

class TestGroupingService(unittest.TestCase):
    def test_group_objects(self):
        """
        Test grouping on sample detections.
        """
        sample_image_path = "./static/uploads/sample_image.jpg"
        sample_detections = [
            {"bbox": [50, 50, 100, 100], "label": "LABEL_1", "score": 0.9},
            {"bbox": [200, 200, 250, 250], "label": "LABEL_2", "score": 0.85},
        ]
        results = group_and_save(sample_image_path, sample_detections)
        self.assertIsInstance(results, dict)
        self.assertIn("grouped_image_path", results)
        self.assertIn("grouped_json_path", results)
