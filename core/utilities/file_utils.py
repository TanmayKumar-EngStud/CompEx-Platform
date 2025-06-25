"""
File utility functions for the question generation system.

This module provides centralized file operations including JSON file
handling, path management, and file system utilities.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Union


def load_json_file(file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
    """
    Load JSON data from a file with error handling.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Loaded JSON data or None if loading fails
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON decode error in {file_path}: {str(e)}")
        return None
    except Exception as e:
        print(f"Error loading file {file_path}: {str(e)}")
        return None


def save_json_file(data: Dict[str, Any], file_path: Union[str, Path], 
                   indent: int = 2, ensure_dir: bool = True) -> bool:
    """
    Save data to a JSON file with error handling.
    
    Args:
        data: Data to save
        file_path: Path to save the file
        indent: JSON indentation level
        ensure_dir: Whether to create directories if they don't exist
        
    Returns:
        True if successful, False otherwise
    """
    try:
        file_path = Path(file_path)
        
        if ensure_dir:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Error saving file {file_path}: {str(e)}")
        return False


def load_text_file(file_path: Union[str, Path]) -> Optional[str]:
    """
    Load text content from a file.
    
    Args:
        file_path: Path to the text file
        
    Returns:
        File content as string or None if loading fails
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except Exception as e:
        print(f"Error loading file {file_path}: {str(e)}")
        return None


def save_text_file(content: str, file_path: Union[str, Path], 
                   ensure_dir: bool = True) -> bool:
    """
    Save text content to a file.
    
    Args:
        content: Text content to save
        file_path: Path to save the file
        ensure_dir: Whether to create directories if they don't exist
        
    Returns:
        True if successful, False otherwise
    """
    try:
        file_path = Path(file_path)
        
        if ensure_dir:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"Error saving file {file_path}: {str(e)}")
        return False


def ensure_directory_exists(dir_path: Union[str, Path]) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        dir_path: Path to the directory
        
    Returns:
        True if directory exists or was created successfully
    """
    try:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory {dir_path}: {str(e)}")
        return False


def get_project_root() -> Path:
    """
    Get the project root directory.
    
    Returns:
        Path to the project root
    """
    # Assume this file is in core/utilities/, so project root is two levels up
    return Path(__file__).parent.parent.parent


def get_data_directory() -> Path:
    """
    Get the data directory path.
    
    Returns:
        Path to the data directory
    """
    return get_project_root() / "data"


def get_config_directory() -> Path:
    """
    Get the config directory path.
    
    Returns:
        Path to the config directory
    """
    return get_project_root() / "config"


def get_papers_directory() -> Path:
    """
    Get the papers directory path.
    
    Returns:
        Path to the papers directory
    """
    return get_project_root() / "papers"


def find_files_by_pattern(directory: Union[str, Path], pattern: str) -> List[Path]:
    """
    Find files matching a pattern in a directory.
    
    Args:
        directory: Directory to search in
        pattern: Glob pattern to match
        
    Returns:
        List of matching file paths
    """
    try:
        directory = Path(directory)
        return list(directory.glob(pattern))
    except Exception as e:
        print(f"Error finding files in {directory}: {str(e)}")
        return []


def get_file_extension(file_path: Union[str, Path]) -> str:
    """
    Get the file extension from a path.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File extension (without the dot)
    """
    return Path(file_path).suffix.lstrip('.')


def create_backup_filename(file_path: Union[str, Path], suffix: str = "backup") -> Path:
    """
    Create a backup filename for a given file.
    
    Args:
        file_path: Original file path
        suffix: Suffix to add before the extension
        
    Returns:
        Backup file path
    """
    file_path = Path(file_path)
    stem = file_path.stem
    extension = file_path.suffix
    
    return file_path.parent / f"{stem}_{suffix}{extension}"


def list_directory_contents(directory: Union[str, Path], 
                          files_only: bool = False, 
                          dirs_only: bool = False) -> List[Path]:
    """
    List contents of a directory.
    
    Args:
        directory: Directory to list
        files_only: Only return files
        dirs_only: Only return directories
        
    Returns:
        List of paths in the directory
    """
    try:
        directory = Path(directory)
        contents = []
        
        for item in directory.iterdir():
            if files_only and item.is_file():
                contents.append(item)
            elif dirs_only and item.is_dir():
                contents.append(item)
            elif not files_only and not dirs_only:
                contents.append(item)
        
        return sorted(contents)
    except Exception as e:
        print(f"Error listing directory {directory}: {str(e)}")
        return []


def copy_file(source: Union[str, Path], destination: Union[str, Path]) -> bool:
    """
    Copy a file from source to destination.
    
    Args:
        source: Source file path
        destination: Destination file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        import shutil
        
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(source, destination)
        return True
    except Exception as e:
        print(f"Error copying file from {source} to {destination}: {str(e)}")
        return False


def move_file(source: Union[str, Path], destination: Union[str, Path]) -> bool:
    """
    Move a file from source to destination.
    
    Args:
        source: Source file path
        destination: Destination file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        import shutil
        
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.move(source, destination)
        return True
    except Exception as e:
        print(f"Error moving file from {source} to {destination}: {str(e)}")
        return False


def delete_file(file_path: Union[str, Path], safe: bool = True) -> bool:
    """
    Delete a file.
    
    Args:
        file_path: Path to the file to delete
        safe: If True, don't delete if file doesn't exist
        
    Returns:
        True if successful, False otherwise
    """
    try:
        file_path = Path(file_path)
        
        if safe and not file_path.exists():
            return True
        
        file_path.unlink()
        return True
    except Exception as e:
        print(f"Error deleting file {file_path}: {str(e)}")
        return False