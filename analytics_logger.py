"""
Analytics Logger Module
Logs generation metrics to CSV file for tracking performance over time.
"""

import csv
import os
from datetime import datetime
from typing import Optional


def log_analytics(model_used: str, total_api_calls: int, total_input_tokens: int,
                  total_output_tokens: int, total_time_seconds: float,
                  gre_questions: int = 0, gmat_questions: int = 0,
                  csv_path: Optional[str] = None) -> None:
    """
    Log generation analytics to CSV file.
    Creates file with headers if it doesn't exist, otherwise appends.
    
    Args:
        model_used: Name of the model used
        total_api_calls: Total number of API calls made
        total_input_tokens: Total input tokens consumed (raw int)
        total_output_tokens: Total output tokens generated (raw int)
        total_time_seconds: Total time taken in seconds (raw float)
        gre_questions: Number of GRE questions generated
        gmat_questions: Number of GMAT questions generated
        csv_path: Path to CSV file (defaults to log_json_files/analytics.csv)
    """
    if csv_path is None:
        csv_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'log_json_files',
            'analytics.csv'
        )
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    
    # Check if file exists to determine if we need to write headers
    file_exists = os.path.exists(csv_path)
    
    # Conversion Logic
    minutes = total_time_seconds / 60
    input_millions = total_input_tokens / 1_000_000
    output_millions = total_output_tokens / 1_000_000
    
    # Prepare row data
    row = {
        'datetime': datetime.now().isoformat(),
        'model_used': model_used,
        'total_api_calls': total_api_calls,
        'total_input_tokens': f"{input_millions:.3f}M",
        'total_output_tokens': f"{output_millions:.3f}M",
        'total_time_minutes': f"{minutes:.2f}",
        'gre_questions': gre_questions,
        'gmat_questions': gmat_questions
    }
    
    # Write to CSV
    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        fieldnames = ['datetime', 'model_used', 'total_api_calls', 'total_input_tokens',
                      'total_output_tokens', 'total_time_minutes', 'gre_questions', 'gmat_questions']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        # Write header if file is new
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(row)
