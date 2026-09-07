import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock pyautogui before importing app
mock_pyautogui = MagicMock()
sys.modules['pyautogui'] = mock_pyautogui

import app as app_module  # noqa: E402
from app import app  # noqa: E402


class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        app_module.FAILED_ATTEMPTS = 0

    def tearDown(self):
        mock_pyautogui.write.reset_mock()
        mock_pyautogui.hotkey.reset_mock()
        app_module.FAILED_ATTEMPTS = 0

    def _authenticate(self):
        with self.app.session_transaction() as sess:
            sess['authenticated'] = True

    def test_unauthenticated_get_index_shows_login(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Authentication Required', response.data)
        self.assertIn(b'<form action="/login" method="post"', response.data)

    def test_unauthenticated_post_type_ignored(self):
        response = self.app.post('/type', data={'text': 'Hello World'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Authentication Required', response.data)
        mock_pyautogui.write.assert_not_called()

    def test_unauthenticated_post_shortcut_ignored(self):
        response = self.app.post('/shortcut', data={'action': 'copy'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Authentication Required', response.data)
        mock_pyautogui.hotkey.assert_not_called()

    def test_successful_login(self):
        response = self.app.post(
            '/login', data={'pin': app_module.SERVER_PIN}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/'))

        # Verify now authenticated and can access index
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<title>Phone Keyboard</title>', response.data)

    def test_invalid_pin_login(self):
        invalid_pin = '00000' if app_module.SERVER_PIN != '00000' else '11111'
        response = self.app.post('/login', data={'pin': invalid_pin})
        self.assertEqual(response.status_code, 401)
        self.assertIn(b'Invalid PIN', response.data)
        self.assertEqual(app_module.FAILED_ATTEMPTS, 1)

    def test_brute_force_exit_after_five_failed_attempts(self):
        invalid_pin = '00000' if app_module.SERVER_PIN != '00000' else '11111'
        for i in range(4):
            response = self.app.post('/login', data={'pin': invalid_pin})
            self.assertEqual(response.status_code, 401)
            self.assertEqual(app_module.FAILED_ATTEMPTS, i + 1)

        # 5th attempt should exit process
        with self.assertRaises(SystemExit):
            self.app.post('/login', data={'pin': invalid_pin})

    def test_successful_login_resets_failed_attempts(self):
        app_module.FAILED_ATTEMPTS = 3
        response = self.app.post(
            '/login', data={'pin': app_module.SERVER_PIN}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(app_module.FAILED_ATTEMPTS, 0)

    def test_home_page_form_when_authenticated(self):
        self._authenticate()
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<title>Phone Keyboard</title>', response.data)
        self.assertIn(b'<form action="/type" method="post"', response.data)
        self.assertIn(
            b'<form id="shortcuts" action="/shortcut" method="post">',
            response.data
        )
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
        self._authenticate()
        test_text = "Line 1\nLine 2"
        response = self.app.post(
            '/type', data={'text': test_text, 'use_shift_enter': 'on'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/'))
        mock_pyautogui.write.assert_any_call("Line 1")
        mock_pyautogui.write.assert_any_call("Line 2")
        self.assertEqual(mock_pyautogui.write.call_count, 2)
        mock_pyautogui.hotkey.assert_called_once_with('shift', 'enter')

    def test_submit_route_without_shift_enter(self):
        self._authenticate()
        test_text = "Line 1\nLine 2"
        response = self.app.post('/type', data={'text': test_text})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/'))
        mock_pyautogui.write.assert_called_once_with(test_text)
        mock_pyautogui.hotkey.assert_not_called()

    def test_shortcut_route_copy(self):
        self._authenticate()
        response = self.app.post('/shortcut', data={'action': 'copy'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/#shortcuts'))
        mock_pyautogui.hotkey.assert_called_once_with('ctrl', 'c')

    def test_shortcut_route_window_switch(self):
        self._authenticate()
        response = self.app.post('/shortcut', data={'action': 'window_switch'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/#shortcuts'))
        mock_pyautogui.hotkey.assert_called_once_with('alt', 'tab')

    def test_shortcut_route_paste(self):
        self._authenticate()
        response = self.app.post('/shortcut', data={'action': 'paste'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/#shortcuts'))
        mock_pyautogui.hotkey.assert_called_once_with('ctrl', 'v')

    def test_shortcut_route_close_tab(self):
        self._authenticate()
        response = self.app.post('/shortcut', data={'action': 'close_tab'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/#shortcuts'))
        mock_pyautogui.hotkey.assert_called_once_with('ctrl', 'w')

    @patch('app.generate_certificate', return_value=False)
    @patch('os.path.exists', return_value=False)
    def test_main_exits_when_https_fails(self, mock_exists, mock_gen_cert):
        with self.assertRaises(SystemExit):
            app_module.main()


if __name__ == '__main__':
    unittest.main()
