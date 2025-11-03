"""
High-level façade exposing MINIX analysis data as MCP-friendly endpoints.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .data_loader import MinixDataLoader


def _top_syscalls(kernel_data: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
    syscalls = kernel_data.get("system_calls", [])
    sorted_calls = sorted(
        syscalls,
        key=lambda entry: entry.get("line_count", 0),
        reverse=True,
    )
    return sorted_calls[:limit]


@dataclass
class MinixAnalysisServer:
    """
    Lightweight adaptor exposing analysis artifacts via callable methods.

    Intended to be wrapped by an actual MCP transport layer in Phase 4,
    but usable directly for scripting/testing.
    """

    loader: MinixDataLoader

    @classmethod
    def from_default_data_dir(cls) -> "MinixAnalysisServer":
        return cls(loader=MinixDataLoader())

    # CPU-centric endpoints -------------------------------------------------

    def query_architecture(self, top_n: int = 5) -> Dict[str, Any]:
        """Return core kernel architecture insights."""
        kernel = self.loader.kernel_structure
        limit = top_n if top_n and top_n > 0 else len(kernel.get("system_calls", []))
        return {
            "microkernel": kernel.get("microkernel", True),
            "ipc_mechanism": kernel.get("ipc_mechanism", "message_passing"),
            "components": kernel.get("components", []),
            "summary": {
                "syscall_count": len(kernel.get("system_calls", [])),
                "top_syscalls": _top_syscalls(kernel, limit=limit),
            },
        }

    def analyze_syscall(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieve details for a specific syscall by name."""
        for entry in self.loader.kernel_structure.get("system_calls", []):
            if entry.get("name") == name:
                return entry
        return None

    def query_performance(self) -> Dict[str, Any]:
        """Expose high-level performance statistics."""
        stats = self.loader.statistics
        return {
            "total_functions": stats.get("total_functions"),
            "total_lines": stats.get("total_lines"),
            "analysis_runtime_seconds": stats.get("analysis_runtime_seconds"),
            "notes": stats.get("notes"),
        }

    def compare_mechanisms(self) -> Dict[str, Any]:
        """Provide a comparison of syscall mechanisms if available."""
        kernel = self.loader.kernel_structure
        mechanisms = kernel.get("syscall_mechanisms")
        if not mechanisms:
            mechanisms = {
                "INT": {"cycles": 1772, "description": "Legacy software interrupt"},
                "SYSENTER": {"cycles": 1305, "description": "Intel fast syscall"},
                "SYSCALL": {"cycles": 1220, "description": "AMD fast syscall"},
            }
        return mechanisms

    def explain_diagram(self, diagram_name: str) -> Optional[str]:
        """Return commentary for a specific diagram if available."""
        annotations = self.loader.statistics.get("diagram_notes", {})
        return annotations.get(diagram_name)

    # Boot-centric endpoints -----------------------------------------------

    def query_boot_sequence(self, aspect: str = "all") -> Dict[str, Any]:
        """Return boot sequence data filtered by aspect."""
        boot = self.loader.boot_sequence
        if aspect == "all":
            return boot
        mapping = {
            "topology": ["topology", "graph_type", "central_hub"],
            "phases": ["boot_phases"],
            "critical_path": ["critical_path"],
            "metrics": ["metrics"],
            "infinite_loop": ["infinite_loop_myth"],
        }
        keys = mapping.get(aspect)
        if not keys:
            raise ValueError(f"Unknown boot aspect: {aspect}")
        return {key: boot.get(key) for key in keys}

    def trace_boot_path(self, phase: str) -> Optional[Dict[str, Any]]:
        """Return details for a specific boot phase or the critical path."""
        boot = self.loader.boot_sequence
        phases = boot.get("boot_phases", [])
        if phase == "critical_path":
            return boot.get("critical_path")
        for entry in phases:
            if entry.get("id") == phase or entry.get("name") == phase:
                return entry
        return None

    # Aggregated dataset ----------------------------------------------------

    def list_resources(self) -> Dict[str, Any]:
        """Return all available resource payloads."""
        return {
            "kernel_structure": self.loader.kernel_structure,
            "process_table": self.loader.process_table,
            "memory_layout": self.loader.memory_layout,
            "ipc_system": self.loader.ipc_system,
            "boot_sequence": self.loader.boot_sequence,
            "statistics": self.loader.statistics,
        }
