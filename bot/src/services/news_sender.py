import asyncio
from aiogram import Bot
from bot.src.data.database import DB
from config import bot_token
import bot.src.msg.messages as m


db = DB()
bot = Bot(token=bot_token)


async def news_listener():
    while True:
        await asyncio.sleep(3000)
        users = db.get_subscribed_users()

        if not users:
            continue

        for user_id in users:
            await m.automated_news(chat_id=user_id)


