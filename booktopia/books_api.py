
import requests
import base64
import json
from bs4 import BeautifulSoup as bs
import csv
import pandas as pd
import os
import logging
import concurrent.futures
import time, datetime
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import random

# set up logging configuration
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s-%(levelname)s-%(message)s')


def parse(page_html):
    # Parse the HTML with BeautifulSoup
    try:
        soup = bs(page_html, 'html.parser')
        script_data = soup.find('script', attrs={'id': '__NEXT_DATA__'})
        if script_data:
            json_data = json.loads(script_data.string)
            if json_data is not None:
                props = json_data.get('props', {})
                page_props = props.get('pageProps', {})

                if not page_props:
                    print("Warning: 'pageProps' is None or empty. book not found !")

                # product_data = json_data['props']['pageProps'].get('product',{})
                product_data = page_props.get('product', {})
                if product_data:
                    data = {'Title of the book':str(product_data.get('displayName','Book not found')),
                            'Author/s': str(product_data.get('contributors', [{}])[0].get('name')) if product_data.get('contributors') else '',
                            'Book_type': str(product_data.get('bindingFormat')),
                            'Original Price(RRP)': float(product_data.get('retailPrice')),
                            'Discount Price': float(product_data.get('salePrice')),
                            'ISBN-10':int(product_data.get('code')),
                            'Published Date':str(product_data.get('publicationDate')),
                            'Publisher': str(product_data.get('publisher')),
                            'No of pages':int(product_data.get('numberOfPages')) if product_data.get('numberOfPages') else '',
                            'Product url':str("https://www.booktopia.com.au/"+product_data.get('productUrl'))
                            }
                    print('data:', data)
                    return data
                else:
                    data={'Title of the book':str('Book not found')}
                    return data
    except ValueError:
        print('product details not found')


def sent_requests(url):
    ua = UserAgent()
    random_user_agent = ua.random

    user_agent_list = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36',
        'Opera/9.80 (Windows NT 6.1; WOW64) Presto/2.12.388 Version/12.18',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36 OPR/84.0.4316.14',
        'Opera/9.80 (Linux armv7l) Presto/2.12.407 Version/12.51 , D50u-D1-UHD/V1.5.16-UHD (Vizio, D50u-D1, Wireless)',
        'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36 OPR/42.0.2393.94',
        'Mozilla/5.0 (Linux; U; Android 8.1.0; zh-CN; EML-AL00 Build/HUAWEIEML-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.108 baidu.sogo.uc.UCBrowser/11.9.4.974 UWS/2.13.1.48 Mobile Safari/537.36 AliApp(DingTalk/4.5.11) com.alibaba.android.rimet/10487439 Channel/227200 language/zh-CN',
        'Mozilla/5.0 (X11; U; Linux i686; en-US) U2/1.0.0 UCBrowser/9.3.1.344',
        'Mozilla/5.0 (Linux; U; Android 10; en-US; RMX1901 Build/QKQ1.190918.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/78.0.3904.108 UCBrowser/13.4.0.1306 Mobile Safari/537.36',
        'UCWEB/2.0 (Java; U; MIDP-2.0; Nokia203/20.37) U2/1.0.0 UCBrowser/8.7.0.218 U2/1.0.0 Mobile'
        ]

    data = {
            "url": url,
            "httpResponseBody": True
            }

    headers = {
            'Content-Type': 'application/json',
            'X-Api-Key': '760a08c8-1856-4d1b-ae6f-0363ffd26e8b',
            'Accept-Encoding':'gzip, deflate, br, zstd',
            'Accept-Language':'en-US,en;q=0.9',
            'User-Agent':random_user_agent
            }

    try:
        for _ in user_agent_list:
            # Pick a random user agent
            user_agent = random.choice(user_agent_list)

            # Set the headers
            fake_headers = {'User-Agent': user_agent}

            session = requests.Session()
            retries = Retry(total=5, backoff_factor=1, status_forcelist=[500])
            session.mount('http://', HTTPAdapter(max_retries=retries))
            session.mount('https://', HTTPAdapter(max_retries=retries))
            session.headers.update(fake_headers)
            response = session.post('https://api.proxyscrape.com/v3/accounts/freebies/scraperapi/request', headers=headers, json=data)
            # response = requests.post('https://api.proxyscrape.com/v3/accounts/freebies/scraperapi/request', headers=headers, json=data)

            # response.raise_for_status()
            if response.status_code == 200:
                json_response = response.json()
                if 'browserHtml' in json_response['data']:
                    page_html = json_response['data']['browserHtml']
                else:
                    page_html = base64.b64decode(json_response['data']['httpResponseBody']).decode()
                    return page_html
            if response.status_code != 200:
                res = requests.get(
                    url='https://proxy.scrapeops.io/v1/',
                    params={
                        'api_key': 'e6bf9657-6a2e-4fd4-bb49-631acb5b1941',
                        'url': url,
                        },
                    )
                page_html = res.text
                return page_html
    except requests.exceptions.HTTPError as err:
        logging.error(f'HTTP Error: {err}')
        print(err)


def main():
    with open('run_log.csv', 'r', encoding='utf8') as logfile:
        csv_data = list(csv.DictReader(logfile))
        completed = [sel['ISBN'] for sel in csv_data]
        print('completed:', completed)
    df = pd.read_csv('input_list.csv')

    for i, id in df['ISBN13'].items():
        print('input:', i+1, ':', id)
        # checking the id is avaialble in completed list
        if id not in completed:
            url = f'https://www.booktopia.com.au/book/{id}.html'
            start_time = time.time()
            json_data = sent_requests(url)
            result = parse(json_data)
            total_time = time.time() - start_time
            print('time for each request: ', total_time)
            if not result:
                print(f"Warning: No result for ISBN {id}")
                continue
            finished_url = result.get('Product url', '')

            # print('res:', type(result), ':', result)
            folder_path = 'output'
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            file_name='outputfile_isbn.csv'
            path = os.path.join(folder_path, file_name)
            file_exists = os.path.isfile(path)
            if isinstance(result, dict):
                result.pop('Product url', '')
                fields = list(result.keys())
                # writing output to csv file in append mode
                with open(file_name, 'a', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=fields, lineterminator='\r')
                    # if not file_exists:
                    if file.tell() == 0:
                        writer.writeheader()  # Write the header if the file is empty
                    writer.writerow(result)

            # writing log file
            file_log = {'ISBN': int(id), 'URL': finished_url, 'Time per requests':total_time}
            file_exists = os.path.isfile("run_log.csv")
            with open("run_log.csv", 'a', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=file_log.keys(), lineterminator='\r')
                if not file_exists:
                    writer.writeheader()
                writer.writerow(file_log)


if __name__ == "__main__":
    main()

#
# def process_isbn(id, completed):
#     url = f'https://www.booktopia.com.au/book/{id}.html'
#     if id not in completed:
#         print('Processing ISBN:', id)
#         start_time = time.time()
#         json_data = sent_requests(url)
#         if json_data:
#             result = parse(json_data)
#             total_time = time.time() - start_time
#             print('Time taken for ISBN', id, ':', total_time)
#             if result:
#                 return result
#         else:
#             print(f"Warning: No result for ISBN {id}")
#     return None
#
#
# def main():
#     completed = set()
#     if os.path.isfile('run_log.csv'):
#         with open('run_log.csv', 'r', encoding='utf8') as logfile:
#             reader = csv.DictReader(logfile)
#             completed = {row['ISBN'] for row in reader}
#
#     df = pd.read_csv('input_list.csv')
#
#     output_folder = 'output'
#     os.makedirs(output_folder, exist_ok=True)
#
#     with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
#         futures = []
#         for id in df['ISBN13']:
#             futures.append(executor.submit(process_isbn, id, completed))
#
#         output_file = os.path.join(output_folder, 'outputfile_isbn.csv')
#         for future in concurrent.futures.as_completed(futures):
#             result = future.result()
#             finished_url = result.get('Product url', '')
#             with open(output_file, 'a', encoding='utf-8', newline='') as output_csv:
#                 fieldnames = list(result.keys())
#                 writer = csv.DictWriter(output_csv, fieldnames=fieldnames)
#                 if os.path.getsize(output_file) == 0:
#                     writer.writeheader()
#             if result:
#                 print('result:', result)
#                 writer.writerow(result)
#
#     # Update run_log.csv
#     with open('run_log.csv', 'a', encoding='utf-8', newline='') as run_log:
#         fieldnames = ['ISBN','URL','Time per requests']
#         writer = csv.DictWriter(run_log, fieldnames=fieldnames)
#         for id in df['ISBN13']:
#             if id not in completed:
#                 writer.writerow({'ISBN': id})
#
#
# # if __name__ == "__main__":
# #     main()