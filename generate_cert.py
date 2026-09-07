import logging
import os
import socket
import subprocess

logger = logging.getLogger(__name__)


def get_local_ip():
    """Returns the local IP address of the machine."""
    try:
        # Create a dummy socket to determine the local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"


def generate_certificate(output_dir):
    """Generates a self-signed certificate and key using openssl."""

    cert_path = os.path.join(output_dir, "cert.pem")
    key_path = os.path.join(output_dir, "key.pem")

    local_ip = get_local_ip()
    logger.info(f"Generating self-signed certificate for {local_ip}")

    cmd = [
        "openssl", "req", "-x509", "-newkey", "rsa:4096",
        "-keyout", key_path, "-out", cert_path,
        "-sha256", "-days", "365", "-nodes",
        "-subj", "/C=US/ST=State/L=City/O=Phone Keyboard Flask App/"
                 f"OU=Unit/CN={local_ip}",
        "-addext", f"subjectAltName=IP:{local_ip},IP:127.0.0.1,DNS:localhost"
    ]

    try:
        subprocess.run(cmd, check=True)
        logger.info(
            f"Certificate and key generated successfully in {output_dir}."
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logger.error(f"Error generating certificate: {e}")
        return False
    return True
