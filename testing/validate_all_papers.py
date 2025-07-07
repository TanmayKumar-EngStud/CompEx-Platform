#!/usr/bin/env python3
"""
Batch Question Paper Validation Script

This script validates all question papers in the papers directory
and generates a summary report showing validation status for all papers.
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from tabulate import tabulate
from validate_question_paper import QuestionPaperValidator
from datetime import datetime


def find_all_papers(papers_dir: str = "papers") -> List[str]:
    """Find all JSON paper files in the papers directory"""
    paper_files = []
    if os.path.exists(papers_dir):
        for root, dirs, files in os.walk(papers_dir):
            for file in files:
                if file.endswith('.json') and not file.endswith('_validation_report.json'):
                    paper_files.append(os.path.join(root, file))
    return sorted(paper_files)


def validate_all_papers():
    """Validate all papers and generate summary report"""
    print("=" * 80)
    print("BATCH VALIDATION OF ALL QUESTION PAPERS")
    print("=" * 80)
    
    papers = find_all_papers()
    if not papers:
        print("No question papers found in the papers directory.")
        return
    
    print(f"Found {len(papers)} paper(s) to validate...")
    print()
    
    validator = QuestionPaperValidator()
    summary_results = []
    
    for i, paper_path in enumerate(papers, 1):
        print(f"[{i}/{len(papers)}] Validating: {os.path.basename(paper_path)}")
        
        try:
            # Validate the paper
            validation_results = validator.validate_paper(paper_path)
            
            # Calculate summary statistics
            total_checks = 0
            passed_checks = 0
            total_questions = 0
            complete_questions = 0
            ready_questions = 0
            
            # Count section validation results
            section_results = validation_results.get('section_validation', [])
            for result in section_results:
                total_checks += 1
                if result.get('status') == 'PASS':
                    passed_checks += 1
            
            # Count question completeness results
            completeness_results = validation_results.get('completeness_validation', [])
            total_questions = len(completeness_results)
            complete_questions = sum(1 for r in completeness_results if r.get('status') == 'COMPLETE')
            
            # Count database readiness results
            readiness_results = validation_results.get('database_readiness', [])
            ready_questions = sum(1 for r in readiness_results if r.get('status') == 'READY')
            
            # Determine overall status
            section_pass_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
            question_completeness_rate = (complete_questions / total_questions * 100) if total_questions > 0 else 0
            
            if section_pass_rate >= 80 and question_completeness_rate >= 90:
                overall_status = "EXCELLENT"
            elif section_pass_rate >= 60 and question_completeness_rate >= 75:
                overall_status = "GOOD"
            elif section_pass_rate >= 40 and question_completeness_rate >= 50:
                overall_status = "NEEDS_IMPROVEMENT"
            else:
                overall_status = "POOR"
            
            # Extract exam type from path
            exam_type = "GMAT" if "GMAT" in paper_path else "GRE" if "GRE" in paper_path else "Unknown"
            
            summary_results.append({
                'paper': os.path.basename(paper_path),
                'exam_type': exam_type,
                'overall_status': overall_status,
                'total_questions': total_questions,
                'complete_questions': complete_questions,
                'ready_questions': ready_questions,
                'section_pass_rate': f"{section_pass_rate:.1f}%",
                'completeness_rate': f"{question_completeness_rate:.1f}%",
                'section_checks': f"{passed_checks}/{total_checks}",
                'path': paper_path
            })
            
        except Exception as e:
            print(f"  ERROR: {str(e)}")
            summary_results.append({
                'paper': os.path.basename(paper_path),
                'exam_type': 'Unknown',
                'overall_status': 'ERROR',
                'total_questions': 0,
                'complete_questions': 0,
                'ready_questions': 0,
                'section_pass_rate': 'N/A',
                'completeness_rate': 'N/A',
                'section_checks': 'N/A',
                'path': paper_path
            })
    
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY REPORT")
    print("=" * 80)
    
    # Generate summary table
    headers = [
        'Paper', 'Exam', 'Status', 'Questions', 'Complete', 'DB Ready', 
        'Section Pass', 'Completeness'
    ]
    
    table_data = []
    for result in summary_results:
        table_data.append([
            result['paper'][:30] + '...' if len(result['paper']) > 30 else result['paper'],
            result['exam_type'],
            result['overall_status'],
            result['total_questions'],
            result['complete_questions'],
            result['ready_questions'],
            result['section_pass_rate'],
            result['completeness_rate']
        ])
    
    print(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    # Generate overall statistics
    print("\nOVERALL STATISTICS")
    print("-" * 40)
    
    total_papers = len(summary_results)
    excellent_count = sum(1 for r in summary_results if r['overall_status'] == 'EXCELLENT')
    good_count = sum(1 for r in summary_results if r['overall_status'] == 'GOOD')
    needs_improvement_count = sum(1 for r in summary_results if r['overall_status'] == 'NEEDS_IMPROVEMENT')
    poor_count = sum(1 for r in summary_results if r['overall_status'] == 'POOR')
    error_count = sum(1 for r in summary_results if r['overall_status'] == 'ERROR')
    
    print(f"Total Papers: {total_papers}")
    print(f"Excellent: {excellent_count} ({excellent_count/total_papers*100:.1f}%)")
    print(f"Good: {good_count} ({good_count/total_papers*100:.1f}%)")
    print(f"Needs Improvement: {needs_improvement_count} ({needs_improvement_count/total_papers*100:.1f}%)")
    print(f"Poor: {poor_count} ({poor_count/total_papers*100:.1f}%)")
    print(f"Errors: {error_count} ({error_count/total_papers*100:.1f}%)")
    
    # Group by exam type
    gmat_papers = [r for r in summary_results if r['exam_type'] == 'GMAT']
    gre_papers = [r for r in summary_results if r['exam_type'] == 'GRE']
    
    if gmat_papers:
        print(f"\nGMAT Papers: {len(gmat_papers)}")
        avg_gmat_questions = sum(r['total_questions'] for r in gmat_papers) / len(gmat_papers)
        print(f"Average Questions per GMAT Paper: {avg_gmat_questions:.1f}")
        
    if gre_papers:
        print(f"\nGRE Papers: {len(gre_papers)}")
        avg_gre_questions = sum(r['total_questions'] for r in gre_papers) / len(gre_papers)
        print(f"Average Questions per GRE Paper: {avg_gre_questions:.1f}")
    
    # Save detailed results to JSON
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    report_filename = f"validation_summary_{timestamp}.json"
    
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'total_papers': total_papers,
            'summary_statistics': {
                'excellent': excellent_count,
                'good': good_count,
                'needs_improvement': needs_improvement_count,
                'poor': poor_count,
                'errors': error_count
            },
            'detailed_results': summary_results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetailed results saved to: {report_filename}")


if __name__ == "__main__":
    validate_all_papers()