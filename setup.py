from setuptools import setup

setup(
    name='phone-keyboard',
    version='0.1.0',
    py_modules=['app'],
    install_requires=[
        'Flask==3.1.3',
        'pyperclip==1.11.0',
        'pyautogui==0.9.54',
    ],
    entry_points={
        'console_scripts': [
            'phone-keyboard=app:main',
        ],
    },
)
