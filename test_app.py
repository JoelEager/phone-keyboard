import unittest
from unittest.mock import patch, MagicMock
import sys

# Mock pyautogui before importing app
mock_pyautogui = MagicMock()
sys.modules['pyautogui'] = mock_pyautogui

from app import app

class FlaskHelloWorldTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_page_form(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<title>Phone Keyboard</title>', response.data)
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
        # Verify pyautogui.write was called (on the mock)
        mock_pyautogui.write.assert_called_once_with(test_text)
        mock_pyautogui.write.reset_mock()

    def test_xss_protection(self):
        test_text = "<script>alert('xss')</script>"
        response = self.app.post('/submit', data={'text': test_text})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/'))
        # Verify pyautogui.write was called (on the mock)
        mock_pyautogui.write.assert_called_once_with(test_text)
        mock_pyautogui.write.reset_mock()

if __name__ == '__main__':
    unittest.main()
