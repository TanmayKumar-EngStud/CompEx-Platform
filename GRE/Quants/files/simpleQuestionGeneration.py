import os, json, re, random
from typing import Dict, Any, Optional

# Import unified components
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.enums.section_types import SectionType
from core.interfaces.question_generator import BaseQuestionGenerator
from core.components.question_components import create_question_component
from core.components.adapters.gre_adapter import GREAdapter


class SimpleQuestionGeneration(BaseQuestionGenerator):
    """GRE Quantitative Simple Question Generator using unified architecture."""
    
    def __init__(self, global_state, lock, api_IDX, prompt):
        # Initialize base class with proper types
        super().__init__(
            exam_type=ExamType.GRE,
            question_type=QuestionType.PROBLEM_SOLVING,
            global_state=global_state,
            lock=lock,
            api_idx=api_IDX,
            prompt=prompt
        )
    
    # Removed _load_default_system_instructions - now uses unified instruction system from base class

    def generate_question(self, prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Generate a GRE Quantitative Simple question.
        
        Args:
            prompt: Optional prompt override
            
        Returns:
            Generated question data or None if generation fails
        """
        try:
            # Initialize question data using base class
            self.initialize_question_data(prompt)
            
            # Determine question type
            if "(multi-correct MCQ)" in self.prompt:
                self.question_data["type"] = "MCQ-Multi"
            else:
                self.question_data["type"] = "MCQ-Single"
            
            # Create unified component and wrap with GRE adapter
            component = create_question_component(
                question_type=QuestionType.PROBLEM_SOLVING,
                llm=self.llm,
                system_instructions=self.system_instructions,
                global_state=self.global_state,
                lock=self.lock,
                prompt=self.prompt,
                exam_type=ExamType.GRE
            )
            questionContent = GREAdapter.adapt_simple_question(component)
            
            # Generate question components
            self.question_data["question"] = questionContent.generate_questionText()
            self.question_data["title"] = questionContent.generate_questionTitle()
            self.question_data["solution"] = questionContent.generate_questionSolution()
            
            # Generate options and answers
            options, answer = questionContent.generate_questionOptions()
            
            # Check if options is already a list (from new unified system) or dict (from old system)
            if isinstance(options, list):
                options_list = options
            elif isinstance(options, dict):
                options_list = list(options.values())
            else:
                options_list = []
                
            if isinstance(answer, list):
                ans = []
                for i in answer:
                    if isinstance(options, dict) and i in options:
                        ans.append(options[i])
                    elif i in options_list:
                        ans.append(i)
                self.question_data["answer"] = ans
            else:
                if isinstance(options, dict) and answer in options:
                    self.question_data["answer"] = options[answer]
                elif answer in options_list:
                    self.question_data["answer"] = answer
                else:
                    self.question_data["answer"] = options_list[0] if options_list else ""
            
            random.shuffle(options_list)
            self.question_data["options"] = options_list
            
            return self.question_data
            
        except Exception as e:
            print(f"Error generating GRE Quantitative Simple question: {e}")
            return None
    
    def validate_output(self, question_data: Dict[str, Any]) -> bool:
        """
        Validate GRE Quantitative Simple question format.
        
        Args:
            question_data: Generated question data to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["type", "question", "answer", "solution", "options"]
        
        # Check required fields
        for field in required_fields:
            if field not in question_data:
                return False
        
        # Validate options
        options = question_data.get("options", [])
        if not isinstance(options, list) or len(options) == 0:
            return False
        
        # Validate answer
        answer = question_data.get("answer")
        if answer is None:
            return False
        
        return True
    
    def get_supported_types(self) -> list[QuestionType]:
        """Get supported question types."""
        return [QuestionType.PROBLEM_SOLVING]
    
    def get_exam_type(self) -> ExamType:
        """Get exam type."""
        return ExamType.GRE