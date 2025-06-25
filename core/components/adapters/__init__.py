"""
Exam-Specific Adapters Module

This module provides adapter classes that handle exam-specific differences
while using the unified question components.

Author: Claude Code (Migration CHUNK 2)
Date: 2025-06-25
"""

from .gmat_adapter import GMATAdapter
from .gre_adapter import GREAdapter

__all__ = ['GMATAdapter', 'GREAdapter']