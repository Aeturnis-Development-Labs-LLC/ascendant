"""Setup configuration for Ascendant: The Eternal Spire"""

from setuptools import setup, find_packages
import os

# Read version from VERSION file
with open("VERSION", "r", encoding="utf-8") as f:
    version = f.read().strip()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ascendant",
    version=version,
    author="Aeturnis Development Labs LLC",
    author_email="projects@aeturnis.dev",
    description="A roguelike tower climbing game",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Aeturnis-Development-Labs-LLC/ascendant",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment :: Role-Playing",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=[
        # Game dependencies will be added here
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "mypy>=1.5.0",
            "black>=23.7.0",
            "flake8>=6.1.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "ascendant=src.__main__:main",
        ],
    },
)