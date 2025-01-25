from prisma import Prisma
import json
from datetime import datetime

class DB: 
    def __init__(self, prisma_client: Prisma):
      self.db= prisma_client
      self.current_exam_id = 0
      self.current_section_id = 0
      self._initialize_primary_tables()
      
    # initializing IDs
      self.current_problem_id = 0
      self.current_tag_id = 0
      self.current_problemset_id = 0
      self.current_mocktest_id = 0
      self.current_mocktestquestion_id = 0
      return None

    def _initialize_primary_tables(self):
        """Initialize primary tables if they don't exist"""
        try:
            with open('PrimaryTablesDefinitions.json', 'r') as f:
                self.definitions = json.load(f)

            # Initialize exam types and sections
            for exam_name, exam_data in self.definitions['examtypes'].items():
                # Check if exam type exists
                existing_exam =  self.db.examtypes.find_first(
                    where={'examtypeid': exam_data['id']}
                )
                if not existing_exam:
                    exam_type =  self.db.examtypes.create({
                        'examtypeid': exam_data['id'],
                        'name': exam_name,
                        'description': exam_data['description']
                    })
                    print(f"Exam type {exam_name} created successfully")
                    for section_name, section_data in exam_data['sections'].items():
                        section =  self.db.sections.create({
                            'sectionid': section_data['id'],
                            'examtypeid': exam_type.examtypeid,
                            'name': section_name,
                            'description': section_data['description']
                        })

            # Initialize primary user if not exists
            existing_user =  self.db.users.find_first()
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

    def _get_exam_section_ids(self, exam_section):
       section_components = {
           "V": "Verbal",
           "Q": "Quants",
           "IR": "Integrated Reasoning"
       } 
       exam_name, section = exam_section.split("_")
       try: 
         section_name = section_components[section]
       except KeyError: 
         raise ValueError(f"Invalid section name: {section}")
       exam =  self.db.examtypes.find_first(where= {'name': exam_name})
       section =  self.db.sections.find_first(where= {'name': section_name, 'examtypeid': exam.examtypeid})
       if not exam or not section: 
         raise ValueError(f"Exam or section not found: {exam_name} {section_name}")
       self.current_exam_id = int(exam.examtypeid)
       self.current_section_id = int(section.sectionid)
       return None

    def _register_problem(self, exam_section, question, isChildQuestion=False, isMockQuestion=False):
       """Register a single problem"""
       try:
           self._get_exam_section_ids(exam_section)
           
           # Format metadata as JSON string
           metadata = json.dumps({})
           if 'part1' in question and 'part2' in question:
               metadata = json.dumps({
                   "type": "parts",
                   "content": {
                       "part1": question['part1'],
                       "part2": question['part2']
                   }
               })
           elif 'passages' in question:
               metadata = json.dumps({
                   "type": "CR",
                   "content": question['passages']
               })
           elif 'graphs' in question:
               metadata = json.dumps({
                   "type": "Graphical",
                   "content": question['graphs']
               })
           else:
               metadata = json.dumps({})
           
           # Format solution
           solution = question.get('solution', {})
           if isinstance(solution, (str, dict)):
               solution = json.dumps({"solution": solution})
           else: 
               solution = json.dumps(solution)
           # Create problem with proper Prisma format
           question_data = {
               "title": question.get('title', ''),
               "text": question.get('question', ''),
               "difficulty": question.get('difficulty', 1),
               "metadata": metadata,  # Prisma will handle JSON conversion
               "solution": solution,  # Prisma will handle JSON conversion
               "isChildren": isChildQuestion,
               "isMockQuestion": isMockQuestion,
               "sections": {"connect": {"sectionid": self.current_section_id}},
               "examtypes": {"connect": {"examtypeid": self.current_exam_id}}
           }
           if isChildQuestion:
               question_data["ProblemsSet"] = {"connect": {"problemsSetId": self.current_problemset_id}}    
           if isMockQuestion: 
               question_data["mocktestquestions"] = {"connect": {"mocktestquestionid": self.current_mocktestquestion_id}}

           problem =  self.db.problems.create(data = question_data)
           self.current_problem_id = problem.problemid

           options = question.get('options', [])
           answer = question.get('answer', '')
           
           for option in options:
               if isinstance(option, str):
                   self._register_problem_options(option, answer)
               else:
                   group = "A"
                   for suboption in option:
                       self._register_problem_options(suboption, answer, group)
                       group = chr(ord(group) + 1)
                       
           # Register tags 
           self._register_problem_tags(question.get('tags', []))

           return True
           
       except Exception as e:
           print(f"Error in _register_problem: {str(e)}")
           return False

    def _register_problem_options(self, option, answers, group=None):
       
       correct_answers = []
       if isinstance(answers, dict): # for TA questions
           for option, answer in answers.items():
               if answer == "Yes":
                   correct_answers.append(option)
       elif isinstance(answers, list):
           correct_answers = answers
       else: 
           correct_answers = [answers]
       
       option_data = {
            'optiontext': option,
            'iscorrect': True if option in correct_answers else False,
            'problems': {'connect': {'problemid': self.current_problem_id}}
        }
       if group:
           option_data['group'] = group
       try: 
            self.db.problemoptions.create(
               data = option_data
               )
       except Exception as e: 
           print(f"Error creating problem option in _register_problem_options: {str(e)}")
           return False
       return True
   
    def _register_problem_tags(self, tags):
       try:
           for tag in tags:
               tagid =  self._register_tag(tag) # ✅
               tag_data = {
                   'tags': {'connect': {'tagid': tagid}},
                   'problems': {'connect': {'problemid': self.current_problem_id}}
               }
               self.db.problemtags.create(data = tag_data) # ❌
       except Exception as e: 
           print(f"Error creating problem tags in _register_problem_tags: {str(e)}")
           return False
       return True
   
    def _register_problemsset_tags(self, tags):
       try:
           for tag in tags:
               tagid =  self._register_tag(tag)
               tag_data = {
                   'tags': {'connect': {'tagid': tagid}},
                   'ProblemsSet': {'connect': {'problemsSetId': self.current_problem_id}}
               }
               self.db.problemssettags.create(
                   data = tag_data
               )
       except Exception as e: 
           print(f"Error creating problemset tags in _register_problemsset_tags: {str(e)}")
           return False
       return True
    
    # ✅
    def _register_tag(self, tag):
       try: 
           tagid =  self.db.tags.find_first(where={'name': tag})
           if tagid:
               return tagid.tagid
           else:
               tag_data = {
                   'name': tag,
                   'examtypes': {'connect': {'examtypeid': self.current_exam_id}},
                   'sections': {'connect': {'sectionid': self.current_section_id}}
               }
               tagid =  self.db.tags.create(
                   data = tag_data
               )
               return tagid.tagid
       except Exception as e: 
           print(f"Error creating tag in _register_tag: {str(e)}")
           return False
       return True
   
    def _register_problemsset(self, exam_section, parent_question, isMockQuestion=False):
       """Register a problem set with its child questions"""
       try:
           self._get_exam_section_ids(exam_section)
           
           # Determine content type and data
           problemsset_data = {
                'title': parent_question.get('title', ''),
                'sections': {'connect': {'sectionid': self.current_section_id}},
                'examtypes': {'connect': {'examtypeid': self.current_exam_id}}
            }
           if 'sources' in parent_question:
               problemsset_data['type'] = "MSR"
               problemsset_data['content'] = json.dumps(parent_question['sources'])
           elif 'passages' in parent_question:
               problemsset_data['type'] = "RC"
               problemsset_data['content'] = json.dumps(parent_question['passages'])
           elif 'graphs' in parent_question:
               problemsset_data['type'] = "GI"
               problemsset_data['content'] = json.dumps(parent_question['graphs'])
           elif 'graph/table' in parent_question:
               problemsset_data['type'] = "graph/table"
               problemsset_data['content'] = json.dumps(parent_question['graph/table'])
           else:
                raise ValueError("No content found in parent question")
                return False
           if isMockQuestion:
                problemsset_data['mocktestquestions'] = {'connect': {'mocktestquestionid': self.current_mocktestquestion_id}}
           # Create problem set
           try: 
               
               problemsset =  self.db.problemsset.create(data = problemsset_data)
               self.current_problemset_id = problemsset.problemsSetId
           except Exception as e: 
               print(f"Error registering parent question component in _register_problemset: {str(e)}")
               return False


           # Register child questions
           child_questions = (
               parent_question.get('childQuestions', []) or 
               parent_question.get('questions', [])
           )
           
           for child in child_questions:
               if not  self._register_problem(exam_section, child, isChildQuestion=True, isMockQuestion=isMockQuestion):
                   raise Exception("Error registering child problem")

           self.current_problemset_id += 1
           return True
           
       except Exception as e:
           print(f"Error in _register_problemset: {str(e)}")
           return False

    def registerQuestion(self, exam_section, questions, isMockQuestion=False):
       """Main method to register questions"""
       try:
           for question in questions:
               # Check for parent-child questions using multiple possible keys
               if any(key in question for key in ['childQuestions', 'questions', 'sources']):
                   # Handle parent-child questions
                   if not  self._register_problemsset(exam_section, question, isMockQuestion=isMockQuestion):
                       raise Exception(f"Error registering problem set for {exam_section}")
               else:
                   # Handle single questions
                   if not  self._register_problem(exam_section, question, isMockQuestion=isMockQuestion):
                       raise Exception(f"Error registering problem for {exam_section}")
           return True
       except Exception as e:
           print(f"Error in registerQuestion: {str(e)}")
           return False
