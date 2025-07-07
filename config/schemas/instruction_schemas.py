"""
Instruction configuration schemas for GMAT/GRE question generation.

This module provides schemas for instruction management,
mode configurations, and template specifications.
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum

from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType


class ResponseType(Enum):
    """Response type classifications for instruction modes."""
    JSON = "json"
    PLAIN_TEXT = "plain_text"
    MIXED = "mixed"


@dataclass
class ModeSchema:
    """
    Schema for a specific instruction mode.
    
    Defines the structure, requirements, and behavior
    for a particular instruction mode.
    """
    mode_name: str
    display_name: str
    description: str
    input_format: str
    response_type: ResponseType
    output_structure: Dict[str, Any]
    is_required: bool = True
    depends_on: Optional[List[str]] = None
    examples: Optional[List[Dict[str, str]]] = None
    
    def __post_init__(self):
        """Post-initialization validation."""
        if self.depends_on is None:
            self.depends_on = []
        if self.examples is None:
            self.examples = []


@dataclass
class InstructionSchema:
    """
    Comprehensive schema for instruction management.
    
    Defines all instruction modes, their relationships,
    and execution requirements for question types.
    """
    question_type: QuestionType
    supported_exams: Set[ExamType]
    modes: List[ModeSchema]
    execution_order: List[str]
    template_requirements: Dict[str, Any] = field(default_factory=dict)
    customization_points: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization validation and setup."""
        # Validate execution order matches available modes
        mode_names = {mode.mode_name for mode in self.modes}
        for mode_name in self.execution_order:
            if mode_name not in mode_names:
                raise ValueError(f"Execution order references unknown mode: {mode_name}")
        
        # Validate dependencies
        for mode in self.modes:
            for dep in mode.depends_on:
                if dep not in mode_names:
                    raise ValueError(f"Mode {mode.mode_name} depends on unknown mode: {dep}")
    
    def get_mode(self, mode_name: str) -> Optional[ModeSchema]:
        """Get schema for a specific mode."""
        for mode in self.modes:
            if mode.mode_name == mode_name:
                return mode
        return None
    
    def get_required_modes(self) -> List[str]:
        """Get list of required modes."""
        return [mode.mode_name for mode in self.modes if mode.is_required]
    
    def get_execution_order(self) -> List[str]:
        """Get recommended execution order for modes."""
        return self.execution_order.copy()
    
    def validate_mode_sequence(self, mode_sequence: List[str]) -> List[str]:
        """
        Validate a proposed mode execution sequence.
        
        Args:
            mode_sequence: Proposed sequence of mode names
            
        Returns:
            List of validation issues
        """
        issues = []
        mode_names = {mode.mode_name for mode in self.modes}
        
        # Check all modes exist
        for mode_name in mode_sequence:
            if mode_name not in mode_names:
                issues.append(f"Unknown mode in sequence: {mode_name}")
        
        # Check dependencies are satisfied
        executed_modes = set()
        for mode_name in mode_sequence:
            mode = self.get_mode(mode_name)
            if mode:
                for dep in mode.depends_on:
                    if dep not in executed_modes:
                        issues.append(f"Mode {mode_name} executed before dependency {dep}")
            executed_modes.add(mode_name)
        
        # Check required modes are included
        required_modes = set(self.get_required_modes())
        provided_modes = set(mode_sequence)
        missing_required = required_modes - provided_modes
        if missing_required:
            issues.append(f"Missing required modes: {missing_required}")
        
        return issues


class InstructionSchemaRegistry:
    """
    Registry for all instruction schemas.
    
    Provides centralized access to instruction schemas
    and validation functionality.
    """
    
    def __init__(self):
        """Initialize with predefined instruction schemas."""
        self._schemas: Dict[QuestionType, InstructionSchema] = {}
        self._initialize_schemas()
    
    def _initialize_schemas(self):
        """Initialize all instruction schemas."""
        self._add_data_sufficiency_schema()
        self._add_critical_reasoning_schema()
        self._add_reading_comprehension_schema()
        self._add_graphic_interpretation_schema()
        self._add_numeric_entry_schema()
    
    def _add_data_sufficiency_schema(self):
        """Add Data Sufficiency instruction schema."""
        self._schemas[QuestionType.DATA_SUFFICIENCY] = InstructionSchema(
            question_type=QuestionType.DATA_SUFFICIENCY,
            supported_exams={ExamType.GMAT, ExamType.GRE},
            modes=[
                ModeSchema(
                    mode_name="questionText",
                    display_name="Question Text Generation",
                    description="Generate passage, statements, and question text",
                    input_format="QuestionText: <topic> - <skill> - <difficulty>",
                    response_type=ResponseType.JSON,
                    output_structure={
                        "passage": "string",
                        "statements": ["string", "string"],
                        "question": "string"
                    },
                    examples=[
                        {
                            "input": "QuestionText: Algebra - Logical Reasoning - 3",
                            "output": '{"passage": "...", "statements": [...], "question": "..."}'
                        }
                    ]
                ),
                ModeSchema(
                    mode_name="questionTitle",
                    display_name="Question Title Generation",
                    description="Generate concise question title",
                    input_format="QuestionTitle",
                    response_type=ResponseType.JSON,
                    output_structure={"title": "string"},
                    depends_on=["questionText"]
                ),
                ModeSchema(
                    mode_name="questionSolution",
                    display_name="Solution Explanation",
                    description="Generate step-by-step solution explanation",
                    input_format="QuestionSolution",
                    response_type=ResponseType.PLAIN_TEXT,
                    output_structure={"solution": "plain_text"},
                    depends_on=["questionText"]
                ),
                ModeSchema(
                    mode_name="questionAnswer",
                    display_name="Answer Generation",
                    description="Generate correct answer choice",
                    input_format="QuestionAnswer",
                    response_type=ResponseType.JSON,
                    output_structure={"answer": "A|B|C|D|E"},
                    depends_on=["questionText", "questionSolution"]
                )
            ],
            execution_order=["questionText", "questionTitle", "questionSolution", "questionAnswer"],
            template_requirements={
                "standard_options": "Data sufficiency standard options A-E",
                "json_formatting": "Strict JSON format requirements",
                "solution_format": "Plain text solution without final answer"
            },
            customization_points={
                "exam_specific_instructions": "GMAT vs GRE specific guidance",
                "difficulty_scaling": "Difficulty-based complexity adjustments",
                "topic_focus": "Subject area specific requirements"
            }
        )
    
    def _add_critical_reasoning_schema(self):
        """Add Critical Reasoning instruction schema."""
        self._schemas[QuestionType.CRITICAL_REASONING] = InstructionSchema(
            question_type=QuestionType.CRITICAL_REASONING,
            supported_exams={ExamType.GMAT},
            modes=[
                ModeSchema(
                    mode_name="questionPassage",
                    display_name="Passage Generation",
                    description="Generate argument passage for critical reasoning",
                    input_format="<PassageNumber>: <Theme> - <QuestionType> - <Category> - <Difficulty>",
                    response_type=ResponseType.JSON,
                    output_structure={"passage": "string"}
                ),
                ModeSchema(
                    mode_name="questionText",
                    display_name="Question Text Generation",
                    description="Generate question text based on passage",
                    input_format="QuestionText",
                    response_type=ResponseType.JSON,
                    output_structure={"question": "string"},
                    depends_on=["questionPassage"]
                ),
                ModeSchema(
                    mode_name="questionTitle",
                    display_name="Question Title Generation",
                    description="Generate descriptive question title",
                    input_format="QuestionTitle",
                    response_type=ResponseType.JSON,
                    output_structure={"title": "string"},
                    depends_on=["questionText"]
                ),
                ModeSchema(
                    mode_name="questionOptions",
                    display_name="Answer Options Generation",
                    description="Generate 5 answer options with correct answer",
                    input_format="QuestionOptions",
                    response_type=ResponseType.JSON,
                    output_structure={
                        "options": {"A": "string", "B": "string", "C": "string", "D": "string", "E": "string"},
                        "answer": "A|B|C|D|E"
                    },
                    depends_on=["questionText"]
                ),
                ModeSchema(
                    mode_name="questionSolution",
                    display_name="Solution Explanation",
                    description="Generate comprehensive solution with argument analysis",
                    input_format="QuestionSolution",
                    response_type=ResponseType.PLAIN_TEXT,
                    output_structure={"solution": "plain_text"},
                    depends_on=["questionText", "questionOptions"]
                ),
                ModeSchema(
                    mode_name="questionAnswer",
                    display_name="Answer Confirmation",
                    description="Confirm correct answer choice",
                    input_format="QuestionAnswer",
                    response_type=ResponseType.JSON,
                    output_structure={"answer": "A|B|C|D|E"},
                    depends_on=["questionOptions"]
                )
            ],
            execution_order=["questionPassage", "questionText", "questionTitle", "questionOptions", "questionSolution", "questionAnswer"],
            template_requirements={
                "business_context": "GMAT business and management focus",
                "argument_structure": "Clear premise-conclusion structure",
                "critical_reasoning_categories": "8 standard CR question types"
            }
        )
    
    def _add_reading_comprehension_schema(self):
        """Add Reading Comprehension instruction schema."""
        self._schemas[QuestionType.READING_COMPREHENSION] = InstructionSchema(
            question_type=QuestionType.READING_COMPREHENSION,
            supported_exams={ExamType.GMAT, ExamType.GRE},
            modes=[
                ModeSchema(
                    mode_name="questionPassage",
                    display_name="Passage Generation",
                    description="Generate reading comprehension passage",
                    input_format="<PassageNumber>: <Theme> - <Length> - <Difficulty>",
                    response_type=ResponseType.JSON,
                    output_structure={"passage": "string"}
                ),
                ModeSchema(
                    mode_name="questionText",
                    display_name="Question Text Generation",
                    description="Generate question based on passage",
                    input_format="QuestionText",
                    response_type=ResponseType.JSON,
                    output_structure={"question": "string"},
                    depends_on=["questionPassage"]
                ),
                ModeSchema(
                    mode_name="questionTitle",
                    display_name="Question Title Generation",
                    description="Generate descriptive question title",
                    input_format="QuestionTitle",
                    response_type=ResponseType.JSON,
                    output_structure={"title": "string"},
                    depends_on=["questionText"]
                ),
                ModeSchema(
                    mode_name="questionOptions",
                    display_name="Answer Options Generation",
                    description="Generate answer options for RC question",
                    input_format="QuestionOptions",
                    response_type=ResponseType.JSON,
                    output_structure={
                        "options": {"A": "string", "B": "string", "C": "string", "D": "string", "E": "string"},
                        "answer": "A|B|C|D|E"
                    },
                    depends_on=["questionText"]
                ),
                ModeSchema(
                    mode_name="questionSolution",
                    display_name="Solution Explanation",
                    description="Generate solution with passage analysis",
                    input_format="QuestionSolution",
                    response_type=ResponseType.PLAIN_TEXT,
                    output_structure={"solution": "plain_text"},
                    depends_on=["questionText", "questionOptions"]
                ),
                ModeSchema(
                    mode_name="questionAnswer",
                    display_name="Answer Confirmation",
                    description="Confirm correct answer choice",
                    input_format="QuestionAnswer",
                    response_type=ResponseType.JSON,
                    output_structure={"answer": "A|B|C|D|E"},
                    depends_on=["questionOptions"]
                )
            ],
            execution_order=["questionPassage", "questionText", "questionTitle", "questionOptions", "questionSolution", "questionAnswer"],
            customization_points={
                "passage_length": "Variable length based on exam (GMAT vs GRE)",
                "question_count": "Number of child questions per passage",
                "academic_level": "Appropriate academic complexity"
            }
        )
    
    def _add_graphic_interpretation_schema(self):
        """Add Graphic Interpretation instruction schema."""
        self._schemas[QuestionType.GRAPHIC_INTERPRETATION] = InstructionSchema(
            question_type=QuestionType.GRAPHIC_INTERPRETATION,
            supported_exams={ExamType.GMAT},
            modes=[
                ModeSchema(
                    mode_name="questionGraph",
                    display_name="Graph Generation",
                    description="Generate graph data and structure",
                    input_format="<GI> - <skill> - <graph_type> - <theme> - <difficulty>",
                    response_type=ResponseType.JSON,
                    output_structure={"graphs": [{"type": "string", "title": "string", "data": "object"}]}
                ),
                ModeSchema(
                    mode_name="questionText",
                    display_name="Question Text with Blanks",
                    description="Generate question with fill-in-the-blank format",
                    input_format="QuestionText",
                    response_type=ResponseType.JSON,
                    output_structure={"question": "string_with_blanks"},
                    depends_on=["questionGraph"]
                ),
                ModeSchema(
                    mode_name="questionTitle",
                    display_name="Question Title Generation",
                    description="Generate title based on graph theme",
                    input_format="QuestionTitle",
                    response_type=ResponseType.JSON,
                    output_structure={"title": "string"},
                    depends_on=["questionGraph", "questionText"]
                ),
                ModeSchema(
                    mode_name="questionOptions",
                    display_name="Blank Options Generation",
                    description="Generate options for each blank",
                    input_format="QuestionOptions",
                    response_type=ResponseType.JSON,
                    output_structure={
                        "options": {
                            "blank_1": {"A": "string", "B": "string", "C": "string"},
                            "blank_2": {"A": "string", "B": "string", "C": "string"}
                        }
                    },
                    depends_on=["questionText"]
                ),
                ModeSchema(
                    mode_name="questionSolution",
                    display_name="Graph Analysis Solution",
                    description="Generate solution with graph interpretation",
                    input_format="QuestionSolution",
                    response_type=ResponseType.PLAIN_TEXT,
                    output_structure={"solution": "plain_text"},
                    depends_on=["questionGraph", "questionText", "questionOptions"]
                ),
                ModeSchema(
                    mode_name="questionAnswer",
                    display_name="Blank Answers",
                    description="Generate correct answers for blanks",
                    input_format="QuestionAnswer",
                    response_type=ResponseType.JSON,
                    output_structure={"answer": {"blank_1": "A|B|C", "blank_2": "A|B|C"}},
                    depends_on=["questionOptions"]
                )
            ],
            execution_order=["questionGraph", "questionText", "questionTitle", "questionOptions", "questionSolution", "questionAnswer"],
            template_requirements={
                "graph_types": "Bar, pie, line, scatter, stacked-bar charts",
                "fill_in_blanks": "Exactly 2 blanks per question",
                "business_data": "Business-relevant graph data"
            }
        )
    
    def _add_numeric_entry_schema(self):
        """Add Numeric Entry instruction schema."""
        self._schemas[QuestionType.NUMERIC_ENTRY] = InstructionSchema(
            question_type=QuestionType.NUMERIC_ENTRY,
            supported_exams={ExamType.GRE},
            modes=[
                ModeSchema(
                    mode_name="questionText",
                    display_name="Question Text Generation",
                    description="Generate numeric entry question",
                    input_format="QuestionText: <topic> - <difficulty>",
                    response_type=ResponseType.JSON,
                    output_structure={"question": "string"}
                ),
                ModeSchema(
                    mode_name="questionTitle",
                    display_name="Question Title Generation",
                    description="Generate question title",
                    input_format="QuestionTitle",
                    response_type=ResponseType.JSON,
                    output_structure={"title": "string"},
                    depends_on=["questionText"]
                ),
                ModeSchema(
                    mode_name="questionSolution",
                    display_name="Solution with Calculation",
                    description="Generate solution with detailed calculation",
                    input_format="QuestionSolution",
                    response_type=ResponseType.PLAIN_TEXT,
                    output_structure={"solution": "plain_text"},
                    depends_on=["questionText"]
                ),
                ModeSchema(
                    mode_name="questionAnswer",
                    display_name="Numeric Answer",
                    description="Generate precise numeric answer",
                    input_format="QuestionAnswer",
                    response_type=ResponseType.JSON,
                    output_structure={"answer": "number"},
                    depends_on=["questionText", "questionSolution"]
                )
            ],
            execution_order=["questionText", "questionTitle", "questionSolution", "questionAnswer"],
            template_requirements={
                "precision": "2 decimal places accuracy",
                "calculation_focus": "Mathematical computation emphasis",
                "academic_context": "Graduate-level mathematical scenarios"
            }
        )
    
    def get_schema(self, question_type: QuestionType) -> Optional[InstructionSchema]:
        """Get instruction schema for a question type."""
        return self._schemas.get(question_type)
    
    def get_supported_question_types(self) -> Set[QuestionType]:
        """Get all supported question types."""
        return set(self._schemas.keys())
    
    def validate_instruction_sequence(
        self,
        question_type: QuestionType,
        mode_sequence: List[str]
    ) -> Dict[str, Any]:
        """
        Validate an instruction mode sequence.
        
        Args:
            question_type: Question type to validate for
            mode_sequence: Proposed sequence of modes
            
        Returns:
            Validation result with issues and recommendations
        """
        schema = self.get_schema(question_type)
        if not schema:
            return {
                "is_valid": False,
                "issues": [f"Unknown question type: {question_type}"],
                "recommendations": []
            }
        
        issues = schema.validate_mode_sequence(mode_sequence)
        recommendations = []
        
        # Generate recommendations
        if not issues:
            recommended_order = schema.get_execution_order()
            if mode_sequence != recommended_order:
                recommendations.append(f"Consider using recommended order: {recommended_order}")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "recommendations": recommendations,
            "schema_info": {
                "question_type": question_type.value,
                "total_modes": len(schema.modes),
                "required_modes": len(schema.get_required_modes()),
                "recommended_order": schema.get_execution_order()
            }
        }
    
    def get_registry_summary(self) -> Dict[str, Any]:
        """Get comprehensive registry summary."""
        return {
            "total_schemas": len(self._schemas),
            "question_types": [qt.value for qt in self._schemas.keys()],
            "exam_coverage": {
                exam_type.value: len([
                    qt for qt, schema in self._schemas.items() 
                    if exam_type in schema.supported_exams
                ])
                for exam_type in ExamType
            },
            "mode_statistics": {
                qt.value: {
                    "total_modes": len(schema.modes),
                    "required_modes": len(schema.get_required_modes()),
                    "response_types": list(set(mode.response_type.value for mode in schema.modes))
                }
                for qt, schema in self._schemas.items()
            }
        }