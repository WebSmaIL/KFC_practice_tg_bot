import sqlite3


conn = sqlite3.connect('test_base.db')
cur = conn.cursor()

cur.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY NOT NULL, user_id INTEGER NOT NULL, drinks TEXT, burgers TEXT, potato TEXT, meat TEXT, desserts TEXT, sauce TEXT);")
conn.commit()