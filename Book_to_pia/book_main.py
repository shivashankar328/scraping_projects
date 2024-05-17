
import requests
import json
from bs4 import BeautifulSoup as bs
import csv
import pandas as pd
import os
import logging
import concurrent.futures
import time
# from fake_useragent import UserAgent
# from requests.adapters import HTTPAdapter
# from urllib3.util.retry import Retry
import random
import threading


'author=shiva shankar'
'date=16-05-2024'

# set up logging configuration
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s-%(levelname)s-%(message)s')


def parse(page_html):
    """
    parse the html of web page and extracts relevant book data 
    
    args:
        page_html(str): the HTML content of the web page
    
    returns:
        dict: a dictionary containing the extracte book data the dictionary has the folliwing kyes:
        keys = ['Title of the book', 'Author/s','Book_type','Original Price(RRP)','Discount Price','ISBN-10','Published Date',
            'Publisher','No of pages','Product url' ]
                            
    """
    
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
                    # print('data:', data)
                    return data
                else:
                    data={'Title of the book':str('Book not found')}
                    return data
    except ValueError:
        print('product details not found')


def sent_requests(url):
    """
    Sends HTTP requests to a given URL using different user agents.

    Args:
        url (str): The URL to send the requests to. here i have used proxy api 
        https://proxy.scrapeops.io/v1/

    Returns:
        str: The HTML content of the response.

    Raises:
        requests.exceptions.HTTPError: If an HTTP error occurs.

    """

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

    try:
        for _ in user_agent_list:
            # Pick a random user agent
            user_agent = random.choice(user_agent_list)

            # Set the headers
            # fake_headers = {'User-Agent': user_agent}
            res = requests.get(
                url='https://proxy.scrapeops.io/v1/',
                params={
                    'api_key': '9046d7ed-aa00-46e8-9d8c-5811322c070d',
                    'url': url,
                    'User-Agent':user_agent
                    
                    },
                )
            if res.status_code == 200:
                page_html = res.text
                return page_html
    except requests.exceptions.HTTPError as err:
        logging.error(f'HTTP Error: {err}')
        print(err)


def save_to_csv(result, total_time, id):
    """
    saving the result dictionary and log files into csv file.
    args:
        result-->dict, total_time--> sec, id-->str
    return:
        saving the result dict to outputfile_isbn.csv and logs to run_log.csv
        
    """
    finished_url = result.get('Product url', '')
    file_name = 'outputfile_isbn.csv'
    print('result:', result)
    if isinstance(result, dict):
        result.pop('Product url', '')
        # fields = list(result.keys())
        fields = ['Title of the book', 'Author/s', 'Book_type', 'Original Price(RRP)', 'Discount Price', 'ISBN-10',
                  'Published Date', 'Publisher', 'No of pages']
        # writing output to csv file in append mode
        with open(file_name, 'a', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fields, lineterminator='\r')
            # if not file_exists:
            if file.tell() == 0:
                writer.writeheader()  # Write the header if the file is empty
            writer.writerow(result)

    # writing log file
    file_log = {'ISBN': int(id), 'URL': finished_url, 'Time per requests': total_time}
    file_exists = os.path.isfile("run_log.csv")
    with open("run_log.csv", 'a', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=file_log.keys(), lineterminator='\r')
        if not file_exists:
            writer.writeheader()
        writer.writerow(file_log)


# Define a lock for synchronizing access to the CSV file
csv_lock = threading.Lock()


def process_isbn(id, completed):
    """
    Process the ISBN of a book.

    Args:
        id (str): The ISBN of the book.from input_list.csv file
        completed (list): A list of completed ISBNs from run_log.csv file.
        it check the id with complted list if it maches skip that id to sent_requests

    Returns:
        json_data: from sent_requests function and and input as parse funtions
        result: dict from parse function, 
        calling save_to_csv funtion to save the result dict to csv file 
        
    """
    if id not in completed:
        print('current_id:', id)
        url = f'https://www.booktopia.com.au/book/{id}.html'
        start_time = time.time()
        json_data = sent_requests(url)
        result = parse(json_data)
        if not result:
            print(f"Warning: No result for ISBN: {id}")
            result = {'Title of the book':str('Book not found')}
        total_time = time.time() - start_time
        print('time for each request: ', total_time)
        # Acquire the lock before writing to the CSV file
        with csv_lock:
            save_to_csv(result, total_time, id)

def main():
    """
    This function is the entry point of the program.

    It reads data from a CSV file named 'run_log.csv' and stores it in a list called csv_data.
    It then extracts the 'ISBN' values from csv_data and stores them in a list called completed.

    It reads data from another CSV file named 'input_list.csv' using pandas and stores it in a DataFrame called df.

    It creates a ThreadPoolExecutor with a maximum of 4 worker threads.

    It iterates over the 'ISBN13' values in df and submits a task to the executor to process each ISBN.
    The process_isbn function is called with the ISBN and the completed list as arguments.

    Finally, it waits for all tasks to complete before exiting.
    """
    with open('run_log.csv', 'r', encoding='utf8') as logfile:
        csv_data = list(csv.DictReader(logfile))
        completed = [sel['ISBN'] for sel in csv_data]

    df = pd.read_csv('input_list.csv')

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for i, id in df['ISBN13'].items():
            futures.append(executor.submit(process_isbn, id, completed))

        # Wait for all tasks to complete
        concurrent.futures.wait(futures)


if __name__ == "__main__":
    main()

