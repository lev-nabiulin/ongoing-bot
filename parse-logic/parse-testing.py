import requests
from bs4 import BeautifulSoup as bs

# Подключить бд.
# Нужно бахнуть по ООП, с классами и всей херней.


urls = [
    "https://animejoy.ru/tv-serialy/2891-vremya-nindzya.html",
    "http://rutor.info/torrent/890745/nadvoe-01-02-iz-09-2022-web-dl-1080p",
]

for url in urls:
    r = requests.get(url)
    soup = bs(r.text, "html.parser")
    if "animejoy" in url:
        blocks = soup.find_all("div", class_="titleup")
        for block in blocks:
            title = block.find("h1", class_="h2 ntitle").get_text()
            print(title)

    if "rutor" in url:
        name = soup.find("h1").get_text()
        print(name)
