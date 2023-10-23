from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from database_helper import DatabaseHelper
import sqlite3
import requests
import re
import os
    
# Список URL которые уже есть в базе
completed_urls = []

# Список очереди URL на парсинг
urls_to_parse = []

# Путь до драйвера Google Chrome
driver_path = 'C:\\Users\\Plusharky\\Desktop\\Уник\\Дипломчик\\ChromeDriver\\chromedriver.exe'

# Подключение к базе данных
db_helper = DatabaseHelper('database.db')

# Последний ID сайта
last_id = db_helper.get_last_id()

# Разрешение скриншотов (ширина х высота)
desired_width = 1280
desired_height = 720

# Create Chrome options
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # This runs Chrome in headless mode (without opening a window)

def scrape_and_save_data(url):
     # Create a new ChromeService instance for each URL
    chrome_service = ChromeService(executable_path=driver_path)
    
    # Create a new Chrome webdriver instance
    driver = webdriver.Chrome(service=chrome_service, options=options)
    
    # Set the window size to the desired resolution
    driver.set_window_size(desired_width, desired_height)
    try:
        response = requests.get(url)
    except:
        print(f"Не удалось получить доступ к сайту {url}")
        driver.quit()
        return
    
    # Extract site name from URL
    site_name = url_to_windows_folder_name(url)
    
    # Create a directory for each site
    site_directory = f"./{site_name}"
    os.makedirs(site_directory, exist_ok=True)
    
    # Save a screenshot
    screenshot_filename = f"screenshot-{site_name}.png"
    driver.get(url)
    driver.save_screenshot(os.path.join(site_directory, screenshot_filename))
    
    # Extract text from the site
    soup = BeautifulSoup(driver.page_source, "html.parser")
    text = soup.get_text()
    
    #добавить найденные URL в очередь
    add_finded_URLs(soup)

    # Save the text to a text file
    text_filename = f"text-{site_name}.txt"
    with open(os.path.join(site_directory, text_filename), "w", encoding="utf-8") as text_file:
        text_file.write(text)
    
    print(f"Сохранены данные для сайта {url} в папку {site_directory}")
    
    driver.quit()

def url_to_windows_folder_name(url):
    # Удаление недопустимых символов
    cleaned_name = re.sub(r'[\/:*?"<>|]', '_', url)

    # Обрезка имени, если оно слишком длинное (максимум 255 символов в Windows)
    max_length = 200
    if len(cleaned_name) > max_length:
        cleaned_name = cleaned_name[:max_length]

    return cleaned_name

def add_finded_URLs(soup):

    # Add the found URLs to urls_to_parse
    links = soup.find_all('a', href=True)

    # Extract and add the URLs to urls_to_parse
    for link in links:
        found_url = link['href']
        if found_url.startswith("http") or found_url.startswith("https"):
            if found_url not in urls_to_parse:
                if found_url not in completed_urls:
                    urls_to_parse.append(found_url)

def get_completed_urls(directory):
    completed_urls = []
    for root, dirs, files in os.walk(directory):
        for dir_name in dirs:
            completed_urls.append()
    return completed_urls






first_url = input("Введите url: ")
urls_to_parse.append(first_url)

for url in urls_to_parse:
    scrape_and_save_data(url)
    completed_urls.append(url_to_windows_folder_name(url))

conn.close()