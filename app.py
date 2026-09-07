import sys
import os
import secrets
from flask import Flask, request, redirect, url_for, render_template, session
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


SERVER_PIN = f"{secrets.randbelow(100000):05d}"
FAILED_ATTEMPTS = 0

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)


@app.before_request
def require_authentication():
    # Allow static resources and login endpoint without auth
    if request.endpoint in ('static', 'login'):
        return None

    if not session.get('authenticated'):
        if request.endpoint == 'type_text':
            text = request.form.get('text')
            print(
                f'Unauthenticated request to /type ignored. Payload text: '
                f'{text}',
                flush=True
            )
        elif request.endpoint == 'shortcut':
            action = request.form.get('action')
            print(
                f'Unauthenticated request to /shortcut ignored. '
                f'Payload action: {action}',
                flush=True
            )

        return render_template('login.html'), 200


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    global FAILED_ATTEMPTS

    if request.method == 'GET':
        if session.get('authenticated'):
            return redirect(url_for('index'))
        return render_template('login.html')

    pin = request.form.get('pin', '')
    if secrets.compare_digest(pin, SERVER_PIN):
        FAILED_ATTEMPTS = 0
        session['authenticated'] = True
        return redirect(url_for('index'))
    else:
        FAILED_ATTEMPTS += 1
        print(
            f"Invalid PIN attempt ({FAILED_ATTEMPTS}/5)",
            file=sys.stderr,
            flush=True
        )
        if FAILED_ATTEMPTS >= 5:
            print(
                "Error: Maximum failed authentication attempts (5) reached. "
                "Exiting process to prevent brute forcing.",
                file=sys.stderr,
                flush=True
            )
            sys.exit(1)

        error_msg = (
            f"Invalid PIN. {5 - FAILED_ATTEMPTS} attempt(s) remaining."
        )
        return render_template('login.html', error=error_msg), 401


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
            print(
                "Error: Failed to generate SSL certificates. "
                "HTTPS is required. Exiting.",
                file=sys.stderr,
                flush=True
            )
            sys.exit(1)

    if not (os.path.exists(cert_path) and os.path.exists(key_path)):
        print(
            "Error: SSL certificate or key file missing. "
            "HTTPS is required. Exiting.",
            file=sys.stderr,
            flush=True
        )
        sys.exit(1)

    print(f"Authentication PIN: {SERVER_PIN}", flush=True)
    app.run(host=host, port=port, ssl_context=(cert_path, key_path))


if __name__ == '__main__':
    main()
