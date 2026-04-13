import subprocess
import socket
import os


def get_repo_root():
    """Returns the absolute path to the directory containing this script."""
    return os.path.dirname(os.path.abspath(__file__))


def get_local_ip():
    """Returns the local IP address of the machine."""
    try:
        # Create a dummy socket to determine the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return '127.0.0.1'


def generate_certificate(output_dir=None):
    """Generates a self-signed certificate and key using openssl."""
    if output_dir is None:
        output_dir = get_repo_root()

    cert_path = os.path.join(output_dir, "cert.pem")
    key_path = os.path.join(output_dir, "key.pem")

    local_ip = get_local_ip()
    print(f"Generating self-signed certificate for {local_ip}")

    cmd = [
        "openssl", "req", "-x509", "-newkey", "rsa:4096",
        "-keyout", key_path, "-out", cert_path,
        "-sha256", "-days", "365", "-nodes",
        "-subj", "/C=US/ST=State/L=City/O=Joel local phone keyboard/"
                 f"OU=Unit/CN={local_ip}",
        "-addext", f"subjectAltName=IP:{local_ip},IP:127.0.0.1,DNS:localhost"
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"Certificate and key generated successfully in {output_dir}.")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error generating certificate: {e}")
        return False
    return True
