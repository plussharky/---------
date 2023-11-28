from database_helper import DatabaseHelper
import rate_URL
from urllib.parse import urlparse

def get_domain_from_url(url: str):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    return domain

# Подключение к базе данных
db_helper = DatabaseHelper('database.db')

data_count = db_helper.get_last_id()

urls_flags_count = db_helper.url_flag_get_last_id()

while urls_flags_count < data_count:
    urls_flags_count = db_helper.url_flag_get_last_id()
    print("Количество url которым проставлены флаги: " + str(urls_flags_count-1))
    url = db_helper.get_url_from_website_data_by_id(urls_flags_count)
    url_falgs = rate_URL.get_url_data(url)
    domain = get_domain_from_url(url)

    db_helper.write_in_url_flag(domain, url_falgs)
