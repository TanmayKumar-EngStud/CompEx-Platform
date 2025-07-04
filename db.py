from prisma import Prisma
import json
import re
from datetime import datetime
from typing import Dict, Any, List


class DB:
    def __init__(self, prisma_client: Prisma):
        self.db = prisma_client
        self.current_exam_id = 0
        self.current_section_id = 0
        self._initialize_primary_tables()

    # initializing IDs
        self.current_problem_id = 0
        self.current_tag_id = 0
        self.current_problemset_id = 0
        self.current_mocktest_id = 0
        self.current_mocksection_id = None
        self.current_mockquestion_number = None
        self.question_type = ""
        self.current_question_type = ""
        self.question_correction_validator = ""
        
        # Define answer type mappings
        self.answer_type_mappings = {
            "Yes/No": {"positive": "Yes", "negative": "No"},
            "Would Help/Would Not Help": {"positive": "Would Help", "negative": "Would Not Help"},
            "True/False": {"positive": "True", "negative": "False"},
            "Inference/Conflicting": {"positive": "Inference", "negative": "Conflicting"},
            "Sufficient/Insufficient": {"positive": "Sufficient", "negative": "Insufficient"},
            "Valid/Invalid": {"positive": "Valid", "negative": "Invalid"},
            "Consistent/Inconsistent": {"positive": "Consistent", "negative": "Inconsistent"},
            "Conclusion/Assumption": {"positive": "Conclusion", "negative": "Assumption"},
            "Acceptable/Not Acceptable": {"positive": "Acceptable", "negative": "Not Acceptable"}
        }
        return None

    def process_table_analysis_answers(self, problem_id: int, answer_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process Table Analysis answers and prepare them for database insertion.
        
        Args:
            problem_id: The ID of the problem
            answer_data: Dictionary containing answer group and options
            
        Returns:
            List of dictionaries containing processed options ready for database insertion
        """
        processed_options = []
        
        # Get the answer group and options
        group = answer_data.get('group')
        options = answer_data.get('options', {})
        
        # Get the mapping for this answer type
        mapping = self.answer_type_mappings.get(group)
        if not mapping:
            raise ValueError(f"Unknown answer group type: {group}")
            
        # Process each option
        for option_text, option_data in options.items():
            is_correct = option_data.get('isCorrect', False)
            value = option_data.get('value')
            
            processed_options.append({
                'problemid': problem_id,
                'optiontext': option_text,
                'iscorrect': is_correct,
                'group': group
            })
            
        return processed_options

    def create_problem_options(self, problem_id: int, answer_data: Dict[str, Any]) -> None:
        """
        Create problem options in the database.
        
        Args:
            problem_id: The ID of the problem
            answer_data: Dictionary containing answer data
        """
        processed_options = self.process_table_analysis_answers(problem_id, answer_data)
        
        # Create all options in the database
        for option in processed_options:
            self.db.problemoptions.create(data=option)

    def _initialize_primary_tables(self):
        """Initialize primary tables if they don't exist"""
        try:
            with open('PrimaryTablesDefinitions.json', 'r') as f:
                self.definitions = json.load(f)

            # Initialize exam types and sections
            for exam_name, exam_data in self.definitions['examtypes'].items():
                # Check if exam type exists
                existing_exam = self.db.examtypes.find_first(
                    where={'examtypeid': exam_data['id']}
                )
                if not existing_exam:
                    print(f"Exam type {exam_name} not found, creating it")
                    exam_type = self.db.examtypes.create(data={
                        'examtypeid': exam_data['id'],
                        'name': exam_name,
                        'description': exam_data['description']
                    })
                    print(f"Exam type {exam_name} created successfully")
                    for section_name, section_data in exam_data['sections'].items():
                        section = self.db.sections.create(data={
                            'sectionid': section_data['id'],
                            'examtypeid': exam_type.examtypeid,
                            'name': section_name,
                            'description': section_data['description']
                        })

            # Initialize primary user if not exists
            existing_user = self.db.users.find_first()
            if not existing_user:
                self.db.users.create(data={
                    'userid': 1,
                    'username': 'admin',
                    'password': 'admin',
                    'email': 'admin@compex.com',
                    'registrationdate': datetime.now()
                })
                print("Primary user created successfully")
            else:
                print("Primary user already exists")

        except Exception as e:
            print(f"Error initializing primary tables: {str(e)}")
            raise

    def _get_exam_section_ids(self, exam_section):
        section_components = {
            "V": "Verbal",
            "Q": "Quants",
            "IR": "Integrated Reasoning"
        }
        
        # Handle empty or malformed exam_section
        if not exam_section or "_" not in exam_section:
            raise ValueError(f"Invalid exam section format: '{exam_section}'. Expected format: 'EXAM_SECTION' (e.g., 'GMAT_Q', 'GRE_V')")
        
        try:
            exam_name, section = exam_section.split("_", 1)  # Split only on first underscore
        except ValueError:
            raise ValueError(f"Invalid exam section format: '{exam_section}'. Expected format: 'EXAM_SECTION'")
        
        # Validate that section is not empty
        if not section:
            raise ValueError(f"Invalid section name: empty section in '{exam_section}'")
            
        try:
            section_name = section_components[section]
        except KeyError:
            raise ValueError(f"Invalid section name: '{section}'. Valid sections are: {list(section_components.keys())}")
            
        exam = self.db.examtypes.find_first(where={'name': exam_name})
        if not exam:
            raise ValueError(f"Exam type not found: '{exam_name}'")
            
        section_obj = self.db.sections.find_first(
            where={'name': section_name, 'examtypeid': exam.examtypeid})
        if not section_obj:
            raise ValueError(f"Section not found: '{section_name}' for exam '{exam_name}'")
            
        self.current_exam_id = int(exam.examtypeid)
        self.current_section_id = int(section_obj.sectionid)
        return None

    def _register_problem(self, exam_section, question, isChildQuestion=False, isMockQuestion=False):
        """Register a single problem"""
        try:
            self._get_exam_section_ids(exam_section)

            # Format metadata as JSON string
            # Format solution

            solution = question.get('solution', {})
            if isinstance(solution, (str, dict)):
                solution = json.dumps({"solution": solution})
            else:
                solution = json.dumps(solution)
            # Create problem with proper Prisma format
            self.question_type = question.get('type', '')
            if (question.get('type', '') == "TA"):
                temp = ""
                type = question.get('prompt', '').split("-")[3].strip()
                if type == "Yes/No":
                    temp = "Yes"
                elif type == "Would Help/Would Not Help":
                    temp = "Would Help"
                elif type == "True/False":
                    temp = "True"
                elif type == "Inference/Conflicting":
                    temp = "Inference"
                elif type == "Sufficient/Insufficient":
                    temp = "Sufficient"
                elif type == "Valid/Invalid":
                    temp = "Valid"
                elif type == "Consistent/Inconsistent":
                    temp = "Consistent"
                elif type == "Conclusion/Assumption":
                    temp = "Conclusion"
                if question['answer'][question['options'][0]] in "Yes/No":
                    temp = "Yes"
                question["content"]["connection_validator"] = temp
                self.question_correction_validator = temp

            # Ensure text field has a value (required field, handle null/empty)
            question_text = question.get('question') or ''
            if not question_text or question_text == '':
                question_text = question.get('title') or 'Question text not available'
            
            # Ensure title field has a value (required field, handle null/empty)
            question_title = question.get('title') or ''
            if not question_title or question_title == '':
                question_title = f"Question {question.get('type', 'Unknown')} - Difficulty {question.get('difficulty', 1)}"
            
            question_data = {
                "type": question.get('type', ''),
                "prompt": question.get('prompt', ''),
                "title": question_title,
                "text": question_text,  # Ensure text field is not empty
                "difficulty": question.get('difficulty', 1),
                "sectionid": self.current_section_id,  # Direct field assignment
                "examtypeid": self.current_exam_id,    # Direct field assignment
                # Prisma will handle JSON conversion
                "metadata": json.dumps(question.get('content', {})),
                "solution": solution,  # Prisma will handle JSON conversion
                "isChildren": isChildQuestion,
                "isMockQuestion": isMockQuestion
            }

            if isChildQuestion:
                question_data["problemsSetId"] = self.current_problemset_id  # Direct field assignment
            if isMockQuestion:
                question_data["mocksectionid"] = self.current_mocksection_id  # Direct field assignment
                question_data["mockquestionnumber"] = self.current_mockquestion_number
            if self.question_type == "NE":
                question_data["metadata"] = json.dumps(
                    {"answer": question.get('answer', '')})

            problem = self.db.problems.create(data=question_data)
            self.current_problem_id = problem.problemid

            options = question.get('options', [])
            answer = question.get('answer', '')
            self.current_question_type = question.get('type', '')
            for option in options:
                if isinstance(option, str):
                    self._register_problem_options(option, answer)
                elif isinstance(option, int):
                    self._register_problem_options(option, answer)
                elif isinstance(option, list):
                    group = "A"
                    for suboption in option:
                        self._register_problem_options(
                            suboption, answer, group)
                        group = chr(ord(group) + 1)

            # Register tags
            self._register_problem_tags(question.get('tags', []))

            return True

        except Exception as e:
            print(
                f"Error in _register_problem: {str(e)}\n\n here is the question content: {json.dumps(question, indent=4)}")
            return False

    def _register_problem_options(self, option, answers, group=None):
        """Register problem options in the database.
        
        Args:
            option: The option text or object
            answers: The correct answers (can be dict, list, or single value)
            group: Optional group identifier for the option
        """
        # Special handling for Table Analysis questions
        if self.current_question_type == "TA":
            # For TA questions, answers should be a dict with format:
            # {"group": "Acceptable/Not Acceptable", "options": {"option1": {"value": "Acceptable", "isCorrect": true}, ...}}
            answer_group = None
            is_correct = False
            
            # Find the appropriate answer group based on the question content
            for group_name, mapping in self.answer_type_mappings.items():
                if mapping["positive"] in str(answers) or mapping["negative"] in str(answers):
                    answer_group = group_name
                    break
            
            # Determine if this option is correct based on the answer mapping
            if isinstance(answers, dict) and option in answers:
                answer_value = answers[option]
                if isinstance(answer_value, dict):
                    is_correct = answer_value.get("isCorrect", False)
                else:
                    # For legacy format where answer is direct value
                    for group_name, mapping in self.answer_type_mappings.items():
                        if answer_value == mapping["positive"]:
                            is_correct = True
                            break
            
            option_data = {
                'optiontext': str(option),
                'iscorrect': is_correct,
                'problemid': self.current_problem_id,  # Direct field assignment
                'group': answer_group if answer_group else group
            }
            
        else:
            # Handle all other question types as before
            correct_answers = []
            if isinstance(answers, dict):
                # First, check if this is a True/False or Yes/No type question with inverted structure
                if "True" in answers or "False" in answers or "Yes" in answers or "No" in answers:
                    for key, value in answers.items():
                        if value == option:
                            is_correct = key.lower() in ["true", "yes"]
                            break
                    else:
                        is_correct = False
                else:
                    # Original code for other questions where option is a key in answers dict
                    finder = self.question_correction_validator
                    ansVal = finder if finder else "Yes"
                    try:
                        if "dicotomous" in self.current_question_type.lower():
                            match = re.search(r"\(([^/]*)(?:/|$)", self.current_question_type)
                            if match:
                                is_correct = answers[match]
                        else:
                            is_correct = answers[option].lower().strip() == ansVal.lower().strip()
                    except KeyError:
                        print(f"Warning: Option '{option}' not found in answers dictionary")
                        is_correct = False
            elif isinstance(answers, list):
                is_correct = option in answers
            else:
                is_correct = option == answers

            option_data = {
                'optiontext': str(option),
                'iscorrect': is_correct,
                'problemid': self.current_problem_id  # Direct field assignment
            }
            if group:
                option_data['group'] = group

        try:
            self.db.problemoptions.create(
                data=option_data
            )
        except Exception as e:
            print(
                f"Error creating problem option in _register_problem_options: {str(e)} \n\n here is the option: {option} \n\n here is the answer: {answers}")
            return False
        return True

    def _register_problem_tags(self, tags):
        try:
            for tag in tags:
                tagid = self._register_tag(tag)  # ✅
                tag_data = {
                    'tagid': tagid,  # Direct field assignment
                    'problemid': self.current_problem_id  # Direct field assignment
                }
                self.db.problemtags.create(data=tag_data)  # ❌
        except Exception as e:
            print(
                f"Error creating problem tags in _register_problem_tags: {str(e)}")
            print(f"here is the value received for tagid: {tagid}")
            return False
        return True

    def _register_problemsset_tags(self, tags):
        try:
            for tag in tags:
                tagid = self._register_tag(tag)
                tag_data = {
                    'tagid': tagid,  # Direct field assignment
                    'problemsSetId': self.current_problemset_id  # Direct field assignment (fix: was using current_problem_id)
                }
                self.db.problemssettags.create(
                    data=tag_data
                )
        except Exception as e:
            print(
                f"Error creating problemset tags in _register_problemsset_tags: {str(e)}")
            return False
        return True

    # ✅
    def _register_tag(self, tag):
        try:
            pattern = r'\(.*?\)'
            tag = re.sub(pattern, '', tag).strip()

            # remove anything after comma
            tag = re.sub(r' ,*', '', tag) if ' ,' in tag else tag
            tagid = self.db.tags.find_first(where={
                'name': tag,
                'examtypeid': self.current_exam_id,
                'sectionid': self.current_section_id
            })  # because two different exams/sections can have same tag
            if tagid:
                return tagid.tagid
            else:
                tag_data = {
                    'name': tag,
                    'examtypeid': self.current_exam_id,  # Direct field assignment
                    'sectionid': self.current_section_id  # Direct field assignment
                }
                tagid = self.db.tags.create(
                    data=tag_data
                )
                return tagid.tagid
        except Exception as e:
            print(f"Error creating tag in _register_tag: {str(e)}")
            print(f"for {self.current_mockquestion_number}")
            print(f"here is the tag value that is causing the issue:- {tag} ")
            return False

    def _register_problemsset(self, exam_section, parent_question, isMockQuestion=False):
        """Register a problem set with its child questions"""
        try:
            self._get_exam_section_ids(exam_section)

            # Ensure required fields have values (handle null/empty)
            title = parent_question.get('title') or ''
            if not title or title == '':
                title = f"{parent_question.get('type', 'Question')} - {exam_section}"
            
            # Determine content type and data
            problemsset_data = {
                'type': parent_question.get('type', ''),
                'content': json.dumps(parent_question.get('content', {})),
                'title': title,  # Ensure title is not empty
                'sectionid': self.current_section_id,    # Direct field assignment (required)
                'examtypeid': self.current_exam_id       # Direct field assignment (required)
            }

            if isMockQuestion:
                problemsset_data['mockquestionnumber'] = self.current_mockquestion_number
                problemsset_data['mocksectionid'] = self.current_mocksection_id  # Direct field assignment

            # Create problem set
            try:
                # Note: Prisma Python client uses lowercase for model names
                problemsset = self.db.problemsset.create(data=problemsset_data)
                self.current_problemset_id = problemsset.problemsSetId
            except Exception as e:
                print(
                    f"Error registering parent question component in _register_problemset: {str(e)} \n\n here is the parent question content: {json.dumps(parent_question.get('content', {}), indent=4)}")
                return False

            # Register child questions
            child_questions = (
                parent_question.get('childQuestions', []) or
                parent_question.get('questions', [])
            )

            for child in child_questions:
                if not self._register_problem(exam_section, child, isChildQuestion=True, isMockQuestion=isMockQuestion):
                    raise Exception("Error registering child problem")

            self.current_problemset_id += 1
            return True

        except Exception as e:
            print(f"Error in _register_problemset: {str(e)}")
            return False

    def having_any_empty_value(self, component):
        if not component:
            return False  # None
        if isinstance(component, int) or isinstance(component, float):
            return True
        if isinstance(component, list):
            if len(component):
                for cell in component:
                    val = self.having_any_empty_value(cell)
                    if not val:
                        return False
                return True
            return False  # []
        if isinstance(component, str):
            if len(component):
                return True
            return False  # ""
        for key, value in component.items():

            if key == 'graph':
                if not value:
                    content = component.get('table', None)
                    if not self.having_any_empty_value(content):
                        return False
            elif key == 'table':
                if not value:
                    content = component.get('graph', None)
                    if not self.having_any_empty_value(content):
                        return False
            else:
                if not self.having_any_empty_value(value):
                    return False
        return True

    def registerQuestion(self, paper, isMockQuestion=False, difficulty=0):
        """Main method to register questions"""
        if isMockQuestion:
            exam_section = list(paper.keys())[0]
            self._get_exam_section_ids(exam_section)
            current_mocktest = self.db.mocktests.create(data={
                'difficulty': difficulty,
                'examtypeid': self.current_exam_id,
                'date': datetime.now(),
                'starttime': datetime.now(),
                'endtime': datetime.now(),
                'isactive': True
            })
            self.current_mocktest_id = current_mocktest.mocktestid
        for exam_section, subSections in paper.items():
            self._get_exam_section_ids(exam_section)
            for sectionNumber, questions in subSections.items():
                print(f"sectionNumber: {sectionNumber}")
                if isMockQuestion:
                    secNo = int(sectionNumber[-1])
                    current_mocksection = self.db.mocksections.create(data={
                        'mocktestid': self.current_mocktest_id,
                        'sectionnumber': secNo,
                        'sectionid': self.current_section_id
                    })
                    self.current_mocksection_id = current_mocksection.mocksectionid
                try:
                    self.current_mockquestion_number = 1
                    for question in questions:
                        # Check for parent-child questions using multiple possible keys
                        if any(key in question for key in ['childQuestions', 'questions', 'sources']):
                            # Handle parent-child questions
                            if not self._register_problemsset(exam_section, question, isMockQuestion=isMockQuestion):
                                raise Exception(
                                    f"Error registering problem set for {exam_section}")
                        else:
                            # Handle single questions
                            if not self._register_problem(exam_section, question, isMockQuestion=isMockQuestion):
                                raise Exception(
                                    f"Error registering problem for {exam_section}")
                        self.current_mockquestion_number += 1
                except Exception as e:
                    print(f"Error in registerQuestion: {str(e)}")
                    return False
        return True

    def __del__(self):
        """Destructor to ensure database connection is closed"""
        if hasattr(self, 'db') and self.db.is_connected():
            self.db.disconnect()

    def delete_all_questions(self):
        input("💀 Warning you are deleting all the questions: Enter if you want to continue\nelse control + c..\n")
        """Delete all question content from the database while preserving primary tables"""
        try:
            # Delete in order to respect foreign key constraints
            print("Deleting question content...")

            # First delete the many-to-many relationships
            print("- Deleting problem tags...")
            self.db.problemtags.delete_many()

            print("- Deleting problem set tags...")
            self.db.problemssettags.delete_many()

            # Delete options
            print("- Deleting problem options...")
            self.db.problemoptions.delete_many()

            # Delete problems
            print("- Deleting problems...")
            self.db.problems.delete_many()

            # Delete problem sets
            print("- Deleting problem sets...")
            self.db.problemsset.delete_many()

            # Delete tags (but not exam types and sections)
            print("- Deleting tags...")
            self.db.tags.delete_many()

            # Delete mocksections
            print("- Deleting mocksections...")
            self.db.mocksections.delete_many()

            # Delete mocktests
            print("- Deleting mocktests...")
            self.db.mocktests.delete_many()

            print("✅💀💀 Successfully deleted all question content")

        except Exception as e:
            print(f"Error deleting question content: {str(e)}")
            raise
