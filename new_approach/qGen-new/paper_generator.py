"""
Paper Generation Module
Aggregates generated questions and saves them to JSON files organized by exam.
"""

import json
import os
from typing import Dict, List, Any
from datetime import datetime


def count_questions(questions: List[Dict[str, Any]]) -> int:
    """
    Count total questions excluding parent questions.
    Counts child questions within parent questions.
    """
    total = 0
    for q in questions:
        if 'child-questions' in q:
            # It's a parent question - count only children
            total += len(q['child-questions'])
        else:
            # It's a simple question
            total += 1
    return total


def save_paper(exam: str, sections_data: Dict[str, List[Dict]], model_used: str, 
               total_time: float, output_dir: str = None) -> str:
    """
    Save generated paper to JSON file.
    
    Args:
        exam: Exam name (e.g., 'GRE', 'GMAT')
        sections_data: Dict mapping section names to lists of questions
        model_used: Name of the model used for generation
        total_time: Total time taken in seconds
        output_dir: Directory to save papers (defaults to log_json_files/paper)
    
    Returns:
        Relative path to saved file
    """
    if output_dir is None:
        output_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'log_json_files',
            'paper'
        )
    
    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Count total questions
    total_questions = sum(count_questions(questions) for questions in sections_data.values())
    
    # Build paper structure
    paper = {
        "exam": exam,
        "sections": sections_data,
        "metadata": {
            "total_questions": total_questions,
            "generation_datetime": datetime.now().isoformat(),
            "generation_time_seconds": round(total_time, 2),
            "model_used": model_used
        }
    }
    
    # Save to file
    filepath = os.path.join(output_dir, f"{exam}.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(paper, f, indent=2, ensure_ascii=False)
    
    # Return relative path
    rel_path = os.path.relpath(filepath, os.path.dirname(os.path.abspath(__file__)))
    return rel_path
