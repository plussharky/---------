import re
import sqlite3
from langdetect import detect

# Подключение к базе данных SQLite
conn = sqlite3.connect('database.db')
c = conn.cursor()

c.execute("SELECT ID, site_text FROM website_data WHERE language IS Null")
rows = c.fetchall()
count = 0

for row in rows:
    try:
        # Определение языка текста
        id = row[0]
        text = row[1]
        lang = detect(text)
        c.execute("UPDATE website_data SET language = ? WHERE ID = ?", (lang,id,))
        print(f'В строке {id} установлен язык {lang}')
        count = count + 1
        if count == 100:
            count = 0
            conn.commit()
            print(f"Сделан коммит БД")
    except:
        print(f"Language detection failed for row ID: {row[0]}")
