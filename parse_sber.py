import datetime
import hashlib
from time import sleep
import requests
from bs4 import BeautifulSoup
import json
import os.path
from selenium_sber import SberSelenium
from pathlib import Path

valid_categories = {
    'Автотовары',
    'Бакалея',
    'Бытовая химия, уборка',
    'Вода, соки, напитки',
    'Всё для ремонта',
    'Готовые блюда и полуфабрикаты',
    'Готовые блюда, полуфабрикаты',
    'Дача, сад',
    'Детские товары',
    'Замороженные продукты',
    'Зоотовары',
    'Канцелярия',
    'Колбасы, сосиски, деликатесы',
    'Консервы, соленья',
    'Косметика, гигиена',
    'Молочные продукты, яйца',
    'Мясо, птица',
    'Овощи, фрукты, орехи',
    'Одежда, обувь, аксессуары',
    'Рыба, морепродукты',
    'Сладости',
    'Соусы, специи, масло',
    'Спортивные товары',
    'Сыры',
    'Товары для дома',
    'Хлеб, выпечка',
    'Чай и кофе',
    'Чай, кофе',
    'Чипсы, снеки',
    'Электроника, бытовая техника'
}


def get_img_lst():
    path_dir_script = Path(__file__).parent.joinpath("src/")
    for root, dirs, files in os.walk(path_dir_script):
        return files


def get_file_categories(id_store):
    name = f'sber_market_categories_{id_store}.json'
    path = Path(__file__).parent.joinpath(name)
    if not Path.exists(path):
        response = requests.get(f"https://sbermarket.ru/api/categories?store_id={id_store}")
        with open(name, 'w', encoding="utf-8") as file:
            a = json.loads(response.text)
            a = delete_bad_categories(a)
            json.dump(a, file, indent=4, ensure_ascii=False)
        return a
    else:
        with open(name, 'r', encoding="utf-8") as file:
            return json.load(file)


def delete_bad_categories(categories: dict):
    valid_categories_lst = []
    for category in categories['categories']:
        if category['name'] in valid_categories:
            valid_categories_lst.append(category)
    return valid_categories_lst


def create_src_catalog():
    path = Path(__file__).parent.joinpath('src/')
    if not Path.exists(path):
        os.mkdir(path)


def create_products_file():
    path = Path(__file__).parent.joinpath('sber_market_products.json')
    if not Path.exists(path):
        with open('sber_market_products.json', 'w', encoding="utf-8") as f:
            json.dump([], f, indent=4, ensure_ascii=False)


create_products_file()
create_src_catalog()
result = []
img_file_list = get_img_lst()


def save_file(result):
    with open('sber_market_products.json', 'r', encoding="utf-8") as f:
        file = json.load(f)

    file.extend(result)

    with open('sber_market_products.json', 'w', encoding="utf-8") as f:
        json.dump(file, f, indent=4, ensure_ascii=False)


def recursive(categories, store, id_store, category_names=None):
    for category in categories:

        category_list = [category['name']]
        if category_names:
            category_list.extend(category_names)
        if category["children"]:
            recursive(category["children"], store, id_store, category_list)
        else:
            recurs_products = get_products(
                category["icon"]["normal_url"],
                category_list,
                category["permalink"],
                store,
                id_store
            )
            if recurs_products:
                result.extend(recurs_products)
    return


MAIN_LINK = "https://sbermarket.ru"

# Для Requests
UA = "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
HEADERS = {
    "User-Agent": UA,
    "Accept": "*/*",
    "client-token": "7ba97b6f4049436dab90c789f946ee2f",
    "etag": 'W/"c7d9dd4bc62f24f13f85a7786d4a6b16"',
    'x-request-id': "7b5aa5317802c85cac2c077fe982586f",
}
COOKIES = {
    "_Instamart_session": "YnFFMjl0QkdoQnRFZ0RPSy9hRkQ5a1dwR00vMmFRS1dVMWM1LzRvVnExYm85UGYvMEl6OTFGRW53V2paV0xRSGtvdkJaY3NoN1BWY0sxVmI0cnNWT3NLc0Q2S1d5OEp0MEZFcnBPaS9CT3VqYWJGRXBRem1wclVJVlp5YXpQODJSWHg1T29jcnVXc1dSZmlGQXdVMUFFVVloNVRvb2FGYldzOWJMdDgreU9oV0NXeTRZanpQTnRIUGZNcDQ2ckEzMzVUZmJzVkk4RTZzcGtHalJjaUh4NjhHMEpzeUpTTm8wQWNwVi9GOEhFbjJWV3Z6Rjl3WVYvcFdBTzVhdUVwTzFpWmV6MFhBRGovVG9SV3VBS3BXNHc9PS0tMm1aR1RMRVNJQndzWEpBcXVEMk9SQT09--e077947b6c8d1bc5bbd092d54ef9b627bc82785a; Path=/; HttpOnly;"}

session = requests.Session()

error_link = []
file_list = []


def get_img_categories(link, name):
    try:
        response = requests.get(MAIN_LINK + link)
        with open(f'src/{name}', 'wb') as f:
            f.write(response.content)
            img_file_list.append(name)
    except Exception as e:
        error_link.append(MAIN_LINK + link)
        print(f"Error: {e}\n" + ("#" * 20) + f"\nNo img: {MAIN_LINK + link}")


def get_img(link, name):
    response = requests.get(link)
    with open(f'src/{name}', 'wb') as f:
        f.write(response.content)
        img_file_list.append(name)


def get_img_name(link):
    name = link.split("/")[-1]
    name = name.split("?")[0]
    if len(name) <= 120:
        return name
    else:
        extension_file = "." + name.split(".")[-1]
        hash_object = hashlib.sha1(bytes(name, encoding='utf-8'))
        return hash_object.hexdigest() + extension_file


def chek_is_download_file(name):
    return name in img_file_list


def chek_is_img(link):
    if "aHR0cHM6Ly9zYmVybWFya2V0LnJ1L2Fzc2V0cy93ZWJwYWNrL3ByZXZpZXctNWY4MWM1ZmMucG5n.png" in link:
        return False
    else:
        return True


def get_response(link):
    try:
        return session.get(MAIN_LINK + link, headers=HEADERS, cookies=COOKIES, )
    except ConnectionError:
        print("!!! Ошибка соединения !!! Сервер Разорвал соединение.")
        sleep(10)
        return None
    except Exception as e:
        print("Ошибка получения респонс. Будет попытка повторного подключения.\nКод ошибки:\n", e)
        sleep(10)
        return None


SS = SberSelenium()


def get_products(category_img_link, category_list, category_link, store, id_store):
    products = []
    category_link = f"/{store}/c/" + category_link + f"?sid={id_store}"
    category_img_link = category_img_link.split("?")[0]
    page = SS.get_page_products(category_link)
    if not page:
        return
    soup1 = BeautifulSoup(page, "lxml")

    a_block = soup1.find("ul", {"class": "_32CWS"})
    a_list = a_block.find_all("a", {"class": "_3sj6S"})
    page_products_links_list = []

    for href in a_list:
        page_products_links_list.append(href["href"])

    for link in page_products_links_list:
        response = get_response(link)

        while not response:
            print("попытка подключиться")
            response = get_response(link)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")

            # Устарела ссылка
            resource_not_found = soup.find("div", {"class": "resource-not-found__message-block"})
            if resource_not_found:
                continue
            else:

                # картинка категории
                category_img_name = get_img_name(category_img_link)
                if not chek_is_download_file(category_img_name):
                    get_img_categories(category_img_link, category_img_name)

                # картинка продукта
                product_block_img = soup.find_all("div", {"data-node-type": "slides"})
                product_img_link = {}
                product_img_name = {}
                for number, product_img in enumerate(product_block_img):
                    picture_link = product_img.find("img").get("src")
                    if chek_is_img(picture_link):
                        product_img_link[number] = picture_link
                        product_img_name[number] = get_img_name(picture_link)
                        if not chek_is_download_file(product_img_name[number]):
                            get_img(picture_link, product_img_name[number])

                    else:
                        product_img_link = None
                        product_img_name = None

                # название продукта
                product_name = soup.find("h1", {"class": "_2olAT"}).text

                # цена продукта
                product_price_block = soup.find("div", {"class": "_3AvHk"})
                # product_price_block.span.decompose()
                product_price = float(product_price_block.text[:-1].replace(u'\xa0', "").replace(",", "."))

                # единица измерения продукта
                product_unit_quantity = soup.find("p", {"class": "_1tYVg"}).text

                # блок описания
                products_block_desc = soup.find("div", {"class": "_1D90_"})

                # описание продукта
                try:
                    product_description = products_block_desc.find("div", {"class": "_3I-Pz"}).text
                except AttributeError:
                    product_description = None

                # пищевая ценность продукта
                try:
                    product_block_nutritional = products_block_desc.find("div", {"class": "nutrition"})
                    product_block_nutritional_value = product_block_nutritional.find_all("li")
                    product_nutrition = {}
                    for value in product_block_nutritional_value:
                        product_property_name = value.find("div", {"class": "product-property__name"}).text
                        product_property_value = value.find("div", {"class": "product-property__value"}).text
                        product_nutrition[product_property_name] = product_property_value
                except AttributeError:
                    product_nutrition = None

                # название продукта
                try:
                    product_ingredients = products_block_desc.find("div", {"class": "ingredients__text"}).text
                except AttributeError:
                    product_ingredients = None

                # информация продукта
                try:
                    product_information_block = products_block_desc.find("div", {"class": "_3Ttwi"})
                    product_information_list = product_information_block.find_all("li")
                    product_information = {}
                    for value in product_information_list:
                        product_property_name = value.find("strong").text
                        product_property_value = value.find("div", {"class": "product-property__value"}).text
                        product_information[product_property_name] = product_property_value
                except AttributeError:
                    product_information = None

                products.append({
                    "store": store,
                    "main_category_name": category_list[-1],
                    "category_name": category_list[0],
                    "category_img_name": category_img_name,

                    "product_name": product_name,
                    "product_price": product_price,
                    "product_unit_quantity": product_unit_quantity,
                    "product_description": product_description,
                    "product_nutrition": product_nutrition,
                    "product_ingredients": product_ingredients,
                    "product_information": product_information,
                    "product_img_name": product_img_name,
                })

        else:
            print(f"Ошибка на сайте:\n{response.text}")

    save_file(products)
    return products


def run_parse(name_store, id_store):
    time_format = "%Y-%m-%d %H:%M:%S"
    print(f"Время начала: {datetime.datetime.now(): {time_format}}")

    data = get_file_categories(id_store)
    recursive(data, name_store, id_store)

    with open('sber_market_full.json', 'w', encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    with open("test_sber/error_link.json", "w", encoding="utf-8") as f:
        json.dump(error_link, f, indent=4, ensure_ascii=False)

    print(f"Время окончания: {datetime.datetime.now(): {time_format}}")


