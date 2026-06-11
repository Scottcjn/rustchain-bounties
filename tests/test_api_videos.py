import unittest
from flask.testing import FlaskClient
from src.api import app

class TestApiVideos(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_get_videos_invalid_page(self):
        response = self.app.get("/api/videos?page=abc")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid page parameter", response.json["error"])

    def test_get_videos_out_of_range_page(self):
        response = self.app.get("/api/videos?page=0")
        self.assertEqual(response.status_code, 400)
        self.assertIn("page parameter out of range", response.json["error"])

    def test_get_videos_invalid_per_page(self):
        response = self.app.get("/api/videos?per_page=abc")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid per_page parameter", response.json["error"])

    def test_get_videos_out_of_range_per_page(self):
        response = self.app.get("/api/videos?per_page=100")
        self.assertEqual(response.status_code, 400)
        self.assertIn("per_page parameter out of range", response.json["error"])

if __name__ == "__main__":
    unittest.main()