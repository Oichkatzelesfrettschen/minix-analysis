"""
Parallel processing support for analysis pipeline
"""

from .executor import ParallelExecutor, AnalysisTask, ParallelAnalysisPipeline
from .pool import ProcessPoolManager

__all__ = [
    "ParallelExecutor",
    "AnalysisTask",
    "ParallelAnalysisPipeline",
    "ProcessPoolManager",
]
