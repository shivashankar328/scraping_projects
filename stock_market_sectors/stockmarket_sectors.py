import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from collections import OrderedDict


def get_sector_urls(url, headers):
    """
    Function to retrieve sector URLs from a given URL.

    Parameters:
    url (str): The URL to fetch the sector URLs from.
    headers (dict): The headers to be used for the HTTP request.

    Returns:
    list: A list of dictionaries containing the title and link of each sector URL.
          Returns None if sector links are not found or an error occurs during the request.
    """
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        soup = bs(res.text, 'html.parser')
        anchors = soup.find('div', class_='card card-small')
        if anchors:
            links_tags = anchors.find_all('a')
            href_links = [{'title': link.text, 'link': 'https://www.screener.in' + link.get('href')} for link in
                          links_tags]
            return href_links
        else:
            print('sector links not found check the connection.')
            return None
    except requests.exceptions.HTTPError as e:
        print('an error occures while fetchin the main page ', e)
        return None


def pagination_search(page_soup):
    """
    Extracts data from a table in a web page and returns it as a list of dictionaries.

    Args:
        page_soup: BeautifulSoup object representing the web page.

    Returns:
        A list of dictionaries, where each dictionary represents a row in the table.

    Raises:
        None.

    """
    table = page_soup.find('table', class_='data-table text-nowrap striped mark-visited')
    if table:
        # extract table headers
        tab_headers = [th.text.strip() for th in table.find_all('th')]
        table_headers = list(OrderedDict.fromkeys(tab_headers))
        # table_headers = tab_headers[:len(tab_headers) // 2]
        print('len_table_headers:', len(table_headers), table_headers)
        # extract rows from table
        rows = []
        # print('len_rows:', len(table.find_all('tr')))
        for tr in table.find_all('tr'):
            row_data = {}
            td_list = tr.find_all('td')
            if td_list:
                # print('len_td_list:', len(td_list))
                for index, td in enumerate(td_list):
                    name_url = td.find('a')
                    if name_url:
                        row_data['Title_url'] = "https://www.screener.in" + str(name_url.get('href'))
                        row_data['Name'] = name_url.text.strip()
                    else:
                        row_data[table_headers[index]] = td.text.strip()
                if row_data:  # Ensure the row is not empty
                    rows.append(row_data)
        return rows
    else:
        print('no table found on page')
        return None


def search_page_url(href_links, headers, input_str):
    """
    Search for a specific sector URL and extract results from the page.

    Args:
        href_links (list): List of dictionaries containing sector titles and links.
        headers (dict): Headers for the HTTP request.
        input_str (str): The sector title to search for.
        input_str = Aerospace & Defence

    Returns:
        list: List of results extracted from the sector page.

    Raises:
        requests.exceptions.RequestException: If there is an error with the HTTP request.

    """

    for dict_item in href_links:
        if dict_item['title'].strip().lower() == input_str.strip().lower():
            sector_url = dict_item['link']
            try:
                res_sector = requests.get(sector_url, headers=headers)
                res_sector.raise_for_status()  # Raise an exception for HTTP errors

                sector_soup = bs(res_sector.text, 'html.parser')
                results = pagination_search(sector_soup)
                # paginations extraction
                page_num_tag = sector_soup.find_all('div', class_='sub')
                for item in page_num_tag:
                    if 'results found' in item.text:
                        pages = item.text.strip()
                        page_num = pages.split('page 1 of ')[-1]
                        if page_num:
                            for page in range(2, int(page_num)+1):
                                page_url = sector_url + f'?page={page}&limit=50'
                                page_res = requests.get(page_url, headers=headers)
                                page_res.raise_for_status()
                                page_soup = bs(page_res.text, 'html.parser')
                                results += pagination_search(page_soup)
                        else:
                            print('pages not found', page_num)
                            continue
                return results
            except requests.exceptions.RequestException as e:
                print('error as ', e)
        # else:
        #     print(f'url not found for {input_str}, enter valid input')
    print(f'sector {input_str} not found in page.use proper inputs')


def main():
    """
    Main function to retrieve data from screener.in based on input sector.

    Args:
        input_str (str): The sector for which data needs to be retrieved.

    Returns:
        None
    """
    url = 'https://www.screener.in/explore/'
    headers = {'authority': 'www.screener.in', 'method': 'GET',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                         '*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/122.0.0.0 Safari/537.36'
               }
    # input_str = 'Aerospace & Defence'
    input_str = str(input('enter sector to search: '))
    sector_links = get_sector_urls(url, headers)
    if sector_links:
        results = search_page_url(sector_links, headers, input_str)
        if results:
            df = pd.DataFrame(results)
            output_name = input_str.strip().replace('&', '_').replace(' ', '_').lower()
            df.to_csv(f'{output_name}.csv', index=False)
            print(f'data saved to {output_name}.csv')
            print(df.head())
        else:
            print('no data found')
    else:
        print('sector link not found')


if __name__ == '__main__':
    main()
