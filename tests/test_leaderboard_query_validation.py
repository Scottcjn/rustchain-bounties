import unittest
from bottube_server import app

class TestLeaderboardQueryValidation(unittest.TestCase):
    def test_quests_leaderboard_rejects_malformed_limit(self):
        with app.test_client() as client:
            response = client.get('/api/quests/leaderboard?limit=abc')
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid limit parameter', response.json['error'])

    def test_gamification_leaderboard_rejects_malformed_limit(self):
        with app.test_client() as client:
            response = client.get('/api/gamification/leaderboard?limit=abc')
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid limit parameter', response.json['error'])

if __name__ == '__main__':
    unittest.main()