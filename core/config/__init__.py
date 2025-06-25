"""
Configuration module for centralized settings management.

This module provides configuration classes and utilities for managing
exam-specific and system-wide settings in a type-safe manner.
"""

from .exam_config import BaseExamConfig
from .system_config import SystemConfig

__all__ = [
    "BaseExamConfig",
    "SystemConfig"
]