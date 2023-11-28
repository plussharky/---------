import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Цикл для обновления URLs_in_queue для ID от 1 до 10698
for i in range(1, 10699):
    cursor.execute('''
        UPDATE domains
        SET URLs_in_data = (
            SELECT COUNT(*)
            FROM website_data
            WHERE website_data.domain_ID = domains.ID
        )
        WHERE ID = ?;
    ''', (i,))
    
    print(i)

# Применение изменений и закрытие соединения
conn.commit()
conn.close()
