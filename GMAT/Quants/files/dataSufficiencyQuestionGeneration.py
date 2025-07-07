import random, os, sys, json, re
from typing import Dict, Any, Optional

# Import unified components
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.enums.section_types import SectionType
from core.interfaces.question_generator import BaseQuestionGenerator
from core.components.question_components import create_question_component
from core.components.adapters.gmat_adapter import GMATAdapter


class DataSufficiencyQuestionGeneration(BaseQuestionGenerator):
    """GMAT Data Sufficiency Question Generator using unified architecture."""
    
    def __init__(self, global_state, lock, api_IDX, prompt):
        # Initialize base class with proper types
        super().__init__(
            exam_type=ExamType.GMAT,
            question_type=QuestionType.DATA_SUFFICIENCY,
            global_state=global_state,
            lock=lock,
            api_idx=api_IDX,
            prompt=prompt
        )
    
    # Removed _load_default_system_instructions override - now uses unified instruction system
    def generate_question(self, prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Generate a GMAT Data Sufficiency question.
        
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
                question_type=QuestionType.DATA_SUFFICIENCY,
                llm=self.llm,
                system_instructions=self.system_instructions,
                global_state=self.global_state,
                lock=self.lock,
                prompt=self.prompt,
                exam_type=ExamType.GMAT
            )
            questionContent = GMATAdapter.adapt_data_sufficiency_question(component)
            
            # Generate question content
            passages, statements, question = questionContent.generate_questionText()
            self.question_data["content"] = {"passages": passages, "statements": statements}
            self.question_data["question"] = question
            self.question_data["title"] = questionContent.generate_questionTitle()
            solution, answer = questionContent.generate_questionSolution()
            self.question_data["solution"] = solution
            
            # Set standard Data Sufficiency options
            self.question_data["options"] = [
                "Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient", 
                "Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient", 
                "BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient", 
                "EITHER statement ALONE is sufficient", 
                "Statements (1) and (2) TOGETHER are NOT sufficient"
            ]
            
            # Convert letter answer to full text
            if isinstance(answer, str) and len(answer) == 1 and answer.isalpha():
                answer_index = ord(answer.upper()) - ord("A")
                if 0 <= answer_index < len(self.question_data["options"]):
                    self.question_data["answer"] = self.question_data["options"][answer_index]
                else:
                    self.question_data["answer"] = answer
            else:
                self.question_data["answer"] = answer
            
            return self.question_data
            
        except Exception as e:
            print(f"Error generating GMAT Data Sufficiency question: {e}")
            return None
    
    def validate_output(self, question_data: Dict[str, Any]) -> bool:
        """
        Validate GMAT Data Sufficiency question format.
        
        Args:
            question_data: Generated question data to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["type", "content", "question", "answer", "solution", "options"]
        
        # Check required fields
        for field in required_fields:
            if field not in question_data:
                return False
        
        # Validate content structure
        content = question_data.get("content", {})
        if not isinstance(content, dict):
            return False
        
        if "passages" not in content or "statements" not in content:
            return False
        
        # Validate statements
        statements = content.get("statements")
        if not isinstance(statements, list) or len(statements) != 2:
            return False
        
        # Validate options (should be 5 standard DS options)
        options = question_data.get("options", [])
        if not isinstance(options, list) or len(options) != 5:
            return False
        
        return True
    
    def get_supported_types(self) -> list[QuestionType]:
        """Get supported question types."""
        return [QuestionType.DATA_SUFFICIENCY]
    
    def get_exam_type(self) -> ExamType:
        """Get exam type."""
        return ExamType.GMAT