import requests
from bs4 import BeautifulSoup as bs
from parsel import Selector

# Подключить бд.

urls = [
    "https://animejoy.ru/tv-serialy/2891-vremya-nindzya.html",
    "http://rutor.info/torrent/890745/nadvoe-01-02-iz-09-2022-web-dl-1080p",
]


class UrlTest:
    def url_is_valid(urls):
        for url in urls:
            r = requests.get(url)
            r_ok = r.ok
            return r_ok


class Parser:
    def animejoy_parse(urls):
        for url in urls:
            r = requests.get(url)
            soup = bs(r.text, "html.parser")
            if "animejoy" in url:
                blocks = soup.find_all("div", class_="titleup")
                for block in blocks:
                    animejoy_title = block.find("h1", class_="h2 ntitle").get_text()
                    if animejoy_title not in "":
                        return animejoy_title

    def rutor_parse(urls):

        for url in urls:
            r = requests.get(url)
            soup = bs(r.text, "html.parser")
            text_s = requests.get(url).text
            sel = Selector(text=text_s)
            if "rutor" in url:
                rutor_title = soup.find("h1").get_text()
                rutor_year = sel.xpath(
                    '//b[starts-with(text(),"Год выхода")]/following-sibling::text()'
                ).get()
                if rutor_title not in "":
                    return rutor_title, rutor_year


if __name__ == "__main__":
    print(Parser.animejoy_parse(urls))
    print(Parser.rutor_parse(urls))
    UrlTest.url_is_valid(urls)
