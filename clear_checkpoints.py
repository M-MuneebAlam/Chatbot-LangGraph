import sqlite3

conn = sqlite3.connect('chatbot.db')
cur = conn.cursor()
cur.execute("DELETE FROM checkpoints")
conn.commit()
conn.close()

print("All checkpoints deleted.")
