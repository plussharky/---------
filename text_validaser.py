import re
import sqlite3
from langdetect import detect

# Подключение к базе данных SQLite
conn = sqlite3.connect('database.db')
c = conn.cursor()

c.execute("SELECT ID, site_text FROM website_data")
rows = c.fetchall()

for row in rows:
    try:
        # Определение языка текста
        id = row[0]
        text = row[1]
        lang = detect(text)
        if lang == 'ru':
            words = re.findall(r'\b\w+\b', text)
            result = ' '.join(words)
            result = re.sub(r'(?<=\w)(?=[А-Я])', ' ', result)
            c.execute("UPDATE website_data SET site_text = ? WHERE ID = ?", (result,id,))
            conn.commit()
            print(f'В строке {id} русский текст теперь форматирован')
            continue
        print(f'В строке {id} не на русском языке')
    except:
        print(f"Language detection failed for row ID: {row[0]}")

print(result)
