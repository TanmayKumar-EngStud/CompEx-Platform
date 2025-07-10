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
from core.template import (
    QuestionMetadata,
    QuestionText,
    QuestionTitle,
    QuestionSolution,
    QuestionOptions,
    QuestionAnswer
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
        self.question_metadata = QuestionMetadata()
        self.question_text = QuestionText()
        self.question_title = QuestionTitle()
        self.question_solution = QuestionSolution()
        self.question_options = QuestionOptions()
        self.question_answer = QuestionAnswer()
    
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
    
    def get_metadata_template(
        self, 
        question_type: QuestionType, 
        prompt: str,
        customizations: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get appropriate metadata template for GRE questions.
        
        Args:
            question_type: Question type classification
            prompt: Original prompt for context
            customizations: Exam-specific customizations
            
        Returns:
            Processed metadata template
        """
        if question_type == QuestionType.READING_COMPREHENSION:
            return self.question_metadata.passage(
                self.exam_type, question_type, customizations, prompt
            )
        elif "parent" in prompt.lower() and "quant" in prompt.lower():
            return self.question_metadata.graph(
                self.exam_type, question_type, customizations, prompt
            )
        elif question_type == QuestionType.QUANTITATIVE_COMPARISON:
            return self.question_metadata.graph(
                self.exam_type, question_type, customizations, prompt
            )
        elif "parent" in prompt.lower() or "child" in prompt.lower():
            return self.question_metadata.parent_stimulus(
                self.exam_type, question_type, customizations, prompt
            )
        else:
            return self.question_metadata.generic(
                self.exam_type, question_type, customizations, prompt
            )
    
    def get_text_template(
        self, 
        question_type: QuestionType, 
        prompt: str,
        customizations: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get appropriate text template for GRE questions.
        
        Args:
            question_type: Question type classification
            prompt: Original prompt for context
            customizations: Exam-specific customizations
            
        Returns:
            Processed text template
        """
        if question_type == QuestionType.NUMERIC_ENTRY:
            return self.question_text.numeric_entry(
                self.exam_type, question_type, customizations, prompt
            )
        elif "child" in prompt.lower():
            return self.question_text.child_question(
                self.exam_type, question_type, customizations, prompt
            )
        else:
            return self.question_text.generic(
                self.exam_type, question_type, customizations, prompt
            )
    
    def get_solution_template(
        self, 
        question_type: QuestionType, 
        prompt: str,
        customizations: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get appropriate solution template for GRE questions.
        
        Args:
            question_type: Question type classification
            prompt: Original prompt for context
            customizations: Exam-specific customizations
            
        Returns:
            Processed solution template
        """
        return self.question_solution.generic(
            self.exam_type, question_type, customizations, prompt
        )
    
    def get_options_template(
        self, 
        question_type: QuestionType, 
        prompt: str,
        customizations: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get appropriate options template for GRE questions.
        
        Args:
            question_type: Question type classification
            prompt: Original prompt for context
            customizations: Exam-specific customizations
            
        Returns:
            Processed options template
        """
        if question_type == QuestionType.SENTENCE_EQUIVALENCE:
            return self.question_options.sentence_equivalence(
                self.exam_type, question_type, customizations, prompt
            )
        elif question_type == QuestionType.TEXT_COMPLETION:
            return self.question_options.text_completion(
                self.exam_type, question_type, customizations, prompt
            )
        elif "true" in prompt.lower() or "false" in prompt.lower():
            return self.question_options.dichotomous_choice(
                self.exam_type, question_type, customizations, prompt
            )
        else:
            return self.question_options.generic(
                self.exam_type, question_type, customizations, prompt
            )
    
    def get_answer_template(
        self, 
        question_type: QuestionType, 
        prompt: str,
        customizations: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get appropriate answer template for GRE questions.
        
        Args:
            question_type: Question type classification
            prompt: Original prompt for context
            customizations: Exam-specific customizations
            
        Returns:
            Processed answer template
        """
        # GRE questions typically don't use separate answer templates
        # Parameters are included for interface compatibility
        return ""


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
    
    def generate_questionOptions(self, num_options: Optional[int] = None) -> Tuple[Dict[str, str], str]:
        """Generate question options (GRE naming convention)."""
        # The base component doesn't use num_options parameter, but we accept it for compatibility
        _ = num_options  # Explicitly mark as unused
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
        return self.component.generate_question_metadata()
    
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
    
    def generate_passages(self) -> Optional[str]:
        """Generate passages for reading comprehension (GRE naming convention)."""
        # For RC questions, we need to generate the passage content
        # This should use the question metadata functionality, Here we also need to add the value of i and total for telling which passage number and what are the total number of passages.
        graph = self.component.generate_question_metadata()
        if graph and isinstance(graph, dict):
            return graph.get('passage') or graph.get('passages') or graph.get('content')
        return None