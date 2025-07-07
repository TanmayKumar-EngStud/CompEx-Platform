#!/usr/bin/env python3
"""
Question Paper Validation Script

This script validates generated question papers for GMAT and GRE exams to ensure:
1. Correct number of questions per section
2. Complete database storage with all required fields
3. Tabular reporting of validation results
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
from tabulate import tabulate
import asyncio
from datetime import datetime


class QuestionPaperValidator:
    """Validates question papers against expected format and database completeness"""
    
    def __init__(self):
        
        # Expected question counts based on component allocation files
        self.GMAT_EXPECTED_COUNTS = {
            "GMAT_V": {  # GMAT Verbal section
                "total_questions": 23,
                "RC": [13, 14],  # Range for Reading Comprehension
                "CR": [9, 10]    # Range for Critical Reasoning
            },
            "GMAT_Q": {  # GMAT Quantitative section
                "total_questions": 21,
                "MCQ-Single": [13, 13],  # Problem Solving questions
                "Data Sufficiency": [8, 8]  # Data Sufficiency questions
            },
            "GMAT_IR": {  # GMAT Integrated Reasoning section
                "total_questions": 20,
                "MSR": [6, 6],  # Multi-Source Reasoning
                "TA": [5, 5],   # Table Analysis
                "GI": [5, 5],   # Graphics Interpretation
                "TPA": [4, 4]   # Two-Part Analysis
            }
        }
        
        self.GRE_EXPECTED_COUNTS = {
            "GRE_Q": {  # GRE Quantitative sections
                "section1": {"total_questions": 20, "DS": [7, 8], "MCQ-Single": [9, 10], "MCQ-Multi": [2, 2], "NE": [1, 1]},
                "section2": {"total_questions": 20, "DS": [7, 8], "MCQ-Single": [9, 10], "MCQ-Multi": [2, 2], "NE": [1, 1]}
            },
            "GRE_V": {  # GRE Verbal sections
                "section1": {"total_questions": 20, "RC": [10, 10], "TC": [6, 6], "SE": [4, 4]},
                "section2": {"total_questions": 20, "RC": [10, 10], "TC": [6, 6], "SE": [4, 4]}
            }
        }
        
        # Required fields for complete question storage
        self.REQUIRED_QUESTION_FIELDS = [
            'type', 'question', 'title', 'answer', 'solution', 'difficulty', 'tags'
        ]
        
        # Optional fields that should be present but may vary by question type
        self.OPTIONAL_QUESTION_FIELDS = [
            'content', 'options', 'prompt'
        ]

    def load_paper(self, paper_path: str) -> Dict[str, Any]:
        """Load question paper from JSON file"""
        try:
            with open(paper_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise ValueError(f"Failed to load paper from {paper_path}: {str(e)}")

    def validate_gmat_paper(self, paper: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate GMAT paper structure and question counts"""
        results = []
        
        for section_name, section_data in paper.items():
            if section_name not in self.GMAT_EXPECTED_COUNTS:
                results.append({
                    'section': section_name,
                    'status': 'UNKNOWN',
                    'expected': 'N/A',
                    'actual': 'N/A',
                    'message': f'Unknown section: {section_name}'
                })
                continue
            
            # Handle section structure - each section has subsections (section0, section1, etc.)
            expected_config = self.GMAT_EXPECTED_COUNTS[section_name]
            expected_total = expected_config.get('total_questions', 0)
            
            # Count total questions across all subsections
            total_questions = 0
            for subsection_name, questions in section_data.items():
                if isinstance(questions, list):
                    total_questions += len(questions)
            
            # Validate total count
            if total_questions == expected_total:
                status = 'PASS'
                message = 'Question count matches expected'
            else:
                status = 'FAIL'
                message = f'Question count mismatch'
                
            results.append({
                'section': section_name,
                'status': status,
                'expected': expected_total,
                'actual': total_questions,
                'message': message
            })
            
            # Validate question type distribution within the section
            self._validate_gmat_question_types(section_name, section_data, expected_config, results)
                
        return results

    def validate_gre_paper(self, paper: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate GRE paper structure and question counts"""
        results = []
        
        for section_name, section_data in paper.items():
            if section_name not in self.GRE_EXPECTED_COUNTS:
                results.append({
                    'section': section_name,
                    'status': 'UNKNOWN',
                    'expected': 'N/A',
                    'actual': 'N/A',
                    'message': f'Unknown section: {section_name}'
                })
                continue
                
            expected_sections = self.GRE_EXPECTED_COUNTS[section_name]
            
            for subsection_name, questions in section_data.items():
                if subsection_name in expected_sections:
                    expected_config = expected_sections[subsection_name]
                    expected_count = expected_config['total_questions']
                    actual_count = len(questions) if isinstance(questions, list) else 0
                    
                    if actual_count == expected_count:
                        status = 'PASS'
                        message = 'Question count matches expected'
                    else:
                        status = 'FAIL'
                        message = f'Question count mismatch'
                        
                    results.append({
                        'section': f'{section_name}.{subsection_name}',
                        'status': status,
                        'expected': expected_count,
                        'actual': actual_count,
                        'message': message
                    })
                    
                    # Validate question type distribution within subsection
                    self._validate_gre_question_types(section_name, subsection_name, questions, expected_config, results)
                    
        return results

    def _validate_gmat_question_types(self, section_name: str, section_data: Dict, expected_config: Dict, results: List[Dict]):
        """Validate GMAT question type distribution within a section"""
        # Collect all questions from all subsections
        all_questions = []
        for subsection_name, questions in section_data.items():
            if isinstance(questions, list):
                all_questions.extend(questions)
        
        # Count question types
        type_counts = {}
        for question in all_questions:
            q_type = question.get('type', 'Unknown')
            type_counts[q_type] = type_counts.get(q_type, 0) + 1
        
        # Validate against expected ranges
        for q_type, expected_range in expected_config.items():
            if q_type == 'total_questions':
                continue
                
            if isinstance(expected_range, list) and len(expected_range) == 2:
                min_expected, max_expected = expected_range
                actual_count = type_counts.get(q_type, 0)
                
                if min_expected <= actual_count <= max_expected:
                    status = 'PASS'
                    message = f'{q_type} count within expected range'
                else:
                    status = 'FAIL'
                    message = f'{q_type} count outside expected range'
                    
                results.append({
                    'section': f'{section_name}.{q_type}',
                    'status': status,
                    'expected': f'{min_expected}-{max_expected}',
                    'actual': actual_count,
                    'message': message
                })

    def _validate_gre_question_types(self, section_name: str, subsection_name: str, questions: List[Dict], expected_config: Dict, results: List[Dict]):
        """Validate GRE question type distribution within a subsection"""
        # Count question types
        type_counts = {}
        for question in questions:
            q_type = question.get('type', 'Unknown')
            type_counts[q_type] = type_counts.get(q_type, 0) + 1
        
        # Validate against expected ranges
        for q_type, expected_range in expected_config.items():
            if q_type == 'total_questions':
                continue
                
            if isinstance(expected_range, list) and len(expected_range) == 2:
                min_expected, max_expected = expected_range
                actual_count = type_counts.get(q_type, 0)
                
                if min_expected <= actual_count <= max_expected:
                    status = 'PASS'
                    message = f'{q_type} count within expected range'
                else:
                    status = 'FAIL'
                    message = f'{q_type} count outside expected range'
                    
                results.append({
                    'section': f'{section_name}.{subsection_name}.{q_type}',
                    'status': status,
                    'expected': f'{min_expected}-{max_expected}',
                    'actual': actual_count,
                    'message': message
                })

    def validate_question_completeness(self, questions: List[Dict]) -> List[Dict[str, Any]]:
        """Validate individual questions have all required fields"""
        results = []
        
        for i, question in enumerate(questions, 1):
            missing_fields = []
            for field in self.REQUIRED_QUESTION_FIELDS:
                if field not in question or question[field] is None or question[field] == "":
                    missing_fields.append(field)
                    
            if missing_fields:
                results.append({
                    'question_number': i,
                    'status': 'INCOMPLETE',
                    'missing_fields': ', '.join(missing_fields),
                    'message': f'Missing required fields: {", ".join(missing_fields)}'
                })
            else:
                results.append({
                    'question_number': i,
                    'status': 'COMPLETE',
                    'missing_fields': 'None',
                    'message': 'All required fields present'
                })
                
        return results

    def validate_database_readiness(self, questions: List[Dict]) -> List[Dict[str, Any]]:
        """Validate questions are ready for database storage"""
        results = []
        
        # Check if all questions have required fields for database storage
        db_ready_count = 0
        for i, question in enumerate(questions, 1):
            missing_fields = []
            
            # Check required fields
            for field in self.REQUIRED_QUESTION_FIELDS:
                if field not in question or question[field] is None or question[field] == "":
                    missing_fields.append(field)
            
            # Check for at least one optional field
            has_optional = any(field in question and question[field] is not None 
                             for field in self.OPTIONAL_QUESTION_FIELDS)
            
            if not has_optional:
                missing_fields.append('content/options/prompt (at least one required)')
            
            if missing_fields:
                results.append({
                    'question_number': i,
                    'status': 'NOT_READY',
                    'missing_fields': ', '.join(missing_fields),
                    'message': f'Missing fields for database storage'
                })
            else:
                db_ready_count += 1
                results.append({
                    'question_number': i,
                    'status': 'READY',
                    'missing_fields': 'None',
                    'message': 'Ready for database storage'
                })
        
        # Add summary
        results.append({
            'question_number': 'SUMMARY',
            'status': f'{db_ready_count}/{len(questions)} READY',
            'missing_fields': 'N/A',
            'message': f'{db_ready_count} out of {len(questions)} questions ready for database storage'
        })
                
        return results

    def generate_report(self, validation_results: Dict[str, Any], paper_path: str) -> str:
        """Generate comprehensive validation report"""
        report = []
        report.append(f"\n{'='*80}")
        report.append(f"QUESTION PAPER VALIDATION REPORT")
        report.append(f"{'='*80}")
        report.append(f"Paper: {os.path.basename(paper_path)}")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"{'='*80}\n")
        
        # Section count validation
        if validation_results.get('section_validation'):
            report.append("SECTION COUNT VALIDATION")
            report.append("-" * 40)
            headers = ['Section', 'Status', 'Expected', 'Actual', 'Message']
            table_data = []
            for result in validation_results['section_validation']:
                table_data.append([
                    result['section'],
                    result['status'],
                    result['expected'],
                    result['actual'],
                    result['message']
                ])
            report.append(tabulate(table_data, headers=headers, tablefmt='grid'))
            report.append("")
        
        # Question completeness validation
        if validation_results.get('completeness_validation'):
            report.append("QUESTION COMPLETENESS VALIDATION")
            report.append("-" * 40)
            complete_count = sum(1 for r in validation_results['completeness_validation'] if r['status'] == 'COMPLETE')
            total_count = len(validation_results['completeness_validation'])
            report.append(f"Complete Questions: {complete_count}/{total_count}")
            
            # Show incomplete questions only
            incomplete_questions = [r for r in validation_results['completeness_validation'] if r['status'] == 'INCOMPLETE']
            if incomplete_questions:
                report.append("\nINCOMPLETE QUESTIONS:")
                headers = ['Question #', 'Status', 'Missing Fields', 'Message']
                table_data = []
                for result in incomplete_questions:
                    table_data.append([
                        result['question_number'],
                        result['status'],
                        result['missing_fields'],
                        result['message']
                    ])
                report.append(tabulate(table_data, headers=headers, tablefmt='grid'))
            else:
                report.append("\n✓ All questions are complete!")
            report.append("")
        
        # Database readiness validation
        if validation_results.get('database_readiness'):
            report.append("DATABASE READINESS VALIDATION")
            report.append("-" * 40)
            ready_questions = [r for r in validation_results['database_readiness'] if r['status'] == 'READY']
            not_ready_questions = [r for r in validation_results['database_readiness'] if r['status'] == 'NOT_READY']
            summary = [r for r in validation_results['database_readiness'] if r['question_number'] == 'SUMMARY']
            
            if summary:
                report.append(f"Database Readiness: {summary[0]['status']}")
            
            if not_ready_questions:
                report.append("\nQUESTIONS NOT READY FOR DATABASE:")
                headers = ['Question #', 'Status', 'Missing Fields', 'Message']
                table_data = []
                for result in not_ready_questions:
                    table_data.append([
                        result['question_number'],
                        result['status'],
                        result['missing_fields'],
                        result['message']
                    ])
                report.append(tabulate(table_data, headers=headers, tablefmt='grid'))
            else:
                report.append("\n✓ All questions are ready for database storage!")
            report.append("")
        
        # Summary
        report.append("VALIDATION SUMMARY")
        report.append("-" * 40)
        
        total_checks = 0
        passed_checks = 0
        
        for validation_type, results in validation_results.items():
            if isinstance(results, list):
                total_checks += len(results)
                passed_checks += sum(1 for r in results if r.get('status') in ['PASS', 'COMPLETE'])
        
        report.append(f"Total Checks: {total_checks}")
        report.append(f"Passed Checks: {passed_checks}")
        report.append(f"Failed Checks: {total_checks - passed_checks}")
        report.append(f"Success Rate: {(passed_checks/total_checks*100):.1f}%" if total_checks > 0 else "N/A")
        
        return "\n".join(report)

    def validate_paper(self, paper_path: str, exam_type: str = None) -> Dict[str, Any]:
        """Main validation method"""
        if not os.path.exists(paper_path):
            raise FileNotFoundError(f"Paper file not found: {paper_path}")
            
        paper = self.load_paper(paper_path)
        
        # Auto-detect exam type if not provided
        if not exam_type:
            if any(section in paper for section in ['GMAT_IR', 'GMAT_V', 'GMAT_Q']):
                exam_type = 'GMAT'
            elif any(section in paper for section in ['GRE_V', 'GRE_Q']):
                exam_type = 'GRE'
            else:
                exam_type = 'GMAT'  # Default fallback
        
        validation_results = {}
        
        # Validate section structure and counts
        if exam_type.upper() == 'GMAT':
            validation_results['section_validation'] = self.validate_gmat_paper(paper)
        else:
            validation_results['section_validation'] = self.validate_gre_paper(paper)
        
        # Collect all questions for completeness validation
        all_questions = []
        for section_data in paper.values():
            if isinstance(section_data, list):
                all_questions.extend(section_data)
            elif isinstance(section_data, dict):
                for subsection_data in section_data.values():
                    if isinstance(subsection_data, list):
                        all_questions.extend(subsection_data)
        
        # Validate question completeness
        validation_results['completeness_validation'] = self.validate_question_completeness(all_questions)
        
        # Validate database readiness
        validation_results['database_readiness'] = self.validate_database_readiness(all_questions)
        
        return validation_results


def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print("Usage: python validate_question_paper.py <paper_path> [exam_type]")
        print("Example: python validate_question_paper.py papers/GMAT/GMAT_paper-13-06-16-48-difficulty-5.json GMAT")
        print("Example: python validate_question_paper.py papers/GRE/GRE_paper-06-06-20-25-difficulty-3.json GRE")
        sys.exit(1)
    
    paper_path = sys.argv[1]
    exam_type = sys.argv[2] if len(sys.argv) > 2 else None
    
    validator = QuestionPaperValidator()
    
    try:
        print(f"Validating question paper: {paper_path}")
        validation_results = validator.validate_paper(paper_path, exam_type)
        
        # Generate and print report
        report = validator.generate_report(validation_results, paper_path)
        print(report)
        
        # Save report to file
        report_path = paper_path.replace('.json', '_validation_report.txt')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\nDetailed report saved to: {report_path}")
        
    except Exception as e:
        print(f"Validation failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()