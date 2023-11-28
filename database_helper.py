import sqlite3
import csv

class URLData:
    def __init__(self):
        self.url = None
        self.having_ip_address = None
        self.url_length = None
        self.short_service = None
        self.having_at_symbol = None
        self.double_slash_redirecting = None
        self.prefix_suffix = None
        self.having_sub_domain = None
        self.ssl_final_state = None
        self.domain_reg_length = None
        self.favicon = None
        self.https_token = None
        self.request_url = None
        self.url_of_anchor = None
        self.links_in_tags = None
        self.sfh = None
        self.submitting_to_email = None
        self.redirect = None
        self.mouseover = None
        self.right_click = None
        self.iframe = None
        self.age_of_domain = None
        self.dns_record = None
        self.web_traffic = None
        self.page_rank = None
        self.google_index = None
        self.statistical_report = None

class DatabaseHelper:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
    
    # Методы для работы с БД
    def close_connection(self):
        self.conn.close()

    def check_url_exist(self, url: str):
        return self.check_url_in_website_data(url) and self.check_url_in_queue(url) and self.check_url_in_error(url)
    
    def save_query_in_csv(self, query, filename):
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        csv_filename = str(filename) + '.csv' 
        with open(csv_filename, 'w', newline='', encoding='utf-16') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter='\t')  # Используем табуляцию в качестве разделителя
            
            # Запись заголовков
            csv_writer.writerow(['ID', 'URL', 'screenshot_path', 'domain'])
            
            # Запись данных
            csv_writer.writerows(data)

        print(f'Data has been exported to {csv_filename}')

    # Методы для работы с таблицей website_data
    def get_last_id(self):
        self.cursor.execute('SELECT MAX(ID) FROM website_data')
        last_id = self.cursor.fetchone()[0]
        if last_id == None:
            return 1
        return last_id
    
    def get_url_from_website_data_by_id(self, id):
        self.cursor.execute('SELECT URL FROM website_data WHERE ID = ?', (id,))
        url = self.cursor.fetchone()[0]
        if url == None:
            return 1
        return url
    
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
        
    # Методы для работы с таблицей url_flags
    def write_in_url_flag(self, domain, data: URLData):
        try:
            self.cursor.execute("INSERT INTO url_flags (url, domain, having_ip_address, url_length, \
                                short_service, having_at_symbol, double_slash_redirecting, prefix_suffix, \
                                having_sub_domain, ssl_final_state, domain_reg_length, favicon, https_token, \
                                request_url, url_of_anchor, links_in_tags, sfh, submitting_to_email, redirect, \
                                mouseover, right_click, iframe, age_of_domain, dns_record, web_traffic, page_rank, \
                                google_index, statistical_report) \
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                (data.url, domain, data.having_ip_address, data.url_length, 
                                    data.short_service, data.having_at_symbol, data.double_slash_redirecting, data.prefix_suffix,
                                    data.having_sub_domain, data.ssl_final_state, data.domain_reg_length, data.favicon, data.https_token,
                                    data.request_url, data.url_of_anchor, data.links_in_tags, data.sfh, data.submitting_to_email, data.redirect,
                                    data.mouseover, data.right_click, data.iframe, data.age_of_domain, data.dns_record, data.web_traffic, data.page_rank,
                                    data.google_index, data.statistical_report))
            self.conn.commit()
        except sqlite3.Error as e:
            print("Ошибка при работе с базой данных:", e)
            return False
        
    def url_flag_get_last_id(self):
        self.cursor.execute('SELECT count(*) FROM url_flags')
        last_id = self.cursor.fetchone()[0]
        return last_id
    
    # Методы для работы с таблицей phishing
    def get_url_from_fishing(self):
        try:
            self.cursor.execute("SELECT p.url FROM phishing p LEFT JOIN website_data w ON p.url = w.URL WHERE w.URL IS NULL AND p.data_collected IS NULL LIMIT 1;")
            url = self.cursor.fetchone()[0]
            return url
        except sqlite3.Error as e:
            print("Ошибка при работе с базой данных:", e)
            return False
        
    def fill_collected_data_field(self, url, success):
        try:
            self.cursor.execute("UPDATE phishing SET data_collected = ? WHERE url = ?;", (str(success), url))
            self.conn.commit()
        except sqlite3.Error as e:
            print("Ошибка при работе с базой данных:", e)
            return False
        
    def exist_in_phishing(self, url: str):
        try:
            self.cursor.execute("SELECT * FROM phishing WHERE url=? LIMIT 1", (url,))
            result = self.cursor.fetchone()
            if result:
                return True
            else:
                return False
        except sqlite3.Error as e:
            print("Ошибка при работе с базой данных:", e)
            return False