import sqlite3

db_path = '../gptcache_data/gptcache.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

import difflib

# Let's get the two queries for PCLK context evaluation that are near each other in length
c.execute("SELECT question FROM gptcache_question WHERE question LIKE '%%Given the following design specification, generate natural language test plans:%%' AND question LIKE '%%PCLK%%';")
rows = c.fetchall()

if len(rows) >= 2:
    q1 = rows[0][0]
    q2 = rows[1][0]
    if q1 != q2:
        print("Mismatched queries!")
        print(f"Lengths: {len(q1)} vs {len(q2)}")
        diff = list(difflib.context_diff(q1.splitlines(), q2.splitlines(), n=1))
        for line in diff:
            print(line)
    else:
        print("Queries are identical.")
else:
    print(f"Found {len(rows)} matching rows.")
conn.close()
