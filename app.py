import logging
import os
import secrets
import socket
import sys
import pyautogui
from flask import Flask, redirect, render_template, request, session, url_for
from generate_cert import generate_certificate


SERVER_PIN = f"{secrets.randbelow(100000):05d}"
FAILED_ATTEMPTS = 0
print(f"=== Authentication PIN: {SERVER_PIN} ===")

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.logger.setLevel(logging.DEBUG)


@app.context_processor
def inject_hostname():
    return dict(hostname=socket.gethostname())


@app.before_request
def require_authentication():
    # Allow static resources and login endpoint without auth
    if request.endpoint in ("static", "login"):
        return None

    if not session.get("authenticated"):
        if request.endpoint == "type_text":
            text = request.form.get("text")
            app.logger.warning(
                f"Unauthenticated request to /type ignored. Payload text: {text}"
            )
        elif request.endpoint == "shortcut":
            action = request.form.get("action")
            app.logger.warning(
                f"Unauthenticated request to /shortcut ignored. Payload action: {action}"
            )

        return redirect(url_for("login"))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    global FAILED_ATTEMPTS

    if session.get("authenticated"):
        return redirect(url_for("index"))

    if FAILED_ATTEMPTS < 4 and request.method == "GET":
        return render_template("login.html")

    pin = request.form.get("pin", "")
    if FAILED_ATTEMPTS < 5 and secrets.compare_digest(pin, SERVER_PIN):
        app.logger.info("New client authenticated")
        FAILED_ATTEMPTS = 0
        session["authenticated"] = True
        return redirect(url_for("index"))
    elif FAILED_ATTEMPTS < 4:
        FAILED_ATTEMPTS += 1
        app.logger.warning(f"Invalid PIN attempt ({FAILED_ATTEMPTS}/5)")
        return render_template("login.html", error="Invalid PIN"), 401

    app.logger.error("Restart the server to re-enable PIN authentication")
    return "Server not accepting further authentication requests", 401


@app.route("/type", methods=["POST"])
def type_text():
    text = request.form.get("text")

    if text:
        app.logger.debug(f"Received text: {text}")
        try:
            use_shift_enter = request.form.get("use_shift_enter")
            if use_shift_enter:
                lines = text.splitlines()
                for i, line in enumerate(lines):
                    pyautogui.write(line)
                    if i < len(lines) - 1:
                        pyautogui.hotkey("shift", "enter")
            else:
                pyautogui.write(text)
        except Exception as e:
            app.logger.error(f"Error typing text: {e}")

    return redirect(url_for("index"))


@app.route("/shortcut", methods=["POST"])
def shortcut():
    action = request.form.get("action")

    if action:
        app.logger.debug(f"Received shortcut: {action}")
        try:
            if action == "copy":
                pyautogui.hotkey("ctrl", "c")
            elif action == "paste":
                pyautogui.hotkey("ctrl", "v")
            elif action == "window_switch":
                pyautogui.hotkey("alt", "tab")
            elif action == "close_tab":
                pyautogui.hotkey("ctrl", "w")
        except Exception as e:
            app.logger.error(f"Error executing shortcut: {e}")

    return redirect(url_for("index") + "#shortcuts")


def main():
    host = "0.0.0.0"
    port = 5000

    repo_root = os.path.dirname(os.path.abspath(__file__))
    cert_path = os.path.join(repo_root, "cert.pem")
    key_path = os.path.join(repo_root, "key.pem")

    # Check if certificate files exist, if not generate them
    if not (os.path.exists(cert_path) and os.path.exists(key_path)):
        if not generate_certificate(repo_root):
            app.logger.error(
                "Failed to generate SSL certificates. "
                "HTTPS is required. Exiting."
            )
            sys.exit(1)

    if not (os.path.exists(cert_path) and os.path.exists(key_path)):
        app.logger.error(
            "SSL certificate or key file missing. "
            "HTTPS is required. Exiting."
        )
        sys.exit(1)

    app.run(host=host, port=port, ssl_context=(cert_path, key_path))


if __name__ == "__main__":
    main()
