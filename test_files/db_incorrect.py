from prisma import Prisma
import json
import re
import os
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
        """Initialize primary tables (idempotent).

        IMPORTANT:
        - Do NOT set autoincrement PKs (examtypeid/sectionid/userid) manually.
        - Create rows only if they don't already exist (by stable natural keys).
        """
        try:
            definitions_path = os.path.join(os.path.dirname(__file__), 'PrimaryTablesDefinitions.json')
            if not os.path.exists(definitions_path):
                definitions_path = 'PrimaryTablesDefinitions.json'

            with open(definitions_path, 'r', encoding='utf-8') as f:
                self.definitions = json.load(f)

            # ExamTypes + Sections (keyed by name, not by provided ids)
            for exam_name, exam_data in self.definitions.get('examtypes', {}).items():
                exam = self.db.examtypes.find_first(where={'name': exam_name})
                if not exam:
                    exam = self.db.examtypes.create(data={
                        'name': exam_name,
                        'description': exam_data.get('description')
                    })

                for section_name, section_data in exam_data.get('sections', {}).items():
                    existing_section = self.db.sections.find_first(where={
                        'examtypeid': exam.examtypeid,
                        'name': section_name
                    })
                    if not existing_section:
                        self.db.sections.create(data={
                            'examtypeid': exam.examtypeid,
                            'name': section_name,
                            'description': section_data.get('description')
                        })

            # Primary user (admin) - keyed by username/email
            existing_admin = self.db.users.find_first(where={
                'OR': [
                    {'username': 'admin'},
                    {'email': 'admin@compex.com'}
                ]
            })
            if not existing_admin:
                self.db.users.create(data={
                    'username': 'admin',
                    'password': 'admin',
                    'email': 'admin@compex.com',
                    'registrationdate': datetime.now()
                })

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

        section_obj = self.db.sections.find_first(
            where={'name': section_name, 'examtypeid': exam.examtypeid})
        if not section_obj:
            raise ValueError(
                f"Section not found: '{section_name}' for exam '{exam_name}'")

        self.current_exam_id = int(exam.examtypeid)
        self.current_section_id = int(section_obj.sectionid)
        return None


    def _map_question_type(self, q: Dict[str, Any]) -> str:
        """Map generator-facing question types to internal codes used by this DB layer."""
        raw = q.get('type') or q.get('question-type') or q.get('question_type') or ''
        raw = (raw or '').strip()

        mapping = {
            # GMAT
            'Table Analysis': 'TA',
            'Data Sufficiency': 'DS',
            'Graphic Interpretation': 'GI',
            'Multi-Source Reasoning': 'MSR',
            'Two-Part Analysis': 'TPA',
            'Problem Solving Simple': 'PS',
            'Reading Comprehension': 'RC',
            # GRE
            'Numerical Entry': 'NE',
            'Quantitative Comparison': 'QC',
            'Sentence Equivalence': 'SE',
            'Text Completion': 'TC',
            'Problem Solving Meta': 'PS_META',
        }
        return mapping.get(raw, raw)

    def _normalize_question(self, q: Dict[str, Any]) -> Dict[str, Any]:
        """Unify incoming JSON shapes (GMAT/GRE dumps, synthetic tests, etc.)."""
        if not isinstance(q, dict):
            return q  # type: ignore

        nq = dict(q)

        # Normalize type naming
        nq['type'] = self._map_question_type(nq)

        # Normalize metadata/content naming
        if 'metadata' in nq and 'content' not in nq:
            nq['content'] = nq.get('metadata')

        # Normalize child questions naming
        if 'child-questions' in nq and 'childQuestions' not in nq:
            nq['childQuestions'] = nq.get('child-questions')

        return nq

    def _flatten_options(self, options: Any) -> List[Dict[str, Any]]:
        """Return a flat list of option rows with stable correctness semantics.

        Each item: {option_key, option_text, group}
        - option_key: label like 'A', 'B', ...
        - group: used for blanks/parts (e.g., 'Blank 1'), or the label itself for MCQ dicts.
        """
        rows: List[Dict[str, Any]] = []
        if options is None:
            return rows

        if isinstance(options, dict):
            for k, v in options.items():
                rows.append({'option_key': str(k), 'option_text': v, 'group': str(k)})
            return rows

        if isinstance(options, list):
            # Table Analysis (statements)
            if options and all(isinstance(x, str) for x in options):
                for stmt in options:
                    rows.append({'option_key': None, 'option_text': stmt, 'group': None})
                return rows

            # Text Completion (list of dicts, each dict is a blank)
            if options and all(isinstance(x, dict) for x in options):
                for i, blank_dict in enumerate(options, start=1):
                    group = f"Blank {i}"
                    for k, v in blank_dict.items():
                        rows.append({'option_key': str(k), 'option_text': v, 'group': group})
                return rows

            # Generic nested handling
            for i, item in enumerate(options, start=1):
                if isinstance(item, dict):
                    for k, v in item.items():
                        rows.append({'option_key': str(k), 'option_text': v, 'group': str(k)})
                elif isinstance(item, list):
                    group = f"Part {i}"
                    for sub in item:
                        if isinstance(sub, dict):
                            for k, v in sub.items():
                                rows.append({'option_key': str(k), 'option_text': v, 'group': group})
                        else:
                            rows.append({'option_key': None, 'option_text': sub, 'group': group})
                else:
                    rows.append({'option_key': None, 'option_text': item, 'group': None})
            return rows

        rows.append({'option_key': None, 'option_text': options, 'group': None})
        return rows

    def _flatten_answer_labels(self, answers: Any) -> List[str]:
        """Flatten answers into a list of string labels/values for matching."""
        out: List[str] = []
        if answers is None:
            return out
        if isinstance(answers, (str, int, float, bool)):
            return [str(answers)]
        if isinstance(answers, list):
            for a in answers:
                out.extend(self._flatten_answer_labels(a))
            return out
        if isinstance(answers, dict):
            for v in answers.values():
                out.extend(self._flatten_answer_labels(v))
            return out
        return out

    def _register_problem(self, exam_section, question, isChildQuestion=False, isMockQuestion=False):
        """Register a single problem."""
        try:
            self._get_exam_section_ids(exam_section)

            question = self._normalize_question(question)

            self.question_type = question.get('type', '') or ''
            self.current_question_type = self.question_type

            metadata_obj = question.get('content') or question.get('metadata') or {}
            solution_obj = question.get('solution', None)

            question_text = (question.get('question') or question.get('text') or '').strip()
            if not question_text:
                question_text = question.get('title') or 'Question text not available'

            question_title = (question.get('title') or '').strip()
            if not question_title:
                question_title = f"Question {self.question_type or 'Unknown'} - Difficulty {question.get('difficulty', 1)}"

            question_data = {
                "type": self.question_type,
                "prompt": question.get('prompt', ''),
                "title": question_title,
                "text": question_text,
                "difficulty": question.get('difficulty', 1),
                "sectionid": self.current_section_id,
                "examtypeid": self.current_exam_id,
                "metadata": metadata_obj,
                "solution": solution_obj,
                "isChildren": isChildQuestion,
                "isMockQuestion": isMockQuestion,
                "problemsSetId": None
            }

            if isChildQuestion:
                question_data["problemsSetId"] = self.current_problemset_id
            if isMockQuestion:
                question_data["mocksectionid"] = self.current_mocksection_id
                question_data["mockquestionnumber"] = self.current_mockquestion_number

            if self.question_type == "NE":
                merged = dict(metadata_obj) if isinstance(metadata_obj, dict) else {"metadata": metadata_obj}
                merged["answer"] = question.get("answer")
                question_data["metadata"] = merged

            problem = self.db.problems.create(data=question_data)
            self.current_problem_id = problem.problemid

            if self.question_type != "NE":
                options = question.get('options')
                answers = question.get('answer', None)

                for row in self._flatten_options(options):
                    self._register_problem_options(
                        option=row.get('option_text'),
                        answers=answers,
                        group=row.get('group'),
                        option_key=row.get('option_key')
                    )

            self._register_problem_tags(question.get('tags') or [])
            return True

        except Exception as e:
            print(
                f"Error in _register_problem: {str(e)}\n\n here is the question content: {json.dumps(question, indent=4, default=str)}")
            return False

    def _register_problem_options(self, option, answers, group=None, option_key: str | None = None):
        """Register problem options in the database."""

        if self.current_question_type == "TA":
            answer_group = None
            is_correct = False

            if isinstance(answers, dict) and option in answers:
                answer_value = answers[option]
                for group_name, mapping in self.answer_type_mappings.items():
                    if str(answer_value) in (mapping["positive"], mapping["negative"]):
                        answer_group = group_name
                        is_correct = str(answer_value) == mapping["positive"]
                        break

            option_data = {
                'optiontext': str(option),
                'iscorrect': is_correct,
                'problemid': self.current_problem_id,
                'group': answer_group or group
            }
        else:
            flat_answers = set(self._flatten_answer_labels(answers))

            if option_key is not None and str(option_key) in flat_answers:
                is_correct = True
            else:
                is_correct = str(option) in flat_answers

                if isinstance(answers, dict) and group and group in answers:
                    target_flat = set(self._flatten_answer_labels(answers[group]))
                    is_correct = (option_key is not None and str(option_key) in target_flat) or (str(option) in target_flat)

            option_data = {
                'optiontext': str(option),
                'iscorrect': is_correct,
                'problemid': self.current_problem_id,
                'group': group
            }

        try:
            self.db.problemoptions.create(data=option_data)
        except Exception as e:
            print(
                f"Error creating problem option in _register_problem_options: {str(e)}\n\n option: {option}\n answers: {answers}")
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
                    # Direct field assignment (fix: was using current_problem_id)
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
    def _register_tag(self, tag):
        try:
            pattern = r'\(.*?\)'
            tag = re.sub(pattern, '', tag).strip()

            # remove anything after comma
            tag = re.sub(r' ,*', '', tag) if ' ,' in tag else tag

            # Truncate tag to 50 characters maximum (database limit)
            # Try to truncate at word boundaries for better readability
            MAX_TAG_LENGTH = 50
            if len(tag) > MAX_TAG_LENGTH:
                original_tag = tag
                # Try to truncate at the last complete word within the limit
                truncated = tag.split(',')[0]  # tag[:MAX_TAG_LENGTH]
                last_space = truncated.rfind(' ')
                if last_space > MAX_TAG_LENGTH * 0.7:  # Only truncate at word boundary if it's not too short
                    tag = truncated[:last_space].strip()
                else:
                    tag = truncated.strip()
                # print(f"Warning: Tag truncated from '{original_tag}' to '{tag}' (length: {len(tag)})")
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
        """Register a problem set with its child questions."""
        try:
            self._get_exam_section_ids(exam_section)

            parent_question = self._normalize_question(parent_question)

            title = (parent_question.get('title') or '').strip()
            if not title:
                title = f"{parent_question.get('type', 'Component')} - {exam_section}"

            content_obj = parent_question.get('content') or parent_question.get('metadata') or {}
            if isinstance(content_obj, dict):
                content_obj = dict(content_obj)
                content_obj.setdefault('prompt', parent_question.get('prompt'))
                content_obj.setdefault('question_type', parent_question.get('question-type') or parent_question.get('type'))

            problemsset_data = {
                'type': parent_question.get('type', ''),
                'content': content_obj,
                'title': title,
                'sectionid': self.current_section_id,
                'examtypeid': self.current_exam_id
            }

            if isMockQuestion:
                problemsset_data['mockquestionnumber'] = self.current_mockquestion_number
                problemsset_data['mocksectionid'] = self.current_mocksection_id

            problemsset = self.db.problemsset.create(data=problemsset_data)
            self.current_problemset_id = problemsset.problemsSetId

            # Tag the parent component as well
            self._register_problemsset_tags(parent_question.get('tags') or [])

            child_questions = (
                (parent_question.get('childQuestions') or []) or
                (parent_question.get('questions') or []) or
                (parent_question.get('child-questions') or [])
            )

            for child in child_questions:
                if not self._register_problem(exam_section, child, isChildQuestion=True, isMockQuestion=isMockQuestion):
                    raise Exception("Error registering child problem")

            return True

        except Exception as e:
            print(f"Error in _register_problemsset: {str(e)}")
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
        """Main method to register questions."""
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
                    try:
                        secNo = int(str(sectionNumber))
                    except Exception:
                        secNo = int(str(sectionNumber)[-1])

                    current_mocksection = self.db.mocksections.create(data={
                        'mocktestid': self.current_mocktest_id,
                        'sectionnumber': secNo,
                        'sectionid': self.current_section_id
                    })
                    self.current_mocksection_id = current_mocksection.mocksectionid

                try:
                    self.current_mockquestion_number = 1
                    for question in questions:
                        if not isinstance(question, dict):
                            continue
                        qn = self._normalize_question(question)
                        is_parent = any(k in qn for k in ['childQuestions', 'child-questions', 'questions', 'sources'])

                        if is_parent:
                            if not self._register_problemsset(exam_section, qn, isMockQuestion=isMockQuestion):
                                raise Exception(f"Error registering problem set for {exam_section}")
                        else:
                            if not self._register_problem(exam_section, qn, isMockQuestion=isMockQuestion):
                                raise Exception(f"Error registering problem for {exam_section}")

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
