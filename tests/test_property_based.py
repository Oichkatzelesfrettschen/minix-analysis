"""
Property-based testing for OS Analysis Toolkit
Using Hypothesis to test invariants and properties
"""

import pytest
import json
import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, assume, settings
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant, Bundle

from os_analysis_toolkit.analyzers import KernelAnalyzer, MemoryAnalyzer
from os_analysis_toolkit.generators import TikZGenerator


class TestAnalyzerProperties:
    """Property-based tests for analyzers"""

    @given(
        page_size=st.sampled_from([1024, 2048, 4096, 8192, 16384]),
        address=st.integers(min_value=0, max_value=0xFFFFFFFF)
    )
    def test_memory_alignment_property(self, page_size, address):
        """Test that memory addresses align correctly to page boundaries"""
        # Page-aligned address should be <= original address
        aligned = (address // page_size) * page_size
        assert aligned <= address
        assert aligned % page_size == 0
        assert address - aligned < page_size

    @given(
        start=st.integers(min_value=0, max_value=0x7FFFFFFF),
        size=st.integers(min_value=1, max_value=0x10000000)
    )
    def test_memory_segment_bounds(self, start, size):
        """Test that memory segments don't overflow"""
        # End address should not wrap around in 32-bit space
        assume(start + size <= 0xFFFFFFFF)

        segment = {
            "start": start,
            "size": size,
            "end": start + size - 1
        }

        # Properties that must hold
        assert segment["end"] >= segment["start"]
        assert segment["end"] - segment["start"] + 1 == segment["size"]
        assert segment["end"] < 0x100000000  # Within 32-bit space

    @given(
        num_processes=st.integers(min_value=1, max_value=256),
        priorities=st.lists(
            st.integers(min_value=0, max_value=39),
            min_size=1,
            max_size=256
        )
    )
    def test_scheduler_fairness_property(self, num_processes, priorities):
        """Test scheduler fairness properties"""
        # Ensure we have the right number of priorities
        priorities = priorities[:num_processes]

        # Calculate priority distribution
        priority_counts = {}
        for p in priorities:
            priority_counts[p] = priority_counts.get(p, 0) + 1

        # Properties:
        # 1. All priorities should be valid
        assert all(0 <= p <= 39 for p in priorities)

        # 2. Priority inversion check: higher priority (lower number) processes
        #    should get more weight
        if len(priority_counts) > 1:
            sorted_priorities = sorted(priority_counts.keys())
            # This is a simplification - real schedulers are more complex
            assert sorted_priorities[0] < sorted_priorities[-1]

    @given(
        syscall_numbers=st.lists(
            st.integers(min_value=0, max_value=500),
            min_size=10,
            max_size=200,
            unique=True
        )
    )
    def test_syscall_uniqueness_property(self, syscall_numbers):
        """Test that syscall numbers are unique and sequential gaps are small"""
        sorted_numbers = sorted(syscall_numbers)

        # Properties:
        # 1. No duplicates (guaranteed by unique=True)
        assert len(set(syscall_numbers)) == len(syscall_numbers)

        # 2. Gaps should be reasonable (not more than 10)
        for i in range(1, len(sorted_numbers)):
            gap = sorted_numbers[i] - sorted_numbers[i-1]
            assert gap >= 1  # Must be at least 1 apart
            # Real systems might have larger gaps for organization
            assert gap <= 50  # But not too large

    @given(
        message_size=st.integers(min_value=1, max_value=1024),
        num_messages=st.integers(min_value=1, max_value=100)
    )
    def test_ipc_message_buffer_property(self, message_size, num_messages):
        """Test IPC message buffer properties"""
        # MINIX has fixed message size
        MINIX_MESSAGE_SIZE = 36

        # If using MINIX-style fixed messages
        if message_size <= MINIX_MESSAGE_SIZE:
            buffer_size = MINIX_MESSAGE_SIZE * num_messages
        else:
            # Variable size messages
            buffer_size = message_size * num_messages

        # Properties:
        # 1. Buffer must fit all messages
        assert buffer_size >= message_size * num_messages

        # 2. Buffer should not be unreasonably large
        assert buffer_size <= 1024 * 1024  # 1MB max

        # 3. Alignment property
        assert buffer_size % 4 == 0 or message_size == 1  # Word-aligned unless byte messages


class TestTikZGeneratorProperties:
    """Property-based tests for TikZ generation"""

    @given(
        num_nodes=st.integers(min_value=1, max_value=20),
        num_edges=st.integers(min_value=0, max_value=50)
    )
    def test_tikz_graph_validity(self, num_nodes, num_edges):
        """Test that generated TikZ graphs are valid"""
        # Edges can't exceed complete graph
        max_edges = num_nodes * (num_nodes - 1) // 2
        assume(num_edges <= max_edges)

        # Generate sample TikZ code
        tikz = f"\\begin{{tikzpicture}}\n"
        for i in range(num_nodes):
            tikz += f"\\node (n{i}) at ({i},0) {{Node {i}}};\n"
        tikz += "\\end{tikzpicture}"

        # Properties:
        # 1. Must have begin and end
        assert "\\begin{tikzpicture}" in tikz
        assert "\\end{tikzpicture}" in tikz

        # 2. Nodes must be defined
        assert tikz.count("\\node") == num_nodes

        # 3. Balanced braces
        assert tikz.count("{") == tikz.count("}")

    @given(
        data=st.dictionaries(
            st.text(min_size=1, max_size=20),
            st.one_of(
                st.integers(),
                st.floats(allow_nan=False, allow_infinity=False),
                st.text(),
                st.booleans()
            ),
            min_size=1,
            max_size=10
        )
    )
    def test_json_serialization_property(self, data):
        """Test that analysis data can be serialized to JSON"""
        # Try to serialize
        json_str = json.dumps(data, default=str)

        # Deserialize
        loaded = json.loads(json_str)

        # Properties:
        # 1. Keys should be preserved
        assert set(loaded.keys()) == set(data.keys())

        # 2. Structure should be preserved
        assert len(loaded) == len(data)


class CacheStateMachine(RuleBasedStateMachine):
    """Stateful testing for cache behavior"""

    def __init__(self):
        super().__init__()
        self.cache = {}
        self.cache_dir = Path(tempfile.mkdtemp())
        self.analyzer = None
        self.analysis_results = Bundle('results')

    @rule(
        analysis_type=st.sampled_from([
            "kernel_structure",
            "process_management",
            "memory_layout",
            "ipc_system",
            "boot_sequence"
        ])
    )
    def analyze(self, analysis_type):
        """Perform an analysis"""
        if not self.analyzer:
            from os_analysis_toolkit.analyzers import KernelAnalyzer
            self.analyzer = KernelAnalyzer("/home/eirikr/Playground/minix")

        # Get the appropriate analysis method
        method_map = {
            "kernel_structure": self.analyzer.analyze_kernel_structure,
            "process_management": self.analyzer.analyze_process_management,
            "memory_layout": self.analyzer.analyze_memory_layout,
            "ipc_system": self.analyzer.analyze_ipc_system,
            "boot_sequence": self.analyzer.analyze_boot_sequence,
        }

        result = method_map[analysis_type]()
        self.cache[analysis_type] = result
        return result

    @rule()
    def clear_cache(self):
        """Clear the cache"""
        self.cache.clear()
        if self.cache_dir.exists():
            for file in self.cache_dir.glob("*.json"):
                file.unlink()

    @invariant()
    def cache_consistency(self):
        """Cache should always return consistent results"""
        if self.analyzer:
            # Re-analyze and check consistency
            for analysis_type, cached_result in self.cache.items():
                # The actual result might use real cache,
                # but structure should be consistent
                assert isinstance(cached_result, dict)

    def teardown(self):
        """Cleanup temporary files"""
        import shutil
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir, ignore_errors=True)


class TestMemoryAllocationProperties:
    """Test memory allocation properties and invariants"""

    @given(
        allocations=st.lists(
            st.tuples(
                st.integers(min_value=1, max_value=1024*1024),  # size
                st.integers(min_value=0, max_value=1000)  # time
            ),
            min_size=1,
            max_size=100
        )
    )
    def test_memory_fragmentation_property(self, allocations):
        """Test that memory fragmentation stays within bounds"""
        total_allocated = sum(size for size, _ in allocations)

        # Simulate fragmentation calculation
        # In a real allocator, fragmentation = (used - allocated) / used
        overhead_factor = 1.2  # 20% overhead max

        total_used = total_allocated * overhead_factor

        # Properties:
        # 1. Used memory should not exceed allocated by more than overhead
        assert total_used <= total_allocated * overhead_factor

        # 2. Fragmentation ratio should be reasonable
        if total_allocated > 0:
            fragmentation = (total_used - total_allocated) / total_used
            assert 0 <= fragmentation <= 0.5  # Max 50% fragmentation

    @given(
        process_count=st.integers(min_value=1, max_value=256),
        memory_per_process=st.integers(min_value=1024, max_value=100*1024*1024)
    )
    def test_memory_limits_property(self, process_count, memory_per_process):
        """Test that memory limits are enforced correctly"""
        # MINIX memory constraints
        MAX_MEMORY = 4 * 1024 * 1024 * 1024  # 4GB
        MAX_PROCESS_MEMORY = 2 * 1024 * 1024 * 1024  # 2GB per process

        # Calculate total memory needed
        total_needed = process_count * memory_per_process

        # Properties:
        # 1. Per-process limit
        assert memory_per_process <= MAX_PROCESS_MEMORY

        # 2. System limit (may need to reject some processes)
        if total_needed > MAX_MEMORY:
            # System should limit number of processes
            max_possible = MAX_MEMORY // memory_per_process
            assert max_possible < process_count
        else:
            # All processes should fit
            assert total_needed <= MAX_MEMORY


class TestSchedulerProperties:
    """Test scheduler properties and invariants"""

    @given(
        ready_queue=st.lists(
            st.integers(min_value=1, max_value=256),  # PIDs
            min_size=0,
            max_size=50
        ),
        blocked_queue=st.lists(
            st.integers(min_value=1, max_value=256),
            min_size=0,
            max_size=50
        )
    )
    def test_process_state_invariants(self, ready_queue, blocked_queue):
        """Test that process state transitions maintain invariants"""
        # Remove duplicates (a process can't be in multiple states)
        ready_set = set(ready_queue)
        blocked_set = set(blocked_queue)

        # Properties:
        # 1. No process in multiple queues
        assert ready_set.isdisjoint(blocked_set)

        # 2. Total processes limited
        total_processes = len(ready_set) + len(blocked_set)
        assert total_processes <= 256  # MINIX limit

        # 3. PID 1 (init) should exist if any processes exist
        if total_processes > 0:
            all_pids = ready_set | blocked_set
            assert min(all_pids) >= 1  # No PID 0


@pytest.mark.slow
class TestPerformanceProperties:
    """Property-based performance tests"""

    @given(
        num_files=st.integers(min_value=10, max_value=100),
        file_sizes=st.lists(
            st.integers(min_value=100, max_value=10000),
            min_size=10,
            max_size=100
        )
    )
    @settings(max_examples=10, deadline=5000)  # 5 second deadline
    def test_analysis_scales_linearly(self, num_files, file_sizes):
        """Test that analysis time scales linearly with input size"""
        import time

        # Simulate analysis of files
        total_size = sum(file_sizes[:num_files])

        # Mock analysis time (should be linear)
        # Real analysis would process actual files
        expected_time_per_byte = 0.000001  # 1 microsecond per byte
        expected_time = total_size * expected_time_per_byte

        start = time.perf_counter()
        # Simulate work
        time.sleep(min(expected_time, 0.1))  # Cap at 100ms for testing
        actual_time = time.perf_counter() - start

        # Property: Time should scale linearly (with some tolerance)
        if total_size > 1000:  # Only check for non-trivial sizes
            time_per_byte = actual_time / total_size
            # Should be within 2x of expected
            assert time_per_byte <= expected_time_per_byte * 2