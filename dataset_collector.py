from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from database_helper import DatabaseHelper
import sqlite3
import requests
import re
import os
    
def get_domain_from_url(url: str):
    domain = url.split('//')[-1].split('/')[0].split('?')[0].split(':')[0]
    return domain

# Папка датасета
dataset_directory = 'dataset'

## Настройка драйвера Google Chrome
# Разрешение скриншотов (ширина х высота)
desired_width = 1280
desired_height = 720
# Путь до драйвера Google Chrome
driver_path = 'C:\\Users\\Plusharky\\Desktop\\Уник\\Дипломчик\\ChromeDriver\\chromedriver.exe'
# Create Chrome options
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # This runs Chrome in headless mode (without opening a window)
# Create a new ChromeService instance for each URL
chrome_service = ChromeService(executable_path=driver_path)
# Create a new Chrome webdriver instance
driver = webdriver.Chrome(service=chrome_service, options=options)
# Set the window size to the desired resolution
driver.set_window_size(desired_width, desired_height)

# Подключение к базе данных
db_helper = DatabaseHelper('database.db')

def scrape_and_save_data(url):
    try:
        response = requests.get(url)
            # Extract site name from URL
        site_name = get_domain_from_url(url)
        
        # Create a directory for each site
        site_directory = str(db_helper.get_last_id())
        full_path = os.path.join(dataset_directory, site_directory)
        os.makedirs(full_path, exist_ok=True)
        
        # Save a screenshot
        screenshot_filename = f"screenshot-{site_name}.png"
        screenshot_path = os.path.join(full_path, screenshot_filename)
        driver.get(url)
        driver.save_screenshot(screenshot_path)
        
        # Extract text from the site
        soup = BeautifulSoup(driver.page_source, "html.parser")
        text = soup.get_text()
        
        #добавить найденные URL в очередь
        # Add the found URLs to urls_to_parse
        links = soup.find_all('a', href=True)
        url_array = [link['href'] for link in links if link['href'].startswith(('http://', 'https://'))]
        add_finded_URLs(url_array)

        # Save the text to a text file
        text_filename = f"text-{site_name}.txt"
        with open(os.path.join(full_path, text_filename), "w", encoding="utf-8") as text_file:
            text_file.write(text)
        
        db_helper.write_in_DB(url, os.path.abspath(screenshot_path), text)

        print(f"Сохранены данные для сайта {url} в папку {full_path}")
        
        driver.quit()
    except:
        print(f"Не удалось получить доступ к сайту {url}")
        driver.quit()
        db_helper.add_to_error(url)
        return
    


def add_finded_URLs(links):
    # Extract and add the URLs to urls_to_parse
    for link in links:
        if db_helper.check_url_exist(link):
            continue
        db_helper.add_to_queue(link)

def get_completed_urls(directory):
    completed_urls = []
    for root, dirs, files in os.walk(directory):
        for dir_name in dirs:
            completed_urls.append()
    return completed_urls 

#first_url = input("Введите url: ")
first_url = 'https://infoselection.ru/infokatalog/internet-i-programmy/internet-osnovnoe/item/90-50-samykh-poseshchaemykh-sajtov-runeta'
db_helper.add_to_queue(first_url)

while True:
    url = db_helper.get_first_from_queue()
    if url == None:
        break
    scrape_and_save_data(url)
    db_helper.remove_from_queue(url)


db_helper.close_connection()