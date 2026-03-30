from setuptools import setup

setup(
    name='flask_hello_world',
    version='0.1.0',
    py_modules=['app'],
    install_requires=[
        'Flask==3.1.3',
        'pyperclip==1.11.0',
    ],
    entry_points={
        'console_scripts': [
            'flask-hello=app:main',
        ],
    },
)
