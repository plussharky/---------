from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse
from database_helper import DatabaseHelper
import sqlite3
import asyncio
import aiohttp
import requests
import re
import os
from langdetect import detect
import concurrent.futures
    
def get_domain_from_url(url: str):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    return domain

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

def format_text(text):
    try:
        result = text
        if define_language(text) == 'ru':
            words = re.findall(r'\b\w+\b', text)
            result = ' '.join(words)
            result = re.sub(r'(?<=\w)(?=[А-Я])', ' ', result)
        return result
    except:
        print(f"Language detection failed")
        return text

def define_language(text):
    return detect(text)



def get_webdriver():
    ## Настройка драйвера Google Chrome
    # Разрешение скриншотов (ширина х высота)
    desired_width = 1280
    desired_height = 720
    # Путь до драйвера Google Chrome
    driver_path = 'C:\\Users\\Plusharky\\Desktop\\Уник\\Дипломчик\\ChromeDriver\\chromedriver.exe'
    # Create Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # This runs Chrome in headless mode (without opening a window)
    options.add_argument('--ignore-certificate-errors')
    # Create a new ChromeService instance for each URL
    chrome_service = ChromeService(executable_path=driver_path)
    # Create a new Chrome webdriver instance
    driver = webdriver.Chrome(service=chrome_service, options=options)
    # Set the window size to the desired resolution
    driver.set_window_size(desired_width, desired_height)

    return driver

# Подключение к базе данных
db_helper = DatabaseHelper('database.db')

# Папка датасета
dataset_directory = 'dataset'

# Создайте объект блокировки
lock = asyncio.Lock()

async def scrape_and_save_data(url: str):
    async with aiohttp.ClientSession() as session:
            html = None
            soup = None
            try:
                html = await fetch(session, url)
                soup = BeautifulSoup(html, "html.parser")
            except:
                 return Exception
            # Extract site name from URL
            async with lock:
                domain = get_domain_from_url(url)
            # Create a directory for each site
            site_directory = str(db_helper.get_last_id())
            full_path = os.path.join(dataset_directory, site_directory)
            os.makedirs(full_path, exist_ok=True)
            # Save a screenshot
            screenshot_filename = f"screenshot-{domain}.png"
            screenshot_path = os.path.join(full_path, screenshot_filename)
            async with lock:
                driver.get(url)
                driver.implicitly_wait(10)
                driver.save_screenshot(screenshot_path)
            # Extract text from the site
            text = soup.get_text()
            text = format_text(text)
            lang = define_language(text)
            # Add the found URLs to urls_to_parse
            links = soup.find_all('a', href=True)
            url_array = [link['href'] for link in links if link['href'].startswith(('http://', 'https://'))]
            add_finded_URLs(url_array)
            # Save the text to a text file
            text_filename = f"text-{domain}.txt"
            with open(os.path.join(full_path, text_filename), "w", encoding="utf-8") as text_file:
                text_file.write(text)
            
            db_helper.write_in_data(url, os.path.abspath(screenshot_path), text, domain, lang)
            print(f"Сохранены данные для сайта {url} в папку {full_path}")
        

def add_finded_URLs(links):
    # Extract and add the URLs to urls_to_parse
    for link in links:
        if db_helper.check_url_exist(link):
            continue
        
        domain = get_domain_from_url(link)

        db_helper.add_to_queue(link, domain)
        
        if not db_helper.check_domain_exist(domain):
            db_helper.write_in_domain(domain, 0, 0)

        db_helper.increment_domain_count_queue(domain)

async def queue_collection():
    try:
        row = db_helper.get_ru_row_from_queue_with_min_domain_count()
        url = row[1]
        domain = row[2]
        await scrape_and_save_data(url)

        db_helper.increment_domain_count_data(domain)

        db_helper.remove_from_queue(url)
        db_helper.decrement_domain_count_queue(domain)
    except Exception as e:
            db_helper.add_to_error(url, get_domain_from_url(url))
            print(f"Не удалось обработать сайт {url} по причине  в папку {e}")


async def phishing_collection():
    try:
        url = db_helper.get_url_from_fishing()

        domain = get_domain_from_url(url)
    
        if not db_helper.check_domain_exist(domain):
            db_helper.write_in_domain(domain, 0, 0)

            db_helper.increment_domain_count_queue(domain)
        
        exept = await scrape_and_save_data(url)
        if exept == Exception:
            raise Exception
        
        
        db_helper.increment_domain_count_data(domain)
        db_helper.fill_collected_data_field(url, True)
    except Exception as e:
            db_helper.fill_collected_data_field(url, False)

async def ruphishing_collection():
    try:
        url = db_helper.get_url_from_rufishing()

        domain = get_domain_from_url(url)
    
        if not db_helper.check_domain_exist(domain):
            db_helper.write_in_domain(domain, 0, 0)

            db_helper.increment_domain_count_queue(domain)
        
        exept = await scrape_and_save_data(url)
        if exept == Exception:
            raise Exception
        
        
        db_helper.increment_domain_count_data(domain)
        db_helper.fill_collected_data_field_in_ruphishing(url, True)
    except Exception as e:
            db_helper.fill_collected_data_field_in_ruphishing(url, False)
            
driver = get_webdriver()
count = 0

scenario = input("Введите сценарий сбора данных:\n1 - сбор из очереди\n2 - сбор из базы фишинга\n3 - сбор из базы русского фишинга")

def process_queue_collection():
    asyncio.run(queue_collection())

def process_phishing_collection():
    asyncio.run(phishing_collection())

def process_ruphishing_collection():
    asyncio.run(ruphishing_collection())



count = count + 1

if count == 10:
    count = 0
    driver.quit()
    driver = get_webdriver()

while True:
    with concurrent.futures.ThreadPoolExecutor() as executor:
    # Запуск каждого метода в отдельном потоке
        if int(scenario) == 1:
            executor.submit(process_queue_collection)
        elif int(scenario) == 2:
            executor.submit(process_phishing_collection)
        elif int(scenario) == 3:
            executor.submit(process_ruphishing_collection)

        # Дождитесь завершения всех потоков перед продолжением
        executor.shutdown(wait=True)
        
        count = count + 1
        
        if count == 10:
            count = 0
            driver.quit()
            driver = get_webdriver()
            

db_helper.close_connection()