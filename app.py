import sys
import os
from flask import Flask, request, redirect, url_for, render_template
from generate_cert import generate_certificate

# Attempt to import pyautogui, handle cases where DISPLAY is not set
try:
    import pyautogui
except Exception:
    pyautogui = None

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    text = request.form.get('text')

    if text:
        # Echo to stdout
        print(f'Received text: {text}', file=sys.stdout)
        sys.stdout.flush()

        # Type the text using pyautogui
        if pyautogui:
            try:
                pyautogui.write(text)
            except Exception as e:
                print(f'Error typing text: {e}', file=sys.stderr)
        else:
            print('Pyautogui not available (check DISPLAY environment variable)', file=sys.stderr)

    # Redirect back to the form
    return redirect(url_for('hello_world'))

def main():
    host = '0.0.0.0'
    port = 5000
    from generate_cert import get_local_ip, get_repo_root

    repo_root = get_repo_root()
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
