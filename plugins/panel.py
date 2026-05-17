
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import OWNER_ID, ANIME_BANNERS
from database.database import db
from helper_func import admin
import random

def get_panel_markup(settings):
    def get_status(key):
        return "🟢 Oɴ" if settings.get(key, True) else "🔴 Oғғ"

    def get_badge(key):
        return "✅" if settings.get(key, True) else "❌"

    buttons = [
        [
            InlineKeyboardButton(f"ᴠᴇʀɪꜰʏ ꜱʏꜱᴛᴇᴍ {get_badge('shortener_system')}", callback_data="none"),
            InlineKeyboardButton(get_status("shortener_system"), callback_data="tg_shortener_system")
        ],
        [
            InlineKeyboardButton(f"ꜱʜᴏʀᴛᴇɴ ᴀᴅᴍɪɴꜱ {get_badge('shorten_admins')}", callback_data="none"),
            InlineKeyboardButton(get_status("shorten_admins"), callback_data="tg_shorten_admins")
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

@Client.on_message(filters.command(['panel', 'settings']) & filters.private & filters.user(OWNER_ID))
async def owner_panel(client: Client, message: Message):
    settings = await db.get_settings()

    caption = (
        "━━━━━━━━━━━━━━━━━━━\n"
        "🛠️ <b>˹ ᴀɴɪᴢᴏɴᴇꜰʟɪx ᴄᴏʀᴇ ᴄᴏɴᴛʀᴏʟ ˼</b> 🛠️\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "👑 ᴡᴇʟᴄᴏᴍᴇ, ᴋɪɴɢ! ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ʙᴏᴛ's ᴄᴏʀᴇ ᴀssᴇᴛs ᴡɪᴛʜ ʀᴇᴀʟ-ᴛɪᴍᴇ ᴜᴘᴅᴀᴛᴇs.\n\n"
        "📊 <b>sʏsᴛᴇᴍ sᴛᴀᴛᴜs:</b>\n"
        f"• ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ: {'ᴀᴄᴛɪᴠᴇ ⚡' if settings.get('shortener_system', True) else 'ᴅɪsᴀʙʟᴇᴅ 💤'}\n"
        f"• ᴅᴇʟɪᴠᴇʀʏ: {'sᴛᴀʙʟᴇ ✅' if settings.get('file_delivery', True) else 'ᴘᴀᴜsᴇᴅ ⚠️'}\n"
        f"• ᴄᴏʀᴇ: {'ʜᴇᴀʟᴛʜʏ ✨' if settings.get('core_features', True) else 'ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ 🛠️'}\n"
        "━━━━━━━━━━━━━━━━━━━"
    )

    await message.reply_photo(
        photo=random.choice(ANIME_BANNERS),
        caption=caption,
        reply_markup=get_panel_markup(settings)
    )

@Client.on_callback_query(filters.regex(r"^(tg_|refresh_panel)"))
async def panel_callback(client: Client, query: CallbackQuery):
    if query.from_user.id != OWNER_ID:
        return await query.answer("˹ ᴀᴄᴄᴇss ᴅᴇɴɪᴇᴅ, ᴍᴏʀᴛᴀʟ! ˼", show_alert=True)

    data = query.data

    if data == "refresh_panel":
        await query.answer("˹ ʀᴇꜰʀᴇsʜɪɴɢ ᴅᴀsʜʙᴏᴀʀᴅ... ˼", show_alert=False)
    elif data.startswith("tg_"):
        settings = await db.get_settings()
        key = data.replace("tg_", "")
        new_val = not settings.get(key, True)
        await db.update_setting(key, new_val)
        await query.answer(f"˹ {key.replace('_', ' ').title()} {'ᴇɴᴀʙʟᴇᴅ' if new_val else 'ᴅɪsᴀʙʟᴇᴅ'} ˼")

    # Fetch fresh settings for UI update
    settings = await db.get_settings()

    caption = (
        "━━━━━━━━━━━━━━━━━━━\n"
        "🛠️ <b>˹ ᴀɴɪᴢᴏɴᴇꜰʟɪx ᴄᴏʀᴇ ᴄᴏɴᴛʀᴏʟ ˼</b> 🛠️\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "👑 ᴡᴇʟᴄᴏᴍᴇ, ᴋɪɴɢ! ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ʙᴏᴛ's ᴄᴏʀᴇ ᴀssᴇᴛs ᴡɪᴛʜ ʀᴇᴀʟ-ᴛɪᴍᴇ ᴜᴘᴅᴀᴛᴇs.\n\n"
        "📊 <b>sʏsᴛᴇᴍ sᴛᴀᴛᴜs:</b>\n"
        f"• sʜᴏʀᴛᴇɴᴇʀ: {'ᴀᴄᴛɪᴠᴇ ⚡' if settings.get('shortener_system', True) else 'ᴅɪsᴀʙʟᴇᴅ 💤'}\n"
        f"• ᴅᴇʟɪᴠᴇʀʏ: {'sᴛᴀʙʟᴇ ✅' if settings.get('file_delivery', True) else 'ᴘᴀᴜsᴇᴅ ⚠️'}\n"
        f"• ᴄᴏʀᴇ: {'ʜᴇᴀʟᴛʜʏ ✨' if settings.get('core_features', True) else 'ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ 🛠️'}\n"
        "━━━━━━━━━━━━━━━━━━━"
    )

    try:
        await query.message.edit_caption(
            caption=caption,
            reply_markup=get_panel_markup(settings)
        )
    except Exception as e:
        print(f"[PANEL ERROR] {e}")
