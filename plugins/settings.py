
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot import Bot
from config import OWNER_ID
from database.database import db

@Bot.on_message(filters.command(['panel', 'settings']) & filters.private & filters.user(OWNER_ID))
async def settings_panel(client: Bot, message: Message):
    settings = await db.get_settings()

    def get_status(key):
        return "🟢 Enabled" if settings.get(key, True) else "🔴 Disabled"

    buttons = [
        [
            InlineKeyboardButton(f"Shortener System: {get_status('shortener_system')}", callback_data="toggle_shortener_system")
        ],
        [
            InlineKeyboardButton(f"File Delivery: {get_status('file_delivery')}", callback_data="toggle_file_delivery")
        ],
        [
            InlineKeyboardButton(f"Core Features: {get_status('core_features')}", callback_data="toggle_core_features")
        ],
        [
            InlineKeyboardButton("❌ Close", callback_data="close")
        ]
    ]

    await message.reply(
        "<b>🛠️ Admin Settings Panel</b>\n\n"
        "Manage your bot's core features from here.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Bot.on_callback_query(filters.regex(r"^toggle_"))
async def toggle_setting(client: Bot, query: CallbackQuery):
    if query.from_user.id != OWNER_ID:
        return await query.answer("Access Denied!", show_alert=True)

    key = query.data.replace("toggle_", "")
    settings = await db.get_settings()
    current_val = settings.get(key, True)
    new_val = not current_val

    await db.update_setting(key, new_val)
    await query.answer(f"{key.replace('_', ' ').title()} set to {'Enabled' if new_val else 'Disabled'}")

    # Refresh Panel
    settings[key] = new_val # Local update for UI

    def get_status(k):
        return "🟢 Enabled" if settings.get(k, True) else "🔴 Disabled"

    buttons = [
        [
            InlineKeyboardButton(f"Shortener System: {get_status('shortener_system')}", callback_data="toggle_shortener_system")
        ],
        [
            InlineKeyboardButton(f"File Delivery: {get_status('file_delivery')}", callback_data="toggle_file_delivery")
        ],
        [
            InlineKeyboardButton(f"Core Features: {get_status('core_features')}", callback_data="toggle_core_features")
        ],
        [
            InlineKeyboardButton("❌ Close", callback_data="close")
        ]
    ]

    await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
