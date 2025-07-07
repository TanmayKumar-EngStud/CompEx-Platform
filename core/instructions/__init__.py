"""
Core instruction management system for GMAT/GRE question generation.

This module provides centralized instruction management with caching,
template processing, and exam-specific customization.
"""

from .instruction_manager import InstructionManager
from .instruction_loader import InstructionLoader
from .template_processor import TemplateProcessor

__all__ = [
    'InstructionManager',
    'InstructionLoader', 
    'TemplateProcessor'
]