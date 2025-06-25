import random, os, json, re
from typing import Dict, Any, Optional

# Import unified components
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.enums.section_types import SectionType
from core.interfaces.question_generator import BaseQuestionGenerator
from core.components.question_components import SimpleQuestion
from core.components.adapters.gre_adapter import GREAdapter


class SimpleQuestionGeneration(BaseQuestionGenerator):
    """GRE Verbal Simple Question Generator using unified architecture."""
    
    def __init__(self, global_state, lock, api_IDX, prompt):
        # Initialize base class with proper types
        super().__init__(
            exam_type=ExamType.GRE,
            question_type=QuestionType.TEXT_COMPLETION,  # Default, will be refined based on prompt
            global_state=global_state,
            lock=lock,
            api_idx=api_IDX,
            prompt=prompt
        )
        
        # Load SE-specific instructions if needed
        if "SE" in prompt:
            se_instruction_path = os.path.join(
                os.path.dirname(__file__), 
                "../System_instructions/GRE-Verbal-SE.txt"
            )
            try:
                with open(se_instruction_path, "r") as f:
                    self.system_instructions = f.read()
            except FileNotFoundError:
                print(f"SE instruction file not found: {se_instruction_path}")
    
    def _load_default_system_instructions(self) -> str:
        """Load GRE Verbal Simple system instructions."""
        instruction_path = os.path.join(
            os.path.dirname(__file__), 
            "../System_instructions/GRE-Verbal-Simple-Questions.txt"
        )
        try:
            with open(instruction_path, "r") as f:
                return f.read()
        except FileNotFoundError:
            print(f"System instructions file not found: {instruction_path}")
            return ""

    def shuffle_options(self,options):
        option_list = []
        if isinstance(options, dict):
            # Shuffle the values of the dictionary
            option_list = list(options.values())
            random.shuffle(option_list)
        elif isinstance(options, list):
            # Shuffle values of each inner dictionary and convert to list of lists
            for inner_dict in options:
                shuffled_values = list(inner_dict.values())
                random.shuffle(shuffled_values)
                option_list.append(shuffled_values)
        return option_list

    def generate_question(self, prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Generate a GRE Verbal Simple question.
        
        Args:
            prompt: Optional prompt override
            
        Returns:
            Generated question data or None if generation fails
        """
        try:
            # Initialize question data using base class
            self.initialize_question_data(prompt)
            
            # Create base component and adapt for GRE
            base_component = SimpleQuestion(
                self.llm, 
                self.system_instructions, 
                self.global_state, 
                self.lock, 
                self.prompt
            )
            questionContent = GREAdapter.adapt_simple_question(base_component)
            
            # Generate question content
            self.question_data["question"] = questionContent.generate_questionText()
            self.question_data["title"] = questionContent.generate_questionTitle()
            
            # Determine question type and number of options
            num_options = 6  # default
            if "tc-1" in self.prompt.lower():
                self.question_data["type"] = "TC-1"
                num_options = 6
            elif "tc-2" in self.prompt.lower():
                self.question_data["type"] = "TC-2"
                num_options = 8
            elif "tc-3" in self.prompt.lower():
                self.question_data["type"] = "TC-3"
                num_options = 12
            elif "se" in self.prompt.lower():
                self.question_data["type"] = "SE"
                num_options = 6
            else:
                self.question_data["type"] = "TC"
            
            # Generate options and answers
            options, answer = questionContent.generate_questionOptions(num_options)
            
            if isinstance(answer, str):
                self.question_data["answer"] = options[answer] if answer in options else list(options.values())[0]
            else:
                answers = []
                if "<se>" in self.prompt.lower() and isinstance(answer, list) and len(answer) >= 2:
                    answers.append(options[answer[0]] if answer[0] in options else list(options.values())[0])
                    answers.append(options[answer[1]] if answer[1] in options else list(options.values())[1])
                else:
                    option_idx = 0
                    for ans in answer:
                        if isinstance(options, list) and option_idx < len(options):
                            if isinstance(options[option_idx], dict) and ans in options[option_idx]:
                                answers.append(options[option_idx][ans])
                        elif isinstance(options, dict) and ans in options:
                            answers.append(options[ans])
                        option_idx += 1
                self.question_data["answer"] = answers
            
            self.question_data["options"] = self.shuffle_options(options)
            self.question_data["solution"] = questionContent.generate_questionSolution()
            
            # Extract theme and type as tags
            try:
                prompt_parts = self.prompt.split(" - ")
                if len(prompt_parts) >= 2:
                    theme = prompt_parts[0].strip().strip("<>").lower()
                    question_type = prompt_parts[1].strip("<>").lower()
                    self.question_data["tags"] = [theme, question_type]
                else:
                    self.question_data["tags"] = self.extract_tags_from_prompt()
            except Exception as e:
                print(f"Error extracting tags from prompt: {e}")
                self.question_data["tags"] = ["Simple"]
            
            return self.question_data
            
        except Exception as e:
            print(f"Error generating GRE Verbal Simple question: {e}")
            return None
    
    def validate_output(self, question_data: Dict[str, Any]) -> bool:
        """
        Validate GRE Verbal Simple question format.
        
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
        if not isinstance(options, (list, dict)) or len(options) == 0:
            return False
        
        # Validate answer
        answer = question_data.get("answer")
        if answer is None:
            return False
        
        return True
    
    def get_supported_types(self) -> list[QuestionType]:
        """Get supported question types."""
        return [QuestionType.TEXT_COMPLETION, QuestionType.SENTENCE_EQUIVALENCE]
    
    def get_exam_type(self) -> ExamType:
        """Get exam type."""
        return ExamType.GRE