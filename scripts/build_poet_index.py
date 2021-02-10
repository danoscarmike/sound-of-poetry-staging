import requests

from bs4 import BeautifulSoup as bs


_BASE_URL = 'https://www.poetryfoundation.org/poets/'


def build_poet_index():
    page = 1
    f = open('poet_urls.txt', 'w')

    while page < ((4648/20) + 1):
        url = f"{_BASE_URL}browse#page={page}&sort_by=last_name"
        html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        print(f'{page} - {url} : {html.status_code}')
        page_soup = bs(html.content, 'html.parser')
        for poet in page_soup.find_all('h2', class_="c-hdgSans"):
            poet_url = poet.find('a')['href']
            print(f'writing: {poet_url}')
            f.write(f'{poet_url}\n')
        page += 1
    f.close()


if __name__ == "__main__":
    build_poet_index()