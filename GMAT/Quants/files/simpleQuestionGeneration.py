import random
import json, os, re
from typing import Dict, Any, Optional

# Import unified components
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.enums.section_types import SectionType
from core.interfaces.question_generator import BaseQuestionGenerator
from core.components.question_components import create_question_component
from core.components.adapters.gmat_adapter import GMATAdapter


class SimpleQuestionGeneration(BaseQuestionGenerator):
    """GMAT Simple/Problem Solving Question Generator using unified architecture."""
    
    def __init__(self, global_state, lock, api_IDX, prompt=None):
        # Initialize base class with proper types
        super().__init__(
            exam_type=ExamType.GMAT,
            question_type=QuestionType.PROBLEM_SOLVING,
            global_state=global_state,
            lock=lock,
            api_idx=api_IDX,
            prompt=prompt or ""
        )
    
    def _load_default_system_instructions(self) -> str:
        """Load GMAT Simple Questions system instructions."""
        instruction_path = os.path.join(
            os.path.dirname(__file__), 
            "../System_instructions/GMAT-Quants-Simple-Questions.txt"
        )
        try:
            with open(instruction_path, "r") as f:
                return f.read()
        except FileNotFoundError:
            print(f"System instructions file not found: {instruction_path}")
            return ""

    def generate_question(self, prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Generate a GMAT Simple/Problem Solving question.
        
        Args:
            prompt: Optional prompt override
            
        Returns:
            Generated question data or None if generation fails
        """
        try:
            # Initialize question data using base class
            self.initialize_question_data(prompt)
            
            # Create unified component and wrap with GMAT adapter
            component = create_question_component(
                question_type=QuestionType.PROBLEM_SOLVING,
                llm=self.llm,
                system_instructions=self.system_instructions,
                global_state=self.global_state,
                lock=self.lock,
                prompt=self.prompt,
                exam_type=ExamType.GMAT
            )
            questionContent = GMATAdapter.adapt_simple_question(component)
            
            # Generate question text
            question = questionContent.generate_questionText(self.prompt)
            self.question_data["question"] = question if question else ""

            # Generate title
            title = questionContent.generate_questionTitle()
            self.question_data["title"] = title if title else "GMAT Quants Question"

            # Generate solution
            solution = questionContent.generate_questionSolution()
            self.question_data["solution"] = solution if solution else "Solution not available"

            # Generate options and answer
            options, answer = questionContent.generate_questionOptions()
            if options and isinstance(options, dict):
                options_list = list(options.values())
                random.shuffle(options_list)
                self.question_data["options"] = options_list
                self.question_data["answer"] = options.get(answer, options_list[0] if options_list else "")
            else:
                self.question_data["options"] = ["Option A", "Option B", "Option C", "Option D"]
                self.question_data["answer"] = "Option A"

            return self.question_data
            
        except Exception as e:
            print(f"Error generating GMAT Simple question: {e}")
            return None
    
    def validate_output(self, question_data: Dict[str, Any]) -> bool:
        """
        Validate GMAT Simple question format.
        
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
        if not isinstance(options, list) or len(options) < 2:
            return False
        
        # Validate answer is in options
        answer = question_data.get("answer", "")
        if answer not in options:
            return False
        
        return True
    
    def get_supported_types(self) -> list[QuestionType]:
        """Get supported question types."""
        return [QuestionType.PROBLEM_SOLVING]
    
    def get_exam_type(self) -> ExamType:
        """Get exam type."""
        return ExamType.GMAT
