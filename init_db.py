import sqlite3

conn = sqlite3.connect("omi.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    maker TEXT,
    kva INTEGER,
    price INTEGER,
    year INTEGER,
    note TEXT
)
""")

conn.commit()
conn.close()

print("DB initialized")
