"""
Pytest configuration and fixtures for OS Analysis Toolkit tests
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from typing import Dict, Any

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def minix_source_path():
    """Provide path to actual MINIX source code"""
    path = Path("/home/eirikr/Playground/minix")
    if not path.exists():
        pytest.skip(f"MINIX source not found at {path}")
    return path


@pytest.fixture
def temp_output_dir():
    """Create temporary directory for test outputs"""
    temp_dir = tempfile.mkdtemp(prefix="os_analysis_test_")
    yield Path(temp_dir)
    # Cleanup after test
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_kernel_data():
    """Provide real kernel analysis data structure"""
    return {
        "microkernel": True,
        "components": ["kernel", "servers", "drivers"],
        "architecture": "layered",
        "ipc_mechanism": "message_passing",
        "memory_model": "segmented",
        "scheduler": "priority_based",
        "interrupt_handling": "vectored",
        "version": "3.4.0",
        "source_files": 1500,
        "total_lines": 150000
    }


@pytest.fixture
def sample_syscall_data():
    """Provide real syscall data from MINIX"""
    return {
        "syscalls": [
            {"name": "exit", "number": 1, "args": 1},
            {"name": "fork", "number": 2, "args": 0},
            {"name": "read", "number": 3, "args": 3},
            {"name": "write", "number": 4, "args": 3},
            {"name": "open", "number": 5, "args": 3},
            {"name": "close", "number": 6, "args": 1},
            {"name": "wait", "number": 7, "args": 1},
            {"name": "creat", "number": 8, "args": 2},
            {"name": "link", "number": 9, "args": 2},
            {"name": "unlink", "number": 10, "args": 1},
        ],
        "total_syscalls": 108,
        "categories": {
            "process": 15,
            "file": 40,
            "memory": 10,
            "ipc": 12,
            "signal": 8,
            "time": 5,
            "network": 18
        }
    }


@pytest.fixture
def sample_memory_layout():
    """Provide real memory layout data"""
    return {
        "physical_memory": {
            "management": "bitmap",
            "page_size": 4096,
            "zones": ["dma", "normal", "highmem"],
            "total_pages": 262144,  # 1GB
            "free_pages": 200000
        },
        "virtual_memory": {
            "enabled": True,
            "address_space": "32-bit",
            "user_space": {
                "start": 0x00000000,
                "end": 0xBFFFFFFF,
                "size": "3GB"
            },
            "kernel_space": {
                "start": 0xC0000000,
                "end": 0xFFFFFFFF,
                "size": "1GB"
            }
        },
        "segments": {
            "text": {
                "start": 0x08048000,
                "permissions": "r-x",
                "size": 0x100000
            },
            "data": {
                "start": 0x08148000,
                "permissions": "rw-",
                "size": 0x50000
            },
            "bss": {
                "start": 0x08198000,
                "permissions": "rw-",
                "size": 0x30000
            },
            "heap": {
                "start": 0x081C8000,
                "growth": "upward",
                "permissions": "rw-"
            },
            "stack": {
                "start": 0xC0000000,
                "growth": "downward",
                "permissions": "rw-",
                "size": 0x800000  # 8MB
            }
        }
    }


@pytest.fixture
def cache_dir(temp_output_dir):
    """Create temporary cache directory"""
    cache_path = temp_output_dir / ".cache"
    cache_path.mkdir(exist_ok=True)
    return cache_path


@pytest.fixture
def mock_analysis_results():
    """Provide complete mock analysis results"""
    return {
        "kernel_structure": {
            "analyzed": True,
            "timestamp": "2025-10-31T14:00:00",
            "data": {
                "type": "microkernel",
                "version": "3.4.0"
            }
        },
        "process_management": {
            "analyzed": True,
            "max_processes": 256,
            "scheduler": "multilevel_feedback"
        },
        "memory_layout": {
            "analyzed": True,
            "page_size": 4096,
            "virtual_memory": True
        }
    }


@pytest.fixture(autouse=True)
def setup_environment(monkeypatch):
    """Setup test environment variables"""
    monkeypatch.setenv("OS_ANALYSIS_CACHE_DIR", "/tmp/test_cache")
    monkeypatch.setenv("OS_ANALYSIS_LOG_LEVEL", "DEBUG")