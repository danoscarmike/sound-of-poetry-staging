import re
import requests
from unicodedata import normalize
import numpy as np
from bs4 import BeautifulSoup as bs


def scrape_poem(url):
    # get html for poet's page and make soup :)
    print(f"requesting {url}")
    html = requests.get(url)
    print(html.status_code)
    page_soup = bs(html.content, "html.parser")

    image_poem = page_soup.find('img', src=re.compile('.*/jstor/.*'))
    if image_poem:
        return None
    else:
        # scrape poet name
        poet = page_soup.find('a', href=re.compile('.*/poets/.*'))
        if poet:
            poet = poet['href']

        # scrape tags
        tags = []
        for tag in page_soup.find_all('a', href=re.compile('.*/poems/browse#topics=.*')):
            tag = normalize('NFKD', str(tag.contents[0]))
            tags.append(tag)

        # scrape title
        title_soup = page_soup.find('h1')
        if title_soup:
            title = title_soup.get_text().strip()
            # scrape audio_url
            audio_url = title_soup.parent.find('button')
            if audio_url:
                audio_url = audio_url["data-popupview-url"]

        # scrape video_url
        video_url = page_soup.find('a', href=re.compile('.*/video/.*'))
        if video_url:
            video_url = video_url['href']

        try:
            # most frequent formatting
            lines_raw = page_soup.find_all(
                'div', {'style': 'text-indent: -1em; padding-left: 1em;'})
            # normalize text (from unicode)
            lines = [normalize('NFKD', str(line.contents[0]))
                     for line in lines_raw if line.contents]
            # remove some hanging html and left/right whitespace
            lines = [line.replace('<br/>', '').strip() for line in lines
                     if line.replace('<br/>', '').strip()]
            try:
                # remove certain bracket pattern (special cases)
                line_pattern = '>(.*?)<'
                lines = [re.search(line_pattern, line, re.I).group(
                    1) if '<' in line else line for line in lines]
            except:
                try:
                    # remove other bracket pattern (special cases)
                    lines = [
                        re.sub('<.*>', '', line) if '<' in line \
                            else line for line in lines
                    ]
                except:
                    # else NaN
                    lines = np.nan

        except:
            try:
                # if 'text-align' is justified
                lines_raw = page_soup.find_all('div', {'style': 'text-align: justify;'})
                # normalize text (from unicode)
                lines = [normalize('NFKD', str(line.contents[0]))
                         for line in lines_raw if line.contents]
                # remove some hanging html and left/right whitespace
                lines = [line.replace('<br/>', '').strip() for line in lines
                         if line.replace('<br/>', '').strip()]

                if not lines:
                    # if nothing grabbed
                    try:
                        # scrape from PoemView
                        lines_raw = page_soup.find(
                            'div', {
                                'data-view': 'PoemView'}).get_text().split('\r')
                        # remove left/right whitespace
                        lines = [line.strip()
                                 for line in lines_raw if line.strip()]
                    except:
                        # else NaN
                        lines = np.nan
            except:
                # else NaN
                lines = np.nan

        # create string version of poem
        poem_string = '\n'.join(lines)

        # re-scrape for less common formatting
        modes = ['PoemView', 'poempara', 'p_all', 'justify', 'center']
        i = 0
        while poem_string == '' and i < 5:
            lines, poem_string = rescrape(page_soup, modes[i])
            i = i + 1

        if poem_string:
            # create and return dictionary
            poem_info = {'url': url,
                         'poet_url': poet,
                         'title': title,
                         'poem_lines': lines,
                         'poem_string': poem_string,
                         'audio_url': audio_url,
                         'video_url': video_url,
                         'tags': tags}

            return poem_info
        else:
            return None


def rescrape(page_soup, mode):
    # load a page and soupify it

    if mode == 'PoemView':
        # scrape text from soup
        lines_raw = page_soup.find('div', {'data-view': 'PoemView'})
        if lines_raw:
            lines_raw = lines_raw.get_text().split('\r')

            # initial process text
            lines = [normalize('NFKD', line).replace('\ufeff', '')
                     for line in lines_raw if line]
        else:
            return None, None

    elif mode == 'poempara':
        # scrape text from soup
        lines_raw = page_soup.find_all('div', {'class': 'poempara'})

        if lines_raw:
            # initial process text
            lines = [normalize('NFKD', str(line.contents[-1]))
                     for line in lines_raw if line.contents]
        else:
            return None, None

    elif mode == 'p_all':
        # scrape text from soup
        lines_raw = page_soup.find_all('p')
        if lines_raw:
            lines_raw = lines_raw[:-1]

            # initial process text
            lines = [normalize('NFKD', str(line.contents[0]))
                     for line in lines_raw if line]
        else:
            return None, None

    elif mode == 'justify':
        # scrape text from soup
        lines_raw = page_soup.find('div', {'style': 'text-align: justify;'})
        if lines_raw:
            lines_raw = lines_raw.contents

            # initial process text
            lines = [normalize('NFKD', str(line)) for line in lines_raw if line]
        else:
            return None, None

    elif mode == 'center':
        # scrape text from soup
        lines_raw = page_soup.find_all('div', {'style': 'text-align: center;'})
        if lines_raw:
            # initial process text
            lines = [normalize('NFKD', str(line)) for line in lines_raw if line]
        else:
            return None, None

    # process text
    lines = [line.replace('<br/>', '') for line in lines]
    lines = [line.strip() for line in lines if line.strip()]
    line_pattern = '>(.*?)<'
    lines_clean = []

    for line in lines:
        if '<' in line:
            try:
                lines_clean.append(
                    re.search(
                        line_pattern,
                        line,
                        re.I).group(1).strip())
            except BaseException:
                continue
        else:
            lines_clean.append(line.strip())

    # create string version of poem
    poem_string = '\n'.join(lines_clean)

    return lines_clean, poem_string


if __name__ == "__main__":
    print(scrape_poem("https://www.poetryfoundation.org/poems/150985/if-ing"))
