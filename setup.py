#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="nvda_linux",
    version="0.1.0",
    description="Lecteur d'écran NVDA adapté pour Linux",
    author="NVDA-Linux Team",
    author_email="contact@nvda-linux.org",
    packages=find_packages(),
    install_requires=[
        "pyatspi>=2.46.0",
        "speechd>=0.11.0",
        "evdev>=1.6.1",
        "python-brlapi>=0.8.0",
        "PyGObject>=3.42.0",
        "transformers>=4.30.0",
        "torch>=2.0.0",
        "opencv-python>=4.7.0",
        "numpy>=1.24.0",
        "pillow>=9.5.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.3.1",
            "pytest-cov>=4.1.0",
            "black>=23.3.0",
            "flake8>=6.0.0",
            "mypy>=1.3.0",
        ],
        "ai": [
            "transformers>=4.30.0",
            "torch>=2.0.0",
            "opencv-python>=4.7.0",
            "numpy>=1.24.0",
            "pillow>=9.5.0",
        ],
        "android": [
            "kivy>=2.2.1",
            "buildozer>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "nvda-linux=nvda_linux.main:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Desktop Environment :: Desktop Environment",
        "Topic :: System :: Operating System",
        "Topic :: Utilities",
    ],
) 