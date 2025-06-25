"""
Threading-specific exceptions for the GMAT/GRE Question Generation System.

This module defines custom exceptions for thread pool operations and API management.
"""

import time
from typing import Optional, Any, Dict


class ThreadingException(Exception):
    """Base exception for all threading-related errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.error_code = error_code
        self.context = context or {}
        self.timestamp = time.time()


class APIThreadPoolException(ThreadingException):
    """Exception raised when API thread pool operations fail."""
    
    def __init__(self, message: str, api_idx: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.api_idx = api_idx


class ThreadExecutionException(ThreadingException):
    """Exception raised when thread execution fails."""
    
    def __init__(self, message: str, thread_id: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.thread_id = thread_id


class APIRateLimitException(ThreadingException):
    """Exception raised when API rate limits are exceeded."""
    
    def __init__(self, message: str, api_idx: Optional[int] = None, retry_after: Optional[float] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.api_idx = api_idx
        self.retry_after = retry_after


class ThreadPoolShutdownException(ThreadingException):
    """Exception raised when thread pool shutdown operations fail."""
    pass


class TaskSubmissionException(ThreadingException):
    """Exception raised when task submission to thread pool fails."""
    
    def __init__(self, message: str, task_name: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.task_name = task_name