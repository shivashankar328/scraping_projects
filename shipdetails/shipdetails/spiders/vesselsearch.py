import scrapy
import json


class VesselsearchSpider(scrapy.Spider):
    name = "vesselsearch"

    def start_requests(self):
        url = "https://www.steamshipmutual.com/vessel-search?prod_vessel&query=ab"
        yield scrapy.Request(url, callback=self.get_api)

    def get_api(self, response):
        script_data = response.xpath('//script[contains(text(), "vesselSearch")]').extract_first()
        api_key = script_data.split('apiKey":"')[1].split('"')[0]
        app_id = script_data.split('appId":"')[1].split('"')[0]
        self.api_url = "https://866g6frdi8-1.algolianet.com/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.8.3)%3B%20Browser%3B%20instantsearch.js%20(3.7.0)%3B%20JS%20Helper%20(2.28.0)https://866g6frdi8-1.algolianet.com/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.8.3)%3B%20Browser%3B%20instantsearch.js%20(3.7.0)%3B%20JS%20Helper%20(2.28.0)"

        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'X-Algolia-Api-Key': api_key,
            'X-Algolia-Application-Id': app_id
        }
        # print('headers:', headers)

        self.payload = {
            "requests": [
                {
                    "indexName": "prod_vessel",
                    "params": "query=ab&page=0&highlightPreTag=__ais-highlight__&highlightPostTag=__%2Fais-highlight__&facetFilters=hide_from_search%3Ashow&facets=%5B%5D&tagFilters="
                }
            ]
        }

        yield scrapy.Request(self.api_url, method='POST', headers=self.headers, body=json.dumps(self.payload),
                             callback=self.parse_api_response)

    def parse_api_response(self, response):

        json_data = json.loads(response.body)
        for item in json_data['results'][0]['hits']:
            yield {
                'search_term': json_data['results'][0]["query"],
                "imo": item["imo_number"],
                'Vesselname': item['title'],
                "member": item["member"],
                "port_registry": item["port_of_registry"],
                "vessel_type": item["vessel_type"]
            }
        # Extract the current page number from meta
        current_page = json_data['results'][0]["page"]
        # Extract the total number of pages
        total_pages = json_data['results'][0]['nbPages']
        search_query = json_data['results'][0]["query"]
        if current_page < total_pages - 1:
            nextpage = current_page + 1
            print('\ncurrent_page:', nextpage)
            self.payload['requests'][0][
                'params'] = f"query={search_query}&page={nextpage}&highlightPreTag=__ais-highlight__&highlightPostTag=__%2Fais-highlight__&facetFilters=hide_from_search%3Ashow&facets=%5B%5D&tagFilters="

            yield scrapy.Request(self.api_url, method='POST', headers=self.headers, body=json.dumps(self.payload),
                                 callback=self.parse_api_response, meta={'current_page': nextpage})


# Run this spider using the command `scrapy runspider vesselsearch.py -o ship.json`
