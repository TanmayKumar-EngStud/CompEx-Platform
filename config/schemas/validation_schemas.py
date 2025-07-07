"""
Validation schemas for GMAT/GRE question generation system.

This module provides comprehensive validation rules and output format
specifications for question generation and processing.
"""

import re
import json
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum

from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.enums.difficulty_levels import DifficultyLevel


class ValidationSeverity(Enum):
    """Validation error severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationRule:
    """
    Individual validation rule specification.
    
    Defines a single validation check with its criteria,
    error message, and severity level.
    """
    rule_name: str
    description: str
    validator: Callable[[Any], bool]
    error_message: str
    severity: ValidationSeverity = ValidationSeverity.ERROR
    applies_to: Optional[List[str]] = None  # Field names this rule applies to


@dataclass
class OutputFormatSchema:
    """
    Schema for validating output format and structure.
    
    Defines expected output format, required fields, and
    validation rules for question generation outputs.
    """
    format_name: str
    description: str
    required_fields: Dict[str, type]
    optional_fields: Dict[str, type] = field(default_factory=dict)
    validation_rules: List[ValidationRule] = field(default_factory=list)
    format_specific_rules: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Validate data against this format schema.
        
        Args:
            data: Data to validate
            
        Returns:
            List of validation issues found
        """
        issues = []
        
        # Check required fields
        for field_name, field_type in self.required_fields.items():
            if field_name not in data:
                issues.append({
                    "field": field_name,
                    "severity": ValidationSeverity.ERROR.value,
                    "message": f"Required field '{field_name}' is missing",
                    "rule": "required_field_check"
                })
            elif not isinstance(data[field_name], field_type):
                issues.append({
                    "field": field_name,
                    "severity": ValidationSeverity.ERROR.value,
                    "message": f"Field '{field_name}' should be {field_type.__name__}, got {type(data[field_name]).__name__}",
                    "rule": "type_check"
                })
        
        # Check optional fields if present
        for field_name, field_type in self.optional_fields.items():
            if field_name in data and not isinstance(data[field_name], field_type):
                issues.append({
                    "field": field_name,
                    "severity": ValidationSeverity.WARNING.value,
                    "message": f"Optional field '{field_name}' should be {field_type.__name__}, got {type(data[field_name]).__name__}",
                    "rule": "optional_type_check"
                })
        
        # Apply validation rules
        for rule in self.validation_rules:
            if rule.applies_to:
                # Apply to specific fields
                for field_name in rule.applies_to:
                    if field_name in data:
                        if not rule.validator(data[field_name]):
                            issues.append({
                                "field": field_name,
                                "severity": rule.severity.value,
                                "message": rule.error_message.format(field=field_name, value=data[field_name]),
                                "rule": rule.rule_name
                            })
            else:
                # Apply to entire data
                if not rule.validator(data):
                    issues.append({
                        "field": "overall",
                        "severity": rule.severity.value,
                        "message": rule.error_message,
                        "rule": rule.rule_name
                    })
        
        return issues


class ValidationSchema:
    """
    Comprehensive validation system for question generation.
    
    Provides centralized validation functionality for all question types,
    output formats, and content requirements.
    """
    
    def __init__(self):
        """Initialize validation schema with predefined rules."""
        self._output_formats: Dict[str, OutputFormatSchema] = {}
        self._global_rules: List[ValidationRule] = []
        self._initialize_schemas()
    
    def _initialize_schemas(self):
        """Initialize all validation schemas and rules."""
        self._initialize_global_rules()
        self._initialize_output_formats()
    
    def _initialize_global_rules(self):
        """Initialize global validation rules."""
        self._global_rules = [
            ValidationRule(
                rule_name="json_parseable",
                description="Ensure content is valid JSON",
                validator=self._is_valid_json,
                error_message="Content must be valid JSON format",
                severity=ValidationSeverity.ERROR
            ),
            ValidationRule(
                rule_name="no_single_quotes",
                description="Ensure no single quotes in JSON content",
                validator=lambda x: "'" not in json.dumps(x) if isinstance(x, (dict, list)) else True,
                error_message="JSON content must not contain single quotes",
                severity=ValidationSeverity.ERROR
            ),
            ValidationRule(
                rule_name="double_quotes_only",
                description="Ensure only double quotes are used",
                validator=self._uses_double_quotes_only,
                error_message="Use double quotes only, replace single quotes with (`) symbol",
                severity=ValidationSeverity.WARNING
            )
        ]
    
    def _initialize_output_formats(self):
        """Initialize output format schemas."""
        # Data Sufficiency Question Text Format
        self._output_formats["data_sufficiency_questionText"] = OutputFormatSchema(
            format_name="data_sufficiency_questionText",
            description="Data sufficiency question text output format",
            required_fields={
                "passage": str,
                "statements": list,
                "question": str
            },
            validation_rules=[
                ValidationRule(
                    rule_name="statements_count",
                    description="Ensure exactly 2 statements",
                    validator=lambda x: len(x) == 2,
                    error_message="statements must contain exactly 2 items",
                    applies_to=["statements"]
                ),
                ValidationRule(
                    rule_name="passage_length",
                    description="Ensure passage has appropriate length",
                    validator=lambda x: 50 <= len(x) <= 1000,
                    error_message="passage must be between 50 and 1000 characters",
                    applies_to=["passage"]
                ),
                ValidationRule(
                    rule_name="question_length",
                    description="Ensure question has appropriate length",
                    validator=lambda x: 10 <= len(x) <= 500,
                    error_message="question must be between 10 and 500 characters",
                    applies_to=["question"]
                )
            ]
        )
        
        # Question Title Format
        self._output_formats["questionTitle"] = OutputFormatSchema(
            format_name="questionTitle",
            description="Question title output format",
            required_fields={"title": str},
            validation_rules=[
                ValidationRule(
                    rule_name="title_length",
                    description="Ensure title is concise",
                    validator=lambda x: 5 <= len(x) <= 100,
                    error_message="title must be between 5 and 100 characters",
                    applies_to=["title"]
                ),
                ValidationRule(
                    rule_name="title_descriptive",
                    description="Ensure title is descriptive",
                    validator=lambda x: len(x.split()) >= 3,
                    error_message="title should contain at least 3 words",
                    applies_to=["title"]
                )
            ]
        )
        
        # Question Solution Format
        self._output_formats["questionSolution"] = OutputFormatSchema(
            format_name="questionSolution",
            description="Question solution output format",
            required_fields={"solution": str},
            validation_rules=[
                ValidationRule(
                    rule_name="solution_length",
                    description="Ensure solution is comprehensive",
                    validator=lambda x: 100 <= len(x) <= 5000,
                    error_message="solution must be between 100 and 5000 characters",
                    applies_to=["solution"]
                ),
                ValidationRule(
                    rule_name="solution_structure",
                    description="Ensure solution has step-by-step structure",
                    validator=lambda x: "step" in x.lower() or "analysis" in x.lower(),
                    error_message="solution should include step-by-step analysis",
                    applies_to=["solution"],
                    severity=ValidationSeverity.WARNING
                ),
                ValidationRule(
                    rule_name="no_final_answer",
                    description="Ensure solution doesn't include final answer choice",
                    validator=lambda x: not re.search(r'\b[A-E]\b.*correct.*answer|answer.*\b[A-E]\b', x, re.IGNORECASE),
                    error_message="solution should not include the final answer choice",
                    applies_to=["solution"]
                )
            ]
        )
        
        # Question Answer Format
        self._output_formats["questionAnswer"] = OutputFormatSchema(
            format_name="questionAnswer",
            description="Question answer output format",
            required_fields={"answer": str},
            validation_rules=[
                ValidationRule(
                    rule_name="valid_answer_choice",
                    description="Ensure answer is valid choice",
                    validator=lambda x: x in ["A", "B", "C", "D", "E"],
                    error_message="answer must be one of: A, B, C, D, E",
                    applies_to=["answer"]
                )
            ]
        )
        
        # Critical Reasoning Options Format
        self._output_formats["critical_reasoning_questionOptions"] = OutputFormatSchema(
            format_name="critical_reasoning_questionOptions",
            description="Critical reasoning question options format",
            required_fields={
                "options": dict,
                "answer": str
            },
            validation_rules=[
                ValidationRule(
                    rule_name="five_options",
                    description="Ensure exactly 5 options",
                    validator=lambda x: len(x) == 5 and all(k in x for k in ["A", "B", "C", "D", "E"]),
                    error_message="options must contain exactly 5 choices (A, B, C, D, E)",
                    applies_to=["options"]
                ),
                ValidationRule(
                    rule_name="option_length",
                    description="Ensure options have appropriate length",
                    validator=lambda x: all(10 <= len(v) <= 200 for v in x.values()),
                    error_message="each option must be between 10 and 200 characters",
                    applies_to=["options"]
                )
            ]
        )
        
        # Graphic Interpretation Graph Format
        self._output_formats["graphic_interpretation_questionGraph"] = OutputFormatSchema(
            format_name="graphic_interpretation_questionGraph",
            description="Graphic interpretation graph output format",
            required_fields={"graphs": list},
            validation_rules=[
                ValidationRule(
                    rule_name="graph_structure",
                    description="Ensure each graph has required structure",
                    validator=self._validate_graph_structure,
                    error_message="each graph must have type, title, description, and data fields",
                    applies_to=["graphs"]
                ),
                ValidationRule(
                    rule_name="graph_types",
                    description="Ensure valid graph types",
                    validator=lambda x: all(g.get("type") in ["bar-graph", "pie-chart", "line-graph", "scatter-plot", "stacked-bar-graph"] for g in x),
                    error_message="graph type must be one of: bar-graph, pie-chart, line-graph, scatter-plot, stacked-bar-graph",
                    applies_to=["graphs"]
                )
            ]
        )
    
    def _is_valid_json(self, data: Any) -> bool:
        """Check if data can be serialized to valid JSON."""
        try:
            json.dumps(data)
            return True
        except (TypeError, ValueError):
            return False
    
    def _uses_double_quotes_only(self, data: Any) -> bool:
        """Check if JSON uses double quotes only."""
        try:
            json_str = json.dumps(data)
            # Check for problematic single quote patterns
            return not re.search(r"'[^']*'", json_str)
        except:
            return False
    
    def _validate_graph_structure(self, graphs: List[Dict[str, Any]]) -> bool:
        """Validate graph structure requirements."""
        required_fields = {"type", "title", "description", "data"}
        return all(
            isinstance(graph, dict) and required_fields.issubset(graph.keys())
            for graph in graphs
        )
    
    def validate_output(
        self, 
        format_name: str, 
        data: Dict[str, Any],
        question_type: Optional[QuestionType] = None,
        exam_type: Optional[ExamType] = None
    ) -> Dict[str, Any]:
        """
        Validate output against specified format.
        
        Args:
            format_name: Name of the output format to validate against
            data: Data to validate
            question_type: Question type for context (optional)
            exam_type: Exam type for context (optional)
            
        Returns:
            Validation result with issues and summary
        """
        issues = []
        
        # Apply global rules first
        for rule in self._global_rules:
            if not rule.validator(data):
                issues.append({
                    "field": "global",
                    "severity": rule.severity.value,
                    "message": rule.error_message,
                    "rule": rule.rule_name
                })
        
        # Apply format-specific validation
        if format_name in self._output_formats:
            format_schema = self._output_formats[format_name]
            format_issues = format_schema.validate(data)
            issues.extend(format_issues)
        else:
            issues.append({
                "field": "format",
                "severity": ValidationSeverity.WARNING.value,
                "message": f"Unknown format: {format_name}",
                "rule": "format_recognition"
            })
        
        # Compile validation summary
        error_count = sum(1 for issue in issues if issue["severity"] == "error")
        warning_count = sum(1 for issue in issues if issue["severity"] == "warning")
        
        return {
            "is_valid": error_count == 0,
            "issues": issues,
            "summary": {
                "total_issues": len(issues),
                "errors": error_count,
                "warnings": warning_count,
                "format": format_name
            },
            "context": {
                "question_type": question_type.value if question_type else None,
                "exam_type": exam_type.value if exam_type else None
            }
        }
    
    def get_format_requirements(self, format_name: str) -> Optional[Dict[str, Any]]:
        """Get requirements for a specific output format."""
        if format_name in self._output_formats:
            schema = self._output_formats[format_name]
            return {
                "format_name": schema.format_name,
                "description": schema.description,
                "required_fields": {name: typ.__name__ for name, typ in schema.required_fields.items()},
                "optional_fields": {name: typ.__name__ for name, typ in schema.optional_fields.items()},
                "validation_rules": [
                    {
                        "rule_name": rule.rule_name,
                        "description": rule.description,
                        "severity": rule.severity.value,
                        "applies_to": rule.applies_to
                    }
                    for rule in schema.validation_rules
                ]
            }
        return None
    
    def get_available_formats(self) -> List[str]:
        """Get list of available output formats."""
        return list(self._output_formats.keys())
    
    def add_custom_format(self, format_schema: OutputFormatSchema) -> None:
        """Add a custom output format schema."""
        self._output_formats[format_schema.format_name] = format_schema
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get comprehensive validation system summary."""
        return {
            "total_formats": len(self._output_formats),
            "global_rules": len(self._global_rules),
            "available_formats": list(self._output_formats.keys()),
            "validation_capabilities": {
                "json_validation": True,
                "type_checking": True,
                "content_validation": True,
                "structure_validation": True,
                "custom_rules": True
            }
        }