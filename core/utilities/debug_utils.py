"""
Debug Utilities for System Instruction Logging

This module provides utilities for logging system instructions and debug information
to help trace which components are not being properly prepared for question generation.

Author: Claude Code
Date: 2025-07-06
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType


class SystemInstructionDebugger:
    """
    Handles logging of system instructions for debugging purposes.
    
    This class creates debug files in the system_instructions/in_the_run/ directory
    to track what system instructions are being sent to the AI model for each
    question generation attempt.
    """
    
    def __init__(self, base_path: str = "system_instructions/in_the_run"):
        """
        Initialize the debugger.
        
        Args:
            base_path: Base directory for debug files
        """
        self.base_path = Path(base_path)
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure debug directories exist."""
        self.base_path.mkdir(parents=True, exist_ok=True)
        (self.base_path / "gmat").mkdir(exist_ok=True)
        (self.base_path / "gre").mkdir(exist_ok=True)
    
    def log_system_instruction(
        self,
        exam_type: ExamType,
        question_type: QuestionType,
        component_name: str,
        system_instruction: str,
        prompt: str,
        component_system_instruction: str = "",
        response: Optional[str] = None,
        call_priority_index: int = 1
    ) -> str:
        """
        Log system instruction and related debug information.
        
        Args:
            exam_type: GMAT or GRE
            question_type: Type of question being generated
            component_name: Name of the component being generated
            system_instruction: Complete system instruction sent to AI
            prompt: Specific prompt used for generation
            component_system_instruction: System instruction for this specific component
            response: AI response (if any)
            call_priority_index: Order of component call (1, 2, 3, ...)
            
        Returns:
            Path to the debug file created
        """
        exam_dir = self.base_path / exam_type.value.lower()
        
        # Create question type subdirectory
        question_type_dir = exam_dir / question_type.value
        question_type_dir.mkdir(exist_ok=True)
        
        # Create filename with call priority index
        filename = f"{call_priority_index}{component_name}.json"
        filepath = question_type_dir / filename
        
        # Prepare simplified debug data
        debug_data = {
            "prompt_used": prompt,
            "complete_system_instruction": system_instruction,
            "system_instruction_for_component": component_system_instruction,
            "ai_response": response
        }
        
        # Write to file (overwrites existing file)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(debug_data, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def _update_summary_file(
        self,
        exam_type: ExamType,
        question_type: QuestionType,
        component_name: str,
        success: bool,
        error: Optional[str]
    ):
        """Update summary file with generation statistics."""
        summary_file = self.base_path / f"{exam_type.value.lower()}_summary.json"
        
        # Load existing summary or create new one
        if summary_file.exists():
            with open(summary_file, 'r', encoding='utf-8') as f:
                summary = json.load(f)
        else:
            summary = {
                "generation_stats": {},
                "error_patterns": {},
                "last_updated": None
            }
        
        # Update stats
        key = f"{question_type.value}_{component_name}"
        if key not in summary["generation_stats"]:
            summary["generation_stats"][key] = {
                "total_attempts": 0,
                "successful": 0,
                "failed": 0,
                "success_rate": 0.0,
                "last_attempt": None
            }
        
        stats = summary["generation_stats"][key]
        stats["total_attempts"] += 1
        stats["last_attempt"] = datetime.now().isoformat()
        
        if success:
            stats["successful"] += 1
        else:
            stats["failed"] += 1
        
        stats["success_rate"] = (stats["successful"] / stats["total_attempts"]) * 100
        
        # Track error patterns
        if error:
            if error not in summary["error_patterns"]:
                summary["error_patterns"][error] = 0
            summary["error_patterns"][error] += 1
        
        summary["last_updated"] = datetime.now().isoformat()
        
        # Save updated summary
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
    
    def get_recent_failures(self, exam_type: ExamType, limit: int = 10) -> list:
        """
        Get recent failure cases for analysis.
        
        Args:
            exam_type: GMAT or GRE
            limit: Maximum number of failures to return
            
        Returns:
            List of recent failure debug files
        """
        exam_dir = self.base_path / exam_type.value.lower()
        if not exam_dir.exists():
            return []
        
        # Find all debug files
        debug_files = []
        for file in exam_dir.glob("*.json"):
            if file.name.endswith("_summary.json"):
                continue
            
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if not data.get("metadata", {}).get("success", False):
                        debug_files.append({
                            "file": str(file),
                            "data": data,
                            "question_style": data.get("question_style", "unknown"),
                            "last_updated": data.get("metadata", {}).get("last_updated", "NA")
                        })
            except Exception:
                continue
        
        # Sort by last_updated (newest first) and limit
        debug_files.sort(key=lambda x: x["last_updated"], reverse=True)
        return debug_files[:limit]
    
    def cleanup_old_files(self, days_old: int = 7):
        """
        Clean up debug files older than specified days.
        
        Args:
            days_old: Number of days to keep files
        """
        cutoff_time = time.time() - (days_old * 24 * 60 * 60)
        
        for exam_dir in [self.base_path / "gmat", self.base_path / "gre"]:
            if not exam_dir.exists():
                continue
            
            for file in exam_dir.glob("*.json"):
                if file.name.endswith("_summary.json"):
                    continue
                
                if file.stat().st_mtime < cutoff_time:
                    try:
                        file.unlink()
                    except Exception:
                        pass


# Global debugger instance
_debugger = None


def get_debugger() -> SystemInstructionDebugger:
    """Get the global debugger instance."""
    global _debugger
    if _debugger is None:
        _debugger = SystemInstructionDebugger()
    return _debugger


def log_system_instruction(
    exam_type: ExamType,
    question_type: QuestionType,
    component_name: str,
    system_instruction: str,
    prompt: str,
    component_system_instruction: str = "",
    response: Optional[str] = None,
    call_priority_index: int = 1
) -> str:
    """
    Convenience function to log system instruction.
    
    Args:
        exam_type: GMAT or GRE
        question_type: Type of question being generated
        component_name: Name of the component being generated
        system_instruction: Complete system instruction sent to AI
        prompt: Specific prompt used for generation
        component_system_instruction: System instruction for this specific component
        response: AI response (if any)
        call_priority_index: Order of component call (1, 2, 3, ...)
        
    Returns:
        Path to the debug file created
    """
    return get_debugger().log_system_instruction(
        exam_type=exam_type,
        question_type=question_type,
        component_name=component_name,
        system_instruction=system_instruction,
        prompt=prompt,
        component_system_instruction=component_system_instruction,
        response=response,
        call_priority_index=call_priority_index
    )


def get_recent_failures(exam_type: ExamType, limit: int = 10) -> list:
    """Get recent failure cases for analysis."""
    return get_debugger().get_recent_failures(exam_type, limit)


def cleanup_old_debug_files(days_old: int = 7):
    """Clean up old debug files."""
    get_debugger().cleanup_old_files(days_old)