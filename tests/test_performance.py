"""
Performance benchmarks for OS Analysis Toolkit
Testing with real MINIX source code and measuring actual performance
"""

import pytest
import time
import psutil
import tracemalloc
import json
import statistics
from pathlib import Path
from typing import Dict, List, Any, Callable
from dataclasses import dataclass
import multiprocessing as mp

from os_analysis_toolkit.analyzers import KernelAnalyzer, MemoryAnalyzer, ProcessAnalyzer
from os_analysis_toolkit.parallel import ParallelAnalysisPipeline, ParallelExecutor, AnalysisTask
from os_analysis_toolkit.generators import TikZGenerator


@dataclass
class PerformanceMetrics:
    """Container for performance metrics"""
    name: str
    duration: float  # seconds
    memory_peak: float  # MB
    memory_delta: float  # MB
    cpu_percent: float
    iterations: int
    throughput: float  # items/second
    percentile_95: float
    std_dev: float


class PerformanceBenchmark:
    """Base class for performance benchmarks"""

    def __init__(self, minix_source_path: Path, output_dir: Path):
        self.minix_source_path = minix_source_path
        self.output_dir = output_dir
        self.results: List[PerformanceMetrics] = []

    def measure_performance(
        self,
        func: Callable,
        name: str,
        iterations: int = 10,
        warmup: int = 2
    ) -> PerformanceMetrics:
        """Measure performance of a function with real workload"""

        # Warmup runs
        for _ in range(warmup):
            func()

        durations = []
        memory_peaks = []
        cpu_percents = []
        process = psutil.Process()

        for i in range(iterations):
            # Start measurements
            tracemalloc.start()
            cpu_before = process.cpu_percent()
            memory_before = process.memory_info().rss / 1024 / 1024  # MB

            # Execute function
            start_time = time.perf_counter()
            func()
            duration = time.perf_counter() - start_time

            # Collect metrics
            memory_after = process.memory_info().rss / 1024 / 1024
            cpu_after = process.cpu_percent()
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            durations.append(duration)
            memory_peaks.append(peak / 1024 / 1024)  # MB
            cpu_percents.append(cpu_after - cpu_before)

        # Calculate statistics
        metrics = PerformanceMetrics(
            name=name,
            duration=statistics.mean(durations),
            memory_peak=max(memory_peaks),
            memory_delta=statistics.mean([memory_peaks[i] - memory_peaks[0]
                                         for i in range(len(memory_peaks))]),
            cpu_percent=statistics.mean(cpu_percents),
            iterations=iterations,
            throughput=iterations / sum(durations) if sum(durations) > 0 else 0,
            percentile_95=sorted(durations)[int(len(durations) * 0.95)],
            std_dev=statistics.stdev(durations) if len(durations) > 1 else 0
        )

        self.results.append(metrics)
        return metrics


class TestRealWorldPerformance(PerformanceBenchmark):
    """Test performance with real MINIX analysis workloads"""

    @pytest.mark.benchmark
    def test_full_kernel_analysis_performance(self, minix_source_path, temp_output_dir):
        """Benchmark complete kernel analysis"""

        def analyze_kernel():
            analyzer = KernelAnalyzer(str(minix_source_path))
            results = {
                "kernel": analyzer.analyze_kernel_structure(),
                "process": analyzer.analyze_process_management(),
                "memory": analyzer.analyze_memory_layout(),
                "ipc": analyzer.analyze_ipc_system(),
                "boot": analyzer.analyze_boot_sequence()
            }
            return results

        metrics = self.measure_performance(
            analyze_kernel,
            "full_kernel_analysis",
            iterations=5
        )

        # Performance assertions
        assert metrics.duration < 5.0  # Should complete in < 5 seconds
        assert metrics.memory_peak < 200  # Should use < 200MB
        assert metrics.std_dev < metrics.duration * 0.2  # Stable performance

        # Report results
        print(f"\nKernel Analysis Performance:")
        print(f"  Average time: {metrics.duration:.3f}s")
        print(f"  Memory peak: {metrics.memory_peak:.1f}MB")
        print(f"  95th percentile: {metrics.percentile_95:.3f}s")

    @pytest.mark.benchmark
    def test_parallel_vs_sequential_performance(self, minix_source_path, temp_output_dir):
        """Compare parallel vs sequential analysis performance"""

        # Sequential analysis
        def sequential_analysis():
            pipeline = ParallelAnalysisPipeline(
                source_root=str(minix_source_path),
                output_dir=str(temp_output_dir / "sequential")
            )
            pipeline.executor.max_workers = 1
            return pipeline.run_complete_analysis()

        seq_metrics = self.measure_performance(
            sequential_analysis,
            "sequential_analysis",
            iterations=3
        )

        # Parallel analysis
        def parallel_analysis():
            pipeline = ParallelAnalysisPipeline(
                source_root=str(minix_source_path),
                output_dir=str(temp_output_dir / "parallel")
            )
            pipeline.executor.max_workers = mp.cpu_count()
            return pipeline.run_complete_analysis()

        par_metrics = self.measure_performance(
            parallel_analysis,
            "parallel_analysis",
            iterations=3
        )

        # Calculate speedup
        speedup = seq_metrics.duration / par_metrics.duration

        print(f"\nParallel Performance Comparison:")
        print(f"  Sequential: {seq_metrics.duration:.3f}s")
        print(f"  Parallel: {par_metrics.duration:.3f}s")
        print(f"  Speedup: {speedup:.2f}x")
        print(f"  Efficiency: {speedup / mp.cpu_count() * 100:.1f}%")

        # Parallel should be faster
        assert par_metrics.duration < seq_metrics.duration
        # Should achieve at least 1.5x speedup on multi-core
        if mp.cpu_count() > 1:
            assert speedup > 1.5

    @pytest.mark.benchmark
    def test_cache_performance_impact(self, minix_source_path, temp_output_dir, monkeypatch):
        """Measure cache performance impact on repeated analyses"""

        # Configure cache
        cache_dir = temp_output_dir / ".cache"
        cache_dir.mkdir(exist_ok=True)
        monkeypatch.setattr("os_analysis_toolkit.analyzers.base.Path.home",
                          lambda: temp_output_dir)

        analyzer = KernelAnalyzer(str(minix_source_path))

        # First run - no cache
        def cold_analysis():
            # Clear cache first
            for cache_file in cache_dir.glob("*.json"):
                cache_file.unlink()
            return analyzer.analyze_kernel_structure()

        cold_metrics = self.measure_performance(
            cold_analysis,
            "cold_cache_analysis",
            iterations=3
        )

        # Subsequent runs - with cache
        def warm_analysis():
            return analyzer.analyze_kernel_structure()

        warm_metrics = self.measure_performance(
            warm_analysis,
            "warm_cache_analysis",
            iterations=10
        )

        # Calculate cache benefit
        cache_speedup = cold_metrics.duration / warm_metrics.duration

        print(f"\nCache Performance Impact:")
        print(f"  Cold cache: {cold_metrics.duration:.3f}s")
        print(f"  Warm cache: {warm_metrics.duration:.3f}s")
        print(f"  Cache speedup: {cache_speedup:.1f}x")

        # Cache should provide significant speedup
        assert warm_metrics.duration < cold_metrics.duration
        # Cached should be at least 10x faster for small analyses
        assert cache_speedup > 10

    @pytest.mark.benchmark
    def test_memory_efficiency(self, minix_source_path, temp_output_dir):
        """Test memory efficiency during large-scale analysis"""

        def memory_intensive_analysis():
            # Analyze multiple components simultaneously
            analyzers = [
                KernelAnalyzer(str(minix_source_path)),
                MemoryAnalyzer(str(minix_source_path)),
                ProcessAnalyzer(str(minix_source_path))
            ]

            results = []
            for analyzer in analyzers:
                results.append(analyzer.analyze_kernel_structure())
                results.append(analyzer.analyze_memory_layout())
                results.append(analyzer.analyze_process_management())

            return results

        metrics = self.measure_performance(
            memory_intensive_analysis,
            "memory_intensive",
            iterations=3
        )

        print(f"\nMemory Efficiency:")
        print(f"  Peak memory: {metrics.memory_peak:.1f}MB")
        print(f"  Memory delta: {metrics.memory_delta:.1f}MB")
        print(f"  Memory/operation: {metrics.memory_peak / 9:.1f}MB")  # 9 operations

        # Should be memory efficient
        assert metrics.memory_peak < 500  # Less than 500MB for all operations
        assert metrics.memory_delta < 100  # Memory growth less than 100MB

    @pytest.mark.benchmark
    def test_scalability_with_worker_count(self, minix_source_path, temp_output_dir):
        """Test how performance scales with different worker counts"""

        worker_counts = [1, 2, 4, mp.cpu_count()]
        results = {}

        for workers in worker_counts:
            def analysis_with_workers():
                pipeline = ParallelAnalysisPipeline(
                    source_root=str(minix_source_path),
                    output_dir=str(temp_output_dir / f"workers_{workers}")
                )
                pipeline.executor.max_workers = workers
                return pipeline.run_complete_analysis()

            metrics = self.measure_performance(
                analysis_with_workers,
                f"analysis_{workers}_workers",
                iterations=3
            )
            results[workers] = metrics

        # Print scalability results
        print(f"\nScalability Analysis:")
        baseline = results[1].duration
        for workers, metrics in results.items():
            speedup = baseline / metrics.duration
            efficiency = speedup / workers * 100
            print(f"  {workers} workers: {metrics.duration:.3f}s "
                  f"(speedup: {speedup:.2f}x, efficiency: {efficiency:.1f}%)")

        # Should scale with more workers (with diminishing returns)
        if mp.cpu_count() > 1:
            assert results[2].duration < results[1].duration
        if mp.cpu_count() > 2:
            assert results[4].duration < results[2].duration

    @pytest.mark.benchmark
    def test_json_serialization_performance(self, sample_kernel_data, temp_output_dir):
        """Test JSON serialization performance for large datasets"""

        # Create large dataset
        large_data = {
            f"component_{i}": sample_kernel_data.copy()
            for i in range(100)
        }

        def serialize_data():
            output_file = temp_output_dir / "large_data.json"
            with open(output_file, 'w') as f:
                json.dump(large_data, f, indent=2)
            return output_file

        metrics = self.measure_performance(
            serialize_data,
            "json_serialization",
            iterations=5
        )

        print(f"\nJSON Serialization Performance:")
        print(f"  Time: {metrics.duration:.3f}s")
        print(f"  Throughput: {100/metrics.duration:.1f} components/second")

        # Should handle large datasets efficiently
        assert metrics.duration < 1.0  # Less than 1 second for 100 components

    @pytest.mark.benchmark
    def test_tikz_generation_performance(self, sample_kernel_data, temp_output_dir):
        """Test TikZ diagram generation performance"""

        generator = TikZGenerator(str(temp_output_dir))

        def generate_all_diagrams():
            diagrams = []
            diagrams.append(generator.generate_kernel_diagram(sample_kernel_data))
            diagrams.append(generator.generate_process_diagram({}))
            diagrams.append(generator.generate_memory_diagram({}))
            diagrams.append(generator.generate_ipc_diagram({}))
            diagrams.append(generator.generate_boot_diagram({}))
            return diagrams

        metrics = self.measure_performance(
            generate_all_diagrams,
            "tikz_generation",
            iterations=10
        )

        print(f"\nTikZ Generation Performance:")
        print(f"  Time per set: {metrics.duration:.3f}s")
        print(f"  Time per diagram: {metrics.duration/5:.3f}s")

        # TikZ generation should be fast
        assert metrics.duration < 0.1  # Less than 100ms for 5 diagrams


class TestLoadPerformance:
    """Test performance under various load conditions"""

    @pytest.mark.stress
    def test_concurrent_analysis_stress(self, minix_source_path, temp_output_dir):
        """Stress test with many concurrent analyses"""
        from concurrent.futures import ThreadPoolExecutor
        import threading

        completed = threading.Event()
        results = []

        def analyze_component(component_id):
            analyzer = KernelAnalyzer(str(minix_source_path))
            result = analyzer.analyze_kernel_structure()
            results.append((component_id, result))
            return result

        # Run many concurrent analyses
        start_time = time.perf_counter()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(analyze_component, i)
                for i in range(50)
            ]

            # Wait for all to complete
            for future in futures:
                future.result()

        duration = time.perf_counter() - start_time

        print(f"\nConcurrent Stress Test:")
        print(f"  Analyses: 50")
        print(f"  Total time: {duration:.3f}s")
        print(f"  Throughput: {50/duration:.1f} analyses/second")

        # Should handle concurrent load
        assert len(results) == 50
        assert duration < 30  # Should complete within 30 seconds

    @pytest.mark.stress
    def test_memory_leak_detection(self, minix_source_path, temp_output_dir):
        """Test for memory leaks during extended operation"""
        import gc

        analyzer = KernelAnalyzer(str(minix_source_path))
        process = psutil.Process()

        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_samples = []

        # Run multiple iterations
        for i in range(20):
            # Perform analysis
            analyzer.analyze_kernel_structure()
            analyzer.analyze_process_management()
            analyzer.analyze_memory_layout()

            # Force garbage collection
            gc.collect()

            # Measure memory
            current_memory = process.memory_info().rss / 1024 / 1024
            memory_samples.append(current_memory)

        # Check for memory growth
        memory_growth = memory_samples[-1] - initial_memory
        avg_growth_per_iteration = memory_growth / 20

        print(f"\nMemory Leak Detection:")
        print(f"  Initial memory: {initial_memory:.1f}MB")
        print(f"  Final memory: {memory_samples[-1]:.1f}MB")
        print(f"  Total growth: {memory_growth:.1f}MB")
        print(f"  Growth per iteration: {avg_growth_per_iteration:.2f}MB")

        # Should not leak significant memory
        assert avg_growth_per_iteration < 1.0  # Less than 1MB per iteration