#!/usr/bin/env python3
"""
Cleanup script for old system instruction files after CHUNK 6 migration.

This script safely removes duplicate system instruction files that have been
replaced by the unified instruction management system.

Usage:
    python scripts/migration/cleanup_old_instruction_files.py [--dry-run]
"""

import os
import shutil
import argparse
import time
from pathlib import Path
from typing import List, Dict


class InstructionFileCleanup:
    """
    Safe cleanup utility for removing old instruction files.
    """
    
    def __init__(self, dry_run: bool = False):
        """
        Initialize cleanup utility.
        
        Args:
            dry_run: If True, only show what would be deleted without actually deleting
        """
        self.dry_run = dry_run
        self.project_root = Path(__file__).parent.parent.parent
        self.backup_dir = self.project_root / "backup" / f"instructions_backup_{int(time.time())}"
        
        # Files and directories to be removed
        self.old_instruction_paths = [
            # GMAT instruction directories
            "GMAT/Quants/System_instructions",
            "GMAT/Verbal/System_instructions", 
            "GMAT/Integrated_Reasoning/System_instructions",
            
            # GRE instruction directories
            "GRE/Quants/System_instructions",
            "GRE/Verbal/System_Instructions",  # Note: capital I in Instructions
        ]
        
        # Individual files that might exist
        self.old_instruction_files = [
            "GMAT/Quants/System_instructions/GMAT-Quants-Data-Sufficiency-Questions.txt",
            "GMAT/Quants/System_instructions/GMAT-Quants-Simple-Questions.txt",
            "GMAT/Quants/System_instructions/GMAT-Quants-Parent-Child-Questions.txt",
            "GMAT/Verbal/System_instructions/GMAT-Verbal-Simple-Questions.txt",
            "GMAT/Verbal/System_instructions/GMAT-Verbal-Parent-Child-Questions.txt",
            "GMAT/Integrated_Reasoning/System_instructions/Graphic-Interpretation.txt",
            "GMAT/Integrated_Reasoning/System_instructions/Table-Analysis.txt",
            "GMAT/Integrated_Reasoning/System_instructions/Two-Part-Analysis.txt",
            "GMAT/Integrated_Reasoning/System_instructions/Multi-Source-Reasoning.txt",
            "GRE/Quants/System_instructions/GRE-Quants-Data-Sufficiency-Questions.txt",
            "GRE/Quants/System_instructions/GRE-Quants-Simple-Questions.txt",
            "GRE/Quants/System_instructions/GRE-Quants-Parent-Child-Questions.txt",
            "GRE/Quants/System_instructions/GRE-Quants-Numeric-Entry.txt",
            "GRE/Verbal/System_Instructions/GRE-Verbal-Simple-Questions.txt",
            "GRE/Verbal/System_Instructions/GRE-Verbal-Parent-Child-Questions.txt",
            "GRE/Verbal/System_Instructions/GRE-Verbal-SE.txt",
        ]
    
    def validate_new_system(self) -> bool:
        """
        Validate that the new instruction system is in place.
        
        Returns:
            True if new system is properly configured
        """
        required_paths = [
            "system_instructions/templates",
            "system_instructions/gmat/customizations.json",
            "system_instructions/gre/customizations.json",
            "core/instructions/instruction_manager.py",
            "core/instructions/instruction_loader.py",
            "core/instructions/template_processor.py"
        ]
        
        for path in required_paths:
            full_path = self.project_root / path
            if not full_path.exists():
                print(f"❌ Missing required file/directory: {path}")
                return False
        
        print("✅ New instruction system validated")
        return True
    
    def create_backup(self) -> bool:
        """
        Create backup of old instruction files before deletion.
        
        Returns:
            True if backup was successful
        """
        if self.dry_run:
            print(f"[DRY RUN] Would create backup at: {self.backup_dir}")
            return True
        
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created backup directory: {self.backup_dir}")
            
            backed_up_count = 0
            for old_path in self.old_instruction_paths:
                source_path = self.project_root / old_path
                if source_path.exists():
                    backup_path = self.backup_dir / old_path
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copytree(source_path, backup_path, dirs_exist_ok=True)
                    backed_up_count += 1
                    print(f"📋 Backed up: {old_path}")
            
            print(f"✅ Backup completed ({backed_up_count} directories backed up)")
            return True
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False
    
    def scan_old_files(self) -> Dict[str, List[str]]:
        """
        Scan for old instruction files and directories.
        
        Returns:
            Dictionary with existing directories and files
        """
        scan_results = {
            "directories": [],
            "files": []
        }
        
        # Check directories
        for old_path in self.old_instruction_paths:
            full_path = self.project_root / old_path
            if full_path.exists() and full_path.is_dir():
                scan_results["directories"].append(old_path)
        
        # Check individual files
        for old_file in self.old_instruction_files:
            full_path = self.project_root / old_file
            if full_path.exists() and full_path.is_file():
                scan_results["files"].append(old_file)
        
        return scan_results
    
    def remove_old_files(self, scan_results: Dict[str, List[str]]) -> bool:
        """
        Remove old instruction files and directories.
        
        Args:
            scan_results: Results from scan_old_files
            
        Returns:
            True if removal was successful
        """
        if self.dry_run:
            print("\n[DRY RUN] Would remove the following:")
            for directory in scan_results["directories"]:
                print(f"  📁 Directory: {directory}")
            for file_path in scan_results["files"]:
                print(f"  📄 File: {file_path}")
            return True
        
        try:
            removed_count = 0
            
            # Remove directories
            for directory in scan_results["directories"]:
                full_path = self.project_root / directory
                if full_path.exists():
                    shutil.rmtree(full_path)
                    removed_count += 1
                    print(f"🗑️  Removed directory: {directory}")
            
            # Remove individual files (if they exist outside of already removed directories)
            for file_path in scan_results["files"]:
                full_path = self.project_root / file_path
                if full_path.exists():
                    full_path.unlink()
                    removed_count += 1
                    print(f"🗑️  Removed file: {file_path}")
            
            print(f"✅ Cleanup completed ({removed_count} items removed)")
            return True
            
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")
            return False
    
    def run_cleanup(self) -> bool:
        """
        Run the complete cleanup process.
        
        Returns:
            True if cleanup was successful
        """
        print("🧹 Starting old instruction file cleanup...")
        print(f"   Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print(f"   Project root: {self.project_root}")
        
        # Step 1: Validate new system is in place
        if not self.validate_new_system():
            print("❌ Cannot proceed: New instruction system not properly installed")
            return False
        
        # Step 2: Scan for old files
        print("\n🔍 Scanning for old instruction files...")
        scan_results = self.scan_old_files()
        
        total_items = len(scan_results["directories"]) + len(scan_results["files"])
        if total_items == 0:
            print("✅ No old instruction files found - cleanup not needed")
            return True
        
        print(f"📊 Found {total_items} items to clean up:")
        print(f"   Directories: {len(scan_results['directories'])}")
        print(f"   Files: {len(scan_results['files'])}")
        
        # Step 3: Create backup (if not dry run)
        if not self.dry_run:
            print("\n💾 Creating backup...")
            if not self.create_backup():
                print("❌ Cannot proceed: Backup creation failed")
                return False
        
        # Step 4: Remove old files
        print("\n🗑️  Removing old instruction files...")
        if not self.remove_old_files(scan_results):
            return False
        
        # Step 5: Summary
        print(f"\n✅ Cleanup completed successfully!")
        if not self.dry_run:
            print(f"   Backup location: {self.backup_dir}")
        print(f"   Total items processed: {total_items}")
        
        return True


def main():
    """Main entry point for the cleanup script."""
    parser = argparse.ArgumentParser(
        description="Clean up old system instruction files after CHUNK 6 migration"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting anything"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation prompts"
    )
    
    args = parser.parse_args()
    
    # Confirmation prompt (unless dry run or forced)
    if not args.dry_run and not args.force:
        print("⚠️  This will permanently delete old instruction files.")
        print("   A backup will be created before deletion.")
        print("   Make sure the new instruction system is working properly first.")
        
        response = input("\nProceed with cleanup? (yes/no): ").lower().strip()
        if response not in ["yes", "y"]:
            print("❌ Cleanup cancelled")
            return False
    
    # Run cleanup
    cleanup = InstructionFileCleanup(dry_run=args.dry_run)
    success = cleanup.run_cleanup()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())