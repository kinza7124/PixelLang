"""
Setup file for PixelLang Compiler
Install with: pip install .
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pixellang-compiler",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A domain-specific language for pixel art generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pixellang",
    packages=find_packages(),
    py_modules=["main"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Compilers",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Pillow>=9.0.0",
    ],
    entry_points={
        "console_scripts": [
            "pixellang=main:main",
        ],
    },
)
