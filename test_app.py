import unittest
from unittest.mock import MagicMock
import sys

# Mock pyautogui before importing app
mock_pyautogui = MagicMock()
sys.modules['pyautogui'] = mock_pyautogui

from app import app  # noqa: E402


class FlaskHelloWorldTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_page_form(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<title>Phone Keyboard</title>', response.data)
        self.assertIn(b'<form action="/type" method="post">', response.data)
        self.assertIn(b'<textarea name="text"', response.data)
        self.assertIn(b'name="viewport"', response.data)
        self.assertIn(b'style', response.data)
        self.assertIn(b'name="use_shift_enter"', response.data)
        self.assertIn(b'checked', response.data)

    def test_submit_route_redirects(self):
        test_text = "Line 1\nLine 2"
        response = self.app.post(
            '/type', data={'text': test_text, 'use_shift_enter': 'on'}
        )
        self.assertEqual(response.status_code, 302)
        # Check that it redirects back to home
        self.assertTrue(response.location.endswith('/'))
        # Verify pyautogui.write and hotkey were called
        mock_pyautogui.write.assert_any_call("Line 1")
        mock_pyautogui.write.assert_any_call("Line 2")
        self.assertEqual(mock_pyautogui.write.call_count, 2)
        mock_pyautogui.hotkey.assert_called_once_with('shift', 'enter')

        mock_pyautogui.write.reset_mock()
        mock_pyautogui.hotkey.reset_mock()

    def test_submit_route_without_shift_enter(self):
        test_text = "Line 1\nLine 2"
        response = self.app.post('/type', data={'text': test_text})
        self.assertEqual(response.status_code, 302)
        # Check that it redirects back to home
        self.assertTrue(response.location.endswith('/'))
        # Verify pyautogui.write and hotkey were called
        mock_pyautogui.write.assert_called_once_with(test_text)
        mock_pyautogui.hotkey.assert_not_called()

        mock_pyautogui.write.reset_mock()
        mock_pyautogui.hotkey.reset_mock()


if __name__ == '__main__':
    unittest.main()
