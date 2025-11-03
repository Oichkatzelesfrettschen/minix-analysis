"""
Process pool manager for parallel execution
"""

import multiprocessing as mp
from multiprocessing.pool import AsyncResult
from typing import Optional, Callable, Any, List
import logging

logger = logging.getLogger(__name__)


class ProcessPoolManager:
    """
    Manages a pool of worker processes for parallel execution
    """

    def __init__(self, num_workers: Optional[int] = None):
        """
        Initialize the process pool manager

        Args:
            num_workers: Number of worker processes (default: CPU count)
        """
        self.num_workers = num_workers or mp.cpu_count()
        self.pool: Optional[mp.Pool] = None

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()

    def start(self):
        """Start the process pool"""
        if self.pool is None:
            logger.info(f"Starting process pool with {self.num_workers} workers")
            self.pool = mp.Pool(processes=self.num_workers)

    def stop(self):
        """Stop the process pool"""
        if self.pool is not None:
            logger.info("Stopping process pool")
            self.pool.close()
            self.pool.join()
            self.pool = None

    def map(self, func: Callable, iterable: List[Any]) -> List[Any]:
        """
        Apply function to each item in iterable using parallel workers

        Args:
            func: Function to apply
            iterable: Items to process

        Returns:
            List of results
        """
        if self.pool is None:
            raise RuntimeError("Process pool not started")

        return self.pool.map(func, iterable)

    def map_async(self, func: Callable, iterable: List[Any]) -> AsyncResult:
        """
        Apply function to each item in iterable asynchronously

        Args:
            func: Function to apply
            iterable: Items to process

        Returns:
            AsyncResult object
        """
        if self.pool is None:
            raise RuntimeError("Process pool not started")

        return self.pool.map_async(func, iterable)

    def apply(self, func: Callable, args: tuple = (), kwargs: dict = None) -> Any:
        """
        Apply function with arguments using a worker

        Args:
            func: Function to call
            args: Positional arguments
            kwargs: Keyword arguments

        Returns:
            Function result
        """
        if self.pool is None:
            raise RuntimeError("Process pool not started")

        if kwargs is None:
            kwargs = {}

        return self.pool.apply(func, args, kwargs)

    def apply_async(
        self,
        func: Callable,
        args: tuple = (),
        kwargs: dict = None,
        callback: Optional[Callable] = None
    ) -> AsyncResult:
        """
        Apply function with arguments asynchronously

        Args:
            func: Function to call
            args: Positional arguments
            kwargs: Keyword arguments
            callback: Optional callback for result

        Returns:
            AsyncResult object
        """
        if self.pool is None:
            raise RuntimeError("Process pool not started")

        if kwargs is None:
            kwargs = {}

        return self.pool.apply_async(func, args, kwargs, callback)

    def terminate(self):
        """Immediately terminate all workers"""
        if self.pool is not None:
            logger.warning("Terminating process pool")
            self.pool.terminate()
            self.pool.join()
            self.pool = None