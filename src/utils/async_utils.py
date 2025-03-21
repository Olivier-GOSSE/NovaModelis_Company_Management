"""
Async utility module.
This module provides utilities for asynchronous operations.
"""
import asyncio
import concurrent.futures
import functools
import logging
import threading
import time
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union, cast

logger = logging.getLogger(__name__)

# Type variables for better type hinting
T = TypeVar('T')
R = TypeVar('R')

# Thread pool executor for running blocking operations
_thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=10)


def run_in_thread(func: Callable[..., R]) -> Callable[..., concurrent.futures.Future[R]]:
    """
    Decorator for running a function in a separate thread.
    
    Args:
        func: The function to run in a thread.
    
    Returns:
        Decorated function that returns a Future.
    
    Example:
        @run_in_thread
        def my_blocking_function():
            # Function to run in a thread
            pass
            
        future = my_blocking_function()
        result = future.result()  # Wait for the result
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> concurrent.futures.Future[R]:
        return _thread_pool.submit(func, *args, **kwargs)
    
    return wrapper


def run_async(func: Callable[..., R]) -> Callable[..., R]:
    """
    Decorator for running an async function in the current thread.
    
    Args:
        func: The async function to run.
    
    Returns:
        Decorated function that runs the async function and returns its result.
    
    Example:
        @run_async
        async def my_async_function():
            # Async function
            pass
            
        result = my_async_function()  # Run the async function
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> R:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # No event loop in this thread, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(func(*args, **kwargs))
    
    return wrapper


def async_to_sync(func: Callable[..., asyncio.Future[R]]) -> Callable[..., R]:
    """
    Decorator for converting an async function to a sync function.
    
    Args:
        func: The async function to convert.
    
    Returns:
        Decorated function that runs the async function and returns its result.
    
    Example:
        @async_to_sync
        async def my_async_function():
            # Async function
            pass
            
        result = my_async_function()  # Run the async function synchronously
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> R:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # No event loop in this thread, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(func(*args, **kwargs))
    
    return wrapper


def sync_to_async(func: Callable[..., R]) -> Callable[..., asyncio.Future[R]]:
    """
    Decorator for converting a sync function to an async function.
    
    Args:
        func: The sync function to convert.
    
    Returns:
        Decorated async function that runs the sync function in a thread pool.
    
    Example:
        @sync_to_async
        def my_sync_function():
            # Sync function
            pass
            
        await my_sync_function()  # Run the sync function asynchronously
    """
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> R:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            _thread_pool, functools.partial(func, *args, **kwargs)
        )
    
    return wrapper


class AsyncTimer:
    """
    Context manager for measuring execution time of an async block of code.
    
    Example:
        async with AsyncTimer("my_operation"):
            # Async code to measure
            pass
    """
    def __init__(self, name: str, threshold: Optional[float] = None):
        """
        Initialize the timer.
        
        Args:
            name: Name of the operation being timed.
            threshold: Optional threshold in seconds. If the execution time exceeds
                this threshold, a warning is logged.
        """
        self.name = name
        self.threshold = threshold
        self.start_time = 0.0
    
    async def __aenter__(self) -> 'AsyncTimer':
        self.start_time = time.time()
        return self
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        end_time = time.time()
        execution_time = end_time - self.start_time
        
        # Log the execution time
        logger.debug(f"AsyncTimer {self.name}: {execution_time:.6f} seconds")
        
        # Check if execution time exceeds threshold
        if self.threshold is not None and execution_time > self.threshold:
            logger.warning(
                f"AsyncTimer {self.name}: Execution time {execution_time:.6f} seconds "
                f"exceeds threshold {self.threshold:.6f} seconds"
            )


class BackgroundTask:
    """
    Class for running a task in the background.
    
    Example:
        task = BackgroundTask(my_function, args=(1, 2), kwargs={"key": "value"})
        task.start()
        # Do other work
        result = task.get_result()  # Wait for the result
    """
    def __init__(
        self,
        func: Callable[..., R],
        args: Optional[tuple] = None,
        kwargs: Optional[dict] = None,
        daemon: bool = True
    ):
        """
        Initialize the background task.
        
        Args:
            func: The function to run in the background.
            args: Positional arguments to pass to the function.
            kwargs: Keyword arguments to pass to the function.
            daemon: Whether the thread should be a daemon thread.
        """
        self.func = func
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.daemon = daemon
        self.result: Optional[R] = None
        self.exception: Optional[Exception] = None
        self.thread: Optional[threading.Thread] = None
        self.completed = threading.Event()
    
    def _run(self) -> None:
        """
        Run the function and store the result or exception.
        """
        try:
            self.result = self.func(*self.args, **self.kwargs)
        except Exception as e:
            self.exception = e
        finally:
            self.completed.set()
    
    def start(self) -> None:
        """
        Start the background task.
        """
        if self.thread is not None:
            raise RuntimeError("Task already started")
        
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = self.daemon
        self.thread.start()
    
    def is_completed(self) -> bool:
        """
        Check if the task is completed.
        
        Returns:
            True if the task is completed, False otherwise.
        """
        return self.completed.is_set()
    
    def wait(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for the task to complete.
        
        Args:
            timeout: Optional timeout in seconds.
        
        Returns:
            True if the task completed, False if the timeout expired.
        """
        return self.completed.wait(timeout)
    
    def get_result(self, timeout: Optional[float] = None) -> R:
        """
        Get the result of the task.
        
        Args:
            timeout: Optional timeout in seconds.
        
        Returns:
            The result of the task.
        
        Raises:
            TimeoutError: If the timeout expired.
            Exception: If the task raised an exception.
        """
        if not self.wait(timeout):
            raise TimeoutError(f"Task {self.func.__name__} timed out")
        
        if self.exception is not None:
            raise self.exception
        
        return cast(R, self.result)


class AsyncQueue:
    """
    Queue for asynchronous processing.
    
    Example:
        queue = AsyncQueue()
        
        # Producer
        await queue.put(item)
        
        # Consumer
        item = await queue.get()
        await queue.task_done()
    """
    def __init__(self, maxsize: int = 0):
        """
        Initialize the queue.
        
        Args:
            maxsize: Maximum size of the queue. If 0, the queue size is unlimited.
        """
        self.queue = asyncio.Queue(maxsize)
    
    async def put(self, item: Any) -> None:
        """
        Put an item into the queue.
        
        Args:
            item: The item to put into the queue.
        """
        await self.queue.put(item)
    
    async def get(self) -> Any:
        """
        Get an item from the queue.
        
        Returns:
            The item from the queue.
        """
        return await self.queue.get()
    
    async def task_done(self) -> None:
        """
        Indicate that a formerly enqueued task is complete.
        """
        self.queue.task_done()
    
    async def join(self) -> None:
        """
        Block until all items in the queue have been processed.
        """
        await self.queue.join()
    
    def qsize(self) -> int:
        """
        Return the approximate size of the queue.
        
        Returns:
            The approximate size of the queue.
        """
        return self.queue.qsize()
    
    def empty(self) -> bool:
        """
        Return True if the queue is empty, False otherwise.
        
        Returns:
            True if the queue is empty, False otherwise.
        """
        return self.queue.empty()
    
    def full(self) -> bool:
        """
        Return True if the queue is full, False otherwise.
        
        Returns:
            True if the queue is full, False otherwise.
        """
        return self.queue.full()


async def gather_with_concurrency(
    n: int,
    *tasks: asyncio.Future,
    return_exceptions: bool = False
) -> List[Any]:
    """
    Run tasks with a concurrency limit.
    
    Args:
        n: Maximum number of tasks to run concurrently.
        *tasks: Tasks to run.
        return_exceptions: Whether to return exceptions or raise them.
    
    Returns:
        List of results from the tasks.
    """
    semaphore = asyncio.Semaphore(n)
    
    async def run_task(task: asyncio.Future) -> Any:
        async with semaphore:
            return await task
    
    return await asyncio.gather(
        *(run_task(task) for task in tasks),
        return_exceptions=return_exceptions
    )
