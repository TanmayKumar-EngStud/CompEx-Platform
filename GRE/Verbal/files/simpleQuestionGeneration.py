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
        # Determine the correct question type based on prompt
        question_type = self._infer_question_type(prompt)
        
        # Initialize base class with proper types
        super().__init__(
            exam_type=ExamType.GRE,
            question_type=question_type,
            global_state=global_state,
            lock=lock,
            api_idx=api_IDX,
            prompt=prompt
        )
        
        # Load SE-specific instructions if needed
        if "<SE>" in prompt or "SE" in prompt:
            se_instruction_path = os.path.join(
                os.path.dirname(__file__), 
                "../System_instructions/GRE-Verbal-SE.txt"
            )
            try:
                with open(se_instruction_path, "r") as f:
                    self.system_instructions = f.read()
            except FileNotFoundError:
                print(f"SE instruction file not found: {se_instruction_path}")
    
    # Removed _load_default_system_instructions - now uses unified instruction system from base class
    
    def _infer_question_type(self, prompt):
        """
        Infer the question type based on the prompt content.
        
        Args:
            prompt: The input prompt string
            
        Returns:
            QuestionType enum value
        """
        prompt_lower = prompt.lower()
        
        # Check for SE (Sentence Equivalence) questions
        if "<se>" in prompt_lower:
            return QuestionType.SENTENCE_EQUIVALENCE
        
        # Check for TC (Text Completion) questions
        if any(tc_type in prompt_lower for tc_type in ["<tc-1>", "<tc-2>", "<tc-3>"]):
            return QuestionType.TEXT_COMPLETION
        
        # Default to TEXT_COMPLETION if no clear identifier found
        return QuestionType.TEXT_COMPLETION

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

    def generate_question(self) -> Optional[Dict[str, Any]]:
        """
        Generate a GRE Verbal Simple question.
        
        Args:
            prompt: Optional prompt override
            
        Returns:
            Generated question data or None if generation fails
        """
        try:
            # Initialize question data using base class
            self.initialize_question_data(self.prompt)
            
            # Create base component and adapt for GRE
            base_component = SimpleQuestion(
                self.llm, 
                self.system_instructions, 
                self.global_state, 
                self.lock, 
                self.prompt,
                exam_type=ExamType.GRE,
                question_type=self.question_type
            )
            questionContent = GREAdapter.adapt_simple_question(self.prompt, base_component)
            
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
            
            # Options should now be in dictionary format from AI
            # Convert values to list for shuffling, but preserve original answer mapping
            if isinstance(options, dict) and isinstance(answer, str):
                # Single answer case
                self.question_data["answer"] = options.get(answer, "")
            elif isinstance(options, dict) and isinstance(answer, list):
                # Multiple answers case (for SE)
                answer_values = []
                for ans_key in answer:
                    if ans_key in options:
                        answer_values.append(options[ans_key])
                self.question_data["answer"] = answer_values
            else:
                # Fallback for unexpected format
                self.question_data["answer"] = answer
            
            self.question_data["options"] = self.shuffle_options(options)
            self.question_data["solution"] = questionContent.generate_questionSolution()
            
            # Extract theme and type as tags
            try:
                prompt_parts = self.prompt.split(" - ")
                if len(prompt_parts) >= 2:
                    # Handle both old format (SE - <theme>) and new format (<SE> - <theme>)
                    first_part = prompt_parts[0].strip().strip("<>").lower()
                    second_part = prompt_parts[1].strip().strip("<>").lower()
                    
                    # Check if first part is a question type code
                    if first_part in ["se", "tc", "tc-1", "tc-2", "tc-3", "rc"]:
                        # New format: <SE> - <theme>
                        question_type = first_part
                        theme = second_part
                    else:
                        # Old format: theme - question_type (fallback)
                        theme = first_part
                        question_type = second_part
                    
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


# Legacy compatibility aliases for factory
V_S_gen = SimpleQuestionGeneration  # For Text Completion
V_SE_gen = SimpleQuestionGeneration  # For Sentence Equivalence