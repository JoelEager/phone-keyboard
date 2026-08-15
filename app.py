import sys
import os
from flask import Flask, request, redirect, url_for, render_template
from generate_cert import generate_certificate

# Attempt to import pyautogui, handle cases where DISPLAY is not set
try:
    import pyautogui
except Exception as e:
    print(
        f"Error: Failed to import 'pyautogui'. Ensure it is installed and "
        f"the DISPLAY environment variable is set. Details: {e}",
        file=sys.stderr
    )
    sys.exit(1)


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/type', methods=['POST'])
def type_text():
    text = request.form.get('text')

    if text:
        # Echo to stdout
        print(f'Received text: {text}', flush=True)

        # Type the text using pyautogui
        try:
            use_shift_enter = request.form.get('use_shift_enter')
            if use_shift_enter:
                lines = text.splitlines()
                for i, line in enumerate(lines):
                    pyautogui.write(line)
                    if i < len(lines) - 1:
                        pyautogui.hotkey('shift', 'enter')
            else:
                pyautogui.write(text)
        except Exception as e:
            print(f'Error typing text: {e}', file=sys.stderr)

    # Redirect back to the form
    return redirect(url_for('index'))


@app.route('/shortcut', methods=['POST'])
def shortcut():
    action = request.form.get('action')

    if action:
        print(f'Received shortcut: {action}', flush=True)
        try:
            if action == 'copy':
                pyautogui.hotkey('ctrl', 'c')
            elif action == 'paste':
                pyautogui.hotkey('ctrl', 'v')
            elif action == 'window_switch':
                pyautogui.hotkey('alt', 'tab')
            elif action == 'close_tab':
                pyautogui.hotkey('ctrl', 'w')
        except Exception as e:
            print(f'Error executing shortcut {action}: {e}', file=sys.stderr)

    return redirect(url_for('index') + '#shortcuts')


def main():
    host = '0.0.0.0'
    port = 5000

    repo_root = os.path.dirname(os.path.abspath(__file__))
    cert_path = os.path.join(repo_root, "cert.pem")
    key_path = os.path.join(repo_root, "key.pem")

    # Check if certificate files exist, if not generate them
    if not (os.path.exists(cert_path) and os.path.exists(key_path)):
        if not generate_certificate(repo_root):
            print("Failed to generate certificates. Starting without HTTPS.")
            app.run(host=host, port=port)
            return

    app.run(host=host, port=port, ssl_context=(cert_path, key_path))


if __name__ == '__main__':
    main()
