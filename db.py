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

    def register_questions(self, questions: Dict[str, Any]):
        """Main method to register all questions"""
        try:
            # Process GMAT IR questions
            if 'GMAT_IR' in questions:
                for question in questions['GMAT_IR']:
                    self._register_gmat_ir_question(question)

            # Process GMAT Quants questions
            if 'GMAT_Q' in questions:
                for question in questions['GMAT_Q']:
                    self._register_gmat_quants_question(question)

            # Process GMAT Verbal questions
            if 'GMAT_V' in questions:
                self._register_gmat_verbal_question(questions['GMAT_V'])

            # Process GRE Quants questions
            if 'GRE_Q' in questions:
                for question in questions['GRE_Q']:
                    self._register_gre_quants_question(question)

            # Process GRE Verbal questions
            if 'GRE_V' in questions:
                for question in questions['GRE_V']:
                    self._register_gre_verbal_question(question)

        except Exception as e:
            print(f"Error registering questions: {str(e)}")
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

    def _register_gmat_ir_question(self, question: Dict[str, Any]):
        """Register a GMAT IR question"""
        try:
            exam_id, section_id = self._get_exam_section_ids('GMAT', 'Integrated Reasoning')
            
            # For questions with graphs/tables, create a problem set
            if 'graphs' in question or 'tables' in question or 'sources' in question:
                # Prepare content dictionary
                content = {}
                if 'graphs' in question:
                    # Transform graph data to use underscores instead of hyphens
                    content['graphs'] = []
                    for graph in question['graphs']:
                        transformed_graph = {}
                        for k, v in graph.items():
                            new_key = k.replace('-', '_')
                            if isinstance(v, dict):
                                transformed_graph[new_key] = {
                                    k2.replace('-', '_'): v2 
                                    for k2, v2 in v.items()
                                }
                            elif isinstance(v, list):
                                transformed_graph[new_key] = [
                                    {k2.replace('-', '_'): v2 for k2, v2 in item.items()}
                                    if isinstance(item, dict) else item
                                    for item in v
                                ]
                            else:
                                transformed_graph[new_key] = v
                        content['graphs'].append(transformed_graph)
                
                if 'tables' in question:
                    content['tables'] = question['tables']
                if 'sources' in question:
                    content['sources'] = question['sources']

                # Generate a title if not present
                title = question.get('title', '')
                if not title and 'graphs' in content:
                    # Use the first graph's title if available
                    title = next((graph.get('title', '') for graph in content['graphs']), 'GMAT IR Question')
                elif not title:
                    title = 'GMAT IR Question'

                problem_set_id = self._register_problem_set(
                    exam_id=exam_id,
                    section_id=section_id,
                    title=title,
                    content=content,
                    type_str=question.get('tags', [''])[0] if 'tags' in question else ''
                )

                # Register tags for problem set if present
                if 'tags' in question:
                    self._register_problem_set_tags(problem_set_id, question['tags'], exam_id, section_id)

                # For multi-source reasoning or table analysis with multiple questions
                if 'questions' in question:
                    for child_q in question['questions']:
                        # Convert solution to JSON string if it exists
                        solution = json.dumps(child_q.get('solution', {})) if child_q.get('solution') else '{}'
                        
                        problem_id = self._register_problem(
                            exam_id=exam_id,
                            section_id=section_id,
                            title=child_q.get('title', 'Question'),
                            text=child_q.get('question', ''),
                            difficulty=int(question.get('difficulty', 1)),
                            solution=solution,
                            problem_set_id=problem_set_id,
                            is_children=True
                        )
                        if 'options' in child_q and 'answer' in child_q:
                            self._register_problem_options(problem_id, child_q['options'], child_q['answer'])
                else:
                    # Single question case
                    # Convert solution to JSON string if it exists
                    solution = json.dumps(question.get('solution', {})) if question.get('solution') else '{}'
                    
                    problem_id = self._register_problem(
                        exam_id=exam_id,
                        section_id=section_id,
                        title=question.get('title', 'Question'),
                        text=question.get('question', ''),
                        difficulty=int(question.get('difficulty', 1)),
                        solution=solution,
                        problem_set_id=problem_set_id,
                        is_children=False
                    )
                    if 'options' in question and 'answer' in question:
                        self._register_problem_options(problem_id, question['options'], question['answer'])
            else:
                # For questions without graphs/tables
                # Convert solution to JSON string if it exists
                solution = json.dumps(question.get('solution', {})) if question.get('solution') else '{}'
                
                problem_id = self._register_problem(
                    exam_id=exam_id,
                    section_id=section_id,
                    title=question.get('title', 'Question'),
                    text=question.get('question', ''),
                    difficulty=int(question.get('difficulty', 1)),
                    solution=solution,
                    problem_set_id=None,
                    is_children=False
                )
                if 'options' in question and 'answer' in question:
                    self._register_problem_options(problem_id, question['options'], question['answer'])

                # Register tags if present
                if 'tags' in question:
                    self._register_tags(problem_id, question['tags'], exam_id, section_id)

        except Exception as e:
            print(f"Error registering GMAT IR question: {str(e)}")
            raise

    def _register_gmat_quants_question(self, question: Dict[str, Any]):
        """Register a GMAT Quants question"""
        try:
            exam_id, section_id = self._get_exam_section_ids('GMAT', 'Quants')
            
            # Create problem
            problem_id = self._register_problem(
                exam_id=exam_id,
                section_id=section_id,
                title=question['title'],
                text=question['question'],
                difficulty=int(question.get('difficulty', 1)),
                solution=question.get('solution', {})
            )

            # Register options
            self._register_problem_options(problem_id, question['options'], question['answer'])

            # Register tags if present
            if 'tag' in question:
                self._register_tags(problem_id, question['tag'], exam_id, section_id)

        except Exception as e:
            print(f"Error registering GMAT Quants question: {str(e)}")
            raise

    def _register_gmat_verbal_question(self, question: Dict[str, Any]):
        """Register a GMAT Verbal question"""
        try:
            exam_id, section_id = self._get_exam_section_ids('GMAT', 'Verbal')
            
            # Create problem set for passage
            content = {'passage': question['passage']}
            problem_set_id = self._register_problem_set(
                exam_id=exam_id,
                section_id=section_id,
                title=question['title'],
                content=content,
                type_str='RC'
            )

            # Register child questions
            for child_q in question['childQuestions']:
                problem_id = self._register_problem(
                    exam_id=exam_id,
                    section_id=section_id,
                    title=child_q['title'],
                    text=child_q['question'],
                    difficulty=1,  # Default difficulty
                    solution=child_q.get('solution', {}),
                    problem_set_id=problem_set_id,
                    is_children=True
                )
                self._register_problem_options(problem_id, child_q['options'], child_q['answer'])

        except Exception as e:
            print(f"Error registering GMAT Verbal question: {str(e)}")
            raise

    def _register_gre_quants_question(self, question: Dict[str, Any]):
        """Register a GRE Quants question"""
        try:
            exam_id, section_id = self._get_exam_section_ids('GRE', 'Quants')
            
            # Create problem
            problem_id = self._register_problem(
                exam_id=exam_id,
                section_id=section_id,
                title=question['title'],
                text=question['question'],
                difficulty=int(question.get('difficulty', 1)),
                solution=question.get('solution', {})
            )

            # Register options
            self._register_problem_options(problem_id, question['options'], question['answer'])

            # Register tags if present
            if 'tag' in question:
                self._register_tags(problem_id, question['tag'], exam_id, section_id)

        except Exception as e:
            print(f"Error registering GRE Quants question: {str(e)}")
            raise

    def _register_gre_verbal_question(self, question: Dict[str, Any]):
        """Register a GRE Verbal question"""
        try:
            exam_id, section_id = self._get_exam_section_ids('GRE', 'Verbal')
            
            # Create problem set for passage
            content = {'passages': question['passages']}
            problem_set_id = self._register_problem_set(
                exam_id=exam_id,
                section_id=section_id,
                title=question['title'],
                content=content,
                type_str='RC'
            )

            # Register child questions
            for child_q in question['childQuestions']:
                problem_id = self._register_problem(
                    exam_id=exam_id,
                    section_id=section_id,
                    title=child_q['title'],
                    text=child_q['question'],
                    difficulty=1,  # Default difficulty
                    solution=child_q.get('solution', {}),
                    problem_set_id=problem_set_id,
                    is_children=True
                )
                self._register_problem_options(problem_id, child_q['options'], child_q['answer'])

                # Register tags if present
                if 'tag' in child_q:
                    self._register_tags(problem_id, child_q['tag'], exam_id, section_id)

        except Exception as e:
            print(f"Error registering GRE Verbal question: {str(e)}")
            raise

    def __del__(self):
        """Destructor to ensure database connection is closed"""
        if hasattr(self, 'db') and self.db.is_connected():
            self.db.disconnect() 