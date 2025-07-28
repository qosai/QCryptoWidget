# QCryptoWidget/setup.py

from setuptools import setup, find_packages

setup(
    name="QCryptoWidget",
    version="1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "gui_scripts": [
            "crypto_widget = widget.main:main",
        ]
    },
    install_requires=[
        "PySide6>=6.5.0",
        "pyqtgraph>=0.13.0",
        "python-dotenv>=1.0.0",
        "requests>=2.30.0",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A Windows desktop widget for tracking cryptocurrency prices.",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Office/Business :: Financial",
    ],
)