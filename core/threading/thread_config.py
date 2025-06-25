"""
Thread configuration for the GMAT/GRE Question Generation System.

This module provides configuration classes for thread pool management
and API state handling.
"""

import time
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from core.enums.exam_types import ExamType


@dataclass
class APIState:
    """Tracks the state of an individual API instance."""
    
    start_time: float = field(default_factory=time.time)
    request_count: int = 0
    last_request_time: Optional[float] = None
    is_rate_limited: bool = False
    rate_limit_reset_time: Optional[float] = None
    
    def reset_request_count(self) -> None:
        """Reset the request count and start time."""
        self.start_time = time.time()
        self.request_count = 0
        self.last_request_time = None
    
    def increment_request_count(self) -> None:
        """Increment the request count and update last request time."""
        self.request_count += 1
        self.last_request_time = time.time()
    
    def set_rate_limited(self, reset_time: Optional[float] = None) -> None:
        """Mark this API as rate limited."""
        self.is_rate_limited = True
        self.rate_limit_reset_time = reset_time
    
    def clear_rate_limit(self) -> None:
        """Clear rate limit status."""
        self.is_rate_limited = False
        self.rate_limit_reset_time = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for backward compatibility."""
        return {
            "start_time": self.start_time,
            "request_count": self.request_count
        }


@dataclass 
class ThreadConfig:
    """Configuration for thread pool behavior."""
    
    # Basic thread pool settings
    max_workers: int = 8
    exam_type: ExamType = ExamType.GMAT
    
    # API management settings
    max_requests_per_minute: int = 60
    api_timeout_seconds: float = 30.0
    request_delay_seconds: float = 1.0
    
    # Retry settings
    max_retries: int = 3
    retry_delay_seconds: float = 2.0
    exponential_backoff: bool = True
    
    # Resource management
    shutdown_wait_timeout: float = 30.0
    task_completion_check_interval: float = 0.5
    
    # Logging and monitoring
    enable_detailed_logging: bool = False
    log_api_timing: bool = False
    monitor_resource_usage: bool = False
    
    def validate(self) -> bool:
        """Validate configuration values."""
        if self.max_workers <= 0:
            raise ValueError("max_workers must be positive")
        
        if self.max_requests_per_minute <= 0:
            raise ValueError("max_requests_per_minute must be positive")
        
        if self.api_timeout_seconds <= 0:
            raise ValueError("api_timeout_seconds must be positive")
        
        if self.max_retries < 0:
            raise ValueError("max_retries cannot be negative")
        
        if self.request_delay_seconds < 0:
            raise ValueError("request_delay_seconds cannot be negative")
        
        return True
    
    @classmethod
    def create_gmat_config(cls, max_workers: int = 8, **kwargs) -> 'ThreadConfig':
        """Create configuration optimized for GMAT question generation."""
        return cls(
            max_workers=max_workers,
            exam_type=ExamType.GMAT,
            max_requests_per_minute=50,  # Conservative for GMAT's longer questions
            api_timeout_seconds=45.0,    # Longer timeout for complex IR questions
            **kwargs
        )
    
    @classmethod
    def create_gre_config(cls, max_workers: int = 8, **kwargs) -> 'ThreadConfig':
        """Create configuration optimized for GRE question generation."""
        return cls(
            max_workers=max_workers,
            exam_type=ExamType.GRE,
            max_requests_per_minute=60,  # Standard rate for GRE
            api_timeout_seconds=30.0,    # Standard timeout
            **kwargs
        )
    
    @classmethod
    def create_development_config(cls, **kwargs) -> 'ThreadConfig':
        """Create configuration for development/testing."""
        return cls(
            max_workers=2,
            max_requests_per_minute=10,
            api_timeout_seconds=60.0,
            enable_detailed_logging=True,
            log_api_timing=True,
            monitor_resource_usage=True,
            **kwargs
        )


@dataclass
class PaperStructure:
    """Defines the structure of generated papers for different exam types."""
    
    exam_type: ExamType
    sections: Dict[str, List[str]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize default section structure based on exam type."""
        if not self.sections:
            if self.exam_type == ExamType.GMAT:
                self.sections = {
                    "GMAT_Q": ["section0"],
                    "GMAT_V": ["section0"],
                    "GMAT_IR": ["section0"]
                }
            elif self.exam_type == ExamType.GRE:
                self.sections = {
                    "GRE_Q": ["section1", "section2"],
                    "GRE_V": ["section1", "section2"]
                }
    
    def create_paper_dict(self) -> Dict[str, Dict[str, List[Any]]]:
        """Create empty paper dictionary with proper structure."""
        paper = {}
        for section_name, subsections in self.sections.items():
            paper[section_name] = {}
            for subsection in subsections:
                paper[section_name][subsection] = []
        return paper
    
    def validate_section(self, section_name: str, subsection: str) -> bool:
        """Validate that a section and subsection exist in the structure."""
        return (section_name in self.sections and 
                subsection in self.sections[section_name])