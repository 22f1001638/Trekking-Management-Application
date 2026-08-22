import sqlite3
import os
path = os.path.join('instance', 'trek.db')
print('exists', os.path.exists(path))
if not os.path.exists(path):
    raise SystemExit(1)
conn = sqlite3.connect(path)
cur = conn.cursor()
cur.execute('SELECT sql FROM sqlite_master WHERE type="table" AND name="trek_table"')
row = cur.fetchone()
print('sql:', row[0] if row else None)
cur.execute('PRAGMA table_info("trek_table")')
print('columns:', cur.fetchall())
conn.close()