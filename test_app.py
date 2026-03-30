import unittest
from app import app

class FlaskHelloWorldTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_page_form(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<form action="/submit" method="post">', response.data)
        self.assertIn(b'<textarea name="text"', response.data)
        self.assertIn(b'name="viewport"', response.data)
        self.assertIn(b'style', response.data)

    def test_submit_route_redirects(self):
        test_text = "This is a test message."
        response = self.app.post('/submit', data={'text': test_text})
        self.assertEqual(response.status_code, 302)
        # Check that it redirects back to home
        self.assertTrue(response.location.endswith('/'))

if __name__ == '__main__':
    unittest.main()
