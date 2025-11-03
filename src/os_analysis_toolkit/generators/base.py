"""
Base diagram generator class
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path
import json


class DiagramGenerator(ABC):
    """Abstract base class for diagram generators"""

    def __init__(self, output_dir: str = "diagrams"):
        """
        Initialize diagram generator

        Args:
            output_dir: Directory to save generated diagrams
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def generate_kernel_diagram(self, data: Dict[str, Any]) -> str:
        """Generate kernel architecture diagram"""
        pass

    @abstractmethod
    def generate_process_diagram(self, data: Dict[str, Any]) -> str:
        """Generate process management diagram"""
        pass

    @abstractmethod
    def generate_memory_diagram(self, data: Dict[str, Any]) -> str:
        """Generate memory layout diagram"""
        pass

    @abstractmethod
    def generate_ipc_diagram(self, data: Dict[str, Any]) -> str:
        """Generate IPC flow diagram"""
        pass

    @abstractmethod
    def generate_boot_diagram(self, data: Dict[str, Any]) -> str:
        """Generate boot sequence diagram"""
        pass

    def load_data(self, data_file: str) -> Dict[str, Any]:
        """
        Load data from JSON file

        Args:
            data_file: Path to JSON data file

        Returns:
            Loaded data dictionary
        """
        with open(data_file, 'r') as f:
            return json.load(f)

    def save_diagram(self, content: str, filename: str) -> str:
        """
        Save diagram content to file

        Args:
            content: Diagram content
            filename: Output filename

        Returns:
            Path to saved file
        """
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            f.write(content)
        return str(filepath)

    def generate_all(self, data_dir: str) -> Dict[str, str]:
        """
        Generate all diagrams from data directory

        Args:
            data_dir: Directory containing JSON data files

        Returns:
            Dictionary mapping diagram types to file paths
        """
        data_path = Path(data_dir)
        results = {}

        # Generate kernel diagram
        if (data_path / "kernel.json").exists():
            data = self.load_data(data_path / "kernel.json")
            content = self.generate_kernel_diagram(data)
            results["kernel"] = self.save_diagram(content, "kernel.tex")

        # Generate process diagram
        if (data_path / "process.json").exists():
            data = self.load_data(data_path / "process.json")
            content = self.generate_process_diagram(data)
            results["process"] = self.save_diagram(content, "process.tex")

        # Generate memory diagram
        if (data_path / "memory.json").exists():
            data = self.load_data(data_path / "memory.json")
            content = self.generate_memory_diagram(data)
            results["memory"] = self.save_diagram(content, "memory.tex")

        # Generate IPC diagram
        if (data_path / "ipc.json").exists():
            data = self.load_data(data_path / "ipc.json")
            content = self.generate_ipc_diagram(data)
            results["ipc"] = self.save_diagram(content, "ipc.tex")

        # Generate boot diagram
        if (data_path / "boot.json").exists():
            data = self.load_data(data_path / "boot.json")
            content = self.generate_boot_diagram(data)
            results["boot"] = self.save_diagram(content, "boot.tex")

        return results