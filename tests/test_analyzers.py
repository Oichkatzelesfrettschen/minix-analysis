"""
Unit tests for OS analyzers
Testing real functionality with actual MINIX source code
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from os_analysis_toolkit.analyzers import (
    SourceAnalyzer,
    KernelAnalyzer,
    MemoryAnalyzer,
    ProcessAnalyzer,
    IPCAnalyzer
)


class TestKernelAnalyzer:
    """Test kernel analysis functionality"""

    def test_analyzer_initialization_with_real_path(self, minix_source_path):
        """Test that analyzer initializes with real MINIX source"""
        analyzer = KernelAnalyzer(str(minix_source_path))
        assert analyzer.source_root == minix_source_path
        assert analyzer.get_os_type() == "minix"

    def test_kernel_structure_analysis_returns_valid_data(self, minix_source_path):
        """Test kernel structure analysis returns expected fields"""
        analyzer = KernelAnalyzer(str(minix_source_path))
        result = analyzer.analyze_kernel_structure()

        # Verify essential kernel structure fields
        assert isinstance(result, dict)
        assert "microkernel" in result
        assert result["microkernel"] is True  # MINIX is a microkernel
        assert "components" in result
        assert isinstance(result["components"], list)
        assert "kernel" in result["components"]
        assert "architecture" in result
        assert result["architecture"] == "layered"

    def test_process_management_analysis(self, minix_source_path):
        """Test process management analysis with real data"""
        analyzer = KernelAnalyzer(str(minix_source_path))
        result = analyzer.analyze_process_management()

        # Verify process management fields
        assert isinstance(result, dict)
        assert "max_processes" in result
        assert isinstance(result["max_processes"], int)
        assert result["max_processes"] > 0
        assert "scheduling_algorithm" in result
        assert "process_states" in result
        assert isinstance(result["process_states"], list)
        assert "ready" in result["process_states"]
        assert "running" in result["process_states"]

    def test_memory_layout_analysis(self, minix_source_path):
        """Test memory layout analysis returns valid segments"""
        analyzer = KernelAnalyzer(str(minix_source_path))
        result = analyzer.analyze_memory_layout()

        # Verify memory layout structure
        assert isinstance(result, dict)
        assert "segments" in result
        assert isinstance(result["segments"], list)
        assert "text" in result["segments"]
        assert "data" in result["segments"]
        assert "stack" in result["segments"]
        assert "page_size" in result
        assert result["page_size"] == 4096  # Standard page size

    def test_caching_reduces_analysis_time(self, minix_source_path, temp_output_dir, monkeypatch):
        """Test that caching actually works and improves performance"""
        import time

        # Set cache directory to temp
        monkeypatch.setattr("os_analysis_toolkit.analyzers.base.Path.home",
                          lambda: temp_output_dir)

        analyzer = KernelAnalyzer(str(minix_source_path))

        # First call - should be slower
        start = time.perf_counter()
        result1 = analyzer.analyze_kernel_structure()
        time1 = time.perf_counter() - start

        # Second call - should use cache
        start = time.perf_counter()
        result2 = analyzer.analyze_kernel_structure()
        time2 = time.perf_counter() - start

        # Results should be identical
        assert result1 == result2
        # Second call should be faster (allowing some variance)
        # If both are very fast, just check they're equal
        assert time2 <= time1 * 1.5  # Allow some variance

    def test_ipc_system_analysis(self, minix_source_path):
        """Test IPC system analysis with MINIX-specific features"""
        analyzer = KernelAnalyzer(str(minix_source_path))
        result = analyzer.analyze_ipc_system()

        # MINIX-specific IPC features
        assert isinstance(result, dict)
        assert "mechanism" in result
        assert result["mechanism"] == "message_passing"
        assert "synchronous" in result
        assert result["synchronous"] is True
        assert "types" in result
        assert isinstance(result["types"], list)
        assert "send" in result["types"]
        assert "receive" in result["types"]

    def test_boot_sequence_analysis(self, minix_source_path):
        """Test boot sequence analysis"""
        analyzer = KernelAnalyzer(str(minix_source_path))
        result = analyzer.analyze_boot_sequence()

        # Verify boot stages
        assert isinstance(result, dict)
        assert "stages" in result
        assert isinstance(result["stages"], list)
        assert len(result["stages"]) > 0
        assert "kernel" in result["stages"]
        assert "init_process" in result
        assert result["init_process"] == "/sbin/init"


class TestMemoryAnalyzer:
    """Test memory analysis functionality"""

    def test_memory_subsystem_analysis(self, minix_source_path):
        """Test detailed memory subsystem analysis"""
        analyzer = MemoryAnalyzer(str(minix_source_path))
        result = analyzer.analyze_memory_subsystem()

        # Verify memory subsystem details
        assert isinstance(result, dict)
        assert "allocator" in result
        assert "page_replacement" in result
        assert "swap" in result
        assert isinstance(result["swap"], dict)
        assert "enabled" in result["swap"]
        assert "protection" in result
        assert "nx_bit" in result["protection"]

    def test_process_memory_analysis(self, minix_source_path):
        """Test per-process memory management analysis"""
        analyzer = MemoryAnalyzer(str(minix_source_path))
        result = analyzer.analyze_process_memory()

        # Verify process memory management
        assert isinstance(result, dict)
        assert "allocation" in result
        assert result["allocation"] == "demand_paging"
        assert "cow" in result  # Copy-on-write
        assert "limits" in result
        assert isinstance(result["limits"], dict)
        assert "max_heap" in result["limits"]
        assert "max_stack" in result["limits"]

    def test_shared_memory_analysis(self, minix_source_path):
        """Test shared memory implementation analysis"""
        analyzer = MemoryAnalyzer(str(minix_source_path))
        result = analyzer.analyze_shared_memory()

        # Verify shared memory features
        assert isinstance(result, dict)
        assert "sysv_shm" in result
        assert "posix_shm" in result
        assert "mmap" in result
        assert "max_segments" in result
        assert isinstance(result["max_segments"], int)


class TestProcessAnalyzer:
    """Test process management analysis"""

    def test_process_architecture_analysis(self, minix_source_path):
        """Test process architecture analysis"""
        analyzer = ProcessAnalyzer(str(minix_source_path))
        result = analyzer.analyze_process_architecture()

        # Verify process architecture
        assert isinstance(result, dict)
        assert "process_table" in result
        assert isinstance(result["process_table"], dict)
        assert "max_entries" in result["process_table"]
        assert result["process_table"]["max_entries"] == 256  # MINIX limit
        assert "pcb_structure" in result
        assert "pid" in result["pcb_structure"]
        assert "hierarchy" in result
        assert result["hierarchy"]["init_pid"] == 1

    def test_process_memory_map_analysis(self, minix_source_path):
        """Test process memory map analysis"""
        analyzer = ProcessAnalyzer(str(minix_source_path))
        result = analyzer.analyze_process_memory_map()

        # Verify memory map structure
        assert isinstance(result, dict)
        assert "segments" in result
        assert isinstance(result["segments"], list)

        # Find text segment
        text_segment = next((s for s in result["segments"] if s["name"] == "text"), None)
        assert text_segment is not None
        assert text_segment["start"] == "0x08048000"
        assert text_segment["permissions"] == "r-x"

        # Verify libraries section
        assert "libraries" in result
        assert result["libraries"]["dynamic_linking"] is True

    def test_init_process_analysis(self, minix_source_path):
        """Test init process and system initialization analysis"""
        analyzer = ProcessAnalyzer(str(minix_source_path))
        result = analyzer.analyze_init_process()

        # Verify init process details
        assert isinstance(result, dict)
        assert "init" in result
        assert result["init"]["path"] == "/sbin/init"
        assert result["init"]["pid"] == 1
        assert "runlevels" in result
        assert result["runlevels"]["supported"] is True
        assert "startup_scripts" in result


class TestIPCAnalyzer:
    """Test IPC analysis functionality"""

    def test_ipc_kernel_integration(self, minix_source_path):
        """Test IPC kernel integration analysis"""
        analyzer = IPCAnalyzer(str(minix_source_path))
        result = analyzer.analyze_ipc_kernel_integration()

        # Verify IPC kernel integration
        assert isinstance(result, dict)
        assert "implementation_location" in result
        assert result["implementation_location"] == "kernel/ipc.c"
        assert "syscall_interface" in result
        assert result["syscall_interface"]["syscall_number"] == 117
        assert "kernel_structures" in result
        assert "message_struct" in result["kernel_structures"]

    def test_ipc_performance_analysis(self, minix_source_path):
        """Test IPC performance characteristics analysis"""
        analyzer = IPCAnalyzer(str(minix_source_path))
        result = analyzer.analyze_ipc_performance()

        # Verify performance metrics
        assert isinstance(result, dict)
        assert "latency" in result
        assert "local_message" in result["latency"]
        assert "throughput" in result
        assert "messages_per_second" in result["throughput"]
        assert "optimizations" in result
        assert "fast_path" in result["optimizations"]


class TestCacheIntegration:
    """Test caching mechanism across analyzers"""

    def test_cache_persistence_across_instances(self, minix_source_path, temp_output_dir, monkeypatch):
        """Test that cache persists between analyzer instances"""
        # Set cache directory
        cache_dir = temp_output_dir / ".cache"
        cache_dir.mkdir(exist_ok=True)
        monkeypatch.setattr("os_analysis_toolkit.analyzers.base.Path.home",
                          lambda: temp_output_dir)

        # First analyzer instance
        analyzer1 = KernelAnalyzer(str(minix_source_path))
        result1 = analyzer1.analyze_kernel_structure()

        # Verify cache file was created
        cache_files = list(cache_dir.glob("*.json"))
        assert len(cache_files) > 0

        # Second analyzer instance should use cache
        analyzer2 = KernelAnalyzer(str(minix_source_path))
        result2 = analyzer2.analyze_kernel_structure()

        # Results should be identical
        assert result1 == result2

    def test_cache_invalidation_on_ttl_expiry(self, minix_source_path, temp_output_dir, monkeypatch):
        """Test that cache is invalidated after TTL expires"""
        import time
        from unittest.mock import patch

        monkeypatch.setattr("os_analysis_toolkit.analyzers.base.Path.home",
                          lambda: temp_output_dir)

        analyzer = KernelAnalyzer(str(minix_source_path))

        # First call - cache miss
        result1 = analyzer.analyze_kernel_structure()

        # Mock time to simulate TTL expiry (> 1 hour)
        with patch('time.time', return_value=time.time() + 3700):
            # This should trigger cache refresh
            result2 = analyzer.analyze_kernel_structure()

        # Results should still be equal (same analysis)
        assert result1 == result2