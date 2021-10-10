import pickle
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import json


class SberSelenium:
    def __init__(self, hide_window=False):
        self.domain = "https://sbermarket.ru"
        self.chrome_options = Options()
        self.chrome_options.add_argument("headless")
        if hide_window:
            self.driver = webdriver.Chrome(options=self.chrome_options)
        else:
            self.driver = webdriver.Chrome()
        self.driver.get(self.domain)
        for cookie in pickle.load(open("sbermarket_cookies_selenium", "rb")):
            self.driver.add_cookie(cookie)
        self.driver.refresh()
        self.counter = 0
        self.counter_pages = 0

    def __get_move_last_product(self):
        articles = self.driver.find_elements_by_class_name("_3ot63")
        actions = ActionChains(self.driver)
        actions.move_to_element(articles[-1])
        actions.perform()

    def get_page_products(self, link):
        self.driver.get(self.domain + link)
        if self.__chek_is_products(self.driver.page_source):
            while not self.__chek_is_all_products(self.driver.page_source, link):
                self.__get_move_last_product()
            print(self.domain + link)
            return self.driver.page_source
        else:
            return False

    def __chek_is_products(self, page):
        soup = BeautifulSoup(page, "lxml")
        quantyti_block_products_page = soup.find("h4", {"class": "_2Ff3S"})
        if quantyti_block_products_page:
            quantyti_products_page = int(quantyti_block_products_page.text.split()[0])
            if quantyti_products_page != 0:
                return True
            else:
                return False
        else:
            return False

    def __chek_is_all_products(self, page, link):
        self.soup = BeautifulSoup(page, "lxml")
        self.quantyti_products_page = int(self.soup.find("h4", {"class": "_2Ff3S"}).text.split()[0])
        self.products_block = self.soup.find("ul", {"class": "_32CWS"})
        self.quantyti_products_list = len(self.products_block.find_all("li", recursive=False))
        # print(f"{self.quantyti_products_list} из {self.quantyti_products_page}")
        if self.counter == 50:
            self.counter = 0
            self.counter_pages += 1
            print(self.counter_pages)
            # print("Счетчик:", self.counter)
            # print("Выход при привышении счетчика. Ссылка:", link)
            return True
        if self.quantyti_products_page == self.quantyti_products_list:
            self.counter = 0
            self.counter_pages += 1
            print(self.counter_pages)
            # print("Счетчик:", self.counter)
            return True
        else:
            self.counter += 1
            # print("Счетчик:", self.counter)
            return False
        # return True if self.quantyti_products_page == self.quantyti_products_list else False


if __name__ == "__main__":
    domain = "https://sbermarket.ru"

    SS = SberSelenium()
    # page = SS.get_page_products("/auchan/c/dietskiie-tovary/iezhiednievnyi-ukhod/pampers")
    page = SS.get_page_products("/auchan/c/dietskiie-tovary/iezhiednievnyi-ukhod/podghuzniki-i-trusiki")




    soup = BeautifulSoup(page, "lxml")
    resource_not_found = soup.find("div", {"class": "resource-not-found__message-block"})
    print("Resource NF:", resource_not_found)
    products_block = soup.find("ul", {"class": "_32CWS"})
    products_list = products_block.find_all("li", recursive=False)
    print(len(products_list))
    products = []
    for product in products_list:

        product_name = product.find("h3", {"class": "_3pFCt"}).text
        product_link = product.find("a")["href"]

        product_price_block = product.find("div", {"class": "_2zcEX"})
        product_price_block.span.decompose()
        nonBreakSpace = u'\xa0'
        product_price = float(product_price_block.text[:-1].replace(nonBreakSpace, "").replace(",", "."))

        product_unit_quantity = product.find("div", {"class": "_3iKYf"}).text

        products.append({
            "product_name": product_name,
            "product_price": product_price,
            "product_unit_quantity": product_unit_quantity,
        })



    with open('../sber_market_tests.json', 'w') as f:
        json.dump(products, f, indent=4, ensure_ascii=False)
    print("OK")
