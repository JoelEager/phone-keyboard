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

    def tearDown(self):
        mock_pyautogui.write.reset_mock()
        mock_pyautogui.hotkey.reset_mock()

    def test_home_page_form(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<title>Phone Keyboard</title>', response.data)
        self.assertIn(b'<form action="/type" method="post"', response.data)
        self.assertIn(b'<form action="/shortcut" method="post"', response.data)
        self.assertIn(
            b'<textarea id="message_text" name="text"', response.data
        )
        self.assertIn(b'autocapitalize="sentences"', response.data)
        self.assertIn(b'name="viewport"', response.data)
        self.assertIn(b'style', response.data)
        self.assertIn(b'name="use_shift_enter"', response.data)
        self.assertIn(b'checked', response.data)
        self.assertIn(b'id="autocapitalize_toggle"', response.data)
        self.assertIn(b'Auto-capitalize first word', response.data)

        # Check shortcut grid items
        self.assertIn(b'value="copy"', response.data)
        self.assertIn(b'Copy</span>', response.data)
        self.assertIn(b'value="window_switch"', response.data)
        self.assertIn(b'Window Switch</span>', response.data)
        self.assertIn(b'value="paste"', response.data)
        self.assertIn(b'Paste</span>', response.data)
        self.assertIn(b'value="close_tab"', response.data)
        self.assertIn(b'Close Tab</span>', response.data)

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

    def test_submit_route_without_shift_enter(self):
        test_text = "Line 1\nLine 2"
        response = self.app.post('/type', data={'text': test_text})
        self.assertEqual(response.status_code, 302)
        # Check that it redirects back to home
        self.assertTrue(response.location.endswith('/'))
        # Verify pyautogui.write and hotkey were called
        mock_pyautogui.write.assert_called_once_with(test_text)
        mock_pyautogui.hotkey.assert_not_called()

    def test_shortcut_route_copy(self):
        response = self.app.post('/shortcut', data={'action': 'copy'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/'))
        mock_pyautogui.hotkey.assert_called_once_with('ctrl', 'c')

    def test_shortcut_route_window_switch(self):
        response = self.app.post('/shortcut', data={'action': 'window_switch'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/'))
        mock_pyautogui.hotkey.assert_called_once_with('alt', 'tab')

    def test_shortcut_route_paste(self):
        response = self.app.post('/shortcut', data={'action': 'paste'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/'))
        mock_pyautogui.hotkey.assert_called_once_with('ctrl', 'v')

    def test_shortcut_route_close_tab(self):
        response = self.app.post('/shortcut', data={'action': 'close_tab'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/'))
        mock_pyautogui.hotkey.assert_called_once_with('ctrl', 'w')


if __name__ == '__main__':
    unittest.main()
