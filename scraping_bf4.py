from urllib.parse import urljoin
from bs4 import BeautifulSoup
with open('dp.html') as f:
    soup = BeautifulSoup(f, 'html.parser')

for a in soup.select('#listBook > li > a[itemprop="url"]'):
    url = urljoin('https://gihyo.jp/dp', a.get('href'))
    p = a.select('p[itemprop="name"]')[0]
    title = p.text

    print(url, title)