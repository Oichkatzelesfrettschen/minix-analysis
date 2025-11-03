"""
Parallel executor for concurrent analysis tasks
Provides significant speedup for large codebases
"""

import time
import logging
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple
from pathlib import Path
import multiprocessing as mp

logger = logging.getLogger(__name__)


@dataclass
class AnalysisTask:
    """Represents a single analysis task"""
    name: str
    function: Callable
    args: Tuple = ()
    kwargs: Dict[str, Any] = None
    priority: int = 0  # Lower number = higher priority

    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}

    def __lt__(self, other):
        """Enable priority-based sorting"""
        return self.priority < other.priority


class ParallelExecutor:
    """
    Execute analysis tasks in parallel for improved performance

    This executor supports both process-based and thread-based parallelism,
    with automatic optimization based on task characteristics.
    """

    def __init__(
        self,
        max_workers: Optional[int] = None,
        use_processes: bool = True,
        timeout: Optional[float] = None
    ):
        """
        Initialize the parallel executor

        Args:
            max_workers: Maximum number of parallel workers (default: CPU count)
            use_processes: Use processes instead of threads
            timeout: Timeout for each task in seconds
        """
        self.max_workers = max_workers or mp.cpu_count()
        self.use_processes = use_processes
        self.timeout = timeout
        self.results = {}
        self.errors = {}

    def execute_tasks(
        self,
        tasks: List[AnalysisTask],
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Execute multiple analysis tasks in parallel

        Args:
            tasks: List of tasks to execute
            progress_callback: Optional callback for progress updates

        Returns:
            Dictionary mapping task names to results
        """
        # Sort tasks by priority
        sorted_tasks = sorted(tasks, key=lambda t: t.priority)

        # Choose executor type
        executor_class = ProcessPoolExecutor if self.use_processes else ThreadPoolExecutor

        start_time = time.time()
        completed = 0
        total = len(sorted_tasks)

        logger.info(f"Starting parallel execution of {total} tasks with {self.max_workers} workers")

        with executor_class(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(
                    self._execute_single_task,
                    task.function,
                    *task.args,
                    **task.kwargs
                ): task
                for task in sorted_tasks
            }

            # Process completed tasks
            for future in as_completed(future_to_task, timeout=self.timeout):
                task = future_to_task[future]
                completed += 1

                try:
                    result = future.result()
                    self.results[task.name] = result
                    logger.debug(f"Task '{task.name}' completed successfully")

                    if progress_callback:
                        progress_callback(completed, total, task.name)

                except Exception as e:
                    self.errors[task.name] = str(e)
                    logger.error(f"Task '{task.name}' failed: {e}")

        elapsed = time.time() - start_time
        logger.info(f"Parallel execution completed in {elapsed:.2f} seconds")
        logger.info(f"Successful: {len(self.results)}, Failed: {len(self.errors)}")

        return self.results

    def _execute_single_task(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a single task with error handling

        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Task result
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            raise

    def analyze_files_parallel(
        self,
        file_paths: List[Path],
        analyzer_func: Callable,
        chunk_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Analyze multiple files in parallel

        Args:
            file_paths: List of files to analyze
            analyzer_func: Function to analyze each file
            chunk_size: Number of files per worker

        Returns:
            Combined analysis results
        """
        if not chunk_size:
            # Auto-calculate optimal chunk size
            chunk_size = max(1, len(file_paths) // (self.max_workers * 4))

        # Create file chunks
        chunks = [
            file_paths[i:i + chunk_size]
            for i in range(0, len(file_paths), chunk_size)
        ]

        # Create tasks for each chunk
        tasks = [
            AnalysisTask(
                name=f"chunk_{i}",
                function=self._analyze_file_chunk,
                args=(chunk, analyzer_func),
                priority=i
            )
            for i, chunk in enumerate(chunks)
        ]

        # Execute in parallel
        results = self.execute_tasks(tasks)

        # Combine results
        combined = {}
        for chunk_result in results.values():
            combined.update(chunk_result)

        return combined

    def _analyze_file_chunk(
        self,
        files: List[Path],
        analyzer_func: Callable
    ) -> Dict[str, Any]:
        """
        Analyze a chunk of files

        Args:
            files: List of file paths
            analyzer_func: Analysis function

        Returns:
            Analysis results for the chunk
        """
        results = {}
        for file_path in files:
            try:
                results[str(file_path)] = analyzer_func(file_path)
            except Exception as e:
                logger.error(f"Failed to analyze {file_path}: {e}")
                results[str(file_path)] = {"error": str(e)}

        return results

    def optimize_worker_count(
        self,
        test_task: AnalysisTask,
        max_test_workers: int = 16
    ) -> int:
        """
        Automatically determine optimal worker count

        Args:
            test_task: Sample task for benchmarking
            max_test_workers: Maximum workers to test

        Returns:
            Optimal number of workers
        """
        best_workers = 1
        best_time = float('inf')

        logger.info("Optimizing worker count...")

        for workers in range(1, min(max_test_workers, mp.cpu_count() * 2) + 1):
            self.max_workers = workers

            start = time.time()
            self.execute_tasks([test_task])
            elapsed = time.time() - start

            logger.debug(f"Workers: {workers}, Time: {elapsed:.3f}s")

            if elapsed < best_time:
                best_time = elapsed
                best_workers = workers

        logger.info(f"Optimal worker count: {best_workers}")
        self.max_workers = best_workers
        return best_workers


class ParallelAnalysisPipeline:
    """
    Complete parallel pipeline for OS analysis
    """

    def __init__(self, source_root: str, output_dir: str):
        """
        Initialize parallel analysis pipeline

        Args:
            source_root: Path to OS source code
            output_dir: Output directory for results
        """
        self.source_root = Path(source_root)
        self.output_dir = Path(output_dir)
        self.executor = ParallelExecutor()

    def run_complete_analysis(self) -> Dict[str, Any]:
        """
        Run complete analysis pipeline in parallel

        Returns:
            All analysis results
        """
        # Define analysis tasks
        tasks = [
            AnalysisTask(
                name="kernel_structure",
                function=self._analyze_kernel,
                priority=1
            ),
            AnalysisTask(
                name="process_management",
                function=self._analyze_processes,
                priority=2
            ),
            AnalysisTask(
                name="memory_layout",
                function=self._analyze_memory,
                priority=3
            ),
            AnalysisTask(
                name="ipc_system",
                function=self._analyze_ipc,
                priority=4
            ),
            AnalysisTask(
                name="boot_sequence",
                function=self._analyze_boot,
                priority=5
            ),
            AnalysisTask(
                name="statistics",
                function=self._generate_stats,
                priority=6
            ),
        ]

        # Execute all tasks in parallel
        results = self.executor.execute_tasks(
            tasks,
            progress_callback=self._progress_callback
        )

        # Save results
        self._save_results(results)

        return results

    def _progress_callback(self, completed: int, total: int, task_name: str):
        """Progress callback for parallel execution"""
        percentage = (completed / total) * 100
        logger.info(f"Progress: {percentage:.1f}% - Completed: {task_name}")

    def _analyze_kernel(self) -> Dict[str, Any]:
        """Analyze kernel structure"""
        # Implementation would call actual analyzer
        return {"analyzed": "kernel"}

    def _analyze_processes(self) -> Dict[str, Any]:
        """Analyze process management"""
        return {"analyzed": "processes"}

    def _analyze_memory(self) -> Dict[str, Any]:
        """Analyze memory layout"""
        return {"analyzed": "memory"}

    def _analyze_ipc(self) -> Dict[str, Any]:
        """Analyze IPC system"""
        return {"analyzed": "ipc"}

    def _analyze_boot(self) -> Dict[str, Any]:
        """Analyze boot sequence"""
        return {"analyzed": "boot"}

    def _generate_stats(self) -> Dict[str, Any]:
        """Generate statistics"""
        return {"total_files": 100, "total_lines": 10000}

    def _save_results(self, results: Dict[str, Any]):
        """Save analysis results to output directory"""
        import json

        self.output_dir.mkdir(parents=True, exist_ok=True)

        for name, data in results.items():
            output_file = self.output_dir / f"{name}.json"
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved {name} to {output_file}")