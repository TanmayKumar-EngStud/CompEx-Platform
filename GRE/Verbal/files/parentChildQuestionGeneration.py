import random, math, os, json, re
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
        child_prompt = json.load(open(os.path.join(os.path.dirname(__file__), "../combinations/child-combination.json"), "r"))
        prompts = []
        t = child_prompt["combination number"]
        indexes = []
        for i in range(idx):
            option = child_prompt["reading comprehension"]
            idx = t%len(option)
            counter = 0
            for j in indexes:
                if j <= idx+counter:
                    counter += 1
            indexes.append((idx+counter)%len(option))
            t = math.floor(t/len(option))
            difficulty = random.randint(1, 5)
            prompts.append(f"{option[idx]} - {difficulty}")
        child_prompt["combination number"] += 1
        json.dump(child_prompt, open(os.path.join(os.path.dirname(__file__), "../combinations/child-combination.json"), "w"))
        # print(f"indexes: {indexes}")
        return prompts
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