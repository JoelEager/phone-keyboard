import socket
import pyperclip
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

def get_local_ip():
    """Returns the local IP address used for internet access."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to a dummy address to determine the local IP
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

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
