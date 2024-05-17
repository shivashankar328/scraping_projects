import requests
from bs4 import BeautifulSoup as bs
import json
import os
import logging 
import pandas as pd
import csv
from fake_useragent import UserAgent


# set up logging configuration
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s-%(levelname)s-%(message)s')

def parse_json(json_valid):

    # datapoints = title, author, booktype, originalprice, discountedprice, isbn, publisheddate, publisher, no.ofpages
    # product_data = json_valid['props']['pageProps']['product']
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
    else:
        data['Title of the book'] = 'Book not found'
        return data 

def get_html(url):
    ua = UserAgent()
    random_user_agent = ua.random
    headers = {
            'authority':'www.booktopia.com.au',
            'method':'GET',
            'scheme':'https',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding':'gzip, deflate, br, zstd',
            'Accept-Language':'en-US,en;q=0.9',
            'User-Agent':random_user_agent
            }
    
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        if res.status_code == 200:
            soup = bs(res.text, 'html.parser')
            # script_tag = soup.find('script', type='application/ld+json')
            # if script_tag:
            #     json_data = json.loads(script_tag.text)
            script_data = soup.find('script', id='__NEXT_DATA__')
            if script_data:
                json_valid = json.loads(script_data.string)
            return json_valid
    except requests.exceptions.HTTPError as err:
        logging.error(f'HTTP Error: {err}')
        print(err)

def main():
    df = pd.read_csv('input_list.csv')
    for i, id in df['ISBN13'].items():
        print('input:', i+1)
        url = f'https://www.booktopia.com.au/book/{id}.html'
        data = get_html(url)
        result = parse_json(data)
        print(result)
        file_name = 'outputfile.csv'
        fields = list(result.keys())
        print('columna: ',fields)
        with open(file_name, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            if file.tell() == 0:
                writer.writeheaders()
            writer.writerow(result)
            
                
    
if __name__ == '__main__':
    main()

# SEARCH URL 
# https://www.booktopia.com.au/search?keywords=9780061763403&productType=917504&pn=1

#api
'https://azureserv.com/__cpi.php?s=aXZqM0xLVXZpY3FBbHNKN0VOMy9vSkFVSnVQZnM4b3hkaG81aDV2MmNqd29taS9tQ3hQSWVxM1piZGYwYTJ1bGpDcGtjRHMycDFGN082TmtDRXdPMXdnRlMyZ0NDRnFDS3d2cUpab041bWdrdnNiVGZPVTVhZS9zVFBIUk1Dbmo1a1dOS3ZjUGtNQ3NTb2xEYk1sbWJRPT0%3D&r=aHR0cHM6Ly9henVyZXNlcnYuY29tL3RoZS1zY3Jld3RhcGUtbGV0dGVycy1sZXR0ZXJzLWZyb20tYS1zZW5pb3ItdG8tYS1qdW5pb3ItZGV2aWwtYy1zLWxld2lzL2Jvb2svOTc4MDAwNzQ2MTI0MC5odG1sP19fY3BvPWFIUjBjSE02THk5M2QzY3VZbTl2YTNSdmNHbGhMbU52YlM1aGRR&__cpo=1'