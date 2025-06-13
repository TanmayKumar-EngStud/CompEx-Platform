from db import DB
from prisma import Prisma

db = Prisma(auto_register=True)
db.connect()
database = DB(db)

database.delete_all_questions()
