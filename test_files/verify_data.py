
import json
from prisma import Prisma

def verify():
    prisma = Prisma()
    prisma.connect()
    
    print("\n" + "="*50)
    print("       DATABASE REGISTRATION VERIFICATION       ")
    print("="*50)
    
    # 1. Question Types and Counts
    print("\n[1] Question Type Distribution:")
    types_query = prisma.query_raw('SELECT type, COUNT(*) as count FROM problems GROUP BY type;')
    for t in types_query:
        print(f" - {t['type']}: {t['count']}")

    # 2. Check Reading Comprehension & MSR (Parent-Child)
    print("\n[2] Parent-Child Linking (RC & MSR):")
    pc_types = ["Reading Comprehension", "Multi-Source Reasoning"]
    for pc_type in pc_types:
        problems = prisma.problems.find_many(
            where={"type": pc_type},
            take=3,
            include={"ProblemsSet": True}
        )
        if problems:
            print(f" -> {pc_type}:")
            for p in problems:
                ps_title = p.ProblemsSet.title if p.ProblemsSet else "MISSING"
                print(f"    - Problem: {p.title[:40]}... | PS: {ps_title[:40]}...")
        else:
            print(f" -> {pc_type}: No records found.")

    # 3. Check Text Completion Grouping
    print("\n[3] Text Completion Grouping:")
    tc_problems = prisma.problems.find_many(
        where={"type": "Text Completion"},
        take=2,
        include={"problemoptions": True}
    )
    if tc_problems:
        for p in tc_problems:
            groups = {}
            for opt in p.problemoptions:
                grp = opt.group or "None"
                groups[grp] = groups.get(grp, 0) + 1
            print(f" - {p.title[:40]}...: Groups={groups}, Total Options={len(p.problemoptions)}")
    else:
        print(" - No Text Completion records found.")

    # 4. Check Data Sufficiency & Problem Solving (Simple)
    print("\n[4] Simple Questions (DS, PS):")
    simple_types = ["Data Sufficiency", "Problem Solving Simple"]
    for stype in simple_types:
        count = prisma.problems.count(where={"type": stype})
        print(f" - {stype}: {count} records found.")

    # 5. Check Solution Format
    print("\n[5] Solution JSON Format Check:")
    sample = prisma.problems.find_first()
    if sample:
        sol = sample.solution
        is_valid = isinstance(sol, dict) and "explanation" in sol
        status = "PASSED" if is_valid else "FAILED (Not in {'explanation': '...'} format)"
        print(f" - Format Check: {status}")
        if is_valid:
            print(f" - Sample Preview: {str(sol['explanation'])[:80]}...")

    # 6. Data Integrity (Difficulty & Tags)
    print("\n[6] Data Integrity:")
    missing_diff = prisma.problems.count(where={"difficulty": None})
    total = prisma.problems.count()
    tag_count = prisma.tags.count()
    sample_tag = prisma.tags.find_first()
    
    print(f" - Problems with missing difficulty: {missing_diff} / {total}")
    print(f" - Total unique categorized tags registered: {tag_count}")
    if sample_tag:
        print(f" - Sample Tag: Type={sample_tag.type}, Theme={sample_tag.theme}, Topic={sample_tag.topic}")

    print("\n" + "="*50)
    print("VERIFICATION COMPLETE")
    print("="*50 + "\n")

    prisma.disconnect()

if __name__ == '__main__':
    verify()
