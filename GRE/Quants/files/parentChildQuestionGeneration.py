import os, json, re, random
from typing import Dict, Any, Optional

# Import unified components
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.enums.section_types import SectionType
from core.interfaces.question_generator import BaseQuestionGenerator
from core.components.question_components import ParentChildQuestion
from core.components.adapters.gre_adapter import GREAdapter


class ParentChildQuestionGeneration(BaseQuestionGenerator):
    """GRE Quantitative Parent-Child Question Generator using unified architecture."""
    
    def __init__(self, global_state, lock, api_IDX, prompt):
        # Initialize base class with proper types
        super().__init__(
            exam_type=ExamType.GRE,
            question_type=QuestionType.READING_COMPREHENSION,  # Using RC for parent-child structure
            global_state=global_state,
            lock=lock,
            api_idx=api_IDX,
            prompt=prompt
        )
        
        # Extract total child questions from prompt
        match = re.search(r"parent_child-(\d+)", prompt)
        self.total_child_questions = int(match.group(1)) if match else 2
        self.prompt = re.sub(
            r"parent_child-(\d+)", 
            f'total child questions that you would have to generate for this parentChildQuestion will be {self.total_child_questions} so prepare other question data accordigly, prompt: ', 
            prompt
        )
    
    # Removed _load_default_system_instructions - now uses unified instruction system from base class

    def generate_question(self, prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Generate a GRE Quantitative Parent-Child question.
        
        Args:
            prompt: Optional prompt override
            
        Returns:
            Generated question data or None if generation fails
        """
        try:
            # Initialize question data using base class
            self.initialize_question_data(prompt)
            
            # Set GRE PS specific type
            self.question_data["type"] = "PS"
            
            # Create base component and adapt for GRE
            base_component = ParentChildQuestion(
                self.llm, 
                self.system_instructions, 
                self.global_state, 
                self.lock, 
                self.prompt
            )
            parentChildQuestion = GREAdapter.adapt_parent_child_question(base_component)
            
            # Generate parent content
            content = parentChildQuestion.generate_questionGraph()
            self.question_data["content"] = content
            self.question_data["title"] = parentChildQuestion.generate_parentTitle()
            
            # Generate child questions
            self.question_data["questions"] = []
            for i in range(self.total_child_questions):
                childQuestionData = {
                    "type": "PS",
                    "prompt": self.prompt,
                    "number": i + 1,
                    "question": parentChildQuestion.generate_childQuestion(i + 1),
                    "title": parentChildQuestion.generate_childQuestionTitle(i + 1),
                    "solution": parentChildQuestion.generate_childSolution(i + 1),
                    "tags": self.extract_tags_from_prompt(),
                    "difficulty": self.extract_difficulty_from_prompt()
                }
                
                # Generate options and answer
                options, answer = parentChildQuestion.generate_childOptions(i + 1)
                
                # Handle None options or empty options
                if options is None:
                    options = []
                
                # Check if options is already a list (from new unified system) or dict (from old system)
                if isinstance(options, list):
                    option_list = options
                    childQuestionData["answer"] = answer if answer in options else (options[0] if options else "")
                elif isinstance(options, dict):
                    option_list = list(options.values())
                    childQuestionData["answer"] = options[answer] if answer in options else (option_list[0] if option_list else "")
                else:
                    option_list = []
                    childQuestionData["answer"] = ""
                
                random.shuffle(option_list)
                childQuestionData["options"] = option_list
                
                self.question_data["questions"].append(childQuestionData)
            
            return self.question_data
            
        except Exception as e:
            print(f"Error generating GRE Quantitative Parent-Child question: {e}")
            return None
    
    def validate_output(self, question_data: Dict[str, Any]) -> bool:
        """
        Validate GRE Quantitative Parent-Child question format.
        
        Args:
            question_data: Generated question data to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["type", "content", "questions", "title"]
        
        # Check required fields
        for field in required_fields:
            if field not in question_data:
                return False
        
        # Validate questions array
        questions = question_data.get("questions", [])
        if not isinstance(questions, list) or len(questions) == 0:
            return False
        
        # Validate each child question
        for question in questions:
            if not isinstance(question, dict):
                return False
            required_question_fields = ["type", "question", "options", "answer"]
            for field in required_question_fields:
                if field not in question:
                    return False
        
        return True
    
    def get_supported_types(self) -> list[QuestionType]:
        """Get supported question types."""
        return [QuestionType.READING_COMPREHENSION]  # Using RC for parent-child structure
    
    def get_exam_type(self) -> ExamType:
        """Get exam type."""
        return ExamType.GRE
