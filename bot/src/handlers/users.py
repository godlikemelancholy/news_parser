from bot.src.data.database import DB
import bot.src.msg.messages as m


from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import F, Router


db = DB()
router = Router()


class SettingsState(StatesGroup):
    waiting_for_news_limit = State()


@router.message(Command("start"))
async def start_command(message: Message):
    user_exists = db.check_user(user_id=message.from_user.id)

    if not user_exists:
        db.reg_user(message=message)

    await m.main_label(chat_id=message.from_user.id)


@router.message(Command("news"))
async def news_command(message: Message):
    await m.send_news(chat_id=message.from_user.id, message=message)


@router.message(Command("settings"))
async def settings_command(message: Message):
    await m.change_default_source_label(chat_id=message.from_user.id)


@router.callback_query(F.data.startswith("selected_source_"))
async def change_source_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    source_id = callback.data.split("_")[-1]
    user_id = callback.from_user.id

    db.change_default_source(source_id, user_id)

    await callback.message.answer("📩 Сколько заголовков новостей показывать за раз? (Введите число)")

    await state.set_state(SettingsState.waiting_for_news_limit)


@router.message(SettingsState.waiting_for_news_limit)
async def process_news_limit(message: Message, state: FSMContext):
    if message.text.isdigit():
        news_limit = int(message.text)

        if 1 <= news_limit <= 10:
            db.change_news_limit(message.from_user.id, news_limit)

            await message.answer(f"✅ Количество заголовков сохранено: {news_limit}")
            await m.change_default_source_label(chat_id=message.from_user.id)
            await state.clear()
        else:
            await message.answer("⚠ Введите число от 1 до 10!")
    else:
        await message.answer("❌ Пожалуйста, введите только число!")


@router.callback_query(F.data == "reset_source")
async def reset_default_source(callback: CallbackQuery):
    db.reset_default_source(user_id=callback.from_user.id)
    await callback.answer('Источник по умолчанию сброшен!')
    await m.change_default_source_label(chat_id=callback.from_user.id)


@router.message(Command("subscribe"))
async def news_command(message: Message):
    await m.subscribe_to_all_news(chat_id=message.from_user.id)


@router.message(Command("subscriptions"))
async def subscriptions_command(message: Message):
    await m.change_subscriptions(chat_id=message.from_user.id)


@router.callback_query(F.data.startswith("toggle_subscription_"))
async def toggle_subscription_callback(callback: CallbackQuery):
    source_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id

    if db.is_subscribed(user_id, source_id):
        db.remove_subscription(user_id, source_id)
        await callback.answer("❌ Подписка удалена!")
    else:
        db.add_subscription(user_id, source_id)
        await callback.answer("✅ Подписка оформлена!")

    await m.change_subscriptions(callback.message.chat.id)
