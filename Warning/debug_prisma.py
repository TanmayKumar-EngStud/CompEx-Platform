import prisma
import os
print(f"Prisma location: {os.path.dirname(prisma.__file__)}")

from prisma import Prisma
print(f"Prisma class available: {Prisma}")

p = Prisma()
print(f"Prisma instance attributes: {dir(p)}")
