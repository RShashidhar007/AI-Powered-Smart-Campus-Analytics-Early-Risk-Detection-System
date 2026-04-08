import sqlite3
path = r'c:\Users\HP\OneDrive\Desktop\programs\AI-Powered-Smart-Campus-Analytics\AI-Powered-Smart-Campus-Analytics-Early-Risk-Detection-System\data\campus_analytics.db'
conn = sqlite3.connect(path)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)
for t in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {t[0]}")
    print(f"  {t[0]}: {cursor.fetchone()[0]} rows")
    cursor.execute(f"PRAGMA table_info({t[0]})")
    cols = cursor.fetchall()
    for c in cols:
        print(f"    {c}")
conn.close()
