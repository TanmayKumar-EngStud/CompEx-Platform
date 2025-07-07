import random, json, os, re
from typing import Dict, Any, Optional

# Import unified components
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.enums.section_types import SectionType
from core.interfaces.question_generator import BaseQuestionGenerator
from core.components.question_components import create_question_component
from core.components.adapters.gmat_adapter import GMATAdapter


class Generate_MSR(BaseQuestionGenerator):
    """GMAT Multi-Source Reasoning Question Generator using unified architecture."""
    
    def __init__(self, global_state, lock, api_IDX, prompt):
        # Initialize base class with proper types
        super().__init__(
            exam_type=ExamType.GMAT,
            question_type=QuestionType.MULTI_SOURCE_REASONING,
            global_state=global_state,
            lock=lock,
            api_idx=api_IDX,
            prompt=prompt
        )
        
        # MSR-specific initialization
        search = re.search(r"total_child_questions: (\d+)", self.prompt)
        self.total_child_questions = 3
        if search:
            self.total_child_questions = int(search.group(1))
        
        try:
            self.MSR = json.load(open(os.path.join(os.path.dirname(__file__), "../combinations/MSR.json")))
        except FileNotFoundError:
            print("MSR combinations file not found, using default values")
            self.MSR = {}
    
    # Removed _load_default_system_instructions - now uses unified instruction system from base class

    def generate_question(self, prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Generate a GMAT Multi-Source Reasoning question.
        
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
                question_type=QuestionType.MULTI_SOURCE_REASONING,
                llm=self.llm,
                system_instructions=self.system_instructions,
                global_state=self.global_state,
                lock=self.lock,
                prompt=self.prompt,
                exam_type=ExamType.GMAT
            )
            msr = GMATAdapter.adapt_multi_source_reasoning(component)
            
            # Load combinations data
            cn = self.MSR.get("combination_number", 0)
            sources = {"sources": []}
            
            # Generate sources
            for source_index in range(1, 4):
                source_type = random.choice(self.MSR.get("source_types", ["text", "table", "chart"]))
                source = msr.generate_SourceInfo(f"Generate SourceInfo_{source_index} having {source_type} of question: {self.prompt}")
                sources["sources"].append(source)
                cn += 1

            self.question_data["content"] = sources
            self.question_data["title"] = msr.generate_MainQuestionTitle()
            self.question_data["questions"] = []
            
            collective_tags = set()
            
            # Generate child questions
            for source_index in range(1, self.total_child_questions + 1):
                question = {}
                focused_skill = random.choice(self.MSR.get("focused_skill", ["Critical Reasoning"]))
                question_style = random.choice(self.MSR.get("question_style", ["MCQ (5 options MCQ)"]))
                
                # Set difficulty level
                difficulty = self.extract_difficulty_from_prompt()
                difficulty_level = max(1, min(5, difficulty + random.randint(-1, 1)))
                
                question["type"] = question_style
                question["prompt"] = f"ChildQuestion: {source_index} <{focused_skill}> - <{question_style}> - <{difficulty_level}>"
                question["question"] = msr.generate_QuestionText(question["prompt"])
                question["title"] = msr.generate_QuestionTitle(f"ChildQuestionTitle: {source_index}")
                question["solution"] = msr.generate_QuestionSolution(f"ChildQuestionSolution: {source_index}")
                
                # Generate options and answers
                if question_style == "MCQ (5 options MCQ)":
                    options, correct_option = msr.generate_QuestionOptions(f"ChildQuestionOptions: {source_index}", question_style)
                    question["answer"] = options[correct_option] if correct_option in options else list(options.values())[0]
                    options = list(options.values())
                else:
                    answer_data = msr.generate_QuestionOptions(f"ChildQuestionOptions: {source_index}", question_style)
                    question["answer"] = answer_data
                    options = list(answer_data.values()) if isinstance(answer_data, dict) else [str(answer_data)]
                
                # Clean up question style and shuffle options
                question_style_clean = re.sub(r' \(.*?\)', '', question_style)
                random.shuffle(options)
                question["options"] = options
                question["tags"] = [focused_skill, question_style_clean, "MSR", source_type]
                collective_tags.update(question["tags"])
                question["difficulty"] = difficulty_level
                self.question_data["questions"].append(question)

            self.question_data["tags"] = list(collective_tags)
            
            # Save combinations data
            self.MSR["combination_number"] = cn
            try:
                json.dump(self.MSR, open(os.path.join(os.path.dirname(__file__), "../combinations/MSR.json"), "w"))
            except Exception as e:
                print(f"Warning: Failed to save MSR combinations: {e}")
            
            return self.question_data
            
        except Exception as e:
            print(f"Error generating GMAT Multi-Source Reasoning question: {e}")
            return None
    
    def validate_output(self, question_data: Dict[str, Any]) -> bool:
        """
        Validate GMAT Multi-Source Reasoning question format.
        
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
        if not isinstance(content, dict) or "sources" not in content:
            return False
        
        sources = content.get("sources", [])
        if not isinstance(sources, list) or len(sources) != 3:
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
        return [QuestionType.MULTI_SOURCE_REASONING]
    
    def get_exam_type(self) -> ExamType:
        """Get exam type."""
        return ExamType.GMAT


# g = Generate_MSR("<MSR> - <total_child_questions: 3> - <Business> - <difficulty_level: 4>")
# content = g.generate_MSR()
# json.dump(content, open(os.path.join(os.path.dirname(__file__), "MSR-component.json"), "w"))