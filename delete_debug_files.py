#!/usr/bin/env python3
"""
Script to delete all debug files from specified directories.
Clears logs, papers, and system instructions run files.
"""

import os
import shutil
from pathlib import Path

def delete_files_in_directory(directory_path):
    """Delete all files in the specified directory, keeping the directory structure."""
    path = Path(directory_path)
    
    if not path.exists():
        print(f"Directory does not exist: {directory_path}")
        return
    
    if not path.is_dir():
        print(f"Path is not a directory: {directory_path}")
        return
    
    deleted_count = 0
    for item in path.iterdir():
        try:
            if item.is_file():
                item.unlink()
                deleted_count += 1
            elif item.is_dir():
                shutil.rmtree(item)
                deleted_count += 1
        except Exception as e:
            print(f"Error deleting {item}: {e}")
    
    print(f"Deleted {deleted_count} items from {directory_path}")

def main():
    """Main function to delete debug files from all specified directories."""
    directories_to_clean = [
        "logs",
        "papers/GMAT",
        "papers/GRE", 
        "system_instructions/in_the_run/gmat",
        "system_instructions/in_the_run/gre"
    ]
    
    print("Starting cleanup of debug files...")
    
    for directory in directories_to_clean:
        delete_files_in_directory(directory)
    
    print("Cleanup completed!")

if __name__ == "__main__":
    main()