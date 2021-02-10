import requests

from bs4 import BeautifulSoup as bs


_BASE_URL = 'https://www.poetryfoundation.org/poets/'


def scrape_poet(name):
    poet = {}

    # get html for Etheridge Knight's page and make soup :)
    html = requests.get(_BASE_URL + name)
    page_soup = bs(html.content, 'html.parser')

    # extract innerHtml and add to return object
    # name
    poet["name"] = page_soup.find('h1', class_="c-hdgSerif").text
    # years of birth/death (if present)
    if page_soup.find('span', class_="c-txt_poetMeta"):
        poet["meta"] = page_soup.find('span', class_="c-txt_poetMeta").text
    else:
        poet["meta"] = ''

    # biography/main text
    poet_bio = page_soup.find('div', class_="c-userContent").text
    poet["bio"] = poet_bio

    # 'more about this poet' section
    poet_attrs = {}
    if page_soup.find('div', class_="o-taxonomyItem"):
        poet_more = page_soup.find_all('div', class_="o-taxonomyItem")
        for div in poet_more:
            attr_key = div.find('span').text
            attr_values = []
            values = div.find_all('li')
            for val in values:
                attr_values.append(val.find('a').text)
            poet_attrs[attr_key] = attr_values
    poet["attrs"] = poet_attrs

    return poet
