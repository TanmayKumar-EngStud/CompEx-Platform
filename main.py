print("Startup in progress...")

import json, pickle
from prisma import Prisma
from db import DB
import time
from terminal_logger import start_terminal_logging, stop_terminal_logging

# importing papers
from GMAT.Mock import GMAT_Mock
from GRE.Mock import GRE_Mock

class Main:
   def __init__(self):
      # Start terminal logging to capture all output
      self.terminal_logger = start_terminal_logging()
      
      self._difficulty_and_is_mock = {
         'difficulty': 1,
         'is_mock': True
      }

      with open('difficulty_and_is_mock.pkl', 'rb') as f:
         self._difficulty_and_is_mock = pickle.load(f)
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
         # GMAT Paper Generation
         print(f"Starting GMAT paper generation - Difficulty: {self._difficulty_and_is_mock['difficulty']}")
         gmat_mock = GMAT_Mock(self._difficulty_and_is_mock['difficulty'])
         GMAT_paper = gmat_mock.generate(8)
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
      
      print("Sleeping for 60 seconds for API rate limit reset")
      time.sleep(60)
      
      try:
         # GRE Paper Generation
         print(f"Starting GRE paper generation - Difficulty: {self._difficulty_and_is_mock['difficulty']}")
         gre_mock = GRE_Mock(self._difficulty_and_is_mock['difficulty'])
         GRE_paper = gre_mock.generate(8)
         timestamp = time.strftime("%d-%m-%H-%M", time.localtime())
         gre_filepath = f'papers/GRE/GRE_paper-{timestamp}-difficulty-{self._difficulty_and_is_mock["difficulty"]}.json'
         
         with open(gre_filepath, 'w') as f:
            try:
               json.dump(GRE_paper, f, indent=2)
               print(f"GRE paper saved successfully: {gre_filepath}")
            except Exception as e:
               print(f"GRE paper storing Error: {str(e)}")
               raise e

         try:
            self.database.registerQuestion(GRE_paper, isMockQuestion=self._difficulty_and_is_mock['is_mock'], difficulty=self._difficulty_and_is_mock['difficulty'])
            print("GRE questions registered in database successfully")
         except Exception as e:
            print(f"GRE database registration failed: {str(e)}")
            raise e
            
         gre_success = True
         print("GRE paper generation completed successfully")
         
      except Exception as e:
         print(f"GRE paper generation failed: {str(e)}")
         gre_success = False
      
      # Update difficulty level
      try:
         self._difficulty_and_is_mock['difficulty'] += 1
         if self._difficulty_and_is_mock['difficulty'] > 5:
            self._difficulty_and_is_mock['difficulty'] = 1
            self._difficulty_and_is_mock['is_mock'] = not self._difficulty_and_is_mock['is_mock']
         with open('difficulty_and_is_mock.pkl', 'wb') as f:
            pickle.dump(self._difficulty_and_is_mock, f)
         print(f"Updated difficulty to {self._difficulty_and_is_mock['difficulty']}, mock: {self._difficulty_and_is_mock['is_mock']}")
      except Exception as e:
         print(f"Failed to update difficulty settings: {str(e)}")
      
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
