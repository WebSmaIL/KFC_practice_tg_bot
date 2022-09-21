import sqlite3


conn = sqlite3.connect('test_base.db')
cursor = conn.cursor()
arr = ['./images/morozhenoe.jpg', './images/pirojok_cherry.jpg', './images/agusha.jpg', './images/donat.jpg', './images/tort.jpg']

for i in range(1, 6):
    cursor.execute(f"UPDATE desserts SET photo='{arr[i-1]}' WHERE id = {i}")
    conn.commit()