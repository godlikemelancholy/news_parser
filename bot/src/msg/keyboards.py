from aiogram import types

from bot.src.data.database import DB

db = DB()


def change_default_source_kb(user_id):
    sources = db.get_all_sources()
    default_source = db.get_default_source(user_id)

    buttons = []
    for s in sources:
        emoji = "✅" if s[1] == default_source else ""
        buttons.append([
            types.InlineKeyboardButton(
                text=f"{emoji} {s[1]}",
                callback_data=f"selected_source_{s[1]}"
            )
        ])
    buttons.append([
        types.InlineKeyboardButton(text="❌ Сбросить источник", callback_data="reset_source")
    ])

    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def subscriptions_kb(user_id):
    sources = db.get_all_sources()
    user_subscriptions = db.get_user_subscriptions(user_id)
    subscribed_sources = {s[0] for s in user_subscriptions}

    buttons = []
    for s in sources:
        emoji = "✅" if s[0] in subscribed_sources else ""
        buttons.append([
            types.InlineKeyboardButton(
                text=f"{emoji} {s[1]}",
                callback_data=f"toggle_subscription_{s[0]}"
            )
        ])

    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

