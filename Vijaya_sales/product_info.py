import datetime
import os
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import csv
import json
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver import chrome, ChromeOptions
# from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By


# options = ChromeOptions()

class Vijaya_scraper():

    def __init__(self):
        self.base_url = 'https://www.vijaysales.com/'
        self.headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                              '*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Accept-Encoding': 'gzip, deflate, br, zstd',
                    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
                    'Cache-Control': 'no - cache',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/123.0.0.0 Safari/537.36'}
        self.final_dict = {}
        self.commonColumns = ['Title', 'Url', 'Price', 'Rating', 'Mrp', 'Vsp', 'Offer_percentage', 'Product_highlights',
                             'Data-sku', 'Category', 'Prodcut_url', 'Description', 'Gtin', 'Availablility']
        # self.output_file = 'output_file.csv'
        # self.driver = webdriver.Chrome(options=options)

    def parse_data(self, soup):
        final_list = []
        try:
            title = soup.find('div', class_='prodHeading').find('h1').text.strip()
            ratings = soup.find('div', class_='starrating')
            rating = ratings.text.strip() if ratings else None
            price_tags = soup.find_all('div', class_='price_sec')
            for tags in price_tags:
                discount_price = tags.find('div', class_='clsSpecPrc clsWithVSP')
                discount_price = discount_price.text.strip() if discount_price else None
                if tags.find('div', class_='clsCpeMrp'):
                    vsp_span = tags.find('div', class_='clsCpeMrp').find('span', class_='unstikeprize')
                    vsp_price = vsp_span.text.strip() if vsp_span else None
                    mrp_span = tags.find_all('div', class_='clsCpeMrp')[1].find('span', class_='unstikeprize')
                    mrp_price = mrp_span.text.strip() if mrp_span else None
                else:
                    vsp_span = soup.find('span', string='VSP')
                    vsp_price = vsp_span.findNext('span').text.strip()
                    mrp_span = soup.find('span', string='MRP')
                    mrp_price = mrp_span.find_next('span').text.strip()

                offer_per = soup.find('span', class_='per_off')
                offer_percentage = offer_per.text.strip() if offer_per else None

                temp_dict = {'Title': title, 'Url': self.url, 'Price': discount_price, 'Rating': rating,
                            'Mrp': mrp_price, 'Vsp': vsp_price, 'Offer_percentage': offer_percentage}

                # print('dict:', self.final_dict)
                for eachCommonCol in self.commonColumns:
                    if eachCommonCol in temp_dict.keys():
                        if eachCommonCol not in self.final_dict.keys():
                            self.final_dict[eachCommonCol] = []
                        # if len(self.final_dict[eachCommonCol])==0:
                        #     self.final_dict[eachCommonCol] = []    
                        self.final_dict[eachCommonCol].append(temp_dict[eachCommonCol])

            # product highlights
            highlights = soup.find_all('div', class_='bodydata vsborderr')

            product_hightlight = []
            for div in highlights:
                high = div.find('div', class_='clsKeyFeatures')
                if high:
                    product_hightlight.append(high.text.strip())
                    # product_hightlight.append(high.text.strip())
            if 'Product_highlights' not in self.final_dict.keys():
                self.final_dict['Product_highlights']= []
            self.final_dict['Product_highlights'].append(','.join(product_hightlight)) 
                
            # extracting json details
            json_string = soup.find_all('script', type='application/ld+json')
            for key in json_string:
                json_tag = key.string
                data_load = json.loads(json_tag)
                json_list = []
                for item in data_load:
                    if isinstance(item, dict):
                        if '@type' in item and item['@type'] == 'Product':
                            json_results = {
                                # 'title': item.get('name', ''),
                                # 'price': item['offers'].get('Price', ''),
                                'Data-sku': item.get('sku', ''),
                                'Category': item.get('category', ''),
                                'Prodcut_url': item.get('url', ''),
                                'Description': item.get('description', ''),
                                'Gtin': item.get('gtin', ''),
                                'Availablility': item['offers'].get('availability', '')
                            }
                            # json_list.append(json_results)
                            # details.update(json_results)
                            # self.final_dict.update(json_results)
                            for eachCommonCol in self.commonColumns:
                                if eachCommonCol in json_results.keys():
                                    if eachCommonCol not in self.final_dict.keys():
                                        self.final_dict[eachCommonCol] = []    
                                    self.final_dict[eachCommonCol].append(json_results[eachCommonCol])

            # product information
            spec_container = soup.find('div', class_='cls-spc-hld')
            details = {}
            # Iterate through each list of details
            for ul in spec_container.find_all('ul', class_='cl-ul-sp'):
                # Iterate through each list item
                colList = []
                for li in ul.find_all('li', class_='spVT'):
                    # Extract the key and value
                    key_element = li.find('div', class_='cls-ty sptyp')
                    value_element = li.find('div', class_='cls-vl spval')
                    if key_element and value_element:
                        # Add the key-value pair to the dictionary
                        keyStr = key_element.text.strip()
                        colList.append(keyStr)
                        valueStr = value_element.text.strip().lstrip("\t")
                        if keyStr in self.final_dict.keys():
                            if colList.count(keyStr)>1:
                                joinedStr = ','.join([self.final_dict[keyStr][-1], valueStr])
                                self.final_dict[keyStr].pop()
                                self.final_dict[keyStr].append(joinedStr)
                            else:
                                self.final_dict[keyStr].append(valueStr)
                        else:
                            self.final_dict[keyStr] = []
                            fillNaValue = len(self.final_dict['Title'])
                            if fillNaValue!=1:
                                self.final_dict[keyStr] = ['NA']*(fillNaValue-1)
                            self.final_dict[keyStr].append(valueStr)

                        details[key_element.text.strip()] = value_element.text.strip().lstrip("\t")

            # with open(output_file, mode='a', newline='', encoding='utf-8') as csvfile:
            #     writer = csv.DictWriter(csvfile, fieldnames=self.final_dict.keys())
            #     if csvfile.tell() == 0:
            #         writer.writeheader()
            #     writer.writerow(self.final_dict)
        except requests.exceptions.RequestException as e:
            print('an error occured:', e)


    def run(self):
        df = pd.read_csv(os.getcwd() + '/laptop-and-printer.csv')
        for i in range(len(df)):
            self.url = df['product_link'][i]
            try:
                res = requests.get(self.url, headers=self.headers)
                if res.status_code == 200:
                    print('res:', res.status_code, '------->', i)
                    soup = bs(res.text, 'html.parser')
                    # time.sleep(2)
                    self.parse_data(soup)
            except requests.exceptions.HTTPError as e:
                print('connection error as:', e)
        output_file = 'vijaya_stores_data.csv'
        for eachCol in self.final_dict: 
            if len(self.final_dict[eachCol])<len(self.final_dict['Title']): 
                toFillNa = len(self.final_dict['Title']) -len(self.final_dict[eachCol])
                for i in range(toFillNa):
                    self.final_dict[eachCol].append('NA')
        finalDataFrame = pd.DataFrame(self.final_dict)
        finalDataFrame.to_csv(output_file)

        len(self.final_dict['Title'])


if __name__ == '__main__':
    Vijaya_scraper().run()
