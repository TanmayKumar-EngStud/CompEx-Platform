import os, json, re
from typing import Dict, Any, Optional

# Import unified components
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.enums.section_types import SectionType
from core.interfaces.question_generator import BaseQuestionGenerator
from core.components.question_components import DataSufficiencyQuestion
from core.components.adapters.gre_adapter import GREAdapter


class DataSufficiencyQuestionGeneration(BaseQuestionGenerator):
    """GRE Data Sufficiency Question Generator using unified architecture."""
    
    def __init__(self, global_state, lock, api_IDX, prompt):
        # Initialize base class with proper types
        super().__init__(
            exam_type=ExamType.GRE,
            question_type=QuestionType.DATA_SUFFICIENCY,
            global_state=global_state,
            lock=lock,
            api_idx=api_IDX,
            prompt=prompt
        )
    
    # Removed _load_default_system_instructions - now uses unified instruction system from base class
    def generate_question(self, prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Generate a GRE Data Sufficiency question.
        
        Args:
            prompt: Optional prompt override
            
        Returns:
            Generated question data or None if generation fails
        """
        try:
            # Initialize question data using base class
            self.initialize_question_data(prompt)
            
            # Set GRE DS specific type
            self.question_data["type"] = "DS"
            
            # Create base component and adapt for GRE
            base_component = DataSufficiencyQuestion(
                self.llm, 
                self.system_instructions, 
                self.global_state, 
                self.lock, 
                self.prompt
            )
            dataSufficiencyQuestion = GREAdapter.adapt_data_sufficiency_question(base_component)
            
            # Generate question content
            passage, statements, question = dataSufficiencyQuestion.generate_questionText()
            
            # Handle None statements
            if statements is None:
                statements = []
            
            # Handle statements formatting
            if len(statements) == 1:
                value = statements[0]
                match = re.search(r'\bstatement\b[^0-9]*?\b2\b', value, re.IGNORECASE)
                if match:
                    index = match.start()
                    part1 = value[:index]
                    part2 = value[index:]
                    statements = [part1, part2]
                else:
                    raise Exception("Statement 2 not found")
            
            content = {
                "passage": passage,
                "statements": statements
            }
            
            self.question_data["content"] = content
            self.question_data["question"] = question
            self.question_data["title"] = dataSufficiencyQuestion.generate_questionTitle()
            
            # Generate solution and answer using new two-step process
            solution, answer = dataSufficiencyQuestion.generate_questionSolution()
            self.question_data["solution"] = solution
            
            # Set standard GRE DS options
            self.question_data["options"] = [
                "Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient",
                "Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient", 
                "BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient",
                "EITHER statement ALONE is sufficient",
                "Statements (1) and (2) TOGETHER are NOT sufficient"
            ]
            
            # Convert letter answer to option text
            if isinstance(answer, str) and len(answer) == 1:
                answer_index = ord(answer.upper()) - ord("A")
                if 0 <= answer_index < len(self.question_data["options"]):
                    self.question_data["answer"] = self.question_data["options"][answer_index]
                else:
                    self.question_data["answer"] = self.question_data["options"][0]
            else:
                self.question_data["answer"] = answer
            
            return self.question_data
            
        except Exception as e:
            print(f"Error generating GRE Data Sufficiency question: {e}")
            return None
    
    def validate_output(self, question_data: Dict[str, Any]) -> bool:
        """
        Validate GRE Data Sufficiency question format.
        
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
        
        if "passage" not in content or "statements" not in content:
            return False
        
        statements = content.get("statements", [])
        if not isinstance(statements, list) or len(statements) != 2:
            return False
        
        # Validate options
        options = question_data.get("options", [])
        if not isinstance(options, list) or len(options) != 5:
            return False
        
        return True
    
    def get_supported_types(self) -> list[QuestionType]:
        """Get supported question types."""
        return [QuestionType.DATA_SUFFICIENCY]
    
    def get_exam_type(self) -> ExamType:
        """Get exam type."""
        return ExamType.GRE