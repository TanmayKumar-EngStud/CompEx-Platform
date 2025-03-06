import json
from db import DB
from prisma import Prisma
GMAT_paper = json.load(open('papers/GMAT/GMAT_paper-26-02-16-49-difficulty-4.json'))

db = Prisma(auto_register=True)
db.connect()
db = DB(db)


db.registerQuestion(GMAT_paper, isMockQuestion=True, difficulty=5)

print("Done")
