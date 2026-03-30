import socket
import sys
import pyperclip
from flask import Flask, request, redirect, url_for

# Attempt to import pyautogui, handle cases where DISPLAY is not set
try:
    import pyautogui
except Exception:
    pyautogui = None

app = Flask(__name__)

@app.route('/')
def hello_world():
    return '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background-color: #f0f0f0;
                }
                form {
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    width: 90%;
                    max-width: 400px;
                }
                textarea {
                    width: 100%;
                    box-sizing: border-box;
                    padding: 10px;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    font-size: 16px;
                    margin-bottom: 10px;
                    resize: vertical;
                }
                input[type="submit"] {
                    width: 100%;
                    padding: 12px;
                    background-color: #007bff;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 18px;
                    cursor: pointer;
                }
                input[type="submit"]:active {
                    background-color: #0056b3;
                }
            </style>
        </head>
        <body>
            <form action="/submit" method="post">
                <textarea name="text" rows="10" placeholder="Type something here..."></textarea><br>
                <input type="submit" value="Submit">
            </form>
        </body>
        </html>
    '''

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
