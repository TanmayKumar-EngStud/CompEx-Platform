
from prisma import Prisma

def verify_rc():
    prisma = Prisma()
    prisma.connect()
    
    # Check what types we have
    print("Distinct question types in database:")
    types = prisma.query_raw('SELECT DISTINCT type FROM problems;')
    for t in types:
        print(f" - {t['type']}")

    print("\nChecking for any parent-child links:")
    links = prisma.problems.count(where={"problemsSetId": {"not": None}})
    print(f"Total problems with problemsSetId: {links}")
    
    if links > 0:
        p = prisma.problems.find_first(
            where={"problemsSetId": {"not": None}},
            include={"ProblemsSet": True}
        )
        print(f"Sample Link: {p.title} -> {p.ProblemsSet.title if p.ProblemsSet else 'NO SET'}")

    prisma.disconnect()

if __name__ == '__main__':
    verify_rc()
