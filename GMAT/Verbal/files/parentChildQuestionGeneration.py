# Import unified components
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.enums.section_types import SectionType
from core.interfaces.question_generator import BaseQuestionGenerator, IMultiPartQuestionGenerator
from core.components.question_components import create_question_component
from core.components.adapters.gmat_adapter import GMATAdapter
from google import genai
from dotenv import load_dotenv
import random
import os
import json
import re
import sys
from typing import Dict, Any, Optional

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)


class ParentChildQuestionGeneration(BaseQuestionGenerator):
    def generate_child_prompt(self, idx, difficulty):
        """
        Generate child prompts by parsing focused skills from parent prompt.
        
        Args:
            idx: Number of child questions to generate
            difficulty: Base difficulty level
            
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
        Parse focused skills from parent prompt based on GMAT nomenclature.
        
        Expected format: <rc-s/rc-m/rc-l> - <theme> - <focused_skill_1/focused_skill_2/focused_skill_3> - <vocabulary_level> - <difficulty_level>
        
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
            exam_type=ExamType.GMAT,
            question_type=QuestionType.READING_COMPREHENSION,
            global_state=global_state,
            lock=lock,
            api_idx=api_IDX,
            prompt=prompt
        )
        
        # Parent-child specific initialization
        child_question_numbers = 0
        if "rc_3" in self.prompt.lower():
            child_question_numbers = 3
        elif "rc_4" in self.prompt.lower():
            child_question_numbers = 4
        self.number_of_child_questions = child_question_numbers
        
        difficulty = re.search(r'<difficulty_level: (\d+)>', self.prompt)
        if difficulty:
            difficulty = int(difficulty.group(1))
        else:
            difficulty = 0
        
        self.child_prompt = self.generate_child_prompt(child_question_numbers, difficulty)
    
    # Removed _load_default_system_instructions - now uses unified instruction system from base class

    def generate_question(self, prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Generate a GMAT Reading Comprehension parent-child question.
        
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
                question_type=QuestionType.READING_COMPREHENSION,
                llm=self.llm,
                system_instructions=self.system_instructions,
                global_state=self.global_state,
                lock=self.lock,
                prompt=self.prompt,
                exam_type=ExamType.GMAT
            )
            questionContent = GMATAdapter.adapt_parent_child_question(component)
            
            # Generate parent content
            passages = questionContent.generate_parentQuestion()
            self.question_data["content"] = {"passages": passages}
            self.question_data["title"] = questionContent.generate_parentTitle()

            # Generate child questions
            self.question_data["questions"] = []
            child_question_numbers = len(
                self.child_prompt) if self.child_prompt else random.randint(2, 4)
            
            for i in range(child_question_numbers):
                childQuestionData = {}
                childQuestionData["type"] = "RC"
                childQuestionData["prompt"] = self.child_prompt[i] if i < len(self.child_prompt) else ""
                childQuestionData["question"] = questionContent.generate_childQuestion(
                    i, self.child_prompt[i] if i < len(self.child_prompt) else "")
                childQuestionData["title"] = questionContent.generate_childQuestionTitle(i)
                
                options, answer = questionContent.generate_childOptions(i)
                if options and answer in options:
                    childQuestionData["answer"] = options[answer]
                    options_list = list(options.values())
                    random.shuffle(options_list)
                    childQuestionData["options"] = options_list
                else:
                    childQuestionData["options"] = ["Option A", "Option B", "Option C", "Option D"]
                    childQuestionData["answer"] = "Option A"
                
                childQuestionData["solution"] = questionContent.generate_childSolution(i)
                
                # Extract difficulty from child prompt
                if i < len(self.child_prompt):
                    pattern = r'<difficulty_level: (\d+)>'
                    difficulty = re.search(pattern, self.child_prompt[i])
                    if difficulty:
                        childQuestionData["difficulty"] = int(difficulty.group(1))
                    else:
                        childQuestionData["difficulty"] = self.extract_difficulty_from_prompt()
                else:
                    childQuestionData["difficulty"] = self.extract_difficulty_from_prompt()
                
                # Extract tags from child prompt
                if i < len(self.child_prompt):
                    childQuestionData["tags"] = self.extract_tags_from_prompt(self.child_prompt[i])
                else:
                    childQuestionData["tags"] = self.extract_tags_from_prompt()
                
                self.question_data["questions"].append(childQuestionData)

            return self.question_data
            
        except Exception as e:
            print(f"Error generating GMAT Reading Comprehension question: {e}")
            return None
    
    def validate_output(self, question_data: Dict[str, Any]) -> bool:
        """
        Validate GMAT Reading Comprehension question format.
        
        Args:
            question_data: Generated question data to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["type", "content", "questions"]
        
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
        return ExamType.GMAT
