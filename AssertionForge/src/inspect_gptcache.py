import os
import sqlite3

db_path = os.path.join(os.getcwd(), 'AssertionForge', 'gptcache_data', 'gptcache.db')
if not os.path.exists(db_path):
    print("No database found at", db_path)
else:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cur.fetchall()
    print("Tables:", tables)
    for t in tables:
        table_name = t[0]
        cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cur.fetchone()[0]
        print(f"Table {table_name} has {count} rows")
        if count > 0:
            cur.execute(f"SELECT * FROM {table_name} LIMIT 3")
            rows = cur.fetchall()
            print(f"First 3 rows of {table_name}:")
            for r in rows:
                print("  ", r)
    conn.close()
