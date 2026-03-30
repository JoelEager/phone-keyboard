import socket
import sys
import pyperclip
from flask import Flask, request, redirect, url_for, render_template

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

def get_local_ip():
    """Returns the local IP address of the machine."""
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception:
        return '127.0.0.1'
    
def main():
    host = '0.0.0.0'
    port = 5000
    local_ip = get_local_ip()
    url = f"http://{local_ip}:{port}"

    try:
        pyperclip.copy(url)
        print(f"URL {url} copied to clipboard.")
    except Exception as e:
        print(f"Could not copy URL to clipboard: {e}")

    app.run(host=host, port=port)

if __name__ == '__main__':
    main()
