"""
API utility functions for the question generation system.

This module provides centralized API management capabilities including
key rotation, rate limiting, and request handling.
"""

import os
import time
import threading
from typing import Dict, Any, Optional, List
from google import genai


def get_api_key(index: int) -> str:
    """
    Get API key by index from environment variables.
    
    Args:
        index: Index of the API key (e.g., 0 for API_0, 1 for API_1)
        
    Returns:
        API key string
        
    Raises:
        ValueError: If API key is not found or invalid
    """
    key_name = f"API_{index}"
    api_key = os.getenv(key_name)
    
    if not api_key:
        raise ValueError(f"API key {key_name} not found in environment variables")
    
    if not _validate_api_key_format(api_key):
        raise ValueError(f"Invalid API key format for {key_name}")
    
    return api_key


def _validate_api_key_format(api_key: str) -> bool:
    """
    Validate API key format.
    
    Args:
        api_key: API key to validate
        
    Returns:
        True if valid format, False otherwise
    """
    # Basic validation for Google Gemini API keys
    return len(api_key) > 20 and isinstance(api_key, str)


def rotate_api_key(current_index: int, max_keys: int = 10) -> int:
    """
    Rotate to the next available API key index.
    
    Args:
        current_index: Current API key index
        max_keys: Maximum number of API keys available
        
    Returns:
        Next API key index
    """
    return (current_index + 1) % max_keys


def get_available_api_keys() -> List[int]:
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


def create_api_client(api_key: str) -> genai.Client:
    """
    Create a Google Gemini API client with the given key.
    
    Args:
        api_key: API key for authentication
        
    Returns:
        Configured Gemini client
        
    Raises:
        Exception: If client creation fails
    """
    try:
        # Configure the API key
        genai.configure(api_key=api_key)
        return genai
    except Exception as e:
        raise Exception(f"Failed to create API client: {str(e)}")


class RateLimitManager:
    """
    Manages API rate limiting to prevent exceeding quota limits.
    """
    
    def __init__(self, requests_per_minute: int = 9):
        """
        Initialize rate limit manager.
        
        Args:
            requests_per_minute: Maximum requests per minute (default: 9 for safety)
        """
        self.requests_per_minute = requests_per_minute
        self.request_count = 0
        self.start_time = time.time()
        self.lock = threading.Lock()
    
    def wait_if_needed(self) -> None:
        """
        Wait if rate limit would be exceeded.
        """
        with self.lock:
            current_time = time.time()
            elapsed = current_time - self.start_time
            
            # Reset window if more than 60 seconds have passed
            if elapsed >= 60:
                self.start_time = current_time
                self.request_count = 0
                elapsed = 0
            
            # Check if we're at the limit
            if self.request_count >= self.requests_per_minute:
                wait_time = 60 - elapsed + 1  # Add 1 second buffer
                if wait_time > 0:
                    print(f"Rate limit safety: waiting {wait_time:.1f}s "
                          f"(requests: {self.request_count}, elapsed: {elapsed:.1f}s)")
                    time.sleep(wait_time)
                    # Reset after waiting
                    self.start_time = time.time()
                    self.request_count = 0
            
            # Increment request count
            self.request_count += 1
    
    def reset_on_error(self) -> None:
        """
        Reset rate limiting state after an error, with extra buffer.
        """
        with self.lock:
            current_time = time.time()
            elapsed = current_time - self.start_time
            if elapsed < 60:
                wait_time = 60 - elapsed + 2  # Extra buffer on error
                time.sleep(wait_time)
            self.start_time = time.time()
            self.request_count = 0


class APIRequestHandler:
    """
    Handles API requests with retry logic and error handling.
    """
    
    def __init__(self, rate_limit_manager: Optional[RateLimitManager] = None):
        """
        Initialize API request handler.
        
        Args:
            rate_limit_manager: Rate limit manager instance
        """
        self.rate_limit_manager = rate_limit_manager or RateLimitManager()
        self.max_retries = 3
    
    def make_request(self, chat_instance, prompt: str, warn: bool = False) -> Optional[str]:
        """
        Make an API request with rate limiting and error handling.
        
        Args:
            chat_instance: Gemini chat instance
            prompt: Prompt to send
            warn: Whether to append warning message
            
        Returns:
            Response text or None if failed
        """
        from .json_utils import JSON_ERROR_WARNING
        
        if warn:
            prompt += f", {JSON_ERROR_WARNING}"
        
        # Apply rate limiting
        self.rate_limit_manager.wait_if_needed()
        
        try:
            response = chat_instance.send_message(prompt)
            return response.text
        except Exception as e:
            print(f"API request failed: {str(e)}")
            print(f"Prompt: {prompt}")
            
            # Reset rate limiting state on error
            self.rate_limit_manager.reset_on_error()
            return None
    
    def retry_request(self, func, *args, **kwargs) -> Any:
        """
        Retry a function with exponential backoff.
        
        Args:
            func: Function to retry
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or None if all retries failed
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                result = func(*args, warn=(attempt > 0), **kwargs)
                if result:  # If we got any non-None result, return it
                    return result
                print(f"\n🔄 RETRY - APIUtils.{func.__name__} - attempt {attempt + 1}/{self.max_retries}")
                print(f"   Reason: Function returned None/empty result")
            except Exception as e:
                last_error = str(e)
                print(f"\n❌ ERROR - APIUtils.{func.__name__} - attempt {attempt + 1}/{self.max_retries}")
                print(f"   Error: {last_error}")
                
                # Wait before retry with exponential backoff
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"   Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
        
        # If we get here, all attempts failed
        print(f"\n💥 FAILED - APIUtils.{func.__name__} - All {self.max_retries} attempts failed")
        if last_error:
            print(f"   Final error: {last_error}")
        return None


def get_model_name() -> str:
    """
    Get the model name from environment variables.
    
    Returns:
        Model name string
    """
    return os.getenv("MODEL", "gemini-1.5-flash")


def create_chat_instance(api_client, system_instructions: str, thinking_enabled: bool = True):
    """
    Create a chat instance with the given configuration.
    
    Args:
        api_client: Configured API client
        system_instructions: System instruction text
        thinking_enabled: Whether to enable thinking mode
        
    Returns:
        Configured chat instance
    """
    from google.genai import types
    
    config = types.GenerateContentConfig(
        system_instruction=system_instructions
    )
    
    if thinking_enabled:
        config.thinking_config = types.ThinkingConfig(include_thoughts=True)
    
    return api_client.chats.create(
        model=get_model_name(),
        config=config
    )