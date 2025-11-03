"""
Base analyzer class for OS source code analysis
Provides plugin architecture for OS-specific implementations
"""

import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


class SourceAnalyzer(ABC):
    """
    Abstract base class for OS source code analyzers

    This class provides the framework for analyzing operating system
    source code and extracting structural information.
    """

    def __init__(self, source_root: str, cache_dir: Optional[str] = None):
        """
        Initialize the source analyzer

        Args:
            source_root: Path to OS source tree
            cache_dir: Optional directory for caching analysis results
        """
        self.source_root = Path(source_root)
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.metadata = {
            "analyzer_version": "1.0.0",
            "analysis_timestamp": None,
            "source_root": str(self.source_root),
            "os_type": self.get_os_type(),
        }

        if not self.source_root.exists():
            raise ValueError(f"Source root does not exist: {source_root}")

        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def get_os_type(self) -> str:
        """Return the type of operating system being analyzed"""
        pass

    @abstractmethod
    def analyze_kernel_structure(self) -> Dict[str, Any]:
        """Extract kernel component structure"""
        pass

    @abstractmethod
    def analyze_process_management(self) -> Dict[str, Any]:
        """Extract process management structures"""
        pass

    @abstractmethod
    def analyze_memory_layout(self) -> Dict[str, Any]:
        """Extract memory layout information"""
        pass

    @abstractmethod
    def analyze_ipc_system(self) -> Dict[str, Any]:
        """Extract IPC system details"""
        pass

    def get_cache_key(self, analysis_type: str) -> str:
        """
        Generate cache key for analysis results

        Args:
            analysis_type: Type of analysis being cached

        Returns:
            Cache key string
        """
        source_hash = hashlib.md5(
            str(self.source_root).encode()
        ).hexdigest()[:8]

        return f"{self.get_os_type()}_{analysis_type}_{source_hash}"

    def load_from_cache(self, analysis_type: str) -> Optional[Dict[str, Any]]:
        """
        Load analysis results from cache if available

        Args:
            analysis_type: Type of analysis to load

        Returns:
            Cached data or None if not available
        """
        if not self.cache_dir:
            return None

        cache_file = self.cache_dir / f"{self.get_cache_key(analysis_type)}.json"

        if cache_file.exists():
            # Check if cache is fresh (less than 1 hour old)
            cache_age = datetime.now().timestamp() - cache_file.stat().st_mtime
            if cache_age < 3600:  # 1 hour in seconds
                logger.info(f"Loading {analysis_type} from cache")
                with open(cache_file, 'r') as f:
                    return json.load(f)

        return None

    def save_to_cache(self, analysis_type: str, data: Dict[str, Any]) -> None:
        """
        Save analysis results to cache

        Args:
            analysis_type: Type of analysis being saved
            data: Analysis results to cache
        """
        if not self.cache_dir:
            return

        cache_file = self.cache_dir / f"{self.get_cache_key(analysis_type)}.json"

        logger.info(f"Caching {analysis_type} results")
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)

    def analyze_all(self) -> Dict[str, Any]:
        """
        Run all analysis methods and return combined results

        Returns:
            Dictionary containing all analysis results
        """
        self.metadata["analysis_timestamp"] = datetime.now().isoformat()

        analyses = {
            "kernel_structure": self.analyze_kernel_structure,
            "process_management": self.analyze_process_management,
            "memory_layout": self.analyze_memory_layout,
            "ipc_system": self.analyze_ipc_system,
        }

        results = {"metadata": self.metadata}

        for name, method in analyses.items():
            # Try cache first
            cached = self.load_from_cache(name)
            if cached:
                results[name] = cached
            else:
                # Run analysis and cache results
                logger.info(f"Running {name} analysis")
                data = method()
                self.save_to_cache(name, data)
                results[name] = data

        return results

    def export_to_json(self, output_dir: str) -> Path:
        """
        Export all analysis results to JSON files

        Args:
            output_dir: Directory to save JSON files

        Returns:
            Path to output directory
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        results = self.analyze_all()

        # Save metadata
        with open(output_path / "metadata.json", 'w') as f:
            json.dump(results["metadata"], f, indent=2)

        # Save each analysis
        for key, data in results.items():
            if key != "metadata":
                with open(output_path / f"{key}.json", 'w') as f:
                    json.dump(data, f, indent=2)

        logger.info(f"Exported analysis results to {output_path}")
        return output_path

    def generate_statistics(self) -> Dict[str, Any]:
        """
        Generate overall statistics from analysis

        Returns:
            Dictionary of statistics
        """
        stats = {
            "os_type": self.get_os_type(),
            "source_root": str(self.source_root),
            "analysis_timestamp": datetime.now().isoformat(),
        }

        return stats