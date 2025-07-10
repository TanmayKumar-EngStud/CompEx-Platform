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
from core.enums.question_types import QuestionType


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
    
    # Instruction-related logging methods
    def log_instruction_request(self, exam_type: ExamType, question_type: QuestionType, mode: str):
        """Log instruction loading request."""
        self.logger.debug(
            f"Loading instruction for {exam_type.value} {question_type.value} {mode}",
            extra={
                "event": "instruction_request",
                "exam_type": exam_type.value,
                "question_type": question_type.value,
                "mode": mode,
                "timestamp": time.time()
            }
        )
    
    def log_instruction_success(self, exam_type: ExamType, question_type: QuestionType, mode: str):
        """Log successful instruction loading."""
        self.logger.debug(
            f"Successfully loaded instruction for {exam_type.value} {question_type.value} {mode}",
            extra={
                "event": "instruction_success",
                "exam_type": exam_type.value,
                "question_type": question_type.value,
                "mode": mode,
                "timestamp": time.time()
            }
        )
    
    def log_instruction_error(self, error: Exception, exam_type: ExamType, question_type: QuestionType, mode: str):
        """Log instruction loading error."""
        self.logger.error(
            f"Failed to load instruction for {exam_type.value} {question_type.value} {mode}: {error}",
            extra={
                "event": "instruction_error",
                "exam_type": exam_type.value,
                "question_type": question_type.value,
                "mode": mode,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "timestamp": time.time()
            }
        )
    
    
    def log_template_loaded(self, template_path: str):
        """Log template loading."""
        self.logger.debug(
            f"Template loaded: {template_path}",
            extra={
                "event": "template_loaded",
                "template_path": template_path,
                "timestamp": time.time()
            }
        )
    
    def log_customization_loaded(self, customization_path: str, customization_count: int):
        """Log customization loading."""
        self.logger.debug(
            f"Customizations loaded: {customization_path} ({customization_count} items)",
            extra={
                "event": "customization_loaded",
                "customization_path": customization_path,
                "customization_count": customization_count,
                "timestamp": time.time()
            }
        )
    
    def log_customization_not_found(self, customization_path: str):
        """Log missing customization file."""
        self.logger.warning(
            f"Customization file not found: {customization_path}",
            extra={
                "event": "customization_not_found",
                "customization_path": customization_path,
                "timestamp": time.time()
            }
        )
    
    def log_customization_error(self, error: Exception, customization_path: str):
        """Log customization loading error."""
        self.logger.error(
            f"Failed to load customizations from {customization_path}: {error}",
            extra={
                "event": "customization_error",
                "customization_path": customization_path,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "timestamp": time.time()
            }
        )
    
    def log_legacy_mode_activated(self):
        """Log legacy mode activation."""
        self.logger.info(
            "Legacy instruction mode activated",
            extra={
                "event": "legacy_mode_activated",
                "timestamp": time.time()
            }
        )
    
    def log_legacy_instruction_loaded(self, instruction_path: str):
        """Log legacy instruction loading."""
        self.logger.debug(
            f"Legacy instruction loaded: {instruction_path}",
            extra={
                "event": "legacy_instruction_loaded",
                "instruction_path": instruction_path,
                "timestamp": time.time()
            }
        )
    
    def log_template_processed(self, exam_type: ExamType, question_type: QuestionType):
        """Log template processing completion."""
        self.logger.debug(
            f"Template processed for {exam_type.value} {question_type.value}",
            extra={
                "event": "template_processed",
                "exam_type": exam_type.value,
                "question_type": question_type.value,
                "timestamp": time.time()
            }
        )
    
    def log_template_processing_error(self, error: Exception, exam_type: ExamType, question_type: QuestionType):
        """Log template processing error."""
        self.logger.error(
            f"Template processing failed for {exam_type.value} {question_type.value}: {error}",
            extra={
                "event": "template_processing_error",
                "exam_type": exam_type.value,
                "question_type": question_type.value,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "timestamp": time.time()
            }
        )
    
    
    def log_system_warning(self, message: str):
        """Log system warning."""
        self.logger.warning(
            message,
            extra={
                "event": "system_warning",
                "timestamp": time.time()
            }
        )
    
    def log_system_validation(self, template_count: int):
        """Log system validation results."""
        # self.logger.info(
        #     f"Instruction system validated ({template_count} templates found)",
        #     extra={
        #         "event": "system_validation",
        #         "template_count": template_count,
        #         "timestamp": time.time()
        #     }
        # )
    
    def log_system_error(self, error: Exception):
        """Log system error."""
        self.logger.error(
            f"Instruction system error: {error}",
            extra={
                "event": "system_error",
                "error_type": type(error).__name__,
                "error_message": str(error),
                "timestamp": time.time()
            }
        )
    
    # Graph Style Management Logging Methods
    def log_graph_styles_loaded(self, count: int):
        """Log successful loading of graph styles."""
        # self.logger.info(
        #     f"Graph styles loaded successfully: {count} styles",
        #     extra={
        #         "event": "graph_styles_loaded",
        #         "count": count,
        #         "timestamp": time.time()
        #     }
        # )
    
    def log_graph_styles_error(self, error: Exception, file_path: str):
        """Log graph styles loading error."""
        self.logger.error(
            f"Failed to load graph styles from {file_path}: {error}",
            extra={
                "event": "graph_styles_error",
                "file_path": file_path,
                "error": str(error),
                "timestamp": time.time()
            }
        )
    
    def log_graph_type_parsed(self, graph_type: str, original_text: str):
        """Log successful graph type parsing."""
        self.logger.debug(
            f"Graph type parsed: '{original_text}' -> '{graph_type}'",
            extra={
                "event": "graph_type_parsed",
                "graph_type": graph_type,
                "original_text": original_text,
                "timestamp": time.time()
            }
        )
    
    def log_graph_style_injected(self, graph_type: str, replacements_count: int):
        """Log successful graph style injection."""
        self.logger.info(
            f"Graph style injected: {graph_type} with {replacements_count} replacements",
            extra={
                "event": "graph_style_injected",
                "graph_type": graph_type,
                "replacements_count": replacements_count,
                "timestamp": time.time()
            }
        )
    
    def log_graph_style_not_found(self, graph_type: str):
        """Log when graph style is not found."""
        self.logger.warning(
            f"Graph style not found: {graph_type}",
            extra={
                "event": "graph_style_not_found",
                "graph_type": graph_type,
                "timestamp": time.time()
            }
        )