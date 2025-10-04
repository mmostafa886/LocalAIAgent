"""
Setup configuration for Test Case Generator package.

This allows the package to be installed in development mode,
making imports work correctly from anywhere in the project.

Usage:
    pip install -e .
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file for long description
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")

setup(
    name="test-case-generator",
    version="1.0.0",
    author="SDET Team",
    description="AI-powered test case generator using local Ollama models",
    long_description=long_description,
    long_description_content_type="text/markdown",

    # Package configuration
    package_dir={"": "src"},
    packages=find_packages(where="src"),

    # Dependencies
    install_requires=[
        "ollama>=0.1.0",
        "flask>=2.3.0",
    ],

    # Optional dependencies for development
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
    },

    # Python version requirement
    python_requires=">=3.8",

    # Entry points for command-line scripts (optional)
    entry_points={
        "console_scripts": [
            "test-case-gen=cli:main",
        ],
    },

    # Package metadata
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)