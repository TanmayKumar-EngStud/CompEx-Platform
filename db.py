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
        processed_options = self.process_table_analysis_answers(
            problem_id, answer_data)

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
                    where={'name': exam_name}
                )
                if not existing_exam:
                    print(f"Exam type {exam_name} not found, creating it")
                    exam_type = self.db.examtypes.create(data={
                        'name': exam_name,
                        'description': exam_data['description']
                    })
                    print(f"Exam type {exam_name} created successfully")
                else:
                    exam_type = existing_exam

                # Check if sections are already initialized for this exam type
                # Fetch all existing sections for this exam
                existing_sections = self.db.sections.find_many(where={'examtypeid': int(exam_type.examtypeid)})
                # Create a list of available (unclaimed) sections to match against definitions
                available_sections = list(existing_sections)

                print(f"Initializing/Verifying sections for {exam_name}...")
                for section_key, section_data in exam_data['sections'].items():
                    name = section_data.get('name', section_key)
                    description = section_data.get('description', '')

                    # Look for a match in available DB sections
                    found_match = None
                    for s in available_sections:
                        if s.name == name:
                            found_match = s
                            break
                    
                    if found_match:
                        # Claim it so it's not reused for the next duplicate definition
                        available_sections.remove(found_match)
                        print(f"Section '{name}' already exists (ID: {found_match.sectionid})")
                    else:
                        # No unclaimed match found, create new
                        try:
                            created_section = self.db.sections.create(data={
                                'examtypeid': exam_type.examtypeid,
                                'name': name,
                                'description': description
                            })
                            print(f"Created section '{name}' for {exam_name} (ID: {created_section.sectionid})")
                        except Exception as e:
                            print(f"Error creating section '{name}': {e}")

                print(f"Sections for {exam_name} verified.")

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

    def _get_exam_section_ids(self, exam_section, section_id=None):
        section_components = {
            "V": "Verbal",
            "Q": "Quants",
            "IR": "Integrated Reasoning"
        }

        # Handle empty or malformed exam_section
        if not exam_section or "_" not in exam_section:
            raise ValueError(
                f"Invalid exam section format: '{exam_section}'. Expected format: 'EXAM_SECTION' (e.g., 'GMAT_Q', 'GRE_V')")

        try:
            exam_name, section = exam_section.split(
                "_", 1)  # Split only on first underscore
        except ValueError:
            raise ValueError(
                f"Invalid exam section format: '{exam_section}'. Expected format: 'EXAM_SECTION'")

        # Validate that section is not empty
        if not section:
            raise ValueError(
                f"Invalid section name: empty section in '{exam_section}'")

        try:
            section_name = section_components[section]
        except KeyError:
            raise ValueError(
                f"Invalid section name: '{section}'. Valid sections are: {list(section_components.keys())}")

        exam = self.db.examtypes.find_first(where={'name': exam_name})
        if not exam:
            raise ValueError(f"Exam type not found: '{exam_name}'")

        self.current_exam_id = int(exam.examtypeid)
        if section_id:
            self.current_section_id = int(section_id)
        else:
            section_obj = self.db.sections.find_first(
                where={'name': section_name, 'examtypeid': exam.examtypeid})
            if not section_obj:
                raise ValueError(
                    f"Section not found: '{section_name}' for exam '{exam_name}'")
            self.current_section_id = int(section_obj.sectionid)
        return None

    def _register_problem(self, exam_section, question, isChildQuestion=False, isMockQuestion=False, section_id=None):
        """Register a single problem"""
        try:
            self._get_exam_section_ids(exam_section, section_id=section_id)

            # PATCH: Flatten lists for singular fields if provided as [v1, v2]
            import random
            for field in ['question', 'solution', 'title']:
                val = question.get(field)
                if isinstance(val, list) and val:
                    question[field] = random.choice(val)

            # Format metadata as JSON string
            # Format solution

            solution = question.get('solution', '')
            # Wrap solution in a dictionary with 'explanation' key as requested
            if isinstance(solution, str):
                solution = json.dumps({"explanation": solution})
            elif isinstance(solution, (dict, list)):
                # If it's already a dict or list, we could either wrap it or store as is
                # The user asked for {"explanation": "..."}, so if it's a dict, we wrap it
                solution = json.dumps({"explanation": str(solution)})
            else:
                solution = json.dumps({"explanation": str(solution)})
            # Create problem with proper Prisma format
            self.question_type = question.get('type') or question.get('question-type', '')
            if (self.question_type == "TA"):
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
                # Check if the answer values are strings that contain "Yes" or "No"
                try:
                    first_option = list(question['options'])[0] if isinstance(question['options'], dict) else question['options'][0]
                    answer_value = question['answer'][first_option]
                    if isinstance(answer_value, str) and answer_value in "Yes/No":
                        temp = "Yes"
                except:
                    pass
                question["content"]["connection_validator"] = temp
                self.question_correction_validator = temp

            # Ensure text field has a value (required field, handle null/empty)
            question_text = question.get('question') or ''
            if not question_text or question_text == '':
                question_text = question.get(
                    'title') or 'Question text not available'

            # Ensure title field has a value (required field, handle null/empty)
            question_title = question.get('title') or ''
            if not question_title or question_title == '':
                question_title = f"Question {self.question_type or 'Unknown'} - Difficulty {question.get('difficulty', 1)}"

            # Robust metadata/content extraction
            metadata_payload = question.get('metadata') or question.get('content', {})

            question_data = {
                "type": self.question_type,
                "prompt": question.get('prompt', ''),
                "title": question_title,
                "text": question_text,  # Ensure text field is not empty
                "difficulty": question.get('difficulty', 1),
                "sectionid": self.current_section_id,  # Reverted to schema name
                "examtypeid": self.current_exam_id,    # Reverted to schema name
                # Prisma will handle JSON conversion
                "metadata": json.dumps(metadata_payload),
                "solution": solution,  # Prisma will handle JSON conversion
                "isChildren": isChildQuestion,        # Reverted to schema name
                "isMockQuestion": isMockQuestion,     # Reverted to schema name
                "problemsSetId": None # Explicitly initialize
            }

            if isChildQuestion:
                # Direct field assignment
                #print(f"DEBUG: Linking Child Question to ProblemSetID: {self.current_problemset_id}")
                question_data["problemsSetId"] = self.current_problemset_id  # Reverted
            if isMockQuestion:
                # Direct field assignment
                question_data["mocksectionid"] = self.current_mocksection_id # Reverted
                question_data["mockquestionnumber"] = self.current_mockquestion_number # Reverted
            if self.question_type == "NE":
                question_data["metadata"] = json.dumps(
                    {"answer": question.get('answer', '')})

            problem = self.db.problems.create(data=question_data)
            self.current_problem_id = problem.problemid

            options = question.get('options') or []
            answer = question.get('answer', '')
            self.current_question_type = question.get('type', '')
            
            if isinstance(options, dict):
                for key, value in options.items():
                    # For simple dict options (like TC 1 blank), key is "A", "B", etc.
                    self._register_problem_options(value, answer, group=None, key=key)
            elif isinstance(options, list):
                for i, option in enumerate(options):
                    if isinstance(option, dict):
                        # For Text Completion with multiple blanks (list of dicts)
                        group = f"Blank {i+1}"
                        for key, value in option.items():
                            self._register_problem_options(value, answer, group=group, key=key)
                    elif isinstance(option, str):
                        self._register_problem_options(option, answer)
                    elif isinstance(option, int):
                        self._register_problem_options(option, answer)
                    elif isinstance(option, list):
                        # Legacy/Special format
                        group = "A"
                        for suboption in option:
                            self._register_problem_options(suboption, answer, group)
                            group = chr(ord(group) + 1)

            # Register tags
            self._register_problem_tags(question.get('tags') or [])

            return True

        except Exception as e:
            print(
                f"Error in _register_problem: {str(e)}\n\n here is the question content: {json.dumps(question, indent=4)}")
            return False

    def _register_problem_options(self, option_text, answers, group=None, key=None):
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
            if isinstance(answers, dict) and option_text in answers:
                answer_value = answers[option_text]
                if isinstance(answer_value, dict):
                    is_correct = answer_value.get("isCorrect", False)
                else:
                    # For legacy format where answer is direct value
                    for group_name, mapping in self.answer_type_mappings.items():
                        if answer_value == mapping["positive"]:
                            is_correct = True
                            break

            option_data = {
                'optiontext': str(option_text),
                'iscorrect': is_correct,
                'problemid': self.current_problem_id,  # Direct field assignment
                'group': answer_group if answer_group else group
            }

        else:
            is_correct = False
            
            # Check correctness based on key or option_text
            if isinstance(answers, list):
                # If key is provided (e.g., "A"), check if it's in the answer list
                if key and key in answers:
                    is_correct = True
                # Fallback: check if option_text itself is in answers
                elif str(option_text) in [str(a) for a in answers]:
                    is_correct = True
            elif isinstance(answers, dict):
                # For dictionaries where keys are groups (e.g., {"Blank 1": "A"})
                if group and group in answers:
                    correct_val = answers[group]
                    if isinstance(correct_val, list):
                        is_correct = (key in correct_val) if key else (option_text in correct_val)
                    else:
                        is_correct = str(key if key else option_text) == str(correct_val)
                else:
                    # Fallback: check if key or option_text is in values
                    is_correct = (key in answers.values()) if key else (option_text in answers.values())
            else:
                # Single value answer
                is_correct = str(key if key else option_text) == str(answers)

            option_data = {
                'optiontext': str(option_text),
                'iscorrect': is_correct,
                'problemid': self.current_problem_id,
                'group': group
            }


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
            if not tags:
                return True
            tagid = self._register_tag(tags)
            if tagid is not False:
                tag_data = {
                    'tagid': tagid,
                    'problemid': self.current_problem_id
                }
                self.db.problemtags.create(data=tag_data)
        except Exception as e:
            print(
                f"Error creating problem tags in _register_problem_tags: {str(e)}")
            return False
        return True

    def _register_problemsset_tags(self, tags):
        try:
            if not tags:
                return True
            tagid = self._register_tag(tags)
            if tagid is not False:
                tag_data = {
                    'tagid': tagid,
                    'problemsSetId': self.current_problemset_id
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
    def _register_tag(self, tags_list):
        try:
            if not tags_list:
                return False

            tag_data = {
                'topic': 'Unknown',
                'theme': 'Unknown',
                'type': 'Unknown',
                'examtypeid': self.current_exam_id,
                'sectionid': self.current_section_id
            }

            for tag_str in tags_list:
                if not isinstance(tag_str, str) or ':' not in tag_str:
                    continue
                
                parts = tag_str.split(':', 1)
                key = parts[0].strip().lower()
                value = parts[1].strip()

                if key in ['topic', 'theme', 'type']:
                    # Truncate to 300 characters as requested
                    tag_data[key] = value[:300]

            # Find or create categorised tag
            existing_tag = self.db.tags.find_first(where={
                'topic': tag_data['topic'],
                'theme': tag_data['theme'],
                'type': tag_data['type'],
                'examtypeid': self.current_exam_id,
                'sectionid': self.current_section_id
            })

            if existing_tag:
                return existing_tag.tagid
            else:
                new_tag = self.db.tags.create(data=tag_data)
                return new_tag.tagid
        except Exception as e:
            print(f"Error in _register_tag (categorized): {str(e)}")
            print(f"Tags list was: {tags_list}")
            return False

    def _register_problemsset(self, exam_section, parent_question, isMockQuestion=False, section_id=None):
        """Register a problem set with its child questions"""
        try:
            self._get_exam_section_ids(exam_section, section_id=section_id)

            # Ensure required fields have values (handle null/empty)
            title = parent_question.get('title') or ''
            if not title or title == '':
                title = f"{parent_question.get('type', 'Question')} - {exam_section}"

            # Determine content type and data
            # Robust metadata/content extraction
            metadata_payload = parent_question.get('metadata') or parent_question.get('content', {})

            problemsset_data = {
                'type': parent_question.get('type') or parent_question.get('question-type', ''),
                'content': json.dumps(metadata_payload),
                'title': title,  # Ensure title is not empty
                # Direct field assignment (required)
                'sectionid': self.current_section_id,     # Reverted to schema name
                # Direct field assignment (required)
                'examtypeid': self.current_exam_id       # Reverted to schema name
            }

            if isMockQuestion:
                problemsset_data['mockquestionnumber'] = self.current_mockquestion_number
                # Direct field assignment
                problemsset_data['mocksectionid'] = self.current_mocksection_id # Reverted

            # Create problem set
            try:
                # Note: Prisma Python client uses lowercase for model names
                problemsset = self.db.problemsset.create(data=problemsset_data)
                # Prisma Python client uses schema field names (or matching aliases)
                self.current_problemset_id = problemsset.problemsSetId
            except Exception as e:
                # Use metadata_payload if available for logging
                error_content = parent_question.get('metadata') or parent_question.get('content', {})
                print(
                    f"Error registering parent question component in _register_problemsset: {str(e)} \n\n here is the parent question content: {json.dumps(error_content, indent=4)}")
                return False

            # Register child questions
            child_questions = (
                (parent_question.get('childQuestions') or []) or
                (parent_question.get('questions') or []) or
                (parent_question.get('child-questions') or [])
            )

            for child in child_questions:
                if not self._register_problem(exam_section, child, isChildQuestion=True, isMockQuestion=isMockQuestion, section_id=section_id):
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
            for sectionNumber, questions in subSections.items():
                section_id = int(sectionNumber) if str(sectionNumber).isdigit() else None
                self._get_exam_section_ids(exam_section, section_id=section_id)
                print(f"sectionNumber: {sectionNumber} -> DB SectionID: {self.current_section_id}")
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
                        if any(key in question for key in ['childQuestions', 'questions', 'sources', 'child-questions']):
                            # Handle parent-child questions
                            if not self._register_problemsset(exam_section, question, isMockQuestion=isMockQuestion, section_id=section_id):
                                raise Exception(
                                    f"Error registering problem set for {exam_section}")
                        else:
                            # Handle single questions
                            if not self._register_problem(exam_section, question, isMockQuestion=isMockQuestion, section_id=section_id):
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
