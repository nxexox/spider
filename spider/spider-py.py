"""
Скрипт сбора ссылок на википедии.

"""
import requests
from bs4 import BeautifulSoup as BS


BASE_URL = "https://ru.wikipedia.org/wiki/Служебная:Все_страницы/Category:{cat_name}"

# Ключ, это категория, значение set ссылок.
# 1040 - 1071; 65-90
# cats = {
#     chr(i): set()
    # for i in range(60, 1100)
    # if 'А' <= chr(i) <= 'Я' or 'A' <= chr(i) <= 'Z'
# }
cats = {'A': set()}

keys = cats.copy()
count_keys = len(keys)
now = 0

for key in keys.keys():
    try:
        response = requests.get(BASE_URL.format(cat_name=key))
        now += 1
        if response.status_code != 200:
            raise Exception('STATUS CODE `{}` on PAGE: `{}`'.format(response.status_code, BASE_URL.format(cat_name=key)))

        soup = BS(response.content, 'lxml')
        if soup.find('div', attrs={'id': 'mw-subcategories'}):
            print('Это список субкатегорий.')
        elif soup.find('div', attrs={'id': 'mw-pages'}):
            print('Это список страниц в категории.')

        print('END TO KEY `{}`/`{}` `{}` '.format(now, count_keys, key))
    except Exception as e:
        print('EXCEPTION ', e)


if __name__ == "__main__":
    pass
