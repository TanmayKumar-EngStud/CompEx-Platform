import sys
from pathlib import Path
# Add main prisma client to path
sys.path.insert(0, str(Path(__file__).parent / "compex-db_prisma" / "generated"))
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
        self.current_dichotomous_mapping = None

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
            self.current_options_type = str(question.get('options_type', 'single'))

            # Ensure text field has a value (required field, handle null/empty)
            question_text = question.get('question') or ''
            if not question_text or question_text == '':
                question_text = question.get(
                    'title') or 'Question text not available'

            # Ensure title field has a value (required field, handle null/empty)
            question_title = question.get('title') or ''
            if not question_title or question_title == '':
                question_title = f"Question {self.question_type or 'Unknown'} - Difficulty {question.get('difficulty', 1)}"

            # Robut metadata/content extraction (OPTIMIZED)
            original_metadata = question.get('metadata') or question.get('content', {})
            if not isinstance(original_metadata, dict):
                original_metadata = {"data": original_metadata}

            # Prepare metadata_payload (ensuring order)
            metadata_payload = {}
            
            # 1. Capture explicit dichotomous-type from question or metadata
            #    Or derive from 'categories' list for Dynamic TPA
            dichotomous_info = question.get('dichotomous-type') or original_metadata.get('dichotomous-type')
            
            # Dynamic TPA Logic: Check for 'categories' in question or content
            categories = question.get('categories') or original_metadata.get('categories')
            if not dichotomous_info and categories and isinstance(categories, list) and len(categories) == 2:
                 dichotomous_info = {
                     "positive": categories[0],
                     "negative": categories[1]
                 }

            if dichotomous_info:
                metadata_payload['dichotomous-type'] = dichotomous_info
                self.current_dichotomous_mapping = dichotomous_info # Store for options registration

            # 2. Add original metadata, but EXCLUDE redundant fields for dichotomous questions
            for k, v in original_metadata.items():
                if dichotomous_info and k in ['answer', 'options', 'questions', 'dichotomous-type']:
                    continue
                metadata_payload[k] = v

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
                "problemsSetId": None, # Explicitly initialize
                "options_type": self.current_options_type # New column
            }

            if isChildQuestion:
                # Direct field assignment
                #print(f"DEBUG: Linking Child Question to ProblemSetID: {self.current_problemset_id}")
                question_data["problemsSetId"] = self.current_problemset_id  # Reverted
            if isMockQuestion:
                # Direct field assignment
                question_data["mocksectionid"] = self.current_mocksection_id # Reverted
                question_data["mockquestionnumber"] = self.current_mockquestion_number # Reverted
            if self.question_type in ["NE", "Numerical Entry"]:
                question_data["metadata"] = json.dumps(
                    {"answer": question.get('answer', '')})

            problem = self.db.problems.create(data=question_data)
            self.current_problem_id = problem.problemid

            options = question.get('options') or []
            answer = question.get('answer', '')
            # Use self.question_type which was already set in line 239
            
            # --- Data Sufficiency Standard Options ---
            if self.question_type == "Data Sufficiency":
                 ds_options = {
                      "A": "Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient.",
                      "B": "Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient.",
                      "C": "BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient.",
                      "D": "EITHER statement ALONE is sufficient.",
                      "E": "Statements (1) and (2) TOGETHER are NOT sufficient."
                 }
                 explanations = question.get('explanations', {})
                 for key, text in ds_options.items():
                      self._register_problem_options(text, answer, group=None, key=key, explanation=explanations.get(key))
            
            # --- Options Registration ---
            # PATCH: Handle Numerical Entry or numeric types with null/empty options
            if (self.question_type in ["NE", "Numerical Entry"] or self.current_options_type == "numeric") and not options:
                if answer is not None and str(answer).strip() != "":
                    self._register_problem_options(str(answer), answer)
            
            elif isinstance(options, dict):
                for key, value in options.items():
                    # Check if value is nested (text + explanation)
                    if isinstance(value, dict):
                        if 'text' in value:
                            # Standard single option with explanation
                            self._register_problem_options(value['text'], answer, group=None, key=key, explanation=value.get('explanation'))
                        else:
                            # Nested group (e.g., "blank 1": { "A": {...}, "B": {...} })
                            # Treat 'key' as the group name (e.g. "blank 1")
                            group_name = key
                            for sub_key, sub_value in value.items():
                                if isinstance(sub_value, dict) and 'text' in sub_value:
                                     self._register_problem_options(sub_value['text'], answer, group=group_name, key=sub_key, explanation=sub_value.get('explanation'))
                                else:
                                     # Fallback for simple key-value within group
                                     self._register_problem_options(sub_value, answer, group=group_name, key=sub_key)
                    else:
                        self._register_problem_options(value, answer, group=None, key=key)
            elif isinstance(options, list):
                for i, option in enumerate(options):
                    if isinstance(option, dict):
                        # For Text Completion with multiple blanks (list of dicts)
                        if 'text' in option and 'explanation' in option:
                             # This is a flat option with explanation
                             self._register_problem_options(option['text'], answer, explanation=option.get('explanation'))
                        else:
                             # Multiple blanks
                             group = f"Blank {i+1}"
                             for key, value in option.items():
                                 if isinstance(value, dict) and 'text' in value:
                                      self._register_problem_options(value['text'], answer, group=group, key=key, explanation=value.get('explanation'))
                                 else:
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

            # Register dichotomous choice labels if applicable
            if dichotomous_info:
                pos = dichotomous_info.get('positive')
                neg = dichotomous_info.get('negative')
                # These are labels, their specific correctness is determined per statement stored above
                self._register_problem_options(pos, None, group="Dichotomous Choice")
                self._register_problem_options(neg, None, group="Dichotomous Choice")

            # Register tags
            self._register_tags_to_entity(question.get('tags') or [], self.current_problem_id, 'problem', is_child=isChildQuestion)

            return True

        except Exception as e:
            print(f"Error in _register_problem: {str(e)}")
            # print(f"here is the question content: {json.dumps(question, indent=4)}")
            import traceback
            traceback.print_exc()
            return False

    def _register_problem_options(self, option_text, answers, group=None, key=None, explanation=None):
        """Register problem options in the database.

        Args:
            option_text: The option text
            answers: The correct answers (can be dict, list, or single value)
            group: Optional group identifier for the option
            key: Optional key (like 'A', 'B')
            explanation: Optional brief explanation for this option
        """
        # Special handling for Dichotomous questions (Mapping based)
        if group == "Dichotomous":
            # Determine if this option is correct based on the answer mapping
            is_correct = (str(option_text).strip().lower() == str(answers).strip().lower())
            
            option_data = {
                'optiontext': str(option_text),
                'iscorrect': is_correct,
                'explanation': explanation,
                'problemid': self.current_problem_id,
                'group': group
            }
        
        # Dichotomous / Table Analysis (TA) Special Handling
        # If options_type is dichotomous, use mapping-based logic
        elif self.current_options_type == "dichotomous":
            answer_group = None
            is_correct = False
            ta_explanation = explanation

            # Find the appropriate answer group
            mapping = None
            
            # 1. Dynamic Mapping Check
            if self.current_dichotomous_mapping:
                 mapping = self.current_dichotomous_mapping
                 answer_group = "Dichotomous Choice" # Or derived?
                 # Actually, we don't strictly need a group name from mappings for Dynamic TPA
                 # But we can use "Dichotomous Pair"
            
            # 2. Static Mapping Check (Fallback)
            if not mapping:
                for group_name, map_item in self.answer_type_mappings.items():
                    if isinstance(answers, dict):
                        # Check if any response in the answers dict matches positive/negative
                        if any(str(val).strip().lower() in [str(map_item["positive"]).lower(), str(map_item["negative"]).lower()] for val in answers.values()):
                            answer_group = group_name
                            mapping = map_item
                            break
                    elif isinstance(answers, list) and answers:
                         # Check first item if it's a mapping
                         mapping_item = answers[0]
                         if isinstance(mapping_item, dict):
                              if any(str(val).strip().lower() in [str(map_item["positive"]).lower(), str(map_item["negative"]).lower()] for val in mapping_item.values()):
                                   answer_group = group_name
                                   mapping = map_item
                                   break
                    elif str(mapping["positive"]) in str(answers) or str(mapping["negative"]) in str(answers):
                        answer_group = group_name
                        mapping = map_item
                        break

            # If answers is a dict (New format: {statement: response})
            if isinstance(answers, dict) and mapping:
                response = answers.get(option_text)
                if response:
                    if str(response).strip().lower() == str(mapping["positive"]).strip().lower():
                        is_correct = True
            
            # If answers is a list of objects (TA old format)
            elif isinstance(answers, list) and mapping:
                 for ans_item in answers:
                      if isinstance(ans_item, dict) and ans_item.get('statement') == option_text:
                           # Check if response matches the "Positive" value for this TA type
                           response = ans_item.get('response')
                           if str(response).strip().lower() == str(mapping["positive"]).strip().lower():
                                is_correct = True
                           break

            option_data = {
                'optiontext': str(option_text),
                'iscorrect': is_correct,
                'explanation': ta_explanation,
                'problemid': self.current_problem_id,
                'group': answer_group if answer_group else group
            }

        else:
            is_correct = False
            
            # Check correctness based on key or option_text
            if isinstance(answers, list):
                if key and key in answers:
                    is_correct = True
                elif str(option_text) in [str(a) for a in answers]:
                    is_correct = True
            elif isinstance(answers, dict):
                if group and group in answers:
                    correct_val = answers[group]
                    if isinstance(correct_val, list):
                        is_correct = (key in correct_val) if key else (option_text in correct_val)
                    else:
                        is_correct = str(key if key else option_text) == str(correct_val)
                else:
                    is_correct = (key in answers.values()) if key else (option_text in answers.values())
            else:
                is_correct = str(key if key else option_text) == str(answers)

            option_data = {
                'optiontext': str(option_text),
                'iscorrect': is_correct,
                'explanation': explanation,
                'problemid': self.current_problem_id,
                'group': group
            }

        try:
            self.db.problemoptions.create(
                data=option_data
            )
        except Exception as e:
            print(
                f"Error creating problem option in _register_problem_options: {str(e)} \n\n here is the option_text: {option_text} \n\n here is the answer: {answers}")
            return False
        return True

    def _register_tags_to_entity(self, tags_list: List[str], entity_id: int, entity_type: str, is_child: bool = False):
        """Generic tag registration for either a Problem or a ProblemsSet.
        
        Args:
            tags_list: List of 'category: value' strings
            entity_id: The ID of the problem or problemsset
            entity_type: 'problem' or 'problemsset'
            is_child: Whether the problem is a child question (only relevant for 'problem' type)
        """
        try:
            if not tags_list:
                return True
            
            # 1. Tag Validator Logic
            categories_found = set()
            for t in tags_list:
                if isinstance(t, str) and ':' in t:
                    cat = t.split(':', 1)[0].strip().lower()
                    if cat == 'question-type': cat = 'type'
                    categories_found.add(cat)
            
            # Check requirements based on context
            if entity_type == 'problem' and is_child:
                if 'sub-topic' not in categories_found:
                    print(f"⚠️  WARNING: Category 'sub-topic' is missing for child question ID {entity_id}")
            else:
                # Top-level question (Simple or Parent/ProblemsSet)
                required = ['type', 'theme', 'topic']
                missing = [r for r in required if r not in categories_found]
                if missing:
                    ctx = f"ProblemsSet {entity_id}" if entity_type == 'problemsset' else f"Problem {entity_id}"
                    print(f"⚠️  WARNING: Categories {missing} are missing for {ctx} (Exam: {self.current_exam_id}, Section: {self.current_section_id})")

            # 2. Registration Logic
            for tag_str in set(tags_list):
                if not isinstance(tag_str, str) or ':' not in tag_str:
                    continue
                
                parts = tag_str.split(':', 1)
                category = parts[0].strip().lower()
                value = parts[1].strip()
                if category == 'question-type': category = 'type'
                
                scope_id = self._get_or_create_tag_id(category, value)
                if scope_id:
                    if entity_type == 'problem':
                        # Idempotency check for problems
                        existing = self.db.problemtags.find_unique(where={
                            'problemid_tagScopeId': {
                                'problemid': entity_id,
                                'tagScopeId': scope_id
                            }
                        })
                        if not existing:
                            self.db.problemtags.create(data={
                                'problemid': entity_id,
                                'tagScopeId': scope_id
                            })
                    else: # entity_type == 'problemsset'
                        # Idempotency check for problemsset
                        existing = self.db.problemssettags.find_unique(where={
                            'tagScopeId_problemsSetId': {
                                'tagScopeId': scope_id,
                                'problemsSetId': entity_id
                            }
                        })
                        if not existing:
                            self.db.problemssettags.create(data={
                                'problemsSetId': entity_id,
                                'tagScopeId': scope_id
                            })
            return True
        except Exception as e:
            print(f"Error in _register_tags_to_entity ({entity_type}): {str(e)}")
            return False

    def _get_or_create_tag_id(self, category: str, name: str) -> int:
        """Finds or creates a global tag and links it to the current scope."""
        try:
            # 1. Ensure Global Tag exists
            tag = self.db.tags.find_unique(where={'name': name})
            if not tag:
                tag = self.db.tags.create(data={'name': name, 'category': category})
            
            # 2. Ensure TagScope exists for current exam/section
            scope = self.db.tag_scopes.find_unique(where={
                'tagid_examtypeid_sectionid': {
                    'tagid': tag.tagid,
                    'examtypeid': self.current_exam_id,
                    'sectionid': self.current_section_id
                }
            })
            if not scope:
                scope = self.db.tag_scopes.create(data={
                    'tagid': tag.tagid,
                    'examtypeid': self.current_exam_id,
                    'sectionid': self.current_section_id
                })
            
            return scope.tagScopeId
        except Exception as e:
            print(f"Error in _get_or_create_tag_id: {str(e)}")
            return None

    # ✅

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
            original_metadata = parent_question.get('metadata') or parent_question.get('content', {})
            if not isinstance(original_metadata, dict):
                original_metadata = {"data": original_metadata}

            # Prepare metadata_payload (ensuring order)
            metadata_payload = {}
            
            # 1. Capture explicit dichotomous-type from question or metadata
            dichotomous_info = parent_question.get('dichotomous-type') or original_metadata.get('dichotomous-type')
            if dichotomous_info:
                metadata_payload['dichotomous-type'] = dichotomous_info

            # 2. Add original metadata, but EXCLUDE redundant fields for dichotomous sets
            for k, v in original_metadata.items():
                if dichotomous_info and k in ['answer', 'options', 'questions', 'dichotomous-type']:
                    continue
                metadata_payload[k] = v

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

            # Register tags for the ProblemSet (Parent)
            self._register_tags_to_entity(parent_question.get('tags') or [], self.current_problemset_id, 'problemsset', is_child=False)

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
        
        # 1. Group input paper by Exam Type
        # Format: { "GMAT": { "GMAT_Q": {...}}, "GRE": { "GRE_V": {...}} }
        exam_groups = {}
        for exam_section_key, subSections in paper.items():
            # exam_section_key e.g., "GMAT_Q" or "GRE_V"
            parts = exam_section_key.split('_')
            exam_name = parts[0]
            
            if exam_name not in exam_groups:
                exam_groups[exam_name] = {}
            exam_groups[exam_name][exam_section_key] = subSections

        # 2. Iterate each Exam Group
        for exam_name, group_paper in exam_groups.items():
            print(f"\\n--- Processing Exam Group: {exam_name} ---")
            
            # Setup Mock Test for this Exam Group (if applicable)
            if isMockQuestion:
                # Find examtypeid for this exam_name
                exam_obj = self.db.examtypes.find_first(where={'name': exam_name})
                if not exam_obj:
                    print(f"Warning: Exam {exam_name} not found. Skipping Mock Creation.")
                    continue
                
                # Create Mock Test
                current_mocktest = self.db.mocktests.create(data={
                    'difficulty': difficulty,
                    'examtypeid': exam_obj.examtypeid,
                    'date': datetime.now(),
                    'starttime': datetime.now(),
                    'endtime': datetime.now(),
                    'isactive': True
                })
                self.current_mocktest_id = current_mocktest.mocktestid
                print(f"Created Mock Test ID: {self.current_mocktest_id} for {exam_name}")

            # 3. Register Sections in this Group
            for exam_section, subSections in group_paper.items():
                print(f"Processing Section Group: {exam_section}")
                short_section = exam_section.split('_')[1] if '_' in exam_section else ""
                section_components = {"V": "Verbal", "Q": "Quants", "IR": "Integrated Reasoning"}
                full_section_name = section_components.get(short_section, "")

                # Get sorted list of sections from the paper JSON
                sorted_paper_section_keys = sorted(subSections.keys(), key=lambda x: int(x) if str(x).isdigit() else x)

                # Get matching DB sections for this exam ordered by ID
                # Re-fetch exam_obj if not already fetched (e.g. if isMockQuestion=False)
                exam_obj = self.db.examtypes.find_first(where={'name': exam_name})
                if not exam_obj:
                    print(f"Warning: Exam {exam_name} not found during registration. Skipping.")
                    continue

                matching_db_sections = self.db.sections.find_many(
                    where={'name': full_section_name, 'examtypeid': int(exam_obj.examtypeid)},
                    order={'sectionid': 'asc'}
                )

                # Iterate and map
                for i, sectionNumber in enumerate(sorted_paper_section_keys):
                    questions = subSections[sectionNumber]
                    
                    # Fetch the correct DB Section ID by index (part 1, part 2, etc.)
                    if i < len(matching_db_sections):
                        section_id = int(matching_db_sections[i].sectionid)
                    else:
                        # Fallback to the first/last if mapping gets weird, but usually indices should match
                        section_id = int(matching_db_sections[-1].sectionid) if matching_db_sections else None

                    self._get_exam_section_ids(exam_section, section_id=section_id)
                    print(f"Paper Section '{sectionNumber}' -> DB SectionID: {self.current_section_id} ({exam_name} {full_section_name})")
                    if isMockQuestion:
                        # Extract basic number from "1" or "section 1"
                        secNo_str = ''.join(filter(str.isdigit, str(sectionNumber)))
                        secNo = int(secNo_str) if secNo_str else (i + 1)
                        
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
                                    # raise Exception(f"Error registering problem for {exam_section}")
                                    print(f"Failed to register question in {exam_section}")

                            if isMockQuestion:
                                self.current_mockquestion_number += 1
                                
                    except Exception as e:
                        print(f"Error processing section {sectionNumber}: {e}")
                        continue

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
