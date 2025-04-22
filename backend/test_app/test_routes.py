import unittest
from app import app

class GameRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'fake_user_id'

    def test_update_money_missing_data(self):
        response = self.client.post('/update-money', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Invalid data', response.data)

    def test_update_birds_missing_data(self):
        response = self.client.post('/update-birds', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Invalid data', response.data)

if __name__ == '__main__':
    unittest.main()
