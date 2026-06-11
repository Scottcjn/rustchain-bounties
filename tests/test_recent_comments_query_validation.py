import unittest
from bottube_server import app, _parse_recent_comments_limit, _parse_recent_comments_since

class TestRecentCommentsQueryValidation(unittest.TestCase):
    def test_recent_comments_rejects_malformed_limit(self):
        with app.test_client() as client:
            response = client.get('/api/comments/recent?limit=abc')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json, {"error": "Limit must be an integer"})

    def test_recent_comments_rejects_malformed_since(self):
        with app.test_client() as client:
            response = client.get('/api/comments/recent?since=abc')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json, {"error": "Since must be a number"})

    def test_recent_comments_rejects_non_finite_since(self):
        test_cases = [(float('nan'), "Since must be a finite number"), (float('inf'), "Since must be a non-negative number"), (float('-inf'), "Since must be a non-negative number")]
        for since, error in test_cases:
            with app.test_client() as client:
                response = client.get(f'/api/comments/recent?since={since}')
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json, {"error": error})

if __name__ == '__main__':
    unittest.main()