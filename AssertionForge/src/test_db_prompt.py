import sqlite3
import os

db_path = '../gptcache_data/gptcache.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("SELECT id, LENGTH(question), substr(question, 1, 200) FROM gptcache_question ORDER BY LENGTH(question) DESC;")
for row in c.fetchall():
    print(f"ID={row[0]} | length={row[1]}")
    print(repr(row[2]))
    print("---")
conn.close()
