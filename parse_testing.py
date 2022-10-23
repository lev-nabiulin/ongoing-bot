from xml.dom.minidom import ReadOnlySequentialNamedNodeMap
import requests
from bs4 import BeautifulSoup as bs
from parsel import Selector

import db.sqlite_connector as sqlite_connector

# TODO:
# попробовать достать серию с помощью regex
# че такое BLOB? !!!
# --->  <---
# Достать:
# name_lat
# картинки BLOB


# def new_series(list):
#    list = [1, 2, 3, 4, 5, 6, 7, 8]
#    dict = {1: 3, 2: 5, 3: 4, 4: 1, 5: 8, 6: 24, 7: 15, 8: 2}
#    return dict

urls = sqlite_connector.get_title_urls()

class UrlTest:
    def url_is_valid(urls):
        for url in urls:
            url = url[0]
            r = requests.get(url)
            r_ok = r.ok
            return r_ok


class Parser:
    def animejoy_parse(urls):
        names_rus = []
        release_years = []

        for url in urls:
            url = url[0]
            
            text_s = requests.get(url).text
            sel = Selector(text=text_s)
            if "animejoy" in url:
                animejoy_year = sel.xpath(
                    '//span[starts-with(text(),"Дата выпуска")]/following-sibling::text()'
                ).get()
                release_year = animejoy_year.replace(u"\xa0c ", u"")
                name_rus = sel.xpath(
                    '//h1[@itemprop = "name"]/text()'
                ).get()
                names_rus.append(name_rus)
                release_years.append(release_year)
        return names_rus, release_years

    def rutor_parse(urls):
        names_rus = []
        release_years = []

        for url in urls:
            url = url[0]
            text_s = requests.get(url).text
            sel = Selector(text=text_s)

            if "rutor" in url:
                rutor_title = sel.xpath(
                    '//b[starts-with(text(),"Название")]/following-sibling::text()'
                ).get()
                rutor_year = sel.xpath(
                    '//b[starts-with(text(),"Год")]/following-sibling::text()'
                ).get()
                rutor_year = rutor_year.replace(u" ", u"")
                if rutor_title not in "":
                    names_rus.append(rutor_title)
                    release_years.append(rutor_year)
        return names_rus, release_years


if __name__ == "__main__":
    print(Parser.animejoy_parse(urls))
    print(Parser.rutor_parse(urls))
