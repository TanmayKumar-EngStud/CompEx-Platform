print("Startup in progress...")

import json, pickle
from prisma import Prisma
from db import DB
import time

# importing papers
from GMAT.Mock import GMAT_Mock
from GRE.Mock import GRE_Mock
class Main:
   def __init__(self):
      self._difficulty_and_is_mock = {
         'difficulty': 1,
         'is_mock': True
      }

      with open('difficulty_and_is_mock.pkl', 'rb') as f:
         self._difficulty_and_is_mock = pickle.load(f)
      self.db = Prisma(auto_register=True)
      self.db.connect()
      self.database = DB(self.db)

   def generate_paper(self):
      start_time = time.time()
      gmat_mock = GMAT_Mock(self._difficulty_and_is_mock['difficulty'])
      GMAT_paper = gmat_mock.generate()
      timestamp = time.strftime("%d-%m-%H-%M", time.localtime())
      with open(f'papers/GMAT/GMAT_paper-{timestamp}-difficulty-{self._difficulty_and_is_mock["difficulty"]}.json', 'w') as f:
         try:
            json.dump(GMAT_paper, f, indent=2)
         except Exception as e:
            print(f"GMAT paper storing Error: {str(e)}")
      self.database.registerQuestion(GMAT_paper, isMockQuestion=self._difficulty_and_is_mock['is_mock'], difficulty=self._difficulty_and_is_mock['difficulty'])
      print("GMAT Done")
      gre_mock = GRE_Mock(self._difficulty_and_is_mock['difficulty'])
      GRE_paper = gre_mock.generate()
      timestamp = time.strftime("%d-%m-%H-%M", time.localtime())
      with open(f'papers/GRE/GRE_paper-{timestamp}-difficulty-{self._difficulty_and_is_mock["difficulty"]}.json', 'w') as f:
         try:
            json.dump(GRE_paper, f, indent=2)
         except Exception as e:
            print(f"GRE paper storing Error: {str(e)}")

      self.database.registerQuestion(GRE_paper, isMockQuestion=self._difficulty_and_is_mock['is_mock'], difficulty=self._difficulty_and_is_mock['difficulty'])
      
      # region updating difficulty level
      self._difficulty_and_is_mock['difficulty'] += 1
      if self._difficulty_and_is_mock['difficulty'] > 5:
         self._difficulty_and_is_mock['difficulty'] = 1
         self._difficulty_and_is_mock['is_mock'] = not self._difficulty_and_is_mock['is_mock']
      with open('difficulty_and_is_mock.pkl', 'wb') as f:
         pickle.dump(self._difficulty_and_is_mock, f)
      # endregion
      print(f"Time taken: {time.time() - start_time} seconds")
if __name__ == "__main__":
   main = Main()
   main.generate_paper()
