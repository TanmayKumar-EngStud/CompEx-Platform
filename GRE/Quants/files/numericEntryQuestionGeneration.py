import json, re, os
from typing import Dict, Any, Optional

# Import unified components
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.enums.section_types import SectionType
from core.interfaces.question_generator import BaseQuestionGenerator
from core.components.question_components import create_question_component
from core.components.adapters.gre_adapter import GREAdapter


class NumericEntryQuestionGeneration(BaseQuestionGenerator):
    """GRE Numeric Entry Question Generator using unified architecture."""
    
    def __init__(self, global_state, lock, api_IDX, prompt):
        # Initialize base class with proper types
        super().__init__(
            exam_type=ExamType.GRE,
            question_type=QuestionType.NUMERIC_ENTRY,
            global_state=global_state,
            lock=lock,
            api_idx=api_IDX,
            prompt=prompt
        )
        self._content_types = self._load_content_types()
    
    def _load_content_types(self) -> list:
        """Load supported content types from GRE customizations."""
        try:
            customizations_path = os.path.join(
                os.path.dirname(__file__), "..", "..", "..", 
                "system_instructions", "gre", "customizations.json"
            )
            
            with open(customizations_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Extract content types from numeric entry section
            content_types = config.get("quants", {}).get("numeric entry", {}).get("graphType/TableType", [])
            # Filter out null values and return list of valid content types
            return [ct for ct in content_types if ct is not None]
            
        except Exception as e:
            print(f"Warning: Could not load GRE content types from customizations.json: {e}")
            # Fallback to basic types
            return ["graph", "table", "bar_chart", "pie_chart", "line_chart", "scatter_plot"]
    
    # Removed _load_default_system_instructions - now uses unified instruction system from base class
   
    def generate_question(self) -> Optional[Dict[str, Any]]:
        """
        Generate a GRE Numeric Entry question.
        
        Args:
            prompt: Optional prompt override
            
        Returns:
            Generated question data or None if generation fails
        """
        try:
            # Initialize question data using base class
            self.initialize_question_data(self.prompt)
            
            # Set GRE NE specific type
            self.question_data["type"] = "NE"
            
            # Check if question needs graph/table content based on loaded content types
            if any(content_type in self.prompt.lower() for content_type in self._content_types):
                # Create parent-child component for graph/table content
                pc_component = create_question_component(
                    question_type=QuestionType.READING_COMPREHENSION,
                    llm=self.llm,
                    system_instructions=self.system_instructions,
                    global_state=self.global_state,
                    lock=self.lock,
                    prompt=self.prompt,
                    exam_type=ExamType.GRE
                )
                numericEntryQuestion = GREAdapter.adapt_parent_child_question(self.prompt, pc_component)
                content = numericEntryQuestion.generate_questionGraph()
                self.question_data["content"] = content
            
            # Create simple question component for numeric entry
            simple_component = create_question_component(
                question_type=QuestionType.NUMERIC_ENTRY,
                llm=self.llm,
                system_instructions=self.system_instructions,
                global_state=self.global_state,
                lock=self.lock,
                prompt=self.prompt,
                exam_type=ExamType.GRE
            )
            numericEntryQuestion = GREAdapter.adapt_simple_question(self.prompt, simple_component)
            
            # Generate question components
            self.question_data["question"] = numericEntryQuestion.generate_questionText()
            self.question_data["title"] = numericEntryQuestion.generate_questionTitle()
            solution, answer = numericEntryQuestion.generate_questionSolution(isNE=True)
            self.question_data["solution"] = solution
            self.question_data["answer"] = answer
            
            return self.question_data
            
        except Exception as e:
            print(f"Error generating GRE Numeric Entry question: {e}")
            return None
    
    def validate_output(self, question_data: Dict[str, Any]) -> bool:
        """
        Validate GRE Numeric Entry question format.
        
        Args:
            question_data: Generated question data to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["type", "question", "answer", "solution"]
        
        # Check required fields
        for field in required_fields:
            if field not in question_data:
                return False
        
        # Validate answer is numeric
        answer = question_data.get("answer")
        if answer is None:
            return False
            
        # Answer should be numeric or a string that can be converted to numeric
        try:
            float(answer)
        except (ValueError, TypeError):
            return False
        
        return True
    
    def get_supported_types(self) -> list[QuestionType]:
        """Get supported question types."""
        return [QuestionType.NUMERIC_ENTRY]
    
    def get_exam_type(self) -> ExamType:
        """Get exam type."""
        return ExamType.GRE