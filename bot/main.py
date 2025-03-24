import asyncio
from aiogram import Bot, Dispatcher
from src.services.news_sender import news_listener
from src.handlers import users
from config import bot_token
from src.data.database import DB


async def main():
    bot = Bot(token=bot_token)
    dp = Dispatcher(bot=bot)

    db = DB()

    dp.include_routers(users.router)

    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(news_listener())

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())