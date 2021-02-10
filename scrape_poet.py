import requests

from bs4 import BeautifulSoup as bs


def scrape_poet():

    # get html for Etheridge Knight's page and make soup :)
    etheridge = requests.get('https://www.poetryfoundation.org/poets/etheridge-knight')
    page_soup = bs(etheridge.content, 'html.parser')

    # extract innerHtml
    poet_name = page_soup.find('h1', class_="c-hdgSerif")
    poet_meta = page_soup.find('span', class_="c-txt_poetMeta")
    poet_bio = page_soup.find('div', class_="c-userContent")
    poet_more = page_soup.find_all('div', class_="o-taxonomyItem")

    # parse 'more about poet' section
    poet_attrs = {}
    for div in poet_more:
        attr_key = div.find('span').text
        attr_values = []
        values = div.find_all('li')
        for value in values:
            attr_values.append(value.find('a').text)
        poet_attrs[attr_key] = attr_values

    print(f'Name: {poet_name.text}')
    print(f'Meta: {poet_meta.text}')
    for key, value in poet_attrs.items():
        print(f'{key} {value}')
    print('Bio:')
    for p in poet_bio.find_all('p'):
        print(p.text)


if __name__ == "__main__":
    scrape_poet()
