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
    
def get_domain_from_url(url: str):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    return domain

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

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
options.add_argument('--ignore-certificate-errors')
# Create a new ChromeService instance for each URL
chrome_service = ChromeService(executable_path=driver_path)
# Create a new Chrome webdriver instance
driver = webdriver.Chrome(service=chrome_service, options=options)
# Set the window size to the desired resolution
driver.set_window_size(desired_width, desired_height)

# Подключение к базе данных
db_helper = DatabaseHelper('database.db')

async def scrape_and_save_data(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            html = await fetch(session, url)
            soup = BeautifulSoup(html, "html.parser")
            # Extract site name from URL
            domain = get_domain_from_url(url)
            # Create a directory for each site
            site_directory = str(db_helper.get_last_id())
            full_path = os.path.join(dataset_directory, site_directory)
            os.makedirs(full_path, exist_ok=True)
            # Save a screenshot
            screenshot_filename = f"screenshot-{domain}.png"
            screenshot_path = os.path.join(full_path, screenshot_filename)
            driver.get(url)
            driver.implicitly_wait(10)
            driver.save_screenshot(screenshot_path)
            # Extract text from the site
            text = soup.get_text()
            # Add the found URLs to urls_to_parse
            links = soup.find_all('a', href=True)
            url_array = [link['href'] for link in links if link['href'].startswith(('http://', 'https://'))]
            add_finded_URLs(url_array)
            # Save the text to a text file
            text_filename = f"text-{domain}.txt"
            with open(os.path.join(full_path, text_filename), "w", encoding="utf-8") as text_file:
                text_file.write(text)
            
            db_helper.write_in_data(url, os.path.abspath(screenshot_path), text, domain)
            print(f"Сохранены данные для сайта {url} в папку {full_path}")
        except Exception as e:
            db_helper.add_to_error(url, get_domain_from_url(url))
            print(f"Не удалось обработать сайт {url} по причине  в папку {e}")

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

async def main():
    while True:
        row = db_helper.get_row_from_queue_with_min_domain_count()
        url = row[1]
        domain = row[2]
        if url == None:
            break
        await scrape_and_save_data(url)

        db_helper.increment_domain_count_data(domain)

        db_helper.remove_from_queue(url)
        db_helper.decrement_domain_count_queue(domain)

asyncio.run(main())

driver.quit()
db_helper.close_connection()