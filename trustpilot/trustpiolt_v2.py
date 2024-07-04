import requests
from bs4 import BeautifulSoup as bs
import json
import pandas as pd

def get_request(url):
    res = requests.get(url)
    if res.status_code == 200:
        soup = bs(res.text, 'html.parser')
        return soup
    else:
        return None

def get_data(soup):
    string_element = soup.find('script', id='__NEXT_DATA__')
    if string_element:
        json_data = string_element.string
        parsed_data = json.loads(json_data)
        data = parsed_data['props']['pageProps']['businessUnits']['businesses']
        page_count = parsed_data['props']['pageProps']['businessUnits']['totalPages']
        return page_count, data
    else:
        return None, None

def get_pagination_data(page_url, page_count):
    all_data = []
    for i in range(2, page_count + 1):  # Start from 1 to include the first page
        url = page_url.format(i)
        soup = get_request(url)
        if soup:
            _, data = get_data(soup)
            if data:
                all_data.extend(data)
    return all_data

def main():
    # Base URL with a placeholder for the page number
    # page_url = 'https://www.trustpilot.com/categories/travel_insurance_company?sort=reviews_count&page={}'
    page_url = 'https://www.trustpilot.com/categories/clinics?sort=reviews_count&page={}'
    # Initial request to get the total page count
    initial_soup = get_request(page_url.format(1))
    if initial_soup:
        page_count, initial_data = get_data(initial_soup)
        
        # Collect data from all pages
        if page_count and initial_data:
            all_data = initial_data + get_pagination_data(page_url, page_count)
            
            # Convert collected data into a DataFrame
            df = pd.DataFrame(all_data)
            print(len(df))
            df.to_csv('trustpilot_clinics.csv')
            print("Data saved to trustpilot.csv")
        else:
            print("Failed to retrieve initial data.")
    else:
        print("Failed to make initial request.")

if __name__ == "__main__":
    main()
