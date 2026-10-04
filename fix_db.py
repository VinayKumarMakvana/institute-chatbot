import sqlite3
import os

db_path = os.path.join("backend", "edubot.db")
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE live_updates SET priority = 'IMPORTANT' WHERE priority = 'HIGH'")
    conn.commit()
    conn.close()
    print("Fixed live_updates priorities in edubot.db.")
else:
    print("DB not found.")
