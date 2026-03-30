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

    def test_submit_route(self):
        test_text = "This is a test message."
        response = self.app.post('/submit', data={'text': test_text})
        self.assertEqual(response.status_code, 200)
        self.assertIn(f'Received: {test_text}'.encode('utf-8'), response.data)

    def test_xss_protection(self):
        test_text = "<script>alert('xss')</script>"
        response = self.app.post('/submit', data={'text': test_text})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"<script>", response.data)
        self.assertIn(b"&lt;script&gt;", response.data)

if __name__ == '__main__':
    unittest.main()
