"""
Here we will get complete prompt dictionary, we will traverse from every question prompt, generate their respective question components as per given in `question_component_types.json`.
"""

import os
import json
import re
from typing import Optional, List, Dict, Any

from io_utils import get_json, prettify, get_Component_Template, record, append_record
from api_utils import get_gemini_generator
from content_generation_manager import manage_generated_content

all_question_structure = get_json('question_component_types')[0]

def log_generation_stage(exam: str,
                         section: Optional[str] = None,
                         detail: Optional[str] = None) -> None:
    """Print the current generation progress using prettify for readability."""
    segments = [
        f"{prettify('Exam', 'Cyan')}: {prettify(exam, 'Green')}"
    ]
    if section:
        segments.append(
            f"{prettify('Section', 'Cyan')}: {prettify(section, 'Yellow')}"
        )
    if detail:
        segments.append(detail)
    print(f"{prettify('Status', 'Blue')}: " + " | ".join(segments))



from question_manager import ManageQuestionData
from thread_creator import SectionThread

class GenQ:
    """
    Coordinator class. Iterates through exams/sections and delegates 
    generation to ManageQuestionData.
    """
    def __init__(self,
                 prompts_dictionary: dict,
                 max_questions: int = 1) -> None:
        self.prompts_dictionary = prompts_dictionary
        self.max_questions = max_questions
        self.generated_count = 0

    def generate(self) -> dict:
        paper_set = {}
        for exam, sections in self.prompts_dictionary.items():
            self.generated_count = 0
            log_generation_stage(
                exam, detail=prettify('Initializing question generation', 'Magenta')
            )
            paper = {}
            for section_id, section_data in sections.items():
                section = section_data['section']
                log_generation_stage(
                    exam, section, detail=prettify('Generating section content', 'Blue')
                )
                paper[section_id] = {
                    'section': section,
                    'questions': []
                }
                
                # Use SectionThread to process all questions in this section concurrently
                section_thread = SectionThread(exam, section, section_data)
                questions = section_thread.get_work_report()
                
                paper[section_id]['questions'].extend(questions)
                
                # After processing a section, check if the target limit is reached
                if self.generated_count >= self.max_questions:
                    print(f"{prettify('Limit Reached', 'Yellow')}: {self.max_questions} questions generated for {exam}")
                    break
            
            paper_set[exam] = paper
            
            # Save paper to log_json_files/paper/{exam}.json
            paper_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_json_files', 'paper')
            os.makedirs(paper_path, exist_ok=True)
            with open(os.path.join(paper_path, f'{exam}.json'), 'w', encoding='utf-8') as f:
                json.dump(paper, f, indent=2, ensure_ascii=False)
                        
            # Save paper to log_json_files/paper/{exam}.json
            paper_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_json_files', 'paper')
            os.makedirs(paper_path, exist_ok=True)
            with open(os.path.join(paper_path, f'{exam}.json'), 'w', encoding='utf-8') as f:
                json.dump(paper, f, indent=2, ensure_ascii=False)

            paper_set[exam] = paper
        return paper_set