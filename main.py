from datetime import date
from pathlib import Path
from collections import defaultdict

import pandas as pd
from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader, select_autoescape

WINERY_FOUNDATION_YEAR = 1920
PRICE_LIST_FILE_PATH = Path('wine3.xlsx')
PRICE_LIST_FILE_SHEET_NAME = 'Лист1'
PRICE_LIST_HEADER_MAPPING = {'Название': 'name', 'Сорт': 'variety',
                             'Цена': 'price', 'Картинка': 'image',
                             'Категория': 'category', 'Акция': 'profitable'}


def main():
    df = pd.read_excel(PRICE_LIST_FILE_PATH,
                       sheet_name=PRICE_LIST_FILE_SHEET_NAME,
                       engine='xlrd')
    if set(df.columns.tolist()) != set(PRICE_LIST_HEADER_MAPPING):
        print(f"There are no expected column names in {PRICE_LIST_FILE_PATH}")

    df.rename(columns=PRICE_LIST_HEADER_MAPPING, inplace=True)

    wines_by_category = defaultdict(list)
    for category, group in df.groupby('category'):
        wines_by_category[category] = group.fillna('').to_dict('records')

    env = Environment(loader=FileSystemLoader('.'),
                      autoescape=select_autoescape('html'))

    template = env.get_template('template.html')

    rendered_page = template.render(
        winery_age=WINERY_FOUNDATION_YEAR - date.today().year,
        wines_by_category=wines_by_category
    )

    with open('index.html', 'w', encoding='utf8') as file:
        file.write(rendered_page)

    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    server.serve_forever()


if __name__ == '__main__':
    main()
