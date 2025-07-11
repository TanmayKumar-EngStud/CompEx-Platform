import random, re
from typing import Dict, Any, Optional

# Import unified components
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.enums.section_types import SectionType
from core.interfaces.question_generator import BaseQuestionGenerator
from core.components.question_components import ParentChildQuestion
from core.components.adapters.gre_adapter import GREAdapter


class ParentChildQuestionGeneration(BaseQuestionGenerator):
    """GRE Verbal Parent-Child Question Generator using unified architecture."""
    def generate_child_prompt(self, idx):
        """
        Generate child prompts by parsing focused skills from parent prompt.
        
        Args:
            idx: Number of child questions to generate
            
        Returns:
            List of child prompts
        """
        prompts = []
        
        # Parse focused skills from parent prompt
        focused_skills = self.parse_focused_skills_from_parent_prompt()
        
        # Generate child prompts using the nomenclature: "RC ChildQuestion - <focused_skill>"
        for i in range(idx):
            if i < len(focused_skills):
                focused_skill = focused_skills[i]
            else:
                # If we need more child questions than skills provided, cycle through them
                focused_skill = focused_skills[i % len(focused_skills)] if focused_skills else "Main Idea Question"
            
            child_prompt = f"RC ChildQuestion - {focused_skill}"
            prompts.append(child_prompt)
        
        return prompts
    
    def parse_focused_skills_from_parent_prompt(self):
        """
        Parse focused skills from parent prompt based on GRE nomenclature.
        
        Expected format: <rc-s/rc-m/rc-l> - <theme> - <focused_skill_1/focused_skill_2/focused_skill_3> - <difficulty_level>
        
        Returns:
            List of focused skills
        """
        try:
            # Split the prompt by ' - '
            parts = self.prompt.split(' - ')
            
            if len(parts) >= 3:
                # The third part should contain focused skills
                focused_skills_part = parts[2]
                
                # Split by '/' to get individual skills
                if '/' in focused_skills_part:
                    skills = [skill.strip() for skill in focused_skills_part.split('/')]
                else:
                    skills = [focused_skills_part.strip()]
                
                # Remove any angle brackets
                skills = [skill.strip('<>') for skill in skills]
                
                return skills
            
        except Exception as e:
            print(f"Error parsing focused skills from prompt: {e}")
        
        return ["Main Idea Question"]  # Default fallback
    def __init__(self, global_state, lock, api_IDX, prompt):
        # Initialize base class with proper types
        super().__init__(
            exam_type=ExamType.GRE,
            question_type=QuestionType.READING_COMPREHENSION,
            global_state=global_state,
            lock=lock,
            api_idx=api_IDX,
            prompt=prompt
        )
    
    # Removed _load_default_system_instructions - now uses unified instruction system from base class

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
        Generate a GRE Verbal Parent-Child question.
        
        Args:
            prompt: Optional prompt override
            
        Returns:
            Generated question data or None if generation fails
        """
        try:
            # Initialize question data using base class
            self.initialize_question_data(prompt)
            
            # Set GRE RC specific type
            self.question_data["type"] = "RC"
            
            # Create base component and adapt for GRE
            base_component = ParentChildQuestion(
                self.llm, 
                self.system_instructions, 
                self.global_state, 
                self.lock, 
                self.prompt
            )
            parentChildQuestion = GREAdapter.adapt_parent_child_question(base_component)
            
            # Generate passages
            passages = parentChildQuestion.generate_passages()
            self.question_data["content"] = {"passages": passages}
            self.question_data["title"] = parentChildQuestion.generate_parentTitle()
            
            # Determine number of child questions based on prompt
            total_child_questions = 2  # default
            if "rc-s" in self.prompt.lower():
                total_child_questions = 2
                self.question_data["tags"] = ["rc-s"]
            elif "rc-m" in self.prompt.lower():
                total_child_questions = 3
                self.question_data["tags"] = ["rc-m"]
            elif "rc-l" in self.prompt.lower():
                total_child_questions = 4
                self.question_data["tags"] = ["rc-l"]
            else:
                self.question_data["tags"] = ["rc"]
            
            # Generate child prompts
            child_prompts = self.generate_child_prompt(total_child_questions)
            
            # Generate child questions
            self.question_data["questions"] = []
            for i in range(total_child_questions):
                childQuestionData = {
                    "type": "RC",
                    "prompt": child_prompts[i],
                    "question": parentChildQuestion.generate_childQuestion(i, child_prompts[i]),
                    "title": parentChildQuestion.generate_childQuestionTitle(i),
                    "solution": parentChildQuestion.generate_childSolution(i),
                    "tags": [child_prompts[i].split("-")[0]] if "-" in child_prompts[i] else ["RC"],
                    "difficulty": int(child_prompts[i].split("-")[1].strip()) if "-" in child_prompts[i] and len(child_prompts[i].split("-")) > 1 else self.extract_difficulty_from_prompt()
                }
                
                # Generate options and answers
                options, answer = parentChildQuestion.generate_childOptions(i)
                if isinstance(answer, str):
                    childQuestionData["answer"] = options[answer] if answer in options else list(options.values())[0]
                else:
                    answers = []
                    option_idx = 0
                    for ans in answer:
                        if isinstance(options, list) and option_idx < len(options):
                            if isinstance(options[option_idx], dict) and ans in options[option_idx]:
                                answers.append(options[option_idx][ans])
                        option_idx += 1
                    childQuestionData["answer"] = answers
                
                childQuestionData["options"] = self.shuffle_options(options)
                
                # Extend main tags with child tags
                if "tags" not in self.question_data:
                    self.question_data["tags"] = []
                self.question_data["tags"].extend(childQuestionData["tags"])
                self.question_data["questions"].append(childQuestionData)
            
            return self.question_data
            
        except Exception as e:
            print(f"Error generating GRE Verbal Parent-Child question: {e}")
            return None
    
    def validate_output(self, question_data: Dict[str, Any]) -> bool:
        """
        Validate GRE Verbal Parent-Child question format.
        
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
        
        # Validate content structure
        content = question_data.get("content", {})
        if not isinstance(content, dict) or "passages" not in content:
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
        return [QuestionType.READING_COMPREHENSION]
    
    def get_exam_type(self) -> ExamType:
        """Get exam type."""
        return ExamType.GRE