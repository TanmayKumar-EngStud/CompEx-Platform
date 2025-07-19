print("Startup in progress...")

import json
from prisma import Prisma
from db import DB
import time
from terminal_logger import start_terminal_logging, stop_terminal_logging

# Import unified mock generation system
from core.mock.unified_mock_generator import UnifiedMockGenerator
from core.enums.exam_types import ExamType

class Main:
   def __init__(self):
      # Start terminal logging to capture all output
      self.terminal_logger = start_terminal_logging()
      
      # Set default difficulty and mock settings (no persistence)
      self._difficulty_and_is_mock = {
         'difficulty': 3,  # Start with medium difficulty
         'is_mock': True
      }
      self.db = Prisma(auto_register=True)
      self.db.connect()
      self.database = DB(self.db)
      
      print(f"Initialized - Difficulty: {self._difficulty_and_is_mock['difficulty']}, Mock: {self._difficulty_and_is_mock['is_mock']}")

   def generate_paper(self):
      start_time = time.time()
      gmat_success = False
      gre_success = False
      
      print("=" * 80)
      print("PAPER GENERATION SESSION STARTED")
      print("=" * 80)
      
      try:
         # GMAT Paper Generation (First) - RC ONLY
         print(f"Starting GMAT paper generation - Difficulty: {self._difficulty_and_is_mock['difficulty']}")
         gmat_mock = UnifiedMockGenerator(ExamType.GMAT, self._difficulty_and_is_mock['difficulty'])
         GMAT_paper = gmat_mock.generate_mock_paper()
         timestamp = time.strftime("%d-%m-%H-%M", time.localtime())
         gmat_filepath = f'papers/GMAT/GMAT_paper-{timestamp}-difficulty-{self._difficulty_and_is_mock["difficulty"]}.json'
         
         with open(gmat_filepath, 'w') as f:
            try:
               json.dump(GMAT_paper, f, indent=2)
               print(f"GMAT paper saved successfully: {gmat_filepath}")
            except Exception as e:
               print(f"GMAT paper storing Error: {str(e)}")
               raise e
         
         try:
            self.database.registerQuestion(GMAT_paper, isMockQuestion=self._difficulty_and_is_mock['is_mock'], difficulty=self._difficulty_and_is_mock['difficulty'])
            print("GMAT questions registered in database successfully")
         except Exception as e:
            print(f"GMAT database registration failed: {str(e)}")
            raise e
            
         gmat_success = True
         print("GMAT paper generation completed successfully")
         
      except Exception as e:
         print(f"GMAT paper generation failed: {str(e)}")
         gmat_success = False
      
      # Skip sleep since we're not using GMAT API
      # print("Sleeping for 60 seconds for API rate limit reset")
      # time.sleep(60)
      
      # COMMENTED OUT FOR GMAT RC DEBUGGING
      # try:
      #    # GRE Paper Generation (Second)
      #    print(f"Starting GRE paper generation - Difficulty: {self._difficulty_and_is_mock['difficulty']}")
      #    gre_mock = UnifiedMockGenerator(ExamType.GRE, self._difficulty_and_is_mock['difficulty'])
      #    GRE_paper = gre_mock.generate_mock_paper()
      #    timestamp = time.strftime("%d-%m-%H-%M", time.localtime())
      #    gre_filepath = f'papers/GRE/GRE_paper-{timestamp}-difficulty-{self._difficulty_and_is_mock["difficulty"]}.json'
      #    
      #    with open(gre_filepath, 'w') as f:
      #       try:
      #          json.dump(GRE_paper, f, indent=2)
      #          print(f"GRE paper saved successfully: {gre_filepath}")
      #       except Exception as e:
      #          print(f"GRE paper storing Error: {str(e)}")
      #          raise e
      #
      #    try:
      #       self.database.registerQuestion(GRE_paper, isMockQuestion=self._difficulty_and_is_mock['is_mock'], difficulty=self._difficulty_and_is_mock['difficulty'])
      #       print("GRE questions registered in database successfully")
      #    except Exception as e:
      #       print(f"GRE database registration failed: {str(e)}")
      #       raise e
      #       
      #    gre_success = True
      #    print("GRE paper generation completed successfully")
      #    
      # except Exception as e:
      #    print(f"GRE paper generation failed: {str(e)}")
      #    gre_success = False
      
      # Skip GRE for debugging
      gre_success = True
      print("GRE paper generation SKIPPED for debugging")
      
      # Note: No persistent difficulty tracking - keeping simple
      print(f"Session used difficulty {self._difficulty_and_is_mock['difficulty']}, mock: {self._difficulty_and_is_mock['is_mock']}")
      
      # Session Summary
      total_time = time.time() - start_time
      print("=" * 80)
      print("PAPER GENERATION SESSION SUMMARY")
      print(f"GMAT Paper: {'SUCCESS' if gmat_success else 'FAILED'}")
      print(f"GRE Paper: {'SUCCESS' if gre_success else 'FAILED'}")
      print(f"Total Time: {total_time:.2f} seconds")
      print("=" * 80)
      
      print(f"Time taken: {total_time:.2f} seconds")
      
      # Stop terminal logging
      stop_terminal_logging()

if __name__ == "__main__":
   main = Main()
   main.generate_paper()
