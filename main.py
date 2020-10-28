import argparse
from datetime import date
from pathlib import Path
import os
from collections import defaultdict

import pandas as pd
from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader, select_autoescape
from dotenv import load_dotenv

ENV_PREFIX = 'WINE'
FILE_SUFFIX = 'xlsx'
WINERY_FOUNDATION_YEAR = 1920
DEFAULT_PRICE_LIST_FILE_SHEET_NAME = 'Лист1'
PRICE_LIST_HEADER_MAPPING = {'Название': 'name', 'Сорт': 'variety',
                             'Цена': 'price', 'Картинка': 'image',
                             'Категория': 'category', 'Акция': 'profitable'}


def process_data_frame(wine_price_list_data_frame):
    wine_price_list_data_frame.rename(columns=PRICE_LIST_HEADER_MAPPING,
                                      inplace=True)

    wines_by_category = defaultdict(list)
    for category, group in wine_price_list_data_frame.groupby('category'):
        wines_by_category[category] = group.fillna('').to_dict('records')
    return wines_by_category


def generate_file(wines_by_category):
    env = Environment(loader=FileSystemLoader('.'),
                      autoescape=select_autoescape('html'))

    template = env.get_template('template.html')

    rendered_page = template.render(
        winery_age=WINERY_FOUNDATION_YEAR - date.today().year,
        wines_by_category=wines_by_category
    )

    with open('index.html', 'w', encoding='utf8') as file:
        file.write(rendered_page)


def start_web_server():
    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description='Generate winery main page '
                                                 'from price list')
    parser.add_argument("-f", "--file", help="Path to price list excel file")
    parser.add_argument("-s", "--sheet", help="Name of the file's sheet")
    args = parser.parse_args()

    sheet_name = os.getenv(
        f"{ENV_PREFIX}_SHEET_NAME") or args.sheet or \
                 DEFAULT_PRICE_LIST_FILE_SHEET_NAME
    file_path = os.getenv(f"{ENV_PREFIX}_FILE_NAME") or args.file
    if not file_path:
        print("Please provide price list file name")
        return
    file_path = Path(file_path)
    if not file_path.exists() or file_path.suffix.lower() == FILE_SUFFIX:
        print("File with price list doesn't exists")
        return

    extracted_sheets = pd.read_excel(file_path,
                                     sheet_name=None,
                                     engine='xlrd')
    wine_price_list_data_frame = extracted_sheets.get(sheet_name)
    if wine_price_list_data_frame is None:
        print(f"There is no {sheet_name} in price list {file_path.name} file")
        return

    if set(wine_price_list_data_frame.columns.tolist()) != set(
            PRICE_LIST_HEADER_MAPPING):
        print(f"There are no expected column names in {file_path}")
        return

    generate_file(process_data_frame(wine_price_list_data_frame))
    start_web_server()


if __name__ == '__main__':
    load_dotenv()
    main()
