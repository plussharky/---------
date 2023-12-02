import sqlite3
import csv
import database_helper

db = database_helper.DatabaseHelper('database.db')
#db.save_query_in_csv('SELECT w.URL, w.screenshot_path, w.domain FROM phishing AS p LEFT JOIN website_data AS w ON w.URL = p.url WHERE p.data_collected = \'True\';', 'phishing')
#db.save_query_in_csv('SELECT wd.URL, wd.screenshot_path, wd.domain FROM website_data wd WHERE NOT EXISTS ( SELECT 1 FROM phishing p WHERE p.url = wd.URL);', 'legitimate')
db.save_query_in_csv('SELECT w.URL, w.site_text FROM website_data AS w WHERE domain LIKE \'%.ru\' OR language = \"ru\";', 'texts')
db.save_query_in_csv('SELECT w.URL, w.site_text FROM ruphishing AS ru LEFT JOIN website_data AS w ON w.URL = ru.url WHERE ru.data_collected = \'True\' AND w.language = \'ru\';', 'phishing_texts')