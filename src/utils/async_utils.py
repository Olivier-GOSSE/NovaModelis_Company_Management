"""
Asynchronous utilities module.
This module provides utilities for asynchronous operations.
"""
import logging
import threading
import functools
import traceback
from typing import Any, Callable, Dict, List, Optional, TypeVar, cast

from PySide6.QtCore import QObject, Signal, QRunnable, QThreadPool, Slot

logger = logging.getLogger(__name__)

# Type variables for better type hinting
T = TypeVar('T')
R = TypeVar('R')

class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    
    Signals:
        started: Signal emitted when the worker starts.
        finished: Signal emitted when the worker finishes.
        error: Signal emitted when an error occurs. Passes the error and traceback.
        result: Signal emitted with the result of the worker.
        progress: Signal emitted to indicate progress (0-100).
    """
    started = Signal()
    finished = Signal()
    error = Signal(Exception, str)
    result = Signal(object)
    progress = Signal(int)


class Worker(QRunnable):
    """
    Worker thread for running tasks asynchronously.
    
    Inherits from QRunnable to handle worker thread setup, signals and wrap-up.
    """
    def __init__(self, fn: Callable, *args: Any, **kwargs: Any):
        """
        Initialize the worker with the function to run and its arguments.
        
        Args:
            fn: The function to run.
            *args: Arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.
        """
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        
        # Add the signals object to the kwargs if the function accepts it
        if 'signals' in self.kwargs:
            self.kwargs['signals'] = self.signals
    
    @Slot()
    def run(self):
        """
        Run the worker function with the provided arguments.
        
        Emits signals for started, result, error, and finished.
        """
        try:
            self.signals.started.emit()
            result = self.fn(*self.args, **self.kwargs)
            self.signals.result.emit(result)
        except Exception as e:
            logger.error(f"Error in worker thread: {str(e)}")
            tb = traceback.format_exc()
            self.signals.error.emit(e, tb)
        finally:
            self.signals.finished.emit()


class AsyncRunner:
    """
    Utility class for running tasks asynchronously.
    
    This class provides methods for running tasks in separate threads
    and handling their results.
    """
    def __init__(self, max_threads: Optional[int] = None):
        """
        Initialize the AsyncRunner with the maximum number of threads.
        
        Args:
            max_threads: Maximum number of threads to use.
                If None, uses the default QThreadPool maximum.
        """
        self.thread_pool = QThreadPool.globalInstance()
        if max_threads is not None:
            self.thread_pool.setMaxThreadCount(max_threads)
        
        logger.debug(f"AsyncRunner initialized with {self.thread_pool.maxThreadCount()} threads")
    
    def run(
        self,
        fn: Callable[..., R],
        *args: Any,
        on_result: Optional[Callable[[R], None]] = None,
        on_error: Optional[Callable[[Exception, str], None]] = None,
        on_finished: Optional[Callable[[], None]] = None,
        on_progress: Optional[Callable[[int], None]] = None,
        **kwargs: Any
    ) -> Worker:
        """
        Run a function asynchronously.
        
        Args:
            fn: The function to run.
            *args: Arguments to pass to the function.
            on_result: Callback for when the function returns a result.
            on_error: Callback for when the function raises an exception.
            on_finished: Callback for when the function finishes (success or error).
            on_progress: Callback for progress updates.
            **kwargs: Keyword arguments to pass to the function.
        
        Returns:
            The worker instance.
        """
        worker = Worker(fn, *args, **kwargs)
        
        if on_result:
            worker.signals.result.connect(on_result)
        if on_error:
            worker.signals.error.connect(on_error)
        if on_finished:
            worker.signals.finished.connect(on_finished)
        if on_progress:
            worker.signals.progress.connect(on_progress)
        
        self.thread_pool.start(worker)
        return worker
    
    def wait_for_finished(self):
        """
        Wait for all tasks to finish.
        """
        self.thread_pool.waitForDone()


# Global instance for convenience
async_runner = AsyncRunner()


def run_async(
    on_result: Optional[Callable[[R], None]] = None,
    on_error: Optional[Callable[[Exception, str], None]] = None,
    on_finished: Optional[Callable[[], None]] = None
) -> Callable[[Callable[..., R]], Callable[..., Worker]]:
    """
    Decorator for running a function asynchronously.
    
    Args:
        on_result: Callback for when the function returns a result.
        on_error: Callback for when the function raises an exception.
        on_finished: Callback for when the function finishes (success or error).
    
    Returns:
        Decorated function that runs asynchronously.
    
    Example:
        @run_async(
            on_result=lambda result: print(f"Result: {result}"),
            on_error=lambda error, tb: print(f"Error: {error}")
        )
        def long_running_task(x, y):
            # Some long running operation
            return x + y
        
        # Call the function asynchronously
        worker = long_running_task(1, 2)
    """
    def decorator(func: Callable[..., R]) -> Callable[..., Worker]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Worker:
            return async_runner.run(
                func,
                *args,
                on_result=on_result,
                on_error=on_error,
                on_finished=on_finished,
                **kwargs
            )
        return wrapper
    return decorator
