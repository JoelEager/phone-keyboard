from setuptools import setup

setup(
    name='phone-keyboard',
    version='0.1.0',
    py_modules=['app', 'generate_cert'],
    install_requires=[
        'Flask==3.1.3',
        'pyautogui==0.9.54',
    ],
    entry_points={
        'console_scripts': [
            'phone-keyboard=app:main',
        ],
    },
)
