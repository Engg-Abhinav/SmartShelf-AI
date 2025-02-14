import unittest
from app.services.detection_services import detect_objects_and_save

class TestDetectionService(unittest.TestCase):
    def test_detect_objects(self):
        """
        Test object detection on a sample image.
        """
        sample_image_path = "./static/uploads/sample_image.jpg"
        results = detect_objects_and_save(sample_image_path)
        self.assertIsInstance(results, dict)
        self.assertIn("detections", results)
        self.assertGreater(len(results["detections"]), 0)
