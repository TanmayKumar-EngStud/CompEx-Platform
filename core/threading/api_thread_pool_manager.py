"""
Unified API Thread Pool Manager for the GMAT/GRE Question Generation System.

This module provides a centralized thread pool manager that handles concurrent
question generation with API rate limiting, resource management, and proper
error handling and recovery.
"""

import time
import threading
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from typing import Dict, List, Any, Callable, Optional, Tuple, Union
from dataclasses import asdict

from core.enums.exam_types import ExamType
from .thread_config import ThreadConfig, APIState, PaperStructure
from .exceptions import (
    APIThreadPoolException,
    ThreadExecutionException, 
    APIRateLimitException,
    ThreadPoolShutdownException,
    TaskSubmissionException
)


class APIThreadPoolManager:
    """
    Unified thread pool manager for concurrent question generation.
    
    This class manages multiple API instances with proper rate limiting,
    resource cleanup, and error handling. It supports both GMAT and GRE
    question generation patterns.
    
    Attributes:
        config: Thread pool configuration
        paper: Generated paper data structure
        executor: ThreadPoolExecutor instance
        futures: List of active futures
        api_states: List of API state tracking objects
        locks: List of threading locks for each API
        logger: Logger instance for monitoring
    """
    
    def __init__(self, config: ThreadConfig, paper: Optional[Dict[str, Any]] = None):
        """
        Initialize the thread pool manager.
        
        Args:
            config: Thread pool configuration
            paper: Optional paper structure (will create default if None)
        """
        self.config = config
        self.config.validate()
        
        # Initialize paper structure
        if paper is None:
            paper_structure = PaperStructure(config.exam_type)
            self.paper = paper_structure.create_paper_dict()
        else:
            self.paper = paper
        
        # Thread pool management
        self.executor = ThreadPoolExecutor(
            max_workers=config.max_workers, 
            initializer=self._init_event_loop
        )
        self.futures: List[Future] = []
        
        # API state management
        self.api_states: List[APIState] = []
        self.locks: List[threading.Lock] = []
        self._setup_api_states()
        
        # Logging and monitoring
        self.logger = logging.getLogger(__name__)
        if config.enable_detailed_logging:
            self.logger.setLevel(logging.DEBUG)
        
        # Thread safety
        self._manager_lock = threading.Lock()
        self._shutdown_initiated = False
    
    def _setup_api_states(self) -> None:
        """Initialize API states and locks for each worker thread."""
        for _ in range(self.config.max_workers):
            self.api_states.append(APIState())
            self.locks.append(threading.Lock())
    
    def _init_event_loop(self) -> None:
        """Initialize event loop for asyncio compatibility in worker threads."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        except RuntimeError as e:
            self.logger.warning(f"Could not initialize event loop: {e}")
    
    def add_task(self, task_factory: Callable, *args) -> None:
        """
        Add a task to be executed with the appropriate API state.
        
        This method handles API reuse and ensures tasks are distributed
        across available API instances with proper rate limiting.
        
        Args:
            task_factory: Factory function that creates the task
            *args: Arguments to pass to the task factory
            
        Raises:
            TaskSubmissionException: If task submission fails
            APIThreadPoolException: If thread pool is in invalid state
        """
        if self._shutdown_initiated:
            raise APIThreadPoolException("Cannot add tasks after shutdown initiated")
        
        try:
            task = task_factory(*args)
        except Exception as e:
            raise TaskSubmissionException(f"Task factory failed: {e}") from e
        
        with self._manager_lock:
            self._add_task_internal(task)
    
    def _add_task_internal(self, task: Callable) -> None:
        """Internal task addition logic with proper synchronization."""
        if len(self.futures) < self.config.max_workers:
            # Available slot - create new future
            api_idx = len(self.futures)
            self._submit_new_task(task, api_idx)
        else:
            # All slots busy - wait for completion and reuse
            self._wait_and_reuse_slot(task)
    
    def _submit_new_task(self, task: Callable, api_idx: int) -> None:
        """Submit a new task to an available API slot."""
        try:
            future = self.executor.submit(
                task,
                self.api_states[api_idx],
                self.locks[api_idx],
                api_idx
            )
            self.futures.append(future)
            
            if self.config.enable_detailed_logging:
                self.logger.debug(f"Submitted new task to API {api_idx}")
                
        except Exception as e:
            raise TaskSubmissionException(f"Failed to submit task to API {api_idx}: {e}") from e
    
    def _wait_and_reuse_slot(self, task: Callable) -> None:
        """Wait for a slot to become available and reuse it."""
        # Wait for at least one future to complete
        while not any(f.done() for f in self.futures):
            time.sleep(self.config.task_completion_check_interval)
        
        # Process the first completed future
        for future in as_completed(self.futures):
            try:
                result = future.result()
                api_idx = self._process_completed_task(future, result)
                
                # Submit new task with reused API
                self._submit_reused_task(task, api_idx)
                return
                
            except Exception as e:
                self.logger.error(f"Task execution failed: {e}")
                # Remove failed future and continue
                if future in self.futures:
                    self.futures.remove(future)
                continue
    
    def _process_completed_task(self, future: Future, result: Any) -> int:
        """Process a completed task and update paper structure."""
        self.futures.remove(future)
        
        # Handle different result formats for GMAT vs GRE
        if len(result) == 5:  # GMAT format: [api_idx, start_time, request_count, exam_section, data]
            api_idx, start_time, request_count, exam_section, data = result
            section_key = "section0"
        elif len(result) == 6:  # GRE format: [api_idx, start_time, request_count, exam_section, section_id, data]
            api_idx, start_time, request_count, exam_section, section_id, data = result
            section_key = f"section{section_id}"
        else:
            raise APIThreadPoolException(f"Invalid result format: expected 5 or 6 elements, got {len(result)}")
        
        # Update API state
        api_state = APIState(start_time=start_time, request_count=request_count)
        self.api_states.append(api_state)
        self.locks.append(threading.Lock())
        
        # Store result in paper
        if exam_section in self.paper and section_key in self.paper[exam_section]:
            self.paper[exam_section][section_key].append(data)
        else:
            self.logger.warning(f"Invalid paper structure: {exam_section}.{section_key}")
        
        return api_idx
    
    def _submit_reused_task(self, task: Callable, original_api_idx: int) -> None:
        """Submit a task using a reused API instance."""
        new_api_idx = len(self.api_states) - 1  # Use the most recently added state
        
        try:
            new_future = self.executor.submit(
                task,
                self.api_states[new_api_idx],
                self.locks[new_api_idx],
                original_api_idx  # Maintain original API index for consistency
            )
            self.futures.append(new_future)
            
            if self.config.enable_detailed_logging:
                self.logger.debug(f"Reused API {original_api_idx} for new task")
                
        except Exception as e:
            raise TaskSubmissionException(f"Failed to submit reused task: {e}") from e
    
    def execute_all(self) -> Dict[str, Any]:
        """
        Execute all remaining tasks and collect results.
        
        This method waits for all pending futures to complete and
        processes their results into the paper structure.
        
        Returns:
            Complete paper dictionary with all generated questions
            
        Raises:
            ThreadExecutionException: If task execution fails
            APIThreadPoolException: If thread pool is in invalid state
        """
        if self._shutdown_initiated:
            raise APIThreadPoolException("Cannot execute tasks after shutdown initiated")
        
        try:
            self._execute_remaining_futures()
            return self.paper
        except Exception as e:
            self.logger.error(f"Failed to execute all tasks: {e}")
            raise ThreadExecutionException(f"Task execution failed: {e}") from e
    
    def _execute_remaining_futures(self) -> None:
        """Process all remaining futures and collect their results."""
        completed_count = 0
        total_futures = len(self.futures)
        
        for future in as_completed(self.futures):
            try:
                result = future.result(timeout=self.config.api_timeout_seconds)
                self._process_final_result(result)
                completed_count += 1
                
                if self.config.enable_detailed_logging:
                    self.logger.debug(f"Completed task {completed_count}/{total_futures}")
                    
            except Exception as e:
                self.logger.error(f"Task failed during final execution: {e}")
                # Continue processing other tasks
                continue
    
    def _process_final_result(self, result: Any) -> None:
        """Process a final task result and update paper structure."""
        # Handle different result formats
        if len(result) == 5:  # GMAT format
            api_idx, start_time, request_count, exam_section, data = result
            section_key = "section0"
        elif len(result) == 6:  # GRE format
            api_idx, start_time, request_count, exam_section, section_id, data = result
            section_key = f"section{section_id}"
        else:
            self.logger.warning(f"Unexpected result format: {result}")
            return
        
        # Store result in paper
        if exam_section in self.paper and section_key in self.paper[exam_section]:
            self.paper[exam_section][section_key].append(data)
        else:
            self.logger.warning(f"Invalid paper structure for final result: {exam_section}.{section_key}")
    
    def shutdown(self, wait: bool = True) -> None:
        """
        Shutdown the thread pool executor properly.
        
        Args:
            wait: Whether to wait for running tasks to complete
            
        Raises:
            ThreadPoolShutdownException: If shutdown fails
        """
        with self._manager_lock:
            if self._shutdown_initiated:
                return
            
            self._shutdown_initiated = True
        
        try:
            if wait:
                self.executor.shutdown(wait=True)
                if self.config.enable_detailed_logging:
                    self.logger.info("Thread pool shutdown completed successfully")
            else:
                # Cancel pending futures
                for future in self.futures:
                    if not future.done():
                        future.cancel()
                self.executor.shutdown(wait=False)
                
        except Exception as e:
            raise ThreadPoolShutdownException(f"Thread pool shutdown failed: {e}") from e
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of the thread pool manager.
        
        Returns:
            Dictionary containing current status information
        """
        with self._manager_lock:
            active_futures = sum(1 for f in self.futures if not f.done())
            completed_futures = sum(1 for f in self.futures if f.done())
            
            return {
                "config": asdict(self.config),
                "total_api_instances": len(self.api_states),
                "active_futures": active_futures,
                "completed_futures": completed_futures,
                "total_futures": len(self.futures),
                "shutdown_initiated": self._shutdown_initiated,
                "paper_sections": list(self.paper.keys()) if self.paper else []
            }
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with proper cleanup."""
        self.shutdown(wait=True)