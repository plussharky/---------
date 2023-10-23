import sqlite3

class DatabaseHelper:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
    
    def get_last_id(self):
        self.cursor.execute('SELECT MAX(ID) FROM website_data')
        last_id = self.cursor.fetchone()[0]
        return last_id
    
    def check_url_exists(self, url):
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
    
    def write_in_DB(self, url, screenshot_path, site_text):
        self.cursor.execute("INSERT INTO website_data (url, screenshot_path, site_text) VALUES (?, ?, ?)",
                            (url, screenshot_path, site_text))
        self.conn.commit()

    def close_connection(self):
        self.conn.close()