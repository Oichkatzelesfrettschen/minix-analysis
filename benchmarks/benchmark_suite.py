#!/usr/bin/env python3
"""
Comprehensive benchmarking suite for OS analysis pipeline
Measures performance, accuracy, and resource usage
"""

import time
import json
import psutil
import statistics
import tracemalloc
from pathlib import Path
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.os_analysis_toolkit.parallel.executor import ParallelExecutor, AnalysisTask


@dataclass
class BenchmarkResult:
    """Results from a single benchmark run"""
    name: str
    duration: float  # seconds
    memory_peak: float  # MB
    memory_avg: float  # MB
    cpu_percent: float
    iterations: int
    throughput: float  # items/second
    timestamp: str
    metadata: Dict[str, Any] = None


class BenchmarkSuite:
    """
    Comprehensive benchmarking for OS analysis pipeline
    """

    def __init__(self, output_dir: str = "benchmarks/results"):
        """
        Initialize benchmark suite

        Args:
            output_dir: Directory to save benchmark results
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: List[BenchmarkResult] = []

    def benchmark_function(
        self,
        func: Callable,
        args: tuple = (),
        kwargs: dict = None,
        iterations: int = 10,
        warmup: int = 2,
        name: Optional[str] = None
    ) -> BenchmarkResult:
        """
        Benchmark a single function

        Args:
            func: Function to benchmark
            args: Function arguments
            kwargs: Function keyword arguments
            iterations: Number of iterations to run
            warmup: Number of warmup iterations
            name: Benchmark name

        Returns:
            Benchmark results
        """
        if kwargs is None:
            kwargs = {}

        if name is None:
            name = func.__name__

        print(f"Benchmarking: {name}")

        # Warmup runs
        for _ in range(warmup):
            func(*args, **kwargs)

        # Actual benchmark
        durations = []
        memory_peaks = []
        cpu_percents = []

        for i in range(iterations):
            # Start memory tracking
            tracemalloc.start()
            process = psutil.Process()
            cpu_start = process.cpu_percent()

            # Run function
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()

            # Collect metrics
            duration = end_time - start_time
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            durations.append(duration)
            memory_peaks.append(peak / 1024 / 1024)  # Convert to MB
            cpu_percents.append(process.cpu_percent() - cpu_start)

            print(f"  Iteration {i+1}/{iterations}: {duration:.3f}s")

        # Calculate statistics
        avg_duration = statistics.mean(durations)
        throughput = iterations / sum(durations) if sum(durations) > 0 else 0

        result = BenchmarkResult(
            name=name,
            duration=avg_duration,
            memory_peak=max(memory_peaks),
            memory_avg=statistics.mean(memory_peaks),
            cpu_percent=statistics.mean(cpu_percents),
            iterations=iterations,
            throughput=throughput,
            timestamp=datetime.now().isoformat(),
            metadata={
                "durations": durations,
                "memory_peaks": memory_peaks,
                "std_dev": statistics.stdev(durations) if len(durations) > 1 else 0,
            }
        )

        self.results.append(result)
        return result

    def benchmark_parallel_scaling(
        self,
        func: Callable,
        args: tuple = (),
        max_workers_list: List[int] = None
    ) -> Dict[int, BenchmarkResult]:
        """
        Benchmark parallel scaling efficiency

        Args:
            func: Function to benchmark
            args: Function arguments
            max_workers_list: List of worker counts to test

        Returns:
            Results for each worker count
        """
        if max_workers_list is None:
            max_workers_list = [1, 2, 4, 8, 16]

        results = {}

        for workers in max_workers_list:
            print(f"\nTesting with {workers} workers")

            executor = ParallelExecutor(max_workers=workers)

            # Create test tasks
            tasks = [
                AnalysisTask(
                    name=f"task_{i}",
                    function=func,
                    args=args,
                    priority=i
                )
                for i in range(workers * 4)  # 4 tasks per worker
            ]

            # Benchmark execution
            result = self.benchmark_function(
                executor.execute_tasks,
                args=(tasks,),
                iterations=5,
                name=f"parallel_{workers}_workers"
            )

            results[workers] = result

        return results

    def benchmark_cache_performance(
        self,
        analyzer_func: Callable,
        test_data: Any,
        cache_sizes: List[int] = None
    ) -> Dict[str, BenchmarkResult]:
        """
        Benchmark cache hit/miss performance

        Args:
            analyzer_func: Analysis function to test
            test_data: Test data for analysis
            cache_sizes: Cache sizes to test

        Returns:
            Results for cache vs no-cache scenarios
        """
        if cache_sizes is None:
            cache_sizes = [0, 100, 1000, 10000]

        results = {}

        for cache_size in cache_sizes:
            # Configure cache
            cache_name = f"cache_size_{cache_size}" if cache_size > 0 else "no_cache"

            # Benchmark with this cache configuration
            result = self.benchmark_function(
                analyzer_func,
                args=(test_data,),
                kwargs={"cache_size": cache_size},
                iterations=10,
                name=cache_name
            )

            results[cache_name] = result

        return results

    def benchmark_file_operations(
        self,
        file_paths: List[Path],
        read_func: Callable
    ) -> BenchmarkResult:
        """
        Benchmark file I/O operations

        Args:
            file_paths: Files to read
            read_func: Function to read files

        Returns:
            Benchmark results
        """
        def read_all_files():
            results = []
            for path in file_paths:
                results.append(read_func(path))
            return results

        return self.benchmark_function(
            read_all_files,
            iterations=5,
            name=f"file_io_{len(file_paths)}_files"
        )

    def compare_implementations(
        self,
        implementations: Dict[str, Callable],
        test_data: Any
    ) -> pd.DataFrame:
        """
        Compare multiple implementations

        Args:
            implementations: Dict of name -> function
            test_data: Test data for all implementations

        Returns:
            Comparison DataFrame
        """
        comparison_results = []

        for name, func in implementations.items():
            result = self.benchmark_function(
                func,
                args=(test_data,),
                iterations=10,
                name=name
            )

            comparison_results.append({
                "Implementation": name,
                "Avg Duration (s)": result.duration,
                "Memory Peak (MB)": result.memory_peak,
                "Throughput (ops/s)": result.throughput,
                "CPU %": result.cpu_percent,
            })

        return pd.DataFrame(comparison_results)

    def visualize_results(self, save_path: Optional[str] = None):
        """
        Create visualization of benchmark results

        Args:
            save_path: Optional path to save figure
        """
        if not self.results:
            print("No results to visualize")
            return

        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle("Benchmark Results", fontsize=16)

        # Duration comparison
        names = [r.name for r in self.results]
        durations = [r.duration for r in self.results]

        axes[0, 0].bar(names, durations)
        axes[0, 0].set_title("Average Duration")
        axes[0, 0].set_xlabel("Benchmark")
        axes[0, 0].set_ylabel("Time (seconds)")
        axes[0, 0].tick_params(axis='x', rotation=45)

        # Memory usage
        memory_peaks = [r.memory_peak for r in self.results]
        axes[0, 1].bar(names, memory_peaks, color='orange')
        axes[0, 1].set_title("Peak Memory Usage")
        axes[0, 1].set_xlabel("Benchmark")
        axes[0, 1].set_ylabel("Memory (MB)")
        axes[0, 1].tick_params(axis='x', rotation=45)

        # Throughput
        throughputs = [r.throughput for r in self.results]
        axes[1, 0].bar(names, throughputs, color='green')
        axes[1, 0].set_title("Throughput")
        axes[1, 0].set_xlabel("Benchmark")
        axes[1, 0].set_ylabel("Operations/second")
        axes[1, 0].tick_params(axis='x', rotation=45)

        # CPU usage
        cpu_percents = [r.cpu_percent for r in self.results]
        axes[1, 1].bar(names, cpu_percents, color='red')
        axes[1, 1].set_title("CPU Usage")
        axes[1, 1].set_xlabel("Benchmark")
        axes[1, 1].set_ylabel("CPU %")
        axes[1, 1].tick_params(axis='x', rotation=45)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)
            print(f"Figure saved to {save_path}")

        plt.show()

    def save_results(self, filename: Optional[str] = None):
        """
        Save benchmark results to JSON

        Args:
            filename: Output filename (default: timestamp-based)
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_results_{timestamp}.json"

        filepath = self.output_dir / filename

        results_dict = {
            "timestamp": datetime.now().isoformat(),
            "results": [asdict(r) for r in self.results],
            "summary": self._generate_summary(),
        }

        with open(filepath, 'w') as f:
            json.dump(results_dict, f, indent=2)

        print(f"Results saved to {filepath}")

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics"""
        if not self.results:
            return {}

        durations = [r.duration for r in self.results]
        memories = [r.memory_peak for r in self.results]

        return {
            "total_benchmarks": len(self.results),
            "total_duration": sum(durations),
            "avg_duration": statistics.mean(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "avg_memory": statistics.mean(memories),
            "max_memory": max(memories),
        }

    def generate_report(self) -> str:
        """
        Generate a text report of benchmark results

        Returns:
            Formatted report string
        """
        report = ["=" * 60]
        report.append("BENCHMARK REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")

        summary = self._generate_summary()
        if summary:
            report.append("SUMMARY")
            report.append("-" * 40)
            for key, value in summary.items():
                if isinstance(value, float):
                    report.append(f"{key}: {value:.3f}")
                else:
                    report.append(f"{key}: {value}")
            report.append("")

        report.append("DETAILED RESULTS")
        report.append("-" * 40)

        for result in self.results:
            report.append(f"\nBenchmark: {result.name}")
            report.append(f"  Duration: {result.duration:.3f}s")
            report.append(f"  Memory Peak: {result.memory_peak:.2f} MB")
            report.append(f"  Throughput: {result.throughput:.2f} ops/s")
            report.append(f"  CPU Usage: {result.cpu_percent:.1f}%")

            if result.metadata and "std_dev" in result.metadata:
                report.append(f"  Std Dev: {result.metadata['std_dev']:.3f}s")

        report.append("")
        report.append("=" * 60)

        return "\n".join(report)


def run_standard_benchmarks():
    """Run standard benchmark suite"""
    suite = BenchmarkSuite()

    # Example benchmark functions
    def sample_analysis(size: int):
        """Sample analysis function"""
        import time
        time.sleep(0.01)  # Simulate work
        return {"size": size, "result": size * 2}

    # Benchmark single function
    print("Running single function benchmark...")
    result1 = suite.benchmark_function(
        sample_analysis,
        args=(1000,),
        iterations=10,
        name="sample_analysis"
    )

    # Benchmark parallel scaling
    print("\nRunning parallel scaling benchmark...")
    scaling_results = suite.benchmark_parallel_scaling(
        sample_analysis,
        args=(100,),
        max_workers_list=[1, 2, 4, 8]
    )

    # Generate report
    report = suite.generate_report()
    print("\n" + report)

    # Save results
    suite.save_results()

    # Visualize
    suite.visualize_results(save_path="benchmarks/results/benchmark_plot.png")


if __name__ == "__main__":
    run_standard_benchmarks()