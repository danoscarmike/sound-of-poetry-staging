import requests

from bs4 import BeautifulSoup as bs


_BASE_URL = "https://www.poetryfoundation.org/poems/browse"

with open('poem_urls.txt', 'w') as poem_url_file:
    for page in range(1, 2292):
        response = requests.get(_BASE_URL, headers='', params={"page": page, "sort_by": "title", "preview": "0"})
        if response.status_code == 200:
            page_soup = bs(response.content, 'html.parser')
            for poem in page_soup.find_all('h2', class_="c-hdgSans"):
                poem_url = poem.find('a')['href']
                poem_url_file.write(f'{poem_url}\n')
            page = page + 1
        else:
            print(f'error - page: {page}')
