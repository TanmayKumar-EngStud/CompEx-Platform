from prisma import Prisma

def main():
    db = Prisma()
    db.connect()
    
    ps = db.problemsset.find_many()
    types = set([p.type for p in ps])
    print(f"Available Types: {types}")
    
    db.disconnect()

if __name__ == "__main__":
    main()
