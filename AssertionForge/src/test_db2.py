import sqlite3
import os

db_path = '../gptcache_data/gptcache.db'

conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("SELECT id, question FROM gptcache_question LIMIT 5;")
for row in c.fetchall():
    print(f"ID: {row[0]}")
    q = row[1]
    print(f"Length: {len(q)}")
    print(f"Snippet: {repr(q[:100])}")
    print("-----")
conn.close()
