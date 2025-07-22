#!/usr/bin/env python3
"""
Setup script for YouTube Transcript Extractor
"""

from setuptools import setup, find_packages
import os

# パッケージディレクトリ
package_dir = os.path.join(os.path.dirname(__file__), 'src')

# README.mdを読み込み
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# requirements.txtを読み込み
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="youtube-transcript-extractor",
    version="1.0.0",
    author="YouTube Transcript Extractor Team",
    author_email="contact@example.com",
    description="YouTube動画から文字起こしを確実に取得するPythonライブラリ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/youtube-transcript-extractor",
    project_urls={
        "Bug Tracker": "https://github.com/your-username/youtube-transcript-extractor/issues",
        "Documentation": "https://github.com/your-username/youtube-transcript-extractor/blob/main/docs/",
        "Source Code": "https://github.com/your-username/youtube-transcript-extractor",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "audio": [
            "openai>=1.0.0",
            "yt-dlp>=2023.1.6",
            "pydub>=0.25.1",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.10.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "isort>=5.10.0",
            "pre-commit>=2.20.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "youtube-transcript=youtube_transcript_extractor.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "youtube",
        "transcript",
        "subtitles",
        "captions",
        "speech-to-text",
        "video-processing",
        "nlp",
        "text-extraction"
    ],
)

