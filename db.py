from prisma import Prisma
import json, re
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
      self.current_mocksection_id = None
      self.current_mockquestion_number = None
      self.question_type = ""
      self.question_correction_validator = ""
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
                    print(f"Exam type {exam_name} not found, creating it")
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
               type = question.get('prompt', '').split("-")[4]
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
            
           question_data = {
               "type": question.get('type', ''),
               "prompt": question.get('prompt', ''),
               "title": question.get('title', ''),
               "text": question.get('question', ''),
               "difficulty": question.get('difficulty', 1),
               "metadata": json.dumps(question.get('content', {})),  # Prisma will handle JSON conversion
               "solution": solution,  # Prisma will handle JSON conversion
               "isChildren": isChildQuestion,
               "isMockQuestion": isMockQuestion,
               "sections": {"connect": {"sectionid": self.current_section_id}},
               "examtypes": {"connect": {"examtypeid": self.current_exam_id}}
           }

           if isChildQuestion:
               question_data["ProblemsSet"] = {"connect": {"problemsSetId": self.current_problemset_id}}    
           if isMockQuestion: 
               question_data["mocksections"] = {"connect": {"mocksectionid": self.current_mocksection_id}}
               question_data["mockquestionnumber"] = self.current_mockquestion_number
           if self.question_type == "NE":
               question_data["metadata"]  = json.dumps({"answer": question.get('answer', '')})
            
           problem =  self.db.problems.create(data = question_data)
           self.current_problem_id = problem.problemid

           options = question.get('options', [])
           answer = question.get('answer', '')
           
           for option in options:
               if isinstance(option, str):
                   self._register_problem_options(option, answer)
               elif isinstance(option, int):
                   self._register_problem_options(option, answer)
               elif isinstance(option, list):
                   group = "A"
                   for suboption in option:
                       self._register_problem_options(suboption, answer, group)
                       group = chr(ord(group) + 1)
                       
           # Register tags 
           self._register_problem_tags(question.get('tags', []))

           return True
           
       except Exception as e:
           print(f"Error in _register_problem: {str(e)}\n\n here is the question content: {json.dumps(question, indent=4)}")
           return False

    def _register_problem_options(self, option, answers, group=None):
       
       correct_answers = []
       if isinstance(answers, dict):
           # First, check if this is a True/False or Yes/No type question with inverted structure
           if "True" in answers or "False" in answers or "Yes" in answers or "No" in answers:
               # Handle case where answer dict keys are True/False and values are option texts
               for key, value in answers.items():
                   if value == option:
                       # This option text matches a value in the answers dict
                       # Mark as correct if the key is "True" or "Yes"
                       is_correct = key.lower() in ["true", "yes"]
                       break
               else:
                   # Option not found in values, default to False
                   is_correct = False
           else:
               # Original code for TA questions where option is a key in answers dict
               finder = self.question_correction_validator # for TA questions
               if finder:
                   ansVal = finder
               else:
                   ansVal = "Yes"
               # Add try/except to catch KeyError
               try:
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
            'problems': {'connect': {'problemid': self.current_problem_id}}
        }
       if group:
           option_data['group'] = group
       try: 
            self.db.problemoptions.create(
               data = option_data
               )
       except Exception as e: 
           print(f"Error creating problem option in _register_problem_options: {str(e)} \n\n here is the option: {option} \n\n here is the answer: {answers}")
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
           print(f"here is the value received for tagid: {tagid}")
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
           pattern = r'\(.*?\)'
           tag = re.sub(pattern, '', tag).strip()

           tag = re.sub(r' ,*', '', tag) if ' ,' in tag else tag # remove anything after comma
           tagid =  self.db.tags.find_first(where={'name': tag, 
                                                   'examtypeid': self.current_exam_id,
                                                   'sectionid': self.current_section_id
                                                   }) #because two different exams/sections can have same tag
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
           print(f"for {self.current_mockquestion_number}")
           print(f"here is the tag value that is causing the issue:- {tag} ")
           return False
   
    def _register_problemsset(self, exam_section, parent_question, isMockQuestion=False):
       """Register a problem set with its child questions"""
       try:
           self._get_exam_section_ids(exam_section)
           
           # Determine content type and data
           problemsset_data = {
                'type': parent_question.get('type', ''),
                'content': json.dumps(parent_question.get('content', {})),
                'title': parent_question.get('title', ''),
                'sections': {'connect': {'sectionid': self.current_section_id}},
                'examtypes': {'connect': {'examtypeid': self.current_exam_id}}
            }
           
           if isMockQuestion:
                problemsset_data['mockquestionnumber'] = self.current_mockquestion_number
                problemsset_data['mocksections'] = {'connect': {'mocksectionid': self.current_mocksection_id}}

           # Create problem set
           try: 
               
               problemsset =  self.db.problemsset.create(data = problemsset_data)
               self.current_problemset_id = problemsset.problemsSetId
           except Exception as e: 
               print(f"Error registering parent question component in _register_problemset: {str(e)} \n\n here is the parent question content: {json.dumps(parent_question.get('content', {}), indent=4)}")
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

    def having_any_empty_value(self, component):
        if not component:
            return False # None
        if isinstance(component, int) or isinstance(component, float):
            return True
        if isinstance(component, list):
            if len(component):
                for cell in component:
                    val = self.having_any_empty_value(cell)
                    if not val:
                        return False
                return True
            return False # []
        if isinstance(component, str):
            if len(component):
                return True
            return False # ""
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
    #    here we will be getting complete paper.
    # region not validating the question components if they are empty or not
    #    for exam_section, subSections in paper.items():
    #        questions_to_remove = []
    #        for questions in subSections.values():
    #             for question in questions:
    #                 if not self.having_any_empty_value(question):
    #                     print(f"some of the component in the string for {exam_section} is empty, thus not registering such question")
    #                     print(f"thread_id: {question.get('thread_id', 'Even thread_id is empty')}")
    #                     isMockQuestion = False # if any question is empty, don't put the whole paper in mock test.
    #                     questions_to_remove.append(question)

    #             for question in questions_to_remove:
    #                 questions.remove(question)
    # endregion

       if isMockQuestion:
           exam_section = list(paper.keys())[0]
           self._get_exam_section_ids(exam_section)
           current_mocktest = self.db.mocktests.create({
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
                    current_mocksection = self.db.mocksections.create({
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
                            if not  self._register_problemsset(exam_section, question,isMockQuestion=isMockQuestion):
                                raise Exception(f"Error registering problem set for {exam_section}")
                        else:
                            # Handle single questions
                            if not  self._register_problem(exam_section, question, isMockQuestion=isMockQuestion):
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
    
