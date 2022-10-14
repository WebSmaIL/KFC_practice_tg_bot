import sqlite3

conn = sqlite3.connect('test_base.db')
cursor = conn.cursor()

# cursor.execute("CREATE TABLE admins (id INTEGER PRIMARY KEY NOT NULL,login TEXT  UNIQUE NOT NULL,password TEXT NOT NULL)")
# conn.commit()

cursor.execute("INSERT INTO admins (login, password) VALUES (?,?)", ("admin", "admin"))
conn.commit()