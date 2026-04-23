# Don't Remove Credit @OTAKULUX, @OTAKULUX
# Ask Doubt on telegram @OTAKULUX
#
# Copyright (C) 2025 by OTAKULUX@OTAKULUX, < https://github.com/OTAKULUX >.
#
# This file is part of < https://t.me/OTAKULUX > project,
# and is released under the MIT License.
# Please see < https://t.me/OTAKULUX/blob/master/LICENSE >
#
# All rights reserved.
#

import asyncio
from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from bot import Bot
from database.database import db
from helper_func import encode, get_message_id, get_messages, parse_media_metadata, fetch_anilist_data, admin
import string
import re

@Bot.on_message(filters.command("index") & filters.private & admin)
async def index_command(client: Client, message: Message):
    # Interactive flow for indexing existing files
    try:
        first_msg = await client.ask(message.chat.id, "🔗 Send the <b>First Message Link</b> from DB Channel:", timeout=60)
        start_id = await get_message_id(client, first_msg)
        if not start_id:
            return await message.reply("❌ Invalid link or message not from DB channel.")

        count_msg = await client.ask(message.chat.id, "🔢 How many messages to index?", timeout=60)
        num_messages = int(count_msg.text)

    except Exception as e:
        return await message.reply(f"❌ Error: {e}")

    progress = await message.reply(f"🔍 Starting indexing 0/{num_messages}...")

    indexed_count = 0
    current_id = start_id

    while indexed_count < num_messages:
        to_fetch = list(range(current_id, current_id + 50))
        try:
            msgs = await get_messages(client, to_fetch)
            if not msgs: break

            for m in msgs:
                if m and (m.video or m.document):
                    media = m.video or m.document
                    text = m.caption or getattr(media, "file_name", "")

                    metadata = parse_media_metadata(text)
                    anilist = await fetch_anilist_data(metadata["anime_name"])
                    metadata["anilist"] = anilist
                    metadata["search_name"] = metadata["anime_name"].lower()

                    await db.save_anime_metadata(m.id, metadata)
                    indexed_count += 1

                    if indexed_count == num_messages: break
                    if indexed_count % 5 == 0:
                        await progress.edit(f"🔍 Indexed {indexed_count}/{num_messages}...")

                current_id = m.id + 1

            if current_id > start_id + num_messages + 1000: break # Safety break

        except Exception as e:
            print(f"Index error: {e}")
            break

    await progress.edit(f"✅ Successfully indexed {indexed_count} files!")

@Bot.on_message(filters.command("browse") & filters.private)
async def browse_handler(client: Client, message: Message):
    buttons = []
    # Generate A-Z buttons
    alphabet = list(string.ascii_uppercase)

    # 4 buttons per row
    for i in range(0, len(alphabet), 4):
        row = [InlineKeyboardButton(char, callback_data=f"idx_{char}") for char in alphabet[i:i+4]]
        buttons.append(row)

    # Add # for numbers
    buttons.append([InlineKeyboardButton("#", callback_data="idx_#")])

    await message.reply_text(
        "<b>📂 Anime Index</b>\n\nSelect a letter to browse anime titles:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Bot.on_callback_query(filters.regex(r"^idx_"))
async def index_callback(client: Client, query: CallbackQuery):
    char = query.data.split("_")[1]
    results = await db.get_anime_by_letter(char)

    if not results:
        await query.answer(f"No anime found starting with {char}", show_alert=True)
        return

    buttons = []
    # Group by anime name to avoid duplicates if multiple episodes exist
    unique_anime = {}
    for res in results:
        name = res['anime_name']
        if name not in unique_anime:
            unique_anime[name] = res['_id']

    for name, msg_id in unique_anime.items():
        converted_id = msg_id * abs(client.db_channel.id)
        base64_string = await encode(f"get-{converted_id}")
        link = f"https://t.me/{client.username}?start={base64_string}"
        buttons.append([InlineKeyboardButton(name, url=link)])

    buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="back_to_index")])

    await query.message.edit_text(
        f"<b>📂 Anime starting with {char}</b>",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Bot.on_callback_query(filters.regex("back_to_index"))
async def back_to_index(client: Client, query: CallbackQuery):
    buttons = []
    alphabet = list(string.ascii_uppercase)
    for i in range(0, len(alphabet), 4):
        row = [InlineKeyboardButton(char, callback_data=f"idx_{char}") for char in alphabet[i:i+4]]
        buttons.append(row)
    buttons.append([InlineKeyboardButton("#", callback_data="idx_#")])

    await query.message.edit_text(
        "<b>📂 Anime Index</b>\n\nSelect a letter to browse anime titles:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
