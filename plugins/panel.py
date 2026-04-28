
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot import Bot
from config import OWNER_ID, ANIME_BANNERS
from database.database import db
import random

def get_panel_markup(settings):
    def get_status(key):
        return "🟢 Oɴ" if settings.get(key, True) else "🔴 Oғғ"

    def get_badge(key):
        return "✅" if settings.get(key, True) else "❌"

    buttons = [
        [
            InlineKeyboardButton(f"ꜱʜᴏʀᴛᴇɴᴇʀ ꜱʏꜱᴛᴇᴍ {get_badge('shortener_system')}", callback_data="none"),
            InlineKeyboardButton(get_status("shortener_system"), callback_data="tg_shortener_system")
        ],
        [
            InlineKeyboardButton(f"ꜰɪʟᴇ ᴅᴇʟɪᴠᴇʀʏ {get_badge('file_delivery')}", callback_data="none"),
            InlineKeyboardButton(get_status("file_delivery"), callback_data="tg_file_delivery")
        ],
        [
            InlineKeyboardButton(f"ᴄᴏʀᴇ ꜰᴇᴀᴛᴜʀᴇꜱ {get_badge('core_features')}", callback_data="none"),
            InlineKeyboardButton(get_status("core_features"), callback_data="tg_core_features")
        ],
        [
            InlineKeyboardButton("✨ Sʏsᴛᴇᴍ Rᴇғʀᴇsʜ ✨", callback_data="refresh_panel")
        ],
        [
            InlineKeyboardButton("🗑️ Cʟᴏsᴇ Pᴀɴᴇʟ 🗑️", callback_data="close")
        ]
    ]
    return InlineKeyboardMarkup(buttons)

@Bot.on_message(filters.command(['panel', 'settings']) & filters.private & filters.user(OWNER_ID))
async def owner_panel(client: Bot, message: Message):
    settings = await db.get_settings()

    caption = (
        "━━━━━━━━━━━━━━━━━━━\n"
        "🛠️ <b>OTAKULUX OWNER DASHBOARD</b> 🛠️\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "Wᴇʟᴄᴏᴍᴇ, Kɪɴɢ! Mᴀɴᴀɢᴇ ʏᴏᴜʀ ʙᴏᴛ's ᴄᴏʀᴇ sᴇᴛᴛɪɴɢs ᴡɪᴛʜ ʀᴇᴀʟ-ᴛɪᴍᴇ ᴜᴘᴅᴀᴛᴇs.\n\n"
        "📊 <b>Sʏsᴛᴇᴍ Sᴛᴀᴛᴜs:</b>\n"
        f"• Sʜᴏʀᴛᴇɴᴇʀ: {'Aᴄᴛɪᴠᴇ ⚡' if settings.get('shortener_system', True) else 'Dɪsᴀʙʟᴇᴅ 💤'}\n"
        f"• Dᴇʟɪᴠᴇʀʏ: {'Sᴛᴀʙʟᴇ ✅' if settings.get('file_delivery', True) else 'Pᴀᴜsᴇᴅ ⚠️'}\n"
        f"• Cᴏʀᴇ: {'Hᴇᴀʟᴛʜʏ ✨' if settings.get('core_features', True) else 'Mᴀɪɴᴛᴇɴᴀɴᴄᴇ 🛠️'}\n"
        "━━━━━━━━━━━━━━━━━━━"
    )

    await message.reply_photo(
        photo=random.choice(ANIME_BANNERS),
        caption=caption,
        reply_markup=get_panel_markup(settings)
    )

@Bot.on_callback_query(filters.regex(r"^(tg_|refresh_panel)"))
async def panel_callback(client: Bot, query: CallbackQuery):
    if query.from_user.id != OWNER_ID:
        return await query.answer("Access Denied, Mortal!", show_alert=True)

    data = query.data
    settings = await db.get_settings()

    if data == "refresh_panel":
        await query.answer("Refreshing dashboard...", show_alert=False)
    else:
        key = data.replace("tg_", "")
        new_val = not settings.get(key, True)
        await db.update_setting(key, new_val)
        settings[key] = new_val
        await query.answer(f"{key.replace('_', ' ').title()} {'Enabled' if new_val else 'Disabled'}")

    caption = (
        "━━━━━━━━━━━━━━━━━━━\n"
        "🛠️ <b>OTAKULUX OWNER DASHBOARD</b> 🛠️\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "Wᴇʟᴄᴏᴍᴇ, Kɪɴɢ! Mᴀɴᴀɢᴇ ʏᴏᴜʀ ʙᴏᴛ's ᴄᴏʀᴇ sᴇᴛᴛɪɴɢs ᴡɪᴛʜ ʀᴇᴀʟ-ᴛɪᴍᴇ ᴜᴘᴅᴀᴛᴇs.\n\n"
        "📊 <b>Sʏsᴛᴇᴍ Sᴛᴀᴛᴜs:</b>\n"
        f"• Sʜᴏʀᴛᴇɴᴇʀ: {'Aᴄᴛɪᴠᴇ ⚡' if settings.get('shortener_system', True) else 'Dɪsᴀʙʟᴇᴅ 💤'}\n"
        f"• Dᴇʟɪᴠᴇʀʏ: {'Sᴛᴀʙʟᴇ ✅' if settings.get('file_delivery', True) else 'Pᴀᴜsᴇᴅ ⚠️'}\n"
        f"• Cᴏʀᴇ: {'Hᴇᴀʟᴛʜʏ ✨' if settings.get('core_features', True) else 'Mᴀɪɴᴛᴇɴᴀɴᴄᴇ 🛠️'}\n"
        "━━━━━━━━━━━━━━━━━━━"
    )

    try:
        await query.message.edit_caption(
            caption=caption,
            reply_markup=get_panel_markup(settings)
        )
    except:
        pass
