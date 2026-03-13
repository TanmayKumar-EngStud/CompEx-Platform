
import sqlite3
import os
import json

db_path = '/Users/tanmaykumar/Desktop/QGen-py-compex/artilaries_prisma/artilaries.db'
output_dir = './legacy_dump'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def dump_table(table_name):
    print(f'📦 Dumping {table_name}...')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table_name}")
    rows = cur.fetchall()
    
    # Get column names
    cur.execute(f"PRAGMA table_info({table_name})")
    cols = [c[1] for c in cur.fetchall()]

    data = [dict(zip(cols, row)) for row in rows]

    with open(os.path.join(output_dir, f"{table_name}.json"), 'w') as f:
        json.dump(data, f, indent = 2)

    conn.close()

tables = [
    'PromptComponent',
    'Stage',
    'Category',
    'PromptComponentValue',
    'ComplexityGuideline',
    'DifficultyDescription'
]

for t in tables:
    try:
        dump_table(t)
    except Exception as e:
        print(f"❌ Error dumping {t}: {e}")

print('✅ Dump complete in ./legacy_dump')
