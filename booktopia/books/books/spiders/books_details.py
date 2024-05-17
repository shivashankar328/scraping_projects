import scrapy
import pandas as pd
import json
from fake_useragent import UserAgent

class BooksDetailsSpider(scrapy.Spider):
    name = "books_details"
    allowed_domains = ["www.booktopia.com.au"]
    # start_urls = ["https://'https://www.booktopia.com.au/'"]
    ua = UserAgent()
    custom_settings = {
        'COOKIES_ENABLED': True,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
        # 'DOWNLOADER_MIDDLEWARES': {
        #     'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        #     'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
        #     'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
        #     'scrapy_proxies.RandomProxy': 100,
        #     'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        # },
        # 'RETRY_ENABLED': True,
        # 'RETRY_HTTP_CODES': [403, 429],
        # 'RETRY_TIMES': 3,
        # 'DOWNLOAD_DELAY': 2,
        # 'RANDOM_UA_PER_PROXY': True,
        # 'PROXY_LIST': 'proxies.txt',
        # 'PROXY_MODE': 0,
    }
    def start_requests(self):
        df = pd.read_csv('input_list.csv')
        for i, isbn in df['ISBN13'].items():
            print('input:', i+1)
            url = f'https://www.booktopia.com.au/book/{isbn}.html'
            yield scrapy.Request(url, callback = self.parse)
    
    def parse(self, response):
        script_data = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        print(script_data.string)
        if script_data:
            json_valid = json.loads(script_data.string)
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
                print(data)
                yield data
