import requests
from bs4 import BeautifulSoup
from datetime import datetime
from scrapper.db.database import DB

db = DB()


def scrape_cnbc():
    url = "https://www.cnbc.com/world/"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return "Ошибка получения данных с cnbc."
    else:
        soup = BeautifulSoup(response.text, "html.parser")
        news = []
        for link in soup.find_all("a", class_="LatestNews-headline")[:10]:
            title = link.text.strip()
            href = link["href"]
            added_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            news.append((title, href, added_at))

        db.add_news(news, "CNBC")

