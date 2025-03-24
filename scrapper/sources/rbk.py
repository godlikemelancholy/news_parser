import requests
from bs4 import BeautifulSoup
from datetime import datetime
from scrapper.db.database import DB

db = DB()


def scrape_rbk():
    URL = "https://www.rbc.ru/"
    HEADERS = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(URL, headers=HEADERS)
    if response.status_code != 200:
        return "Ошибка получения данных с rbk."
    else:
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "html.parser")

        news = []
        for item in soup.find_all("a", class_="news-feed__item")[:10]:
            title_element = item.find("span", class_="news-feed__item__title")
            if title_element:
                title = title_element.text.strip()
                href = item["href"]
                added_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                news.append((title, href, added_at))

        db.add_news(news, "RBK")