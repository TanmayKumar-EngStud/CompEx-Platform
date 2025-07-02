"""
Logging Utilities Module.

This module provides structured logging utilities for the question generation system,
enabling consistent and detailed logging across all components.
"""

import logging
import json
import time
from typing import Dict, Any, Optional

from core.enums.exam_types import ExamType


class StructuredLogger:
    """
    Structured logging utility for consistent logging across the system.
    
    This class provides methods for structured logging with consistent formatting
    and contextual information for debugging and monitoring.
    """
    
    def __init__(self, name: str, level: str = "INFO"):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name/component identifier
            level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Create console handler if none exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_generation_start(self, operation: str, exam_type: ExamType):
        """Log the start of a generation operation."""
        self.logger.info(
            f"Starting {operation}",
            extra={
                "event": "generation_start",
                "operation": operation,
                "exam_type": exam_type.value if isinstance(exam_type, ExamType) else str(exam_type),
                "timestamp": time.time()
            }
        )
    
    def log_generation_success(self, result_data: Dict[str, Any]):
        """Log successful generation completion."""
        self.logger.info(
            "Generation completed successfully",
            extra={
                "event": "generation_success",
                "result": result_data,
                "timestamp": time.time()
            }
        )
    
    def log_generation_error(self, error: Exception, context: Dict[str, Any]):
        """Log generation error with context."""
        self.logger.error(
            f"Generation failed: {str(error)}",
            extra={
                "event": "generation_error",
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context,
                "timestamp": time.time()
            },
            exc_info=True
        )
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log info message."""
        self.logger.info(message, extra=extra)
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log warning message."""
        self.logger.warning(message, extra=extra)
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log error message."""
        self.logger.error(message, extra=extra)
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log debug message."""
        self.logger.debug(message, extra=extra)