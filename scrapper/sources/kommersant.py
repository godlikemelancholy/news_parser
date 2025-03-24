import requests
from bs4 import BeautifulSoup
from datetime import datetime
from scrapper.db.database import DB

db = DB()


def scrape_kommersant():
    url = "https://www.kommersant.ru/"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url=url, headers=headers)
    if response.status_code != 200:
        return "Ошибка получения данных с kommersant."
    else:
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "html.parser")

        news = []
        for link in soup.find_all("a", class_="uho__link")[:25]:
            title = link.text.strip()
            href = url + link["href"]
            added_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            news.append((title, href, added_at))

        db.add_news(news, "Kommersant")