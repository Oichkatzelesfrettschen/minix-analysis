"""
OS Analysis Toolkit
A comprehensive framework for analyzing operating system source code
"""

__version__ = "1.0.0"
__author__ = "MINIX Analysis Team"

from .analyzers import SourceAnalyzer
from .generators import TikZGenerator, DiagramGenerator

__all__ = [
    "SourceAnalyzer",
    "TikZGenerator",
    "DiagramGenerator",
    "__version__",
]