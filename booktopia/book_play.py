import json
from playwright.sync_api import sync_playwright, playwright
import time
from bs4 import BeautifulSoup as bs
import pandas as pd
import csv
from fake_useragent import UserAgent


def scrape_website(url, proxy_list):
    for proxy in proxy_list:
        print(proxy)
        with sync_playwright() as p:
            ua = UserAgent()
            random_user_agent = ua.random
            browser = p.chromium.launch(headless=False, proxy={"server": proxy})
            context = browser.new_context(ignore_https_errors=True, user_agent=random_user_agent)
            page = context.new_page()
            try:
                page.goto(url)
                time.sleep(5)  # Add a delay of 5 seconds
                
                # Find the search input element
                search_input_element = page.query_selector('input[placeholder="Search Title, Author or ISBN"]')
                
                # Type the search input
                search_input_element.type('9780007461240')
                
                # Find the search button element
                search_button = page.query_selector('button[type="button"]')

                # Click the search button
                search_button.click()
                time.sleep(3)
                # Perform scraping actions
                json_data = page.inner_html('script#__NEXT_DATA__')
                # Parsing JSON data
                next_data = json.loads(json_data.text)
                print(next_data)
                # Close the browser
                # browser.close()
            except Exception as e:
                    print(e)

if __name__ == "__main__":
    url = 'https://www.booktopia.com.au'
    proxy_list = [
        "176.113.73.104:3128",
        "176.113.73.99:3128",
        "67.205.190.164:8080",
        "46.21.153.16:3128",
        "84.17.35.129:3128",
        "104.248.59.38:80",
        "12.156.45.155:3128",
        "176.113.73.102:3128",
        "142.11.222.22:80",
        "107.178.9.186:8080",
        "34.29.41.58:3128",]
    scrape_website(url, proxy_list)