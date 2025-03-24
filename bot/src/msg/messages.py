from bot.src.msg.text import Text
from bot.src.data.database import DB
from config import bot_token
import bot.src.msg.keyboards as k

from aiogram import Bot
from aiogram.types import Message


db = DB()
bot = Bot(token=bot_token)


async def main_label(chat_id):
    await bot.send_message(
        chat_id=chat_id,
        text=Text.greetings,
        parse_mode="Markdown"
    )


async def change_default_source_label(chat_id):
    await bot.send_message(
        chat_id=chat_id,
        text=Text.change_default_source,
        reply_markup=k.change_default_source_kb(user_id=chat_id),
        parse_mode="Markdown"
    )


async def change_subscriptions(chat_id):
    await bot.send_message(
        chat_id=chat_id,
        text=Text.change_subscriptions,
        reply_markup=k.subscriptions_kb(user_id=chat_id),
        parse_mode="Markdown"
    )


async def subscribe_to_all_news(chat_id):
    if db.is_user_subscribed(user_id=chat_id):
        db.unsubscribe(user_id=chat_id)
        await bot.send_message(chat_id=chat_id, text=Text.unsubscribe_success)
    else:
        db.subscribe(user_id=chat_id)
        await bot.send_message(chat_id=chat_id, text=Text.subscribe_success)


async def send_news(chat_id, message: Message):
    user_id = message.from_user.id
    args = message.text.split(" ", 1)

    if len(args) == 1:
        news = db.get_news(user_id)
    else:
        source_name = args[1]
        news = db.get_news_by_target(source_name)

    if not news:
        await message.answer("🚫 Новости не найдены.")
        return

    for title, link, published_at, source_name in news:
        text = Text.news_text.format(title=title, link=link,  source=source_name)
        await bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")


async def automated_news(chat_id):
    news = db.get_unsent_news_for_user(chat_id)

    if not news:
        return

    for news_id, title, link, source_name in news:
        text = Text.news_text.format(title=title, link=link, source=source_name)

        try:
            await bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
            db.mark_news_as_sent_for_user(chat_id, news_id)
        except Exception as e:
            print(e)