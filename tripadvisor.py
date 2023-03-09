import requests
from bs4 import BeautifulSoup


def get_sight_href(num_pages, item_per_page=30):
    query_url = 'https://www.tripadvisor.co.uk/Attractions-g32655-Activities-oa{}-Los_Angeles_California.html'
    base_url = 'https://www.tripadvisor.co.uk'
    sights = []
    for i in range(num_pages):
        url = query_url.format(i * item_per_page)
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')
        for section in soup.find_all(name='section', attrs={'class': 'jemSU'}):
            span = section.find(name='span', attrs={'name': 'title'})
            a = section.find(name='a', attrs={'target': '_blank'})
            if span is not None:
                name = span.get_text()
                if 'href' in a.attrs:
                    href = a.attrs['href']
                    sights.append({'name': name, 'href': base_url + href})
    return sights


def get_detailed_info(sights):
    for sight in sights:
        response = requests.get(sight['href'], headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')
        for div in soup.find(name='div', attrs={'class': 'bVvJm'}):
            pass


sights = get_sight_href(20)