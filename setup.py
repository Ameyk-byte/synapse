from setuptools import setup

APP = ['app.py']     # OR desktop_app.py
DATA_FILES = []
OPTIONS = {
    'packages': ['Backend', 'Data'],
    'iconfile': 'appicon.icns',  # optional
}

setup(
    app=APP,
    name="NeuroAI Desktop",
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
