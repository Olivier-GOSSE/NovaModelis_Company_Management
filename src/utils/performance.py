"""
Performance utility module.
This module provides utilities for measuring and optimizing performance.
"""
import time
import logging
import functools
import statistics
from typing import Any, Callable, Dict, List, Optional, TypeVar, cast

logger = logging.getLogger(__name__)

# Type variables for better type hinting
T = TypeVar('T')
R = TypeVar('R')

# Global storage for performance metrics
_performance_metrics: Dict[str, List[float]] = {}


def timeit(func: Callable[..., R]) -> Callable[..., R]:
    """
    Decorator for measuring the execution time of a function.
    
    Args:
        func: The function to measure.
    
    Returns:
        Decorated function that measures execution time.
    
    Example:
        @timeit
        def my_function():
            # Function to measure
            pass
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> R:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Log the execution time
        logger.debug(f"{func.__name__} executed in {execution_time:.6f} seconds")
        
        # Store the execution time for metrics
        func_name = func.__name__
        if func_name not in _performance_metrics:
            _performance_metrics[func_name] = []
        
        _performance_metrics[func_name].append(execution_time)
        
        return result
    
    return wrapper


def profile(
    name: Optional[str] = None,
    threshold: Optional[float] = None
) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """
    Decorator for profiling a function.
    
    Args:
        name: Optional name for the profile. If None, uses the function name.
        threshold: Optional threshold in seconds. If the execution time exceeds
            this threshold, a warning is logged.
    
    Returns:
        Decorated function that profiles execution.
    
    Example:
        @profile(threshold=1.0)
        def my_function():
            # Function to profile
            pass
    """
    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> R:
            profile_name = name or func.__name__
            
            # Start profiling
            start_time = time.time()
            
            # Call the function
            result = func(*args, **kwargs)
            
            # End profiling
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Log the execution time
            logger.debug(f"Profile {profile_name}: {execution_time:.6f} seconds")
            
            # Check if execution time exceeds threshold
            if threshold is not None and execution_time > threshold:
                logger.warning(
                    f"Profile {profile_name}: Execution time {execution_time:.6f} seconds "
                    f"exceeds threshold {threshold:.6f} seconds"
                )
            
            # Store the execution time for metrics
            if profile_name not in _performance_metrics:
                _performance_metrics[profile_name] = []
            
            _performance_metrics[profile_name].append(execution_time)
            
            return result
        
        return wrapper
    
    return decorator


def get_performance_metrics() -> Dict[str, Dict[str, float]]:
    """
    Get performance metrics for all measured functions.
    
    Returns:
        Dictionary of performance metrics for each function.
    """
    metrics: Dict[str, Dict[str, float]] = {}
    
    for func_name, execution_times in _performance_metrics.items():
        if not execution_times:
            continue
        
        metrics[func_name] = {
            "count": len(execution_times),
            "total": sum(execution_times),
            "min": min(execution_times),
            "max": max(execution_times),
            "mean": statistics.mean(execution_times),
            "median": statistics.median(execution_times)
        }
        
        # Calculate standard deviation if there are at least 2 samples
        if len(execution_times) >= 2:
            metrics[func_name]["std_dev"] = statistics.stdev(execution_times)
        
    return metrics


def clear_performance_metrics() -> None:
    """
    Clear all performance metrics.
    """
    global _performance_metrics
    _performance_metrics = {}
    logger.debug("Performance metrics cleared")


class Timer:
    """
    Context manager for measuring execution time of a block of code.
    
    Example:
        with Timer("my_operation"):
            # Code to measure
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
    
    def __enter__(self) -> 'Timer':
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        end_time = time.time()
        execution_time = end_time - self.start_time
        
        # Log the execution time
        logger.debug(f"Timer {self.name}: {execution_time:.6f} seconds")
        
        # Check if execution time exceeds threshold
        if self.threshold is not None and execution_time > self.threshold:
            logger.warning(
                f"Timer {self.name}: Execution time {execution_time:.6f} seconds "
                f"exceeds threshold {self.threshold:.6f} seconds"
            )
        
        # Store the execution time for metrics
        if self.name not in _performance_metrics:
            _performance_metrics[self.name] = []
        
        _performance_metrics[self.name].append(execution_time)


def optimize_imports() -> None:
    """
    Optimize imports by preloading commonly used modules.
    
    This function can be called at application startup to preload
    commonly used modules, reducing import time during runtime.
    """
    import os
    import sys
    import datetime
    import json
    import csv
    import re
    import math
    import random
    import sqlite3
    import threading
    import queue
    import collections
    import itertools
    import functools
    import operator
    import copy
    import pickle
    import hashlib
    import base64
    import uuid
    import tempfile
    import shutil
    import zipfile
    import gzip
    import tarfile
    import io
    import urllib.request
    import urllib.parse
    import urllib.error
    import http.client
    import email
    import smtplib
    import socket
    import ssl
    import xml.etree.ElementTree
    import html
    import webbrowser
    import platform
    import subprocess
    import argparse
    import configparser
    import logging.handlers
    import traceback
    import inspect
    import typing
    import enum
    import dataclasses
    import pathlib
    import contextlib
    import concurrent.futures
    import asyncio
    
    logger.debug("Common modules preloaded")
