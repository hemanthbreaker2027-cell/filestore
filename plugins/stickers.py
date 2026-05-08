
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import OWNER_ID
from database.database import db
from helper_func import admin
import asyncio

@Bot.on_message(filters.command('sticker') & filters.private & admin)
async def setup_stickers(client: Bot, message: Message):
    try:
        ask_count = await client.ask(message.chat.id, "<b>How many names you want to setup?</b>", filters=filters.text, timeout=60)
        count = int(ask_count.text)
    except Exception:
        return await message.reply("❌ Invalid input or timeout.")

    for i in range(1, count + 1):
        try:
            # Get Name
            ask_name = await client.ask(message.chat.id, f"<b>Enter Name #{i}:</b>", filters=filters.text, timeout=60)
            keyword = ask_name.text.strip()

            # Get Sticker
            ask_sticker = await client.ask(message.chat.id, f"<b>Send Sticker for '{keyword}':</b>", filters=filters.sticker, timeout=60)
            sticker_id = ask_sticker.sticker.file_id

            # Save
            await db.add_sticker_mapping(keyword, sticker_id, message.from_user.id)
            await message.reply(f"✅ Setup complete for: <code>{keyword}</code>")

        except Exception as e:
            await message.reply(f"❌ Error during setup: {e}")
            break

    await message.reply("<b>✨ All stickers configured successfully!</b>")

@Bot.on_message(filters.command('liststickers') & filters.private & admin)
async def list_stickers(client: Bot, message: Message):
    stickers = await db.get_all_stickers()
    if not stickers:
        return await message.reply("<b>No stickers configured.</b>")

    text = "<b>📊 Saved Sticker Mappings:</b>\n\n"
    for keyword in stickers:
        text += f"• <code>{keyword}</code>\n"

    await message.reply(text)

@Bot.on_message(filters.command('removesticker') & filters.private & admin)
async def remove_sticker(client: Bot, message: Message):
    if len(message.command) < 2:
        return await message.reply("<b>Usage: /removesticker <keyword></b>")

    keyword = message.text.split(" ", 1)[1].strip()
    await db.remove_sticker_mapping(keyword)
    await message.reply(f"<b>✅ Removed sticker mapping for:</b> <code>{keyword}</code>")
