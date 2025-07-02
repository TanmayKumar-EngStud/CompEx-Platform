"""
Generation Exception Classes.

This module defines custom exception classes for the question generation system,
providing specific error types for different failure modes.
"""

import time
from typing import Optional


class QGenBaseException(Exception):
    """Base exception for all QGen-related errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message)
        self.error_code = error_code
        self.timestamp = time.time()


class QuestionGenerationException(QGenBaseException):
    """Raised when question generation fails."""
    pass


class PromptGenerationException(QGenBaseException):
    """Raised when prompt generation fails."""
    pass


class PromptValidationException(QGenBaseException):
    """Raised when prompt validation fails."""
    pass


class MockGenerationException(QGenBaseException):
    """Raised when mock paper generation fails."""
    pass


class ConfigurationException(QGenBaseException):
    """Raised when configuration is invalid."""
    pass