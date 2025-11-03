#!/usr/bin/env python3
"""
Setup script for OS Analysis Toolkit
A comprehensive framework for analyzing operating system source code
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read long description from README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file) as f:
        requirements = [line.strip() for line in f
                       if line.strip() and not line.startswith('#')]

setup(
    name="os-analysis-toolkit",
    version="1.0.0",
    author="MINIX Analysis Team",
    author_email="",
    description="Comprehensive operating system analysis framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/os-analysis-toolkit",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/os-analysis-toolkit/issues",
        "Documentation": "https://os-analysis-toolkit.readthedocs.io",
        "Source Code": "https://github.com/yourusername/os-analysis-toolkit",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Operating System",
        "Topic :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.6",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
            "sphinx>=7.1.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
        "viz": [
            "matplotlib>=3.7.0",
            "pandas>=2.0.0",
            "numpy>=1.24.0",
            "plotly>=5.17.0",
            "dash>=2.14.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "os-analyze=os_analysis_toolkit.cli:main",
            "minix-analyze=os_analysis_toolkit.minix.cli:main",
            "tikz-generate=os_analysis_toolkit.generators.tikz_cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "os_analysis_toolkit": [
            "templates/*.tex",
            "templates/*.sty",
            "data/*.json",
        ],
    },
    zip_safe=False,
)