from prisma import Prisma
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

class DB:
    def __init__(self, prisma_client: Prisma):
        """Initialize DB with an existing Prisma client"""
        self.db = prisma_client
        
        # Load exam type and section mappings and initialize primary tables
        self._initialize_primary_tables()

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
                    exam_type = self.db.examtypes.create({
                        'examtypeid': exam_data['id'],
                        'name': exam_name,
                        'description': exam_data['description']
                    })
                    print(f"Exam type {exam_name} created successfully")
                    for section_name, section_data in exam_data['sections'].items():
                        section = self.db.sections.create({
                            'sectionid': section_data['id'],
                            'examtypeid': exam_type.examtypeid,
                            'name': section_name,
                            'description': section_data['description']
                        })

            # Initialize primary user if not exists
            existing_user = self.db.users.find_first()
            if not existing_user:
                self.db.users.create({
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

    def _get_exam_section_ids(self, exam_name: str, section_name: str) -> tuple[int, int]:
        """Helper method to get exam type and section IDs"""
        try:
            exam_data = self.definitions['examtypes'][exam_name]
            exam_id = exam_data['id']
            section_id = exam_data['sections'][section_name]['id']
            return exam_id, section_id
        except KeyError as e:
            raise ValueError(f"Invalid exam name or section: {str(e)}")

    def _register_problem_set(self, exam_id: int, section_id: int, title: str, content: Dict[str, Any], type_str: str) -> int:
        """Register a problem set and return its ID"""
        try:
            # Convert content to proper JSON format
            json_content = json.dumps(content)
            
            problem_set = self.db.problemsset.create({
                'examtypeid': exam_id,
                'sectionid': section_id,
                'title': title,
                'type': type_str,
                'content': json_content  # Pass as JSON string
            })
            return problem_set.problemsSetId
        except Exception as e:
            raise Exception(f"Failed to create problem set: {str(e)}")

    def _register_problem(self, exam_id: int, section_id: int, title: str, text: str, 
                         difficulty: int, solution: Dict[str, Any], 
                         problem_set_id: Optional[int] = None,
                         is_children: bool = False) -> int:
        """Register a problem and return its ID"""
        try:
            problem = self.db.problems.create({
                'examtypeid': exam_id,
                'sectionid': section_id,
                'title': title,
                'text': text,
                'difficulty': difficulty,
                'solution': solution,
                'problemsSetId': problem_set_id,
                'isChildren': is_children
            })
            return problem.problemid
        except Exception as e:
            raise Exception(f"Failed to create problem: {str(e)}")

    def _register_problem_options(self, problem_id: int, options: List[str], answer: str):
        """Register options for a problem"""
        try:
            for option in options:
                self.db.problemoptions.create({
                    'problemid': problem_id,
                    'optiontext': option,
                    'iscorrect': option == answer
                })
        except Exception as e:
            raise Exception(f"Failed to create problem options: {str(e)}")

    def _register_tags(self, problem_id: int, tags: List[str], exam_id: int, section_id: int):
        """Register tags for a problem"""
        try:
            for tag_name in tags:
                # Find or create tag
                existing_tag = self.db.tags.find_first(
                    where={
                        'name': tag_name,
                        'examtypeid': exam_id,
                        'sectionid': section_id
                    }
                )
                
                if not existing_tag:
                    existing_tag = self.db.tags.create({
                        'name': tag_name,
                        'examtypeid': exam_id,
                        'sectionid': section_id
                    })

                # Create problem tag relation
                self.db.problemtags.create({
                    'problemid': problem_id,
                    'tagid': existing_tag.tagid
                })
        except Exception as e:
            raise Exception(f"Failed to create tags: {str(e)}")

    def _register_problem_set_tags(self, problem_set_id: int, tags: List[str], exam_id: int, section_id: int):
        """Register tags for a problem set"""
        try:
            for tag_name in tags:
                # Find or create tag
                existing_tag = self.db.tags.find_first(
                    where={
                        'name': tag_name,
                        'examtypeid': exam_id,
                        'sectionid': section_id
                    }
                )
                
                if not existing_tag:
                    existing_tag = self.db.tags.create({
                        'name': tag_name,
                        'examtypeid': exam_id,
                        'sectionid': section_id
                    })

                # Create problem set tag relation
                self.db.problemssettags.create({
                    'problemsSetId': problem_set_id,
                    'tagid': existing_tag.tagid
                })
        except Exception as e:
            raise Exception(f"Failed to create problem set tags: {str(e)}")

    def register_questions(self, questions: Dict[str, List[Dict[str, Any]]]):
        """Register questions in the database"""
        try:
            for exam_section, question_list in questions.items():
                if not isinstance(question_list, list):
                    question_list = [question_list]
                    
                for question in question_list:
                    try:
                        if exam_section == "GMAT_IR":
                            self._register_gmat_ir_question(question)
                        elif exam_section == "GMAT_Q":
                            self._register_gmat_quants_question(question)
                        elif exam_section == "GMAT_V":
                            self._register_gmat_verbal_question(question)
                        elif exam_section == "GRE_Q":
                            self._register_gre_quants_question(question)
                        elif exam_section == "GRE_V":
                            self._register_gre_verbal_question(question)
                        else:
                            print(f"Unknown exam section: {exam_section}")
                            
                    except Exception as e:
                        print(f"Error registering question in {exam_section}: {str(e)}")
                        continue

        except Exception as e:
            print(f"Error in register_questions: {str(e)}")
            raise

    def _transform_graph_data(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform graph data to use valid field names"""
        if not isinstance(graph_data, dict):
            return graph_data

        transformed = {}
        for key, value in graph_data.items():
            # Transform key names
            new_key = key.replace('-', '_')
            
            # Transform nested dictionaries and lists
            if isinstance(value, dict):
                transformed[new_key] = self._transform_graph_data(value)
            elif isinstance(value, list):
                transformed[new_key] = [
                    self._transform_graph_data(item) if isinstance(item, dict) else item 
                    for item in value
                ]
            else:
                transformed[new_key] = value
                
        return transformed

    def _register_gmat_ir_question(self, question_data):
        """Register a GMAT IR question based on its type"""
        try:
            if "error" in question_data:
                print(f"Skipping question due to error: {question_data['error']}")
                return None

            # Determine question type from tags
            question_type = None
            if "tags" in question_data:
                for tag in question_data["tags"]:
                    if tag in ["GI", "MSR", "TA", "TPA"]:
                        question_type = tag
                        break

            if not question_type:
                print("Could not determine question type from tags")
                return None

            # Get exam type and section IDs from PrimaryTablesDefinitions
            exam_id = 2  # GMAT
            section_id = 5  # Integrated Reasoning

            if question_type == "GI":
                return self._register_gmat_ir_gi_question(question_data, exam_id, section_id)
            elif question_type == "MSR":
                return self._register_gmat_ir_msr_question(question_data, exam_id, section_id)
            elif question_type == "TA":
                return self._register_gmat_ir_ta_question(question_data, exam_id, section_id)
            elif question_type == "TPA":
                return self._register_gmat_ir_tpa_question(question_data, exam_id, section_id)

        except Exception as e:
            print(f"Error registering GMAT IR question: {str(e)}")
            return None

    def _register_gmat_ir_gi_question(self, question_data, exam_id, section_id):
        """Register a GMAT IR Graphic Interpretation question"""
        try:
            # Format content as a proper JSON string
            content = json.dumps({
                "graphs": question_data.get("graphs", []),
                "thread_id": question_data.get("thread_id", "")
            })

            # Create problems_set record
            problems_set = self.db.problemsset.create(
                data={
                    "sectionid": section_id,
                    "examtypeid": exam_id,
                    "title": question_data.get("title", "GMAT IR GI Question"),
                    "type": "GI",
                    "content": content  # Pass as JSON string
                }
            )

            # Format metadata and solution as JSON strings
            metadata = json.dumps({
                "prompt": question_data.get("prompt", ""),
                "type": "GI"
            })

            solution = json.dumps(question_data.get("solution", {}))

            # Create the main problem
            problem = self.db.problems.create(
                data={
                    "sectionid": section_id,
                    "examtypeid": exam_id,
                    "title": question_data.get("title", "GMAT IR GI Question"),
                    "text": question_data.get("question", ""),
                    "difficulty": question_data.get("difficulty", 1),
                    "solution": solution,  # Pass as JSON string
                    "problemsSetId": problems_set.problemsSetId,
                    "metadata": metadata  # Pass as JSON string
                }
            )

            # Create options
            options = question_data.get("options", [])
            answer = question_data.get("answer", "")
            
            for option in options:
                self.db.problemoptions.create(
                    data={
                        "problemid": problem.problemid,
                        "optiontext": str(option),  # Ensure string type
                        "iscorrect": option == answer
                    }
                )

            # Create tags
            if "tags" in question_data:
                for tag in question_data["tags"]:
                    # Try to find existing tag first
                    existing_tag = self.db.tags.find_first(
                        where={
                            "name": tag,
                            "examtypeid": exam_id,
                            "sectionid": section_id
                        }
                    )
                    
                    if not existing_tag:
                        # Create new tag if it doesn't exist
                        existing_tag = self.db.tags.create(
                            data={
                                "name": tag,
                                "examtypeid": exam_id,
                                "sectionid": section_id
                            }
                        )

                    # Create problem-tag relation
                    self.db.problemtags.create(
                        data={
                            "problemid": problem.problemid,
                            "tagid": existing_tag.tagid
                        }
                    )

            return problems_set.problemsSetId

        except Exception as e:
            print(f"Error registering GI question: {str(e)}")
            return None

    def _register_gmat_ir_msr_question(self, question_data, exam_id, section_id):
        """Register a GMAT IR Multi Source Reasoning question"""
        try:
            # Create problems_set record
            problems_set = self.db.problemsset.create(
                data={
                    "sectionid": section_id,
                    "examtypeid": exam_id,
                    "title": question_data.get("title", "GMAT IR MSR Question"),
                    "type": "MSR",
                    "content": {
                        "sources": question_data.get("sources", []),
                        "thread_id": question_data.get("thread_id", "")
                    }
                }
            )

            # Create child problems for each question
            for idx, child_q in enumerate(question_data.get("questions", [])):
                problem = self.db.problems.create(
                    data={
                        "sectionid": section_id,
                        "examtypeid": exam_id,
                        "title": child_q.get("title", f"Question {idx + 1}"),
                        "text": child_q.get("question", ""),
                        "difficulty": child_q.get("difficulty", 1),
                        "solution": child_q.get("solution", {}),  # Store raw solution
                        "problemsSetId": problems_set.problemsSetId,
                        "isChildren": True,
                        "metadata": {
                            "prompt": question_data.get("prompt", ""),
                            "type": "MSR",
                            "questionIndex": idx
                        }
                    }
                )

                # Register options for each child question
                options = child_q.get('options', [])
                answer = child_q.get('answer', '')
                
                for option in options:
                    self.db.problemoptions.create(
                        data={
                            "problemid": problem.problemid,
                            "optiontext": option,
                            "iscorrect": option == answer
                        }
                    )

            # Register tags if present
            if 'tags' in question_data:
                for tag in question_data['tags']:
                    tag_record = self.db.tags.create(
                        data={
                            "name": tag,
                            "examtypeid": exam_id,
                            "sectionid": section_id
                        }
                    )
                    self.db.problemssettags.create(
                        data={
                            "problemsSetId": problems_set.problemsSetId,
                            "tagid": tag_record.tagid
                        }
                    )

            return problems_set.problemsSetId

        except Exception as e:
            print(f"Error registering MSR question: {str(e)}")
            return None

    def _register_gmat_ir_ta_question(self, question_data, exam_id, section_id):
        """Register a GMAT IR Table Analysis question"""
        try:
            # Create problems_set record
            problems_set = self.db.problemsset.create(
                data={
                    "sectionid": section_id,
                    "examtypeid": exam_id,
                    "title": question_data.get("title", "GMAT IR TA Question"),
                    "type": "TA",
                    "content": {
                        "tables": question_data.get("tables", []),
                        "thread_id": question_data.get("thread_id", "")
                    }
                }
            )

            # Create the main problem
            problem = self.db.problems.create(
                data={
                    "sectionid": section_id,
                    "examtypeid": exam_id,
                    "title": question_data.get("title", "GMAT IR TA Question"),
                    "text": question_data.get("question", ""),
                    "difficulty": question_data.get("difficulty", 1),
                    "solution": question_data.get("solution", []),  # Store raw solution array
                    "problemsSetId": problems_set.problemsSetId,
                    "metadata": {
                        "prompt": question_data.get("prompt", ""),
                        "type": "TA"
                    }
                }
            )

            # Create options with Yes/No answers
            options = question_data.get("options", [])
            answers = question_data.get("answer", {})
            
            for option in options:
                self.db.problemoptions.create(
                    data={
                        "problemid": problem.problemid,
                        "optiontext": option,
                        "iscorrect": answers.get(option, "No") == "Yes",
                        "group": "Yes/No"  # Special handling for TA questions
                    }
                )

            # Add tags
            for tag in question_data.get("tags", []):
                tag_record = self.db.tags.create(
                    data={
                        "name": tag,
                        "examtypeid": exam_id,
                        "sectionid": section_id
                    }
                )
                self.db.problemssettags.create(
                    data={
                        "problemsSetId": problems_set.problemsSetId,
                        "tagid": tag_record.tagid
                    }
                )

            return problems_set.problemsSetId

        except Exception as e:
            print(f"Error registering TA question: {str(e)}")
            return None

    def _register_gmat_ir_tpa_question(self, question_data, exam_id, section_id):
        """Register a GMAT IR Two Part Analysis question"""
        try:
            # Create problems_set record
            problems_set = self.db.problemsset.create(
                data={
                    "sectionid": section_id,
                    "examtypeid": exam_id,
                    "title": question_data.get("title", "GMAT IR TPA Question"),
                    "type": "TPA",
                    "content": {
                        "part1": self._transform_graph_data(question_data.get("part1", {})),
                        "part2": self._transform_graph_data(question_data.get("part2", {})),
                        "thread_id": question_data.get("thread_id", ""),
                        "type": question_data.get("type", "")
                    }
                }
            )

            # Create the main problem
            problem = self.db.problems.create(
                data={
                    "sectionid": section_id,
                    "examtypeid": exam_id,
                    "title": question_data.get("title", "GMAT IR TPA Question"),
                    "text": question_data.get("question", ""),
                    "difficulty": question_data.get("difficulty", 1),
                    "solution": question_data.get("solution", ""),  # Store raw solution
                    "problemsSetId": problems_set.problemsSetId,
                    "metadata": {
                        "prompt": question_data.get("prompt", ""),
                        "type": "TPA"
                    }
                }
            )

            # Create options
            options = question_data.get("options", [])
            answer = question_data.get("answer", "")
            
            for option in options:
                self.db.problemoptions.create(
                    data={
                        "problemid": problem.problemid,
                        "optiontext": option,
                        "iscorrect": option == answer
                    }
                )

            # Add tags
            for tag in question_data.get("tags", []):
                tag_record = self.db.tags.create(
                    data={
                        "name": tag,
                        "examtypeid": exam_id,
                        "sectionid": section_id
                    }
                )
                self.db.problemssettags.create(
                    data={
                        "problemsSetId": problems_set.problemsSetId,
                        "tagid": tag_record.tagid
                    }
                )

            return problems_set.problemsSetId

        except Exception as e:
            print(f"Error registering TPA question: {str(e)}")
            return None

    def _register_gmat_quants_question(self, question: Dict[str, Any]):
        """Register a GMAT Quants question"""
        try:
            # Get exam type and section IDs from PrimaryTablesDefinitions
            exam_id = 2  # GMAT
            section_id = 3  # Quants
            
            # Create problem
            problem = self.db.problems.create(
                data={
                    "sectionid": section_id,
                    "examtypeid": exam_id,
                    "title": question.get('title', 'GMAT Quants Question'),
                    "text": question.get('question', ''),
                    "difficulty": int(question.get('difficulty', 1)),
                    "solution": question.get('solution', {}),
                    "metadata": {
                        "statements": question.get('statements', []),
                        "type": "DS" if "statements" in question else "PS"
                    }
                }
            )

            # Register options
            options = question.get('options', [])
            answer = question.get('answer', '')
            
            for option in options:
                self.db.problemoptions.create(
                    data={
                        "problemid": problem.problemid,
                        "optiontext": option,
                        "iscorrect": option == answer
                    }
                )

            # Register tags
            if 'tag' in question:
                tags = question['tag'] if isinstance(question['tag'], list) else [question['tag']]
                for tag in tags:
                    tag_record = self.db.tags.create(
                        data={
                            "name": tag,
                            "examtypeid": exam_id,
                            "sectionid": section_id
                        }
                    )
                    self.db.problemtags.create(
                        data={
                            "problemid": problem.problemid,
                            "tagid": tag_record.tagid
                        }
                    )

            return problem.problemid

        except Exception as e:
            print(f"Error registering GMAT Quants question: {str(e)}")
            raise

    def _register_gmat_verbal_question(self, question: Dict[str, Any]):
        """Register a GMAT Verbal question"""
        try:
            # Get exam type and section IDs from PrimaryTablesDefinitions
            exam_id = 2  # GMAT
            section_id = 4  # Verbal
            
            # Create problem set for passage
            problems_set = self.db.problemsset.create(
                data={
                    "sectionid": section_id,
                    "examtypeid": exam_id,
                    "title": question.get('title', 'GMAT Verbal Question'),
                    "type": "RC",
                    "content": {
                        "passage": question.get('passage', ''),
                        "thread_id": question.get('thread_id', '')
                    }
                }
            )

            # Register child questions
            for child_q in question.get('childQuestions', []):
                problem = self.db.problems.create(
                    data={
                        "sectionid": section_id,
                        "examtypeid": exam_id,
                        "title": child_q.get('title', 'GMAT Verbal Child Question'),
                        "text": child_q.get('question', ''),
                        "difficulty": child_q.get('difficulty', 1),
                        "solution": child_q.get('solution', {}),
                        "problemsSetId": problems_set.problemsSetId,
                        "isChildren": True,
                        "metadata": {
                            "type": "RC",
                            "prompt": child_q.get('prompt', '')
                        }
                    }
                )

                # Register options for each child question
                options = child_q.get('options', [])
                answer = child_q.get('answer', '')
                
                for option in options:
                    self.db.problemoptions.create(
                        data={
                            "problemid": problem.problemid,
                            "optiontext": option,
                            "iscorrect": option == answer
                        }
                    )

            # Register tags if present
            if 'tag' in question:
                tags = question['tag'] if isinstance(question['tag'], list) else [question['tag']]
                for tag in tags:
                    tag_record = self.db.tags.create(
                        data={
                            "name": tag,
                            "examtypeid": exam_id,
                            "sectionid": section_id
                        }
                    )
                    self.db.problemssettags.create(
                        data={
                            "problemsSetId": problems_set.problemsSetId,
                            "tagid": tag_record.tagid
                        }
                    )

            return problems_set.problemsSetId

        except Exception as e:
            print(f"Error registering GMAT Verbal question: {str(e)}")
            raise

    def _register_gre_quants_question(self, question: Dict[str, Any]):
        """Register a GRE Quants question"""
        try:
            # Get exam type and section IDs from PrimaryTablesDefinitions
            exam_id = 1  # GRE
            section_id = 1  # Quants
            
            # Create problem
            problem = self.db.problems.create(
                data={
                    "sectionid": section_id,
                    "examtypeid": exam_id,
                    "title": question.get('title', 'GRE Quants Question'),
                    "text": question.get('question', ''),
                    "difficulty": int(question.get('difficulty', 1)),
                    "solution": question.get('solution', {}),
                    "metadata": {
                        "statements": question.get('statements', []),
                        "type": "DS" if "statements" in question else "PS"
                    }
                }
            )

            # Register options
            options = question.get('options', [])
            answer = question.get('answer', '')
            
            for option in options:
                self.db.problemoptions.create(
                    data={
                        "problemid": problem.problemid,
                        "optiontext": option,
                        "iscorrect": option == answer
                    }
                )

            # Register tags
            if 'tags' in question:
                for tag in question['tags']:
                    tag_record = self.db.tags.create(
                        data={
                            "name": tag,
                            "examtypeid": exam_id,
                            "sectionid": section_id
                        }
                    )
                    self.db.problemtags.create(
                        data={
                            "problemid": problem.problemid,
                            "tagid": tag_record.tagid
                        }
                    )

            return problem.problemid

        except Exception as e:
            print(f"Error registering GRE Quants question: {str(e)}")
            raise

    def _register_gre_verbal_question(self, question: Dict[str, Any]):
        """Register a GRE Verbal question"""
        try:
            # Format metadata and solution as JSON strings
            metadata = json.dumps({
                "thread_id": question.get("thread_id", ""),
                "type": "verbal"
            })

            solution = json.dumps({
                "explanation": question.get("solution", "")
            })

            # Create the main problem
            problem = self.db.problems.create(
                data={
                    "sectionid": 2,  # GRE Verbal section ID
                    "examtypeid": 1,  # GRE exam ID
                    "title": question.get("title", ""),
                    "text": question.get("question", ""),
                    "difficulty": question.get("difficulty", 1),
                    "solution": solution,
                    "metadata": metadata
                }
            )

            # Create options
            options = question.get("options", [])
            answer = question.get("answer", "")
            
            for option in options:
                self.db.problemoptions.create(
                    data={
                        "problemid": problem.problemid,
                        "optiontext": str(option),
                        "iscorrect": option == answer
                    }
                )

            # Create tags
            if "tags" in question:
                for tag in question["tags"]:
                    # Try to find existing tag first
                    existing_tag = self.db.tags.find_first(
                        where={
                            "name": tag,
                            "examtypeid": 1,  # GRE
                            "sectionid": 2    # Verbal
                        }
                    )
                    
                    if not existing_tag:
                        # Create new tag if it doesn't exist
                        existing_tag = self.db.tags.create(
                            data={
                                "name": tag,
                                "examtypeid": 1,
                                "sectionid": 2
                            }
                        )

                    # Create problem-tag relation
                    self.db.problemtags.create(
                        data={
                            "problemid": problem.problemid,
                            "tagid": existing_tag.tagid
                        }
                    )

            print(f"Successfully registered GRE Verbal question: {problem.problemid}")
            return problem.problemid

        except Exception as e:
            print(f"Error registering GRE Verbal question: {str(e)}")
            raise

    def __del__(self):
        """Destructor to ensure database connection is closed"""
        if hasattr(self, 'db') and self.db.is_connected():
            self.db.disconnect()

    def delete_all_questions(self):
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
            
            print("✓ Successfully deleted all question content")
            
        except Exception as e:
            print(f"Error deleting question content: {str(e)}")
            raise
    