"""
System-wide configuration settings.

This module provides configuration classes for system-wide settings that
apply across all exam types and components.
"""

import os
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from pathlib import Path


@dataclass
class SystemConfig:
    """
    System-wide configuration settings.
    
    This class manages global settings that affect the entire question
    generation system, regardless of exam type.
    """
    
    # Database settings
    database_url: Optional[str] = None
    
    # API settings
    api_timeout_seconds: int = 30
    api_max_retries: int = 3
    api_rate_limit_requests_per_minute: int = 9
    
    # File system settings
    project_root: Optional[str] = None
    papers_output_directory: Optional[str] = None
    logs_directory: Optional[str] = None
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    enable_file_logging: bool = True
    max_log_file_size_mb: int = 10
    max_log_files: int = 5
    
    # Threading settings
    max_worker_threads: int = 4
    thread_pool_timeout_seconds: int = 300
    
    # Generation settings
    default_max_retries: int = 3
    default_timeout_seconds: int = 300
    enable_caching: bool = True
    cache_size_limit: int = 1000
    
    # Model settings
    model_name: str = "gemini-1.5-flash"
    enable_thinking_mode: bool = True
    
    def __post_init__(self):
        """Post-initialization setup."""
        # Set default project root if not provided
        if self.project_root is None:
            self.project_root = str(self._get_project_root())
        
        # Set default directories if not provided
        if self.papers_output_directory is None:
            self.papers_output_directory = str(Path(self.project_root) / "papers")
        
        if self.logs_directory is None:
            self.logs_directory = str(Path(self.project_root) / "logs")
    
    def validate(self) -> bool:
        """
        Validate system configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        # Validate positive numeric values
        if (self.api_timeout_seconds <= 0 or 
            self.api_max_retries < 0 or
            self.api_rate_limit_requests_per_minute <= 0):
            return False
        
        if (self.max_worker_threads <= 0 or
            self.thread_pool_timeout_seconds <= 0):
            return False
        
        if (self.default_max_retries < 0 or
            self.default_timeout_seconds <= 0):
            return False
        
        if (self.max_log_file_size_mb <= 0 or
            self.max_log_files <= 0):
            return False
        
        # Validate log level
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.log_level.upper() not in valid_log_levels:
            return False
        
        # Validate paths exist or can be created
        try:
            Path(self.project_root).mkdir(parents=True, exist_ok=True)
            Path(self.papers_output_directory).mkdir(parents=True, exist_ok=True)
            Path(self.logs_directory).mkdir(parents=True, exist_ok=True)
        except Exception:
            return False
        
        return True
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'SystemConfig':
        """
        Create system config from dictionary.
        
        Args:
            config_dict: Dictionary containing configuration values
            
        Returns:
            SystemConfig instance
        """
        return cls(
            database_url=config_dict.get('database_url'),
            api_timeout_seconds=config_dict.get('api_timeout_seconds', 30),
            api_max_retries=config_dict.get('api_max_retries', 3),
            api_rate_limit_requests_per_minute=config_dict.get('api_rate_limit_requests_per_minute', 9),
            project_root=config_dict.get('project_root'),
            papers_output_directory=config_dict.get('papers_output_directory'),
            logs_directory=config_dict.get('logs_directory'),
            log_level=config_dict.get('log_level', 'INFO'),
            log_format=config_dict.get('log_format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            enable_file_logging=config_dict.get('enable_file_logging', True),
            max_log_file_size_mb=config_dict.get('max_log_file_size_mb', 10),
            max_log_files=config_dict.get('max_log_files', 5),
            max_worker_threads=config_dict.get('max_worker_threads', 4),
            thread_pool_timeout_seconds=config_dict.get('thread_pool_timeout_seconds', 300),
            default_max_retries=config_dict.get('default_max_retries', 3),
            default_timeout_seconds=config_dict.get('default_timeout_seconds', 300),
            enable_caching=config_dict.get('enable_caching', True),
            cache_size_limit=config_dict.get('cache_size_limit', 1000),
            model_name=config_dict.get('model_name', 'gemini-1.5-flash'),
            enable_thinking_mode=config_dict.get('enable_thinking_mode', True)
        )
    
    @classmethod
    def from_environment(cls) -> 'SystemConfig':
        """
        Create system config from environment variables.
        
        Returns:
            SystemConfig instance with values from environment
        """
        return cls(
            database_url=os.getenv('DATABASE_URL'),
            api_timeout_seconds=int(os.getenv('API_TIMEOUT_SECONDS', '30')),
            api_max_retries=int(os.getenv('API_MAX_RETRIES', '3')),
            api_rate_limit_requests_per_minute=int(os.getenv('API_RATE_LIMIT_RPM', '9')),
            project_root=os.getenv('PROJECT_ROOT'),
            papers_output_directory=os.getenv('PAPERS_OUTPUT_DIR'),
            logs_directory=os.getenv('LOGS_DIR'),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            log_format=os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            enable_file_logging=os.getenv('ENABLE_FILE_LOGGING', 'true').lower() == 'true',
            max_log_file_size_mb=int(os.getenv('MAX_LOG_FILE_SIZE_MB', '10')),
            max_log_files=int(os.getenv('MAX_LOG_FILES', '5')),
            max_worker_threads=int(os.getenv('MAX_WORKER_THREADS', '4')),
            thread_pool_timeout_seconds=int(os.getenv('THREAD_POOL_TIMEOUT', '300')),
            default_max_retries=int(os.getenv('DEFAULT_MAX_RETRIES', '3')),
            default_timeout_seconds=int(os.getenv('DEFAULT_TIMEOUT_SECONDS', '300')),
            enable_caching=os.getenv('ENABLE_CACHING', 'true').lower() == 'true',
            cache_size_limit=int(os.getenv('CACHE_SIZE_LIMIT', '1000')),
            model_name=os.getenv('MODEL', 'gemini-1.5-flash'),
            enable_thinking_mode=os.getenv('ENABLE_THINKING_MODE', 'true').lower() == 'true'
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dictionary representation of configuration
        """
        return {
            'database_url': self.database_url,
            'api_timeout_seconds': self.api_timeout_seconds,
            'api_max_retries': self.api_max_retries,
            'api_rate_limit_requests_per_minute': self.api_rate_limit_requests_per_minute,
            'project_root': self.project_root,
            'papers_output_directory': self.papers_output_directory,
            'logs_directory': self.logs_directory,
            'log_level': self.log_level,
            'log_format': self.log_format,
            'enable_file_logging': self.enable_file_logging,
            'max_log_file_size_mb': self.max_log_file_size_mb,
            'max_log_files': self.max_log_files,
            'max_worker_threads': self.max_worker_threads,
            'thread_pool_timeout_seconds': self.thread_pool_timeout_seconds,
            'default_max_retries': self.default_max_retries,
            'default_timeout_seconds': self.default_timeout_seconds,
            'enable_caching': self.enable_caching,
            'cache_size_limit': self.cache_size_limit,
            'model_name': self.model_name,
            'enable_thinking_mode': self.enable_thinking_mode
        }
    
    def _get_project_root(self) -> Path:
        """
        Get the project root directory.
        
        Returns:
            Path to the project root
        """
        # Assume this file is in core/config/, so project root is two levels up
        return Path(__file__).parent.parent.parent
    
    def get_papers_path(self) -> Path:
        """
        Get the papers output directory as a Path object.
        
        Returns:
            Path to papers directory
        """
        return Path(self.papers_output_directory)
    
    def get_logs_path(self) -> Path:
        """
        Get the logs directory as a Path object.
        
        Returns:
            Path to logs directory
        """
        return Path(self.logs_directory)
    
    def get_project_root_path(self) -> Path:
        """
        Get the project root directory as a Path object.
        
        Returns:
            Path to project root
        """
        return Path(self.project_root)
    
    def setup_directories(self) -> bool:
        """
        Ensure all required directories exist.
        
        Returns:
            True if all directories were created successfully
        """
        try:
            self.get_project_root_path().mkdir(parents=True, exist_ok=True)
            self.get_papers_path().mkdir(parents=True, exist_ok=True)
            self.get_logs_path().mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directories: {str(e)}")
            return False
    
    def get_log_file_path(self, filename: str = "qgen.log") -> Path:
        """
        Get the full path for a log file.
        
        Args:
            filename: Name of the log file
            
        Returns:
            Full path to the log file
        """
        return self.get_logs_path() / filename
    
    def get_paper_file_path(self, exam_type: str, filename: str) -> Path:
        """
        Get the full path for a paper file.
        
        Args:
            exam_type: Type of exam (gmat, gre)
            filename: Name of the paper file
            
        Returns:
            Full path to the paper file
        """
        return self.get_papers_path() / exam_type / filename
    
    def configure_logging(self) -> None:
        """
        Configure the logging system based on settings.
        """
        import logging
        import logging.handlers
        
        # Set log level
        log_level = getattr(logging, self.log_level.upper(), logging.INFO)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # Clear existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Create formatter
        formatter = logging.Formatter(self.log_format)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # File handler (if enabled)
        if self.enable_file_logging:
            self.setup_directories()
            log_file_path = self.get_log_file_path()
            
            # Use rotating file handler
            file_handler = logging.handlers.RotatingFileHandler(
                log_file_path,
                maxBytes=self.max_log_file_size_mb * 1024 * 1024,
                backupCount=self.max_log_files
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
    
    def get_available_api_keys(self) -> List[int]:
        """
        Get list of available API key indices from environment.
        
        Returns:
            List of available API key indices
        """
        available_keys = []
        for i in range(20):  # Check for up to 20 API keys
            key_name = f"API_{i}"
            if os.getenv(key_name):
                available_keys.append(i)
        
        return available_keys
    
    def has_required_api_keys(self) -> bool:
        """
        Check if at least one API key is available.
        
        Returns:
            True if at least one API key is available
        """
        return len(self.get_available_api_keys()) > 0


# Global system configuration instance
_system_config: Optional[SystemConfig] = None


def get_system_config() -> SystemConfig:
    """
    Get the global system configuration instance.
    
    Returns:
        SystemConfig instance
    """
    global _system_config
    
    if _system_config is None:
        _system_config = SystemConfig.from_environment()
        _system_config.configure_logging()
    
    return _system_config


def set_system_config(config: SystemConfig) -> None:
    """
    Set the global system configuration instance.
    
    Args:
        config: SystemConfig instance to set as global
    """
    global _system_config
    _system_config = config
    config.configure_logging()