#!/usr/bin/env python3
"""
Test suite for MINIX source analyzer
"""

import sys
import json
import pytest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.minix_source_analyzer import MinixAnalyzer


class TestMinixAnalyzer:
    """Test cases for MinixAnalyzer class"""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance"""
        return MinixAnalyzer()

    def test_analyzer_init(self, analyzer):
        """Test analyzer initialization"""
        assert analyzer.minix_root.exists()
        assert analyzer.kernel_dir.exists()
        assert analyzer.include_dir.exists()

    def test_kernel_structure_analysis(self, analyzer):
        """Test kernel structure extraction"""
        data = analyzer.analyze_kernel_structure()

        assert "system_calls" in data
        assert "arch_specific" in data
        assert "interrupt_handlers" in data
        assert "message_types" in data

        # Verify we found system calls
        assert len(data["system_calls"]) > 0

        # Check system call structure
        if data["system_calls"]:
            syscall = data["system_calls"][0]
            assert "name" in syscall
            assert "file" in syscall
            assert "signature" in syscall
            assert "line_count" in syscall

    def test_process_table_analysis(self, analyzer):
        """Test process table extraction"""
        data = analyzer.analyze_process_table()

        assert "process_states" in data
        assert "process_fields" in data
        assert "max_processes" in data
        assert "scheduling_queues" in data

    def test_memory_layout_analysis(self, analyzer):
        """Test memory layout extraction"""
        data = analyzer.analyze_memory_layout()

        assert "segments" in data
        assert "memory_regions" in data
        assert "page_size" in data
        assert "kernel_base" in data

    def test_ipc_system_analysis(self, analyzer):
        """Test IPC system extraction"""
        data = analyzer.analyze_ipc_system()

        assert "message_size" in data
        assert "message_types" in data
        assert "ipc_functions" in data
        assert "endpoints" in data

    def test_boot_sequence_analysis(self, analyzer):
        """Test boot sequence extraction"""
        data = analyzer.analyze_boot_sequence()

        assert "boot_stages" in data
        assert "initialization_functions" in data
        assert "boot_modules" in data

    def test_statistics_generation(self, analyzer):
        """Test statistics generation"""
        stats = analyzer.generate_statistics()

        assert "kernel_files" in stats
        assert "kernel_lines" in stats
        assert "server_count" in stats
        assert "total_syscalls" in stats
        assert "driver_count" in stats

        # Verify reasonable values
        assert stats["kernel_files"] > 0
        assert stats["kernel_lines"] > 0
        assert stats["total_syscalls"] > 0

    def test_data_export(self, analyzer, tmp_path):
        """Test data export functionality"""
        output_dir = analyzer.export_all_data(str(tmp_path))

        # Check all expected files were created
        expected_files = [
            "kernel_structure.json",
            "process_table.json",
            "memory_layout.json",
            "ipc_system.json",
            "boot_sequence.json",
            "statistics.json"
        ]

        for filename in expected_files:
            filepath = output_dir / filename
            assert filepath.exists(), f"Missing {filename}"

            # Verify JSON is valid
            with open(filepath, 'r') as f:
                data = json.load(f)
                assert isinstance(data, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])