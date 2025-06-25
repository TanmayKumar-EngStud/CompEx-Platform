"""
GRE-Specific Adapter

This adapter handles GRE-specific behaviors and adaptations for the unified
question components, ensuring backward compatibility with existing GRE
question generators.

Author: Claude Code (Migration CHUNK 2)
Date: 2025-06-25
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.components.question_components import (
    BaseQuestionComponent,
    SimpleQuestion,
    DataSufficiencyQuestion,
    ParentChildQuestion
)


class GREAdapter:
    """
    Adapter class for GRE-specific question generation behaviors.
    
    This adapter ensures that the unified question components behave exactly
    like the original GRE question generators, maintaining backward compatibility.
    """
    
    def __init__(self):
        """Initialize GRE adapter."""
        self.exam_type = ExamType.GRE
    
    @staticmethod
    def adapt_simple_question(component: SimpleQuestion) -> 'GRESimpleQuestionAdapter':
        """Adapt SimpleQuestion for GRE-specific behavior."""
        return GRESimpleQuestionAdapter(component)
    
    @staticmethod
    def adapt_data_sufficiency_question(component: DataSufficiencyQuestion) -> 'GREDataSufficiencyAdapter':
        """Adapt DataSufficiencyQuestion for GRE-specific behavior."""
        return GREDataSufficiencyAdapter(component)
    
    @staticmethod
    def adapt_parent_child_question(component: ParentChildQuestion) -> 'GREParentChildAdapter':
        """Adapt ParentChildQuestion for GRE-specific behavior."""
        return GREParentChildAdapter(component)


class GRESimpleQuestionAdapter:
    """GRE-specific adapter for SimpleQuestion components."""
    
    def __init__(self, component: SimpleQuestion):
        """Initialize with SimpleQuestion component."""
        self.component = component
    
    def generate_questionText(self) -> Optional[str]:
        """Generate question text (GRE naming convention)."""
        return self.component.generate_question_text()
    
    def generate_questionTitle(self) -> Optional[str]:
        """Generate question title (GRE naming convention)."""
        return self.component.generate_question_title()
    
    def generate_questionSolution(self, isNE: bool = False) -> Union[str, Tuple[str, float]]:
        """
        Generate question solution (GRE naming convention).
        
        Args:
            isNE: Whether this is a numeric entry question
            
        Returns:
            Solution string for regular questions, or (solution, answer) tuple for NE
        """
        return self.component.generate_question_solution(is_numeric_entry=isNE)
    
    def generate_questionOptions(self) -> Tuple[List[str], str]:
        """Generate question options (GRE naming convention)."""
        return self.component.generate_question_options()


class GREDataSufficiencyAdapter:
    """GRE-specific adapter for DataSufficiencyQuestion components."""
    
    def __init__(self, component: DataSufficiencyQuestion):
        """Initialize with DataSufficiencyQuestion component."""
        self.component = component
    
    def generate_questionText(self) -> Tuple[Optional[str], Optional[List[str]], Optional[str]]:
        """Generate question text components (GRE format: passage, statements, question)."""
        return self.component.generate_question_text()
    
    def generate_questionTitle(self) -> Optional[str]:
        """Generate question title (GRE naming convention)."""
        return self.component.generate_question_title()
    
    def generate_questionSolution(self) -> Tuple[Optional[str], Optional[str]]:
        """Generate question solution and answer (GRE naming convention)."""
        return self.component.generate_question_solution()
    
    def generate_questionOptions(self) -> Tuple[List[str], str]:
        """Generate question options (GRE naming convention)."""
        return self.component.generate_question_options()


class GREParentChildAdapter:
    """GRE-specific adapter for ParentChildQuestion components."""
    
    def __init__(self, component: ParentChildQuestion):
        """Initialize with ParentChildQuestion component."""
        self.component = component
    
    def generate_questionGraph(self) -> Optional[Dict[str, Any]]:
        """Generate question graph/table (for GRE Quants parent-child questions)."""
        return self.component.generate_question_graph()
    
    def generate_parentTitle(self) -> Optional[str]:
        """Generate parent title (GRE naming convention)."""
        return self.component.generate_parent_title()
    
    def generate_childQuestionTitle(self, index: int) -> Optional[str]:
        """Generate child question title (GRE naming convention)."""
        return self.component.generate_child_question_title(index)
    
    def generate_childQuestion(self, index: int, child_prompt: str = "") -> Optional[str]:
        """Generate child question text (GRE naming convention)."""
        return self.component.generate_child_question(index, child_prompt)
    
    def generate_childOptions(self, index: int) -> Tuple[Optional[List[str]], Optional[str]]:
        """Generate child question options (GRE naming convention)."""
        return self.component.generate_child_options(index)
    
    def generate_childSolution(self, index: int) -> Optional[str]:
        """Generate child question solution (GRE naming convention)."""
        return self.component.generate_child_solution(index)