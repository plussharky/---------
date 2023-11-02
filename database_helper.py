import sqlite3

class DatabaseHelper:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
    
    # Методы для работы с БД
    def close_connection(self):
        self.conn.close()

    def check_url_exist(self, url: str):
        return self.check_url_in_website_data(url) and self.check_url_in_queue(url) and self.check_url_in_error(url)

    # Методы для работы с таблицей website_data
    def get_last_id(self):
        self.cursor.execute('SELECT MAX(ID) FROM website_data')
        last_id = self.cursor.fetchone()[0]
        if last_id == None:
            return 1
        return last_id
    
    def check_url_in_website_data(self, url: str):
        try:
            self.cursor.execute("SELECT * FROM website_data WHERE URL=?", (url,))
            result = self.cursor.fetchone()
            if result:
                return True
            else:
                return False
        except sqlite3.Error as e:
            print("Ошибка при работе с базой данных:", e)
            return False
    
    def write_in_data(self, url, screenshot_path, site_text, domain):
        self.cursor.execute("INSERT INTO website_data (url, screenshot_path, site_text, domain) VALUES (?, ?, ?, ?)",
                            (url, screenshot_path, site_text, domain))
        self.conn.commit()

    # Методы для работы с таблицей queue
    def add_to_queue(self, url: str, domain):
        try:
            self.cursor.execute("INSERT INTO queue (URL, domain) VALUES (?, ?)", (url, domain,))
            self.conn.commit()
            print(f'URL "{url}" добавлен в очередь')
        except sqlite3.Error as e:
            print("Ошибка при добавлении в очередь:", e)

    def check_url_in_queue(self, url: str):
        try:
            self.cursor.execute("SELECT * FROM queue WHERE URL=?", (url,))
            result = self.cursor.fetchone()
            if result:
                return True
            else:
                return False
        except sqlite3.Error as e:
            print("Ошибка при работе с базой данных:", e)
            return False
    
    def remove_from_queue(self, url: str):
        try:
            self.cursor.execute("DELETE FROM queue WHERE url=?", (url,))
            self.conn.commit()
            print(f'URL "{url}" удален из очереди')
        except sqlite3.Error as e:
            print("Ошибка при удалении из очереди:", e)

    def get_first_from_queue(self):
        try:
            self.cursor.execute("SELECT url FROM queue ORDER BY RANDOM() LIMIT 1")
            result = self.cursor.fetchone()
            if result:
                return result[0]
            else:
                print("Очередь пуста")
                return None
        except sqlite3.Error as e:
            print("Ошибка при получении первой записи из очереди:", e)

    def get_row_from_queue_with_min_domain_count(self):
        try:
            # Выбираем уникальные домены из таблицы "website_data" и подсчитываем количество записей для каждого домена
            self.cursor.execute('''
                SELECT q.* 
                FROM queue AS q
                INNER JOIN (
                    SELECT *
                    FROM domains
                    WHERE URLs_in_queue > 0 
                    ORDER BY URLs_in_data 
                    LIMIT 1) as d
                ON d.domain = q.domain
                LIMIT 1;
            ''')
            min_domain = self.cursor.fetchone()

            print(f"Выбранный URL с наименьшим доменом: {min_domain[1]}")

            return min_domain if min_domain else None
        except sqlite3.Error as e:
            print("Ошибка при получении записи из очереди с наименьшим количеством данных:", e)

    # Методы для работы с таблицей error_website
    def add_to_error(self, url, domain):
        try:
            self.cursor.execute("INSERT INTO error_website (URL, domain) VALUES (?, ?)", (url, domain,))
            self.conn.commit()
            print(f'URL "{url}" добавлен в список сайтов которые не получилось обработать')
        except sqlite3.Error as e:
            print("Ошибка при добавлении в список сайтов которые не получилось обработать:", e)

    def check_url_in_error(self, url: str):
        try:
            self.cursor.execute("SELECT * FROM error_website WHERE URL=?", (url,))
            result = self.cursor.fetchone()
            if result:
                return True
            else:
                return False
        except sqlite3.Error as e:
            print("Ошибка при работе с базой данных:", e)
            return False
        
    # Методы для работы с таблицей domains
    def check_domain_exist(self, domain: str):
        try:
            self.cursor.execute("SELECT * FROM domains WHERE domain=? LIMIT 1", (domain,))
            result = self.cursor.fetchone()
            if result:
                return True
            else:
                return False
        except sqlite3.Error as e:
            print("Ошибка при работе с базой данных:", e)
            return False
        
    def increment_domain_count_queue(self, domain: str):
        try:
            self.cursor.execute("UPDATE domains SET URLs_in_queue = URLs_in_queue + 1 WHERE domain = ?", (domain,))
            self.conn.commit()
        except sqlite3.Error as e:
            print("Ошибка при работе с базой данных:", e)
    
    def decrement_domain_count_queue(self, domain: str):
        try:
            self.cursor.execute("UPDATE domains SET URLs_in_queue = URLs_in_queue - 1 WHERE domain = ?", (domain,))
            self.conn.commit()
        except sqlite3.Error as e:
            print("Ошибка при работе с базой данных:", e)
    
    def increment_domain_count_data(self, domain: str):
        try:
            self.cursor.execute("UPDATE domains SET URLs_in_data = URLs_in_data + 1 WHERE domain = ?", (domain,))
            self.conn.commit()
        except sqlite3.Error as e:
            print("Ошибка при работе с базой данных:", e)
       
    def write_in_domain(self, domain, queue_count, data_count):
        try:
            self.cursor.execute("INSERT INTO domains (domain, URLs_in_queue, URLs_in_data) VALUES (?, ?, ?)",
                                (domain, queue_count, data_count))
            self.conn.commit()
        except sqlite3.Error as e:
            print("Ошибка при работе с базой данных:", e)
            return False