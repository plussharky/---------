import re
from urllib.parse import urlparse
import requests
import whois
from whois.exceptions import FailedParsingWhoisOutput
import dns.resolver
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import tldextract
import datetime
import time
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
from database_helper import URLData
from database_helper import DatabaseHelper

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

def ip_check(url):
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    match = re.search(ip_pattern, url)
    if match:
        return -1, match
    else:
        return 1, None
    
def url_len_check(url):
    url_len = len(url)
    if url_len < 54:
        return 1
    elif (url_len >= 54) and (url_len <= 75):
        return 0
    return -1

def url_short_check(url):
    url_patterns = [
    r'https?://t.ly',
    r'^https?://clc.to',
    r'^https?://clc.la',
    r'^https?://u.to',
    r'^https?://cutt.us',
    r'^https?://bit.ly',
    r'^https?://is.gd',
    r'^https?://goo.su ',
    r'^https?://rb.gy',
    r'^https?://lnnk.in',
    r'^https?://tinyurl.com',
    r'^https?://tiny.one',
    r'^https?://clck.ru',
    r'^https?://vk.cc',
    ]

    for pattern in url_patterns:
        if re.match(pattern, url):
            return -1
        return 1

def at_symbol_check(url):
    if url.find("@") == -1:
        return 1
    else:
        return -1
    
def double_slash_check(url, request_flag):
    tmp_url = url
    if tmp_url.startswith("http:"):
        tmp_url = tmp_url[7:]
        print(url + " request_flag = " + str(request_flag))
    if tmp_url.startswith("https:"):
        tmp_url = tmp_url[8:]
        print(url + " request_flag = " + str(request_flag))
    if tmp_url.find("//") == -1:
        return 1
    else:
        return -1
    
def prefix_suffix_check(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    if domain.find("-") == -1:
        return 1
    return -1

def sub_domain_check(url, having_ip_address):
    if having_ip_address == -1:
        return 0
    parsed_url = urlparse(url)
    tmp_url = parsed_url.netloc
    # Удаляем "www." из URL-адреса
    tmp_url = re.sub(r'www\.', '', tmp_url)
    # Определяем количество точек в имени домена
    dot_count = tmp_url.count('.')
    if dot_count > 1:
        return 0
    elif dot_count > 2:
        return -1
    return 1

def ssl_and_page_rank_check(url, having_ip_address):
    headers = {'API-OPR': 'cwwo4wgo8swkosgkwsk80c4k8os0occo84s40cg4'}
    if having_ip_address == -1:
        domain = url
    else:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        requested_url = 'https://openpagerank.com/api/v1.0/getPageRank?domains%5B0%5D=' + domain
    try:
        request = requests.get(requested_url, headers=headers, timeout=10)
        result = request.json()
        page_rank = result['response'][0]['page_rank_decimal']
    except requests.exceptions.RequestException:
        page_rank = 0
        protocol_id = 0
    if url.startswith("http://"):
        protocol_id = -1
    elif url.startswith("https://"):
        protocol_id = 1
    if page_rank < 3:
        page_rank_res = -1
    else:
        page_rank_res = 1
    if protocol_id == 1:
        protocol_id = 0
    
    return protocol_id, page_rank_res

def domain_reg_len_check(url, having_ip_address):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    domain_age = 0
    creation_date = None
    domain_age_res = -1
    domain_not_found = 0
    if having_ip_address == -1:
        return -1, 1, -1
    try:
        w = whois.whois(url)
        if w.creation_date != None:
            if isinstance(w.creation_date, list):
                creation_date = w.creation_date[0]
            else:
                creation_date = w.creation_date
            if isinstance(w.updated_date, list):
                updated_date = w.updated_date[0]
            else:
                updated_date = w.updated_date
            if isinstance(w.expiration_date, list):
                expiration_date = w.expiration_date[0]
            else:
                expiration_date = w.expiration_date
            if updated_date != None:
                domain_age = (expiration_date - updated_date).days / 365
            else:
                domain_age = (expiration_date -creation_date).days / 365
            domain_not_found = 0
        else:
            domain_not_found = 1
    except (whois.exceptions.FailedParsingWhoisOutput, AttributeError):
        domain_not_found = 1
        pass

    if creation_date != None:
        days_count = (datetime.datetime.today() -creation_date).days
        if days_count > 179:
            domain_age_res = 1

    if domain_age <= 1:
        return -1, domain_not_found, domain_age_res
    else:
        return 1, domain_not_found, domain_age_res
    
def favicon_check(url, request_flag):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    favicon_url1 = url + '/favicon.ico'
    favicon_url2 = domain + '/favicon.ico'
    #if request_flag == 1:
    #    favicon_url1 = url + '/favicon.ico'
    #    favicon_url2 = domain + '/favicon.ico'
    try:
        # Отправляем GET-запрос для получения фавикона
        response1 = requests.get(favicon_url1, timeout=2)
    except requests.exceptions.RequestException:
        return -1
    
    # Проверяем статус-код ответа
    if response1.status_code == 200:
        return 1
    try:
        # Отправляем GET-запрос для получения фавикона
        response2 = requests.get(favicon_url2, timeout=2)
    except requests.exceptions.RequestException:
        return -1
    # Проверяем статус-код ответа
    if response2.status_code == 200:
        return 1
    return -1

def favicon_one_more(driver):
    # Поиск по слову "favicon" в HTML-коде
    if "favicon" in driver.page_source:
        return 1
    else:
        return -1

def https_on_domain_check(url, having_ip_address):
    if having_ip_address == -1:
        return -1
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    if domain.find('https') == -1:
        return 1
    else:
        return -1

def request_url_check(driver, my_main_domain):
    # всего ссылок на внешние объекты
    external_objects_count = 0
    # всего ссылок на внешние объекты, у которых совпадает домен с доменом исходного url
    external_main_domain_count = 0

    images = driver.find_elements(By.TAG_NAME, 'img')
    # Iterate through the images and check the domain
    for image in images:
        image_url = image.get_attribute('src')
        if image_url is not None:
            if len(image_url) > 6:
                parsed_url = urlparse(image_url)
                image_domain = parsed_url.netloc
                extracted = tldextract.extract(image_domain)
                main_domain = extracted.registered_domain
                external_objects_count += 1
                if main_domain == my_main_domain:
                    external_main_domain_count += 1

    videos = driver.find_elements(By.TAG_NAME, 'video')
    # Iterate through the videos and check the domain
    for video in videos:
        video_url = video.get_attribute('src')
        if video_url is not None:
            if len(video_url) > 6:
                parsed_url = urlparse(video_url)
                video_domain = parsed_url.netloc
                extracted = tldextract.extract(video_domain)
                main_domain = extracted.registered_domain
                external_objects_count += 1
                if main_domain == my_main_domain:
                    external_main_domain_count += 1

    audios = driver.find_elements(By.TAG_NAME, 'audio')
    # Iterate through the audios and check the domain
    for audio in audios:
        audio_url = audio.get_attribute('src')
    if audio_url is not None:
        if len(audio_url) > 6:
            parsed_url = urlparse(audio_url)
            audio_domain = parsed_url.netloc
            extracted = tldextract.extract(audio_domain)
            main_domain = extracted.registered_domain
            external_objects_count += 1
            if main_domain == my_main_domain:
                external_main_domain_count += 1

    external_res = 0
    if external_objects_count != 0:
        # процент ссылок ведущих на левый домен
        external_res = (external_objects_count - external_main_domain_count) / external_objects_count * 100
    if external_res < 31:
        return 1
    else:
        return -1
    
def url_of_anchor_and_mailto_check(driver, my_main_domain):
    mailto = 1
    a_tags = driver.find_elements(By.TAG_NAME, "a")
    a_tags_hrefs = [a.get_attribute('href') for a in a_tags]
    domain_count = 0
    # количество доменов тега <a> совпадающих с исходным доменом
    main_domain_count = 0
    for href in a_tags_hrefs:
        if href:
            if len(href) > 6:
                parsed_url = urlparse(href)
                domain = parsed_url.netloc
                extracted = tldextract.extract(domain)
                main_domain = extracted.registered_domain
                domain_count += 1
                if main_domain == my_main_domain:
                    main_domain_count += 1
                domain_count += 1
                if 'mailto:' in href:
                    mailto = -1
    anchor_res = 0
    if domain_count != 0:
        # процент ссылок ведущих на левый домен
        anchor_res = (domain_count - main_domain_count) / domain_count * 100
    if anchor_res < 31:
        return 1, mailto
    elif (anchor_res >= 31) and (anchor_res <= 67):
        return 0, mailto
    else:
        return -1, mailto

def links_in_tags_check(driver, my_main_domain):
    # всего ссылок в тегах link, meta, script
    links_in_tags_count = 0
    # всего ссылок в тегах link, meta, script, у которых совпадает домен с доменом исходного url
    links_in_maindomain_tags_count = 0
    metas =  driver.find_elements(By.TAG_NAME, 'meta')
    # Iterate through the meta tags and check the domain
    for meta in metas:
        meta_url = meta.get_attribute('content')
        if meta_url is not None:
            if len(meta_url) > 6:
                parsed_url = urlparse(meta_url)
                extracted = tldextract.extract(parsed_url.netloc)
                main_domain = extracted.registered_domain
                links_in_tags_count += 1
                if main_domain == my_main_domain:
                    links_in_maindomain_tags_count += 1

    scripts = driver.find_elements(By.TAG_NAME, 'script')
    # Iterate through the scripts and check the domain
    for script in scripts:
        script_url = script.get_attribute('src')
        if script_url is not None:
            if len(script_url) > 6:
                parsed_url = urlparse(script_url)
                extracted = tldextract.extract(parsed_url.netloc)
                main_domain = extracted.registered_domain
                links_in_tags_count += 1
                if main_domain == my_main_domain:
                    links_in_maindomain_tags_count += 1

    links = driver.find_elements(By.TAG_NAME, 'link')
    # Iterate through the links and check the domain
    for link in links:
        link_url = link.get_attribute('href')
        if link_url is not None:
            if len(link_url) > 6:
                parsed_url = urlparse(link_url)
                extracted = tldextract.extract(parsed_url.netloc)
                main_domain = extracted.registered_domain
                links_in_tags_count += 1
                if main_domain == my_main_domain:
                    links_in_maindomain_tags_count += 1
    
    links_res = 0
    if links_in_tags_count != 0:
        # процент ссылок ведущих на левый домен
        links_res = (links_in_tags_count - links_in_maindomain_tags_count) / links_in_tags_count * 100
    if links_res < 17:
        return 1
    elif (links_res >= 17) and (links_res <= 81):
        return 0
    else:
        return -1

def sfh_check(driver, my_main_domain):
    # Поиск элементов <form> на странице
    forms = driver.find_elements(By.TAG_NAME, "form")
    res = 1
    for form in forms:
        action = form.get_attribute("action")
    # Проверка наличия пустой строки или "about:blank" в атрибуте action
        if action == "" or action == "about:blank":
            return -1
    # Проверка, если домен SFHотличается от домена текущей страницы
        if action and action.startswith("http"):
            parsed_url = urlparse(action)
            extracted = tldextract.extract(parsed_url.netloc)
            main_domain = extracted.registered_domain
            if main_domain != my_main_domain:
                res = 0
    return res

def on_mouseover_check(driver):
    # Ищем элементы с атрибутом onMouseOver
    elements_with_onmouseover = driver.find_elements(By.XPATH, '//*[@onmouseover]')
    # Проверяем, делают ли эти элементы изменения в строке состояния
    for element in elements_with_onmouseover:
        onmouseover_value = element.get_attribute('onmouseover')
        if "window.status" in onmouseover_value:
            return -1
        
    return 1

def right_click_check(driver):
    page_source = driver.page_source
    # Проверяем наличие строки "event.button==2" в исходном коде
    if "event.button==2" in page_source:
        return -1
    
    return 1

def iframe_check(driver):
    # Поиск всех iframe на странице
    iframes = driver.find_elements(By.TAG_NAME, 'iframe')
    # Проверка каждого iframe на наличие атрибута "frameBorder" и его значение
    for ifr in iframes:
        frame_border = ifr.get_attribute('frameBorder')
        if frame_border is not None:
            if frame_border == 'no' or frame_border == '0':
                return -1
            
    return 1

def html_check(my_url, request_flag, having_ip_address, favicon, redirect_count):
    url_of_anchor = 1
    request_url = -1
    links_in_tags = 0
    on_mouseover = 1
    rightClick = 1
    iframe = 1
    SFH = 1
    submitting_to_email = 1

    driver = get_webdriver()

    # Open the web page
    try:
        # Загрузка страницы
        driver.get(my_url)
    except TimeoutException:
        pass

    time.sleep(1.5)
    i = 0
    while i != redirect_count:
        time.sleep(1.5)
        i += 1

    doc = None
    try:
        doc = driver.execute_script("return document.body")
    except:
        pass

    if doc is not None:
        # Get scroll height
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(0.5)
            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            parsed_myurl = urlparse(my_url)
            mydomain = parsed_myurl.netloc
            if having_ip_address == 1:
                myextracted = tldextract.extract(mydomain)
                # домен исходного url
                my_main_domain = myextracted.registered_domain
            else:
                my_main_domain = mydomain
            if favicon == -1:
                favicon = favicon_one_more(driver)
            url_of_anchor, submitting_to_email = url_of_anchor_and_mailto_check(driver, my_main_domain)
            request_url = request_url_check(driver, my_main_domain)
            links_in_tags = links_in_tags_check(driver, my_main_domain)
            on_mouseover = on_mouseover_check(driver)
            rightClick = right_click_check(driver)
            iframe = iframe_check(driver)
            SFH = sfh_check(driver, my_main_domain)

            driver.quit()

    return url_of_anchor, submitting_to_email, request_url, links_in_tags, on_mouseover,  rightClick, iframe, SFH, favicon

def request_and_redirect_check(url):
    redirect_res = 0
    redirect_count = 0
    try:
        response = requests.get(url, timeout=5)
        print(url + " | response.status_code = " + str(response.status_code))
        redirect_count = len(response.history)
        if ('access denied' in response.text.lower()) or ('dont have permission' in response.text.lower()) \
        or ('suspected phishing' in response.text.lower()) or ('human verification' in response.text.lower()) \
        or ('are you human' in response.text.lower()) or ('i\'m not a robot' in response.text.lower()) \
        or ('you are human' in response.text.lower()) or ('you are not robot' in response.text.lower()) \
        or ('are you a robot' in response.text.lower()) or ('you are a human' in response.text.lower()) \
        or ('page not found' in response.text.lower()) or ('url terminated' in response.text.lower()) \
        or ('unauthorized access' in response.text.lower()) or ('не робот' in response.text.lower()) \
        or ('not available' in response.text.lower()) or ("404" in response.text.lower()) \
        or ('я человек' in response.text.lower()) or ('вы человек' in response.text.lower()) \
        or ('index of' in response.text.lower()) \
        or (response.status_code == 404) or (response.status_code == 410):
            return 0, redirect_res, redirect_count
        if redirect_count == 0 and ('http-equiv=\"refresh\"' in response.text.lower()) and ('window.location.href' in response.text.lower()):
            return 0, redirect_res, redirect_count
        if redirect_count > 1:
            redirect_res = 1
            if response.history[redirect_count-1].url != response.url:
                return 1, redirect_res, redirect_count
        if response.status_code != 200:
            return 0, redirect_res, redirect_count
    except requests.exceptions.RequestException:
        return 0, redirect_res, redirect_count
    
    return 1, redirect_res, redirect_count

def dns_record_check(url, having_ip_address, ip):
    if having_ip_address == -1:
        record_types = ['PTR']
        domain = ip
    else:
        record_types = [
        'A', 'AAAA', 'CNAME', 
        'MX', 'NS', 'PTR', 'SOA', 'TXT', 
        'DNSKEY'
        ]
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
    for record_type in record_types:
        try:
            answers = dns.resolver.resolve(domain, record_type)
            if answers:
                return 1
        except dns.exception.DNSException:
            continue

    return -1

def web_traffic_check(url, having_ip_address):
    # https://developers.similarweb.com/docs/digital-rank-api
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    if having_ip_address == 1:
        extracted = tldextract.extract(domain)
        main_domain = extracted.registered_domain
    else:
        main_domain = url

    responseurl = "https://api.similarweb.com/v1/similar-rank/" + main_domain + "/rank?api_key=e8e3e855563041d78d6ef32dd556f97e"
    
    try:
        req = requests.get(responseurl, timeout=5).json()
    except requests.exceptions.RequestException as e:
        print("web_traffic_check. ", e)
        return -1

    if req['meta']['status'] == 'Error':
        rank = -1
    else:
        rank = req['similar_rank']['rank']
    if rank == -1:
        return -1
    elif rank < 100000:
        return 1
    else:
        return 0

def google_index_check(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    google = "https://www.google.com/search?q=site:" + domain + "&hl=en"
    try:
        response = requests.get(google, timeout=1)
    except requests.exceptions.RequestException as e:
        print("google_index_check. ", e)
        return -1
    soup = BeautifulSoup(response.content, "html.parser")
    not_indexed = re.compile("did not match any documents")
    if soup(text=not_indexed):
        return -1
    else:
        return 1
    
def stat_rep_check(url, having_ip_address):
    db = DatabaseHelper('database.db')
    result = 0
    if db.exist_in_phishing(url):
        result = -1
    else:
        result = 1
    db.close_connection()
    return result
    

def get_url_data(url):
    request_flag, redirect, redirect_count = request_and_redirect_check(url)
    #if request_flag == 0:
        #return None

    having_ip_address, ip = ip_check(url)
    url_length = url_len_check(url)
    short_service = url_short_check(url)
    having_at_symbol = at_symbol_check(url)
    double_slash_redirecting = double_slash_check(url, request_flag)
    prefix_suffix = prefix_suffix_check(url)
    having_sub_domain = sub_domain_check(url, having_ip_address)
    ssl_final_state, page_rank = ssl_and_page_rank_check(url, having_ip_address)
    domain_reg_length, domain_not_found, age_of_domain = domain_reg_len_check(url, having_ip_address)
    favicon = favicon_check(url, request_flag)
    https_token = https_on_domain_check(url, having_ip_address)
    url_of_anchor, submitting_to_email, request_url, links_in_tags, mouseover, right_click, iframe, sfh, favicon = html_check(url, request_flag, having_ip_address, favicon, redirect_count)
    dns_record = dns_record_check(url, having_ip_address, ip)
    google_index = google_index_check(url)
    web_traffic = web_traffic_check(url, having_ip_address)
    statistical_report = stat_rep_check(url, having_ip_address)

    result = URLData()
    result.url = url
    result.having_ip_address = having_ip_address
    result.url_length = url_length
    result.short_service = short_service
    result.having_at_symbol = having_at_symbol
    result.double_slash_redirecting = double_slash_redirecting
    result.prefix_suffix = prefix_suffix
    result.having_sub_domain = having_sub_domain
    result.ssl_final_state = ssl_final_state
    result.domain_reg_length = domain_reg_length
    result.favicon = favicon
    result.https_token = https_token
    result.request_url = request_url
    result.url_of_anchor = url_of_anchor
    result.links_in_tags = links_in_tags
    result.sfh = sfh
    result.submitting_to_email = submitting_to_email
    result.redirect = redirect
    result.mouseover = mouseover
    result.right_click = right_click
    result.iframe = iframe
    result.age_of_domain = age_of_domain
    result.dns_record = dns_record
    result.web_traffic = web_traffic
    result.page_rank = page_rank
    result.google_index = google_index
    result.statistical_report = statistical_report

    return result

def transformation_url(url):
    request_flag, redirect, redirect_count = request_and_redirect_check(url)
    if request_flag == 0:
        return None
    result = []
    having_ip_address, ip = ip_check(url)
    url_length = url_len_check(url)
    short_service = url_short_check(url)
    having_at_symbol = at_symbol_check(url)
    double_slash_redirecting = double_slash_check(url, request_flag)
    prefix_suffix = prefix_suffix_check(url)
    having_sub_domain = sub_domain_check(url, having_ip_address)
    ssl_final_state, page_rank = ssl_and_page_rank_check(url, having_ip_address)
    domain_reg_length, domain_not_found, age_of_domain = domain_reg_len_check(url, having_ip_address)
    favicon = favicon_check(url, request_flag)
    https_token = https_on_domain_check(url, having_ip_address)
    url_of_anchor, submitting_to_email, request_url, links_in_tags, mouseover, right_click, iframe, sfh, favicon = html_check(url, request_flag, having_ip_address, favicon, redirect_count)
    dns_record = dns_record_check(url, having_ip_address, ip)
    google_index = google_index_check(url)
    web_traffic = web_traffic_check(url, having_ip_address)
    statistical_report = stat_rep_check(url, having_ip_address)

    result.append(having_ip_address)
    result.append(url_length)
    result.append(short_service)
    result.append(having_at_symbol)
    result.append(double_slash_redirecting)
    result.append(prefix_suffix)
    result.append(having_sub_domain)
    result.append(ssl_final_state)
    result.append(domain_reg_length)
    result.append(favicon)
    result.append(https_token)
    result.append(request_url)
    result.append(url_of_anchor)
    result.append(links_in_tags)
    result.append(sfh)
    result.append(submitting_to_email)
    result.append(redirect)
    result.append(mouseover)
    result.append(right_click)
    result.append(iframe)
    result.append(age_of_domain)
    result.append(dns_record)
    result.append(web_traffic)
    result.append(page_rank)
    result.append(google_index)
    result.append(statistical_report)

    return result

def update_dataset():
    df = pd.read_csv('final.csv').rename(columns={'Unnamed: 0': 'idx'}).drop(columns='idx')
    flag = int(input("Выберите: 1 - phishing_urls.txt, 2 -legitimate_urls.txt"))
    if flag == 1:
        filename = 'phishing_urls.txt'
        phish_flag = -1
    elif flag == 2:
        filename = 'legitimate_urls.txt'
        phish_flag = 1
    else:
        return -1
    with open(filename, 'r') as file:
        lines = file.readlines()
    for line in lines:
        url = line
        url = url.rstrip('\n')
        try:
            transformed_url = transformation_url(url)
        except:
            continue
        if transformed_url == None:
            continue

        transformed_url.append(phish_flag)
        df_trnsf_url = pd.DataFrame([transformed_url])
        df_trnsf_url.columns = ['having_ip_address', 
        'url_length', 'short_service', 
        'having_at_symbol',

        'double_slash_redirecting', 
        'prefix_suffix', 
        'having_sub_domain',

        'ssl_final_state', 
        'domain_reg_length', 'favicon', 
        'https_token',

        'request_url', 'url_of_anchor', 
        'links_in_tags', 'sfh',

        'submitting_to_email', 'redirect', 
        'mouseover', 'right_click', 
        'iframe',

        'age_of_domain', 'dns_record', 
        'web_traffic', 'page_rank',

        'google_index', 
        'statistical_report']

        df = pd.concat([df, 
        df_trnsf_url], ignore_index=True)
        df.to_csv('update_final.csv')
        # Классификация введенного URL

def phishing_check(url):
    # transform_url = transformation_url(url)
    transform_url = [1, 1, 1, 1, 
    1, 1, 1, 0, -1, -1, 1, 1, 1, 0, 1, 
    1, 0, 1, 1, 1, -1, 1, -1, -1, -1, 
    1]
    df_trnsf_url = pd.DataFrame([transform_url])
    df_trnsf_url.columns = ['having_ip_address', 
    'url_length', 'short_service', 
    'having_at_symbol',
    
    'double_slash_redirecting', 
    'prefix_suffix', 
    'having_sub_domain',
    
    'ssl_final_state', 
    'domain_reg_length', 'favicon', 
    'https_token',
    
    'request_url', 'url_of_anchor', 
    'links_in_tags', 'sfh',
    
    'submitting_to_email', 'redirect', 
    'mouseover', 'right_click', 
    'iframe',
    
    'age_of_domain', 'dns_record', 
    'web_traffic', 'page_rank',
    
    'google_index', 
    'statistical_report']

    rf_model = pickle.load(open('random_forest_model.pickle', "rb"))
    ab_model = pickle.load(open('adaboost_model.pickle', "rb"))
    dct_model = pickle.load(open('decision_tree_model.pickle', "rb"))
    knn_model = pickle.load(open('knn_model.pickle', "rb"))
    lr_model = pickle.load(open('logistic_regression_model.pickle', "rb"))
    models = [dct_model, rf_model, knn_model, lr_model, ab_model]
    method_names = ['Decision tree', 'Random forest', 'Knn', 'Logistic regression', 'AdaBoost']
    for i in range(0, 5):
        pred = models[i].predict(df_trnsf_url)
        print('\nmethod: ', method_names[i],'\nprediction: ', pred)
    print('\n')

def print_metrics():
    rf_model = pickle.load(open('random_forest_model.pickle', "rb"))
    ab_model = pickle.load(open('adaboost_model.pickle', "rb"))
    dct_model = pickle.load(open('decision_tree_model.pickle', "rb"))
    knn_model = pickle.load(open('knn_model.pickle', "rb"))
    lr_model = pickle.load(open('logistic_regression_model.pickle', "rb"))
    models = [dct_model, rf_model, knn_model, lr_model, ab_model]
    method_names = ['Decision tree', 'Random forest', 'Knn', 'Logistic regression', 'AdaBoost']
    df = pd.read_csv('final.csv').rename(columns={'Unnamed: 0': 'idx'}).drop(columns='idx')
    X = df.drop(columns='result')
    Y = df['result']
    train_X, test_X, train_Y, test_Y = train_test_split(X, Y, test_size=0.3, random_state=43)
    for i in range(0, 5):
        start = time.time()
        for j in range(0, 20):
            models[i].predict(test_X)
        end = time.time() - start
        pred_time = end / 20
        pred = models[i].predict(test_X)
        print('\nmethod: ', method_names[i],'\nprediction time: ', pred_time,'\nprecision =', precision_score(pred, test_Y),'\nrecall =', recall_score(pred, test_Y),'\naccuracy =', accuracy_score(pred, test_Y),'\nf1 =', f1_score(pred, test_Y),'\nconfusion_matrix:\n', confusion_matrix(y_true=test_Y, y_pred=pred))
        if __name__ == '__main__':
        # phishing_check_and_update_dataset('asd')
        # print_metrics()
            asd = input('Select:\n1:Verify web-page\n2:Update dataset\n3:Check metrics\n')
            print_metrics()
            select_flag = input('Select:\n1:Verify web-page\n2:Update dataset\n3:Check metrics\n')
            if select_flag == '1':
                url = input('Input URL: ')
                phishing_check(url)
            elif select_flag == '2':
                update_dataset()
            elif select_flag == '3':
                print_metrics()
            else:
                print('Wrong.')