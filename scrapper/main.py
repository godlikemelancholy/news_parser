import asyncio
from scrapper.sources.rbk import scrape_rbk
from scrapper.sources.cnbc import scrape_cnbc
from scrapper.sources.kommersant import scrape_kommersant
from scrapper.sources.guardian import scrape_guardian


async def main():
    while True:
        print("Сбор данных с РБК...")
        scrape_rbk()

        print("Сбор данных с CNBC...")
        scrape_cnbc()

        print("Сбор данных с Коммерсанта...")
        scrape_kommersant()

        print("Сбор данных с The Guardian...")
        scrape_guardian()

        print("Ожидание 1 час перед следующим запуском...")
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
