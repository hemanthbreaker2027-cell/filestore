
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot import Bot
from config import OWNER_ID, ANIME_BANNERS
from database.database import db
from helper_func import admin
import random

def get_panel_markup(settings):
    def get_status(key):
        return "🟢 Oɴ" if settings.get(key, True) else "🔴 Oғғ"

    def get_badge(key):
        return "✅" if settings.get(key, True) else "❌"

    mode = settings.get('shortener_mode', 'one_per_time')

    buttons = [
        [
            InlineKeyboardButton(f"ꜱʜᴏʀᴛᴇɴᴇʀ ꜱʏꜱᴛᴇᴍ {get_badge('shortener_system')}", callback_data="none"),
            InlineKeyboardButton(get_status("shortener_system"), callback_data="tg_shortener_system")
        ],
        [
            InlineKeyboardButton("ONE PER TIME" + (" ✅" if mode == 'one_per_time' else ""), callback_data="set_mode_one"),
            InlineKeyboardButton("BASED TIME" + (" ✅" if mode == 'based_time' else ""), callback_data="set_mode_time")
        ],
        [
            InlineKeyboardButton(f"⏱️ Tɪᴍᴇʀ: {settings.get('verify_timer')}s", callback_data="set_val_verify_timer"),
            InlineKeyboardButton(f"⏳ Exᴘɪʀʏ: {settings.get('session_expiry')}s", callback_data="set_val_session_expiry")
        ],
        [
            InlineKeyboardButton(f"🌐 Wᴇʙsɪᴛᴇ", callback_data="set_val_website_url"),
            InlineKeyboardButton(f"🔗 Dᴏᴍᴀɪɴ", callback_data="set_val_shortener_domain")
        ],
        [
            InlineKeyboardButton(f"📁 WRAP URL", callback_data="set_val_wrap_url")
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
        f"• sʜᴏʀᴛᴇɴᴇʀ: {'ᴀᴄᴛɪᴠᴇ ⚡' if settings.get('shortener_system', True) else 'ᴅɪsᴀʙʟᴇᴅ 💤'}\n"
        f"• ᴅᴇʟɪᴠᴇʀʏ: {'sᴛᴀʙʟᴇ ✅' if settings.get('file_delivery', True) else 'ᴘᴀᴜsᴇᴅ ⚠️'}\n"
        f"• ᴄᴏʀᴇ: {'ʜᴇᴀʟᴛʜʏ ✨' if settings.get('core_features', True) else 'ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ 🛠️'}\n"
        "━━━━━━━━━━━━━━━━━━━"
    )

    await message.reply_photo(
        photo=random.choice(ANIME_BANNERS),
        caption=caption,
        reply_markup=get_panel_markup(settings)
    )

@Client.on_callback_query(filters.regex(r"^(tg_|refresh_panel|set_mode_|set_val_)"))
async def panel_callback(client: Client, query: CallbackQuery):
    if query.from_user.id != OWNER_ID:
        return await query.answer("˹ ᴀᴄᴄᴇss ᴅᴇɴɪᴇᴅ, ᴍᴏʀᴛᴀʟ! ˼", show_alert=True)

    data = query.data

    if data == "refresh_panel":
        await query.answer("˹ ʀᴇꜰʀᴇsʜɪɴɢ ᴅᴀsʜʙᴏᴀʀᴅ... ˼", show_alert=False)
    elif data == "set_mode_one":
        await db.update_setting('shortener_mode', 'one_per_time')
        await query.answer("Mode set to: ONE PER TIME")
    elif data == "set_mode_time":
        await query.answer()
        msg = await client.ask(query.message.chat.id, "<b>🛡 ˹ ᴀᴄᴛɪᴠᴀᴛᴇ ʙᴀsᴇᴅ ᴛɪᴍᴇ ᴍᴏᴅᴇ ˼</b>\n\n💎 ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴛʜᴇ ᴠᴀʟɪᴅɪᴛʏ ᴛɪᴍᴇ ɪɴ sᴇᴄᴏɴᴅs (ᴇ.ɢ. 3600 ꜰᴏʀ 1 ʜᴏᴜʀ):")
        try:
            val = int(msg.text)
            await db.update_setting('shortener_mode', 'based_time')
            await db.update_setting('shortener_time', val)
            await msg.reply(f"✅ ʙᴀsᴇᴅ ᴛɪᴍᴇ ᴍᴏᴅᴇ ᴀᴄᴛɪᴠᴀᴛᴇᴅ!\n🚀 Validity: `{val}` seconds.")
        except:
            await msg.reply("❌ Invalid number. Mode not changed.")
            return
    elif data.startswith("set_val_"):
        key = data.replace("set_val_", "")
        await query.answer()
        prompt = {
            'verify_timer': "Enter verification timer in seconds (e.g. 10):",
            'website_url': "Enter your deployment domain (e.g. your-app.onrender.com):",
            'shortener_domain': "Enter whitelist domain (e.g. arolinks.com):",
            'wrap_url': "Enter wrap URL template (e.g. https://darkguruji.com/universtiesstudiess/?studiessinsurancess=):",
            'session_expiry': "Enter JWT session expiry in seconds (e.g. 300):"
        }.get(key, "Enter new value:")

        msg = await client.ask(query.message.chat.id, f"<b>🛠 ˹ Sᴇᴛ {key.replace('_', ' ').upper()} ˼</b>\n\n💎 {prompt}")
        new_val = msg.text.strip()
        if key in ['verify_timer', 'session_expiry']:
            try: new_val = int(new_val)
            except:
                await msg.reply("❌ Invalid number.")
                return

        await db.update_setting(key, new_val)
        await msg.reply(f"✅ {key.replace('_', ' ').title()} updated to: `{new_val}`")
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

