import json
# from playwright.sync_api import sync_playwright, playwright
# import undetected_chromedriver as uc
from selenium import webdriver # replaced with undetected
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup as bs
import pandas as pd
import csv
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

# def run(playwright):
#     start_url = 'https://www.booktopia.com.au'
#     chrome = playwright.chromium
#     browser = chrome.launch(headless=False)
#     page=browser.new_page()
#     page.goto(start_url)


# with sync_playwright() as playwright:
#     run(playwright)

def parse(json_valid):
    product_data = json_valid['props']['pageProps'].get('product',{})
    if product_data:
        data = {'Title of the book':product_data.get('displayName','Book not found'),
                'Author/s':product_data.get('contributors', [{}])[0].get('name') if product_data.get('contributors') else None,
                'Book_type':product_data.get('bindingFormat'),
                'Original_price(RRP)':product_data.get('retailPrice'),
                'Discount_price':product_data.get('salePrice'),
                'ISBN':product_data.get('code'),
                'Published_date':product_data.get('publicationDate'),
                'Publisher':product_data.get('publisher'),
                'No_of_pages':product_data.get('numberOfPages')
                }
        return data
    
def get_html(url):
    options = Options()
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(30)
    page = driver.page_source
    soup = bs(page, 'html.parser')
    script_data = soup.find('script', id='__NEXT_DATA__')
    if script_data:
        json_valid = json.loads(script_data.string)
        return json_valid

def main():
    df = pd.read_csv('input_list.csv')
    base_url = 'https://www.booktopia.com.au'
    options = Options()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36")

    # Add other useful headers
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    # driver = uc.Chrome()
    driver = webdriver.Chrome(options=options)
    for i, id in df['ISBN13'].items():
        print('input:', i+1)
        # url = f'https://www.booktopia.com.au/book/{id}.html'
        driver.get('https://www.booktopia.com.au')
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
            '''
            })
        time.sleep(20)
        page = driver.page_source
        soup = bs(page, 'html.parser')
        input = driver.find_element(By.XPATH, "//input[@placeholder='Search Title, Author or ISBN']").send_keys(id)
        # input.send_keys(Keys.RETURN)
        time.sleep(20)
        driver.find_element(By.XPATH, '//div[@class="MuiGrid-root MuiGrid-item mui-style-1wxaqej"]').click()
        time.sleep(10)
        # json_data = get_html(url)
        # data = parse(json_data)
        # file_name = 'outputfile.csv'
        # fields = list(data.keys())
        # print('columna: ',fields)
        # with open(file_name, 'a+', newline='') as file:
        #     writer = csv.DictWriter(file, fieldnames=fields)
        #     if file.tell == 0:
        #         writer.writeheaders()
        #     writer.writerow(data)
        

if __name__ == "__main__":
    main()