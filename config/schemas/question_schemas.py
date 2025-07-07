"""
Question configuration schemas for GMAT/GRE question generation.

This module defines comprehensive schemas for question types,
their properties, and validation requirements.
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum

from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.enums.difficulty_levels import DifficultyLevel


@dataclass
class QuestionModeConfig:
    """Configuration for a specific question mode."""
    mode_name: str
    description: str
    input_format: str
    output_format: Dict[str, Any]
    is_required: bool = True
    response_type: str = "json"  # "json" or "plain_text"
    validation_rules: Optional[Dict[str, Any]] = None


@dataclass
class QuestionTypeSchema:
    """
    Comprehensive schema for a question type.
    
    Defines all properties, modes, and requirements for a specific
    question type across different exam systems.
    """
    question_type: QuestionType
    display_name: str
    description: str
    supported_exams: Set[ExamType]
    available_modes: List[QuestionModeConfig]
    difficulty_range: tuple[int, int] = (1, 5)
    default_difficulty: int = 3
    
    # Question structure requirements
    requires_passage: bool = False
    requires_options: bool = False
    requires_statements: bool = False
    requires_graphs: bool = False
    requires_tables: bool = False
    
    # Output format specifications
    expected_output_keys: Set[str] = field(default_factory=set)
    optional_output_keys: Set[str] = field(default_factory=set)
    
    # Validation requirements
    min_content_length: int = 50
    max_content_length: int = 5000
    content_validation_rules: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Post-initialization validation and setup."""
        # Ensure difficulty range is valid
        if self.difficulty_range[0] < 1 or self.difficulty_range[1] > 5:
            raise ValueError("Difficulty range must be between 1 and 5")
        
        # Ensure default difficulty is within range
        if not (self.difficulty_range[0] <= self.default_difficulty <= self.difficulty_range[1]):
            raise ValueError("Default difficulty must be within difficulty range")
    
    def get_mode(self, mode_name: str) -> Optional[QuestionModeConfig]:
        """Get configuration for a specific mode."""
        for mode in self.available_modes:
            if mode.mode_name == mode_name:
                return mode
        return None
    
    def is_mode_supported(self, mode_name: str) -> bool:
        """Check if a mode is supported for this question type."""
        return any(mode.mode_name == mode_name for mode in self.available_modes)
    
    def get_required_modes(self) -> List[str]:
        """Get list of required modes for this question type."""
        return [mode.mode_name for mode in self.available_modes if mode.is_required]
    
    def validate_output(self, mode_name: str, output: Dict[str, Any]) -> List[str]:
        """
        Validate output for a specific mode.
        
        Args:
            mode_name: Name of the mode
            output: Output to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        mode_config = self.get_mode(mode_name)
        
        if not mode_config:
            errors.append(f"Unknown mode: {mode_name}")
            return errors
        
        # Check required keys
        required_keys = set(mode_config.output_format.keys())
        missing_keys = required_keys - set(output.keys())
        if missing_keys:
            errors.append(f"Missing required keys: {missing_keys}")
        
        # Validate individual fields
        for key, expected_type in mode_config.output_format.items():
            if key in output:
                if not self._validate_field_type(output[key], expected_type):
                    errors.append(f"Invalid type for {key}: expected {expected_type}, got {type(output[key])}")
        
        return errors
    
    def _validate_field_type(self, value: Any, expected_type: Any) -> bool:
        """Validate individual field type."""
        if expected_type == str:
            return isinstance(value, str)
        elif expected_type == list:
            return isinstance(value, list)
        elif expected_type == dict:
            return isinstance(value, dict)
        elif expected_type == int:
            return isinstance(value, int)
        elif expected_type == float:
            return isinstance(value, (int, float))
        elif expected_type == bool:
            return isinstance(value, bool)
        else:
            return True  # Allow any type for complex specifications


class QuestionSchema:
    """
    Main schema registry for all question types.
    
    Provides centralized access to question type schemas and
    validation functionality across the system.
    """
    
    def __init__(self):
        """Initialize with predefined question type schemas."""
        self._schemas: Dict[QuestionType, QuestionTypeSchema] = {}
        self._initialize_schemas()
    
    def _initialize_schemas(self):
        """Initialize all question type schemas."""
        # Data Sufficiency Schema
        self._schemas[QuestionType.DATA_SUFFICIENCY] = QuestionTypeSchema(
            question_type=QuestionType.DATA_SUFFICIENCY,
            display_name="Data Sufficiency",
            description="Questions testing logical reasoning and data analysis skills",
            supported_exams={ExamType.GMAT, ExamType.GRE},
            requires_statements=True,
            available_modes=[
                QuestionModeConfig(
                    mode_name="questionText",
                    description="Generate question passage and statements",
                    input_format="QuestionText: <topic> - <skill> - <difficulty>",
                    output_format={"passage": str, "statements": list, "question": str}
                ),
                QuestionModeConfig(
                    mode_name="questionTitle",
                    description="Generate question title",
                    input_format="QuestionTitle",
                    output_format={"title": str}
                ),
                QuestionModeConfig(
                    mode_name="questionSolution",
                    description="Generate solution explanation",
                    input_format="QuestionSolution",
                    output_format={"solution": str},
                    response_type="plain_text"
                ),
                QuestionModeConfig(
                    mode_name="questionAnswer",
                    description="Generate correct answer",
                    input_format="QuestionAnswer",
                    output_format={"answer": str}
                )
            ],
            expected_output_keys={"passage", "statements", "question", "title", "solution", "answer"}
        )
        
        # Critical Reasoning Schema
        self._schemas[QuestionType.CRITICAL_REASONING] = QuestionTypeSchema(
            question_type=QuestionType.CRITICAL_REASONING,
            display_name="Critical Reasoning",
            description="Questions testing logical argument analysis skills",
            supported_exams={ExamType.GMAT},
            requires_passage=True,
            requires_options=True,
            available_modes=[
                QuestionModeConfig(
                    mode_name="questionPassage",
                    description="Generate argument passage",
                    input_format="<PassageNumber>: <Theme> - <QuestionType> - <Category> - <Difficulty>",
                    output_format={"passage": str}
                ),
                QuestionModeConfig(
                    mode_name="questionText",
                    description="Generate question text",
                    input_format="QuestionText",
                    output_format={"question": str}
                ),
                QuestionModeConfig(
                    mode_name="questionTitle",
                    description="Generate question title",
                    input_format="QuestionTitle",
                    output_format={"title": str}
                ),
                QuestionModeConfig(
                    mode_name="questionOptions",
                    description="Generate answer options",
                    input_format="QuestionOptions",
                    output_format={"options": dict, "answer": str}
                ),
                QuestionModeConfig(
                    mode_name="questionSolution",
                    description="Generate solution explanation",
                    input_format="QuestionSolution",
                    output_format={"solution": str},
                    response_type="plain_text"
                ),
                QuestionModeConfig(
                    mode_name="questionAnswer",
                    description="Generate correct answer",
                    input_format="QuestionAnswer",
                    output_format={"answer": str}
                )
            ],
            expected_output_keys={"passage", "question", "title", "options", "solution", "answer"}
        )
        
        # Add more schemas for other question types
        self._add_reading_comprehension_schema()
        self._add_numeric_entry_schema()
        self._add_graphic_interpretation_schema()
    
    def _add_reading_comprehension_schema(self):
        """Add Reading Comprehension schema."""
        self._schemas[QuestionType.READING_COMPREHENSION] = QuestionTypeSchema(
            question_type=QuestionType.READING_COMPREHENSION,
            display_name="Reading Comprehension",
            description="Multi-part questions based on reading passages",
            supported_exams={ExamType.GMAT, ExamType.GRE},
            requires_passage=True,
            requires_options=True,
            available_modes=[
                QuestionModeConfig(
                    mode_name="questionPassage",
                    description="Generate reading passage",
                    input_format="<PassageNumber>: <Theme> - <Length> - <Difficulty>",
                    output_format={"passage": str}
                ),
                QuestionModeConfig(
                    mode_name="questionText",
                    description="Generate question text",
                    input_format="QuestionText",
                    output_format={"question": str}
                ),
                QuestionModeConfig(
                    mode_name="questionTitle",
                    description="Generate question title",
                    input_format="QuestionTitle",
                    output_format={"title": str}
                ),
                QuestionModeConfig(
                    mode_name="questionOptions",
                    description="Generate answer options",
                    input_format="QuestionOptions",
                    output_format={"options": dict, "answer": str}
                ),
                QuestionModeConfig(
                    mode_name="questionSolution",
                    description="Generate solution explanation",
                    input_format="QuestionSolution",
                    output_format={"solution": str},
                    response_type="plain_text"
                ),
                QuestionModeConfig(
                    mode_name="questionAnswer",
                    description="Generate correct answer",
                    input_format="QuestionAnswer",
                    output_format={"answer": str}
                )
            ],
            expected_output_keys={"passage", "question", "title", "options", "solution", "answer"}
        )
    
    def _add_numeric_entry_schema(self):
        """Add Numeric Entry schema."""
        self._schemas[QuestionType.NUMERIC_ENTRY] = QuestionTypeSchema(
            question_type=QuestionType.NUMERIC_ENTRY,
            display_name="Numeric Entry",
            description="Open-ended numeric answer questions",
            supported_exams={ExamType.GRE},
            available_modes=[
                QuestionModeConfig(
                    mode_name="questionText",
                    description="Generate question text",
                    input_format="QuestionText: <topic> - <difficulty>",
                    output_format={"question": str}
                ),
                QuestionModeConfig(
                    mode_name="questionTitle",
                    description="Generate question title",
                    input_format="QuestionTitle",
                    output_format={"title": str}
                ),
                QuestionModeConfig(
                    mode_name="questionSolution",
                    description="Generate solution explanation",
                    input_format="QuestionSolution",
                    output_format={"solution": str},
                    response_type="plain_text"
                ),
                QuestionModeConfig(
                    mode_name="questionAnswer",
                    description="Generate numeric answer",
                    input_format="QuestionAnswer",
                    output_format={"answer": float}
                )
            ],
            expected_output_keys={"question", "title", "solution", "answer"}
        )
    
    def _add_graphic_interpretation_schema(self):
        """Add Graphic Interpretation schema."""
        self._schemas[QuestionType.GRAPHIC_INTERPRETATION] = QuestionTypeSchema(
            question_type=QuestionType.GRAPHIC_INTERPRETATION,
            display_name="Graphic Interpretation",
            description="Questions based on graph and chart analysis",
            supported_exams={ExamType.GMAT},
            requires_graphs=True,
            available_modes=[
                QuestionModeConfig(
                    mode_name="questionGraph",
                    description="Generate graph data",
                    input_format="<GI> - <skill> - <graph_type> - <theme> - <difficulty>",
                    output_format={"graphs": list}
                ),
                QuestionModeConfig(
                    mode_name="questionText",
                    description="Generate question with fill-in-blanks",
                    input_format="QuestionText",
                    output_format={"question": str}
                ),
                QuestionModeConfig(
                    mode_name="questionTitle",
                    description="Generate question title",
                    input_format="QuestionTitle",
                    output_format={"title": str}
                ),
                QuestionModeConfig(
                    mode_name="questionOptions",
                    description="Generate options for blanks",
                    input_format="QuestionOptions",
                    output_format={"options": dict}
                ),
                QuestionModeConfig(
                    mode_name="questionSolution",
                    description="Generate solution explanation",
                    input_format="QuestionSolution",
                    output_format={"solution": str},
                    response_type="plain_text"
                ),
                QuestionModeConfig(
                    mode_name="questionAnswer",
                    description="Generate correct answers",
                    input_format="QuestionAnswer",
                    output_format={"answer": dict}
                )
            ],
            expected_output_keys={"graphs", "question", "title", "options", "solution", "answer"}
        )
    
    def get_schema(self, question_type: QuestionType) -> Optional[QuestionTypeSchema]:
        """Get schema for a specific question type."""
        return self._schemas.get(question_type)
    
    def get_supported_question_types(self, exam_type: ExamType) -> Set[QuestionType]:
        """Get question types supported by an exam type."""
        supported = set()
        for question_type, schema in self._schemas.items():
            if exam_type in schema.supported_exams:
                supported.add(question_type)
        return supported
    
    def validate_question_output(
        self, 
        question_type: QuestionType, 
        mode: str, 
        output: Dict[str, Any]
    ) -> List[str]:
        """
        Validate question output against schema.
        
        Args:
            question_type: Type of question
            mode: Generation mode
            output: Output to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        schema = self.get_schema(question_type)
        if not schema:
            return [f"Unknown question type: {question_type}"]
        
        return schema.validate_output(mode, output)
    
    def get_available_schemas(self) -> Dict[QuestionType, QuestionTypeSchema]:
        """Get all available schemas."""
        return self._schemas.copy()
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get comprehensive schema information."""
        return {
            "total_schemas": len(self._schemas),
            "question_types": [qt.value for qt in self._schemas.keys()],
            "exam_coverage": {
                exam_type.value: len(self.get_supported_question_types(exam_type))
                for exam_type in ExamType
            },
            "schema_summary": {
                qt.value: {
                    "display_name": schema.display_name,
                    "supported_exams": [e.value for e in schema.supported_exams],
                    "mode_count": len(schema.available_modes),
                    "requires_passage": schema.requires_passage,
                    "requires_options": schema.requires_options
                }
                for qt, schema in self._schemas.items()
            }
        }