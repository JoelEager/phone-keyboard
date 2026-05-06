# Phone Keyboard
![App icon](static/favicon.svg)
A simple Flask application to enable me to type on a computer using my phone's touch and voice keyboard. Authored using [Google Jules](https://jules.google.com/).

## Installation
### Standard installation
```bash
pip install .
```

### Editable mode
```bash
pip install -e .
```

## Usage
### Run with Python
```bash
python3 app.py
```

### Run with console script
If installed, you can use:
```bash
phone-keyboard
```

## HTTPS and Mobile Setup
The application is configured to use HTTPS to enable the Screen Wake Lock JS API.

1. **Certificate Generation**: The server will automatically generate `cert.pem` and `key.pem` the first time it runs, specific to your local IP address. These files are excluded from the repository via `.gitignore`.
2. **Mobile Device Setup**: To avoid "Insecure Connection" warnings on your phone and enable the Wake Lock API, you must install and trust `cert.pem` on your mobile device:
   - **iOS**:
     - Transfer `cert.pem` to your iPhone.
     - Open the file and follow the prompts to install the profile.
     - Go to `Settings > General > VPN & Device Management` and ensure the profile is installed.
     - Go to `Settings > General > About > Certificate Trust Settings` and enable "Full Trust" for the self-signed certificate.
   - **Android**:
     - Transfer `cert.pem` to your device.
     - Go to `Settings > Security > More security settings > Encryption & credentials > Install a certificate > CA certificate` and select `cert.pem`.
3. **Access**: Navigate to `https://<your-local-ip>:5000` on your mobile browser.

## Running Tests
```bash
python3 test_app.py
```
