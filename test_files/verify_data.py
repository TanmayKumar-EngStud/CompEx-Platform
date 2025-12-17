
import json
from prisma import Prisma

def verify():
    prisma = Prisma()
    prisma.connect()
    
    print("--- Verification Results ---")
    
    # 1. Check Reading Comprehension (Parent-Child)
    print("\n1. Verifying Reading Comprehension Linking:")
    rc_problems = prisma.problems.find_many(
        where={"type": "Reading Comprehension"},
        take=5,
        include={"ProblemsSet": True}
    )
    for p in rc_problems:
        ps_title = p.ProblemsSet.title if p.ProblemsSet else "MISSING"
        print(f"Problem: {p.title} | PS ID: {p.problemsSetId} | PS Title: {ps_title}")

    # 2. Check Text Completion Grouping
    print("\n2. Verifying Text Completion Grouping:")
    tc_problems = prisma.problems.find_many(
        where={"type": "Text Completion"},
        take=2,
        include={"problemoptions": True}
    )
    for p in tc_problems:
        print(f"Problem: {p.title}")
        groups = {}
        for opt in p.problemoptions:
            grp = opt.group or "None"
            groups[grp] = groups.get(grp, 0) + 1
        print(f"  Options per group: {groups}")
        correct_count = sum(1 for opt in p.problemoptions if opt.iscorrect)
        print(f"  Correct options: {correct_count}")

    # 3. Check Sentence Equivalence (Multiple Correct)
    print("\n3. Verifying Sentence Equivalence (Multiple Correct):")
    se_problems = prisma.problems.find_many(
        where={"type": "Sentence Equivalence"},
        take=2,
        include={"problemoptions": True}
    )
    for p in se_problems:
        correct_opts = [opt.optiontext for opt in p.problemoptions if opt.iscorrect]
        print(f"Problem: {p.title} | Correct Options: {correct_opts}")

    # 4. Check Solutions formatting
    print("\n4. Verifying Solutions Formatting:")
    p = prisma.problems.find_first()
    if p:
        print(f"Sample Solution (First 100 chars): {str(p.solution)[:100]}...")

    # 5. Missing values check
    print("\n5. Checking for Missing Values (Difficulty/Tags):")
    missing_diff = prisma.problems.count(where={"difficulty": None})
    total_problems = prisma.problems.count()
    print(f"Problems with missing difficulty: {missing_diff} / {total_problems}")
    
    # Check if tags are registered
    tag_count = prisma.tagid.count() if hasattr(prisma, 'tagid') else prisma.tags.count()
    print(f"Total tags in database: {tag_count}")

    prisma.disconnect()

if __name__ == '__main__':
    verify()
