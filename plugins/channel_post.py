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
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from bot import Bot
from config import *
from helper_func import encode, admin, fetch_anilist_data
from database.database import db

@Bot.on_message(filters.private & admin & ~filters.command(['start', 'commands','users','broadcast','batch', 'custom_batch', 'genlink','stats', 'dlt_time', 'check_dlt_time', 'auto_delete', 'check_auto_delete', 'autodelete', 'checkautodelete', 'dbroadcast', 'ban', 'unban', 'banlist', 'addchnl', 'delchnl', 'listchnl', 'fsub_mode', 'pbroadcast', 'add_admin', 'deladmin', 'admins', 'addpremium', 'premium_users', 'remove_premium', 'myplan', 'count', 'delreq']))
async def channel_post(client: Client, message: Message):
    # Metadata Collection
    try:
        anime_name_msg = await client.ask(message.chat.id, "🎬 Enter Anime Name:", timeout=60)
        anime_name = anime_name_msg.text

        season_msg = await client.ask(message.chat.id, "📅 Enter Season (e.g. 1):", timeout=60)
        season = season_msg.text

        episode_msg = await client.ask(message.chat.id, "🔢 Enter Episode Number:", timeout=60)
        episode = episode_msg.text

        quality_msg = await client.ask(message.chat.id, "💎 Enter Quality (e.g. 1080p):", timeout=60)
        quality = quality_msg.text

    except Exception as e:
        await message.reply_text(f"Metadata collection failed or timed out: {e}")
        return

    reply_text = await message.reply_text("Processing and Fetching Metadata...!", quote = True)

    # Fetch External Metadata
    anilist_metadata = await fetch_anilist_data(anime_name)

    try:
        post_message = await message.copy(chat_id = client.db_channel.id, disable_notification=True)
    except FloodWait as e:
        await asyncio.sleep(e.x)
        post_message = await message.copy(chat_id = client.db_channel.id, disable_notification=True)
    except Exception as e:
        print(e)
        await reply_text.edit_text("Something went Wrong..!")
        return
    converted_id = post_message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])

    # Save Metadata to DB
    metadata = {
        "anime_name": anime_name,
        "season": season,
        "episode": episode,
        "quality": quality,
        "anilist": anilist_metadata,
        "search_name": anime_name.lower()
    }
    await db.save_anime_metadata(post_message.id, metadata)

    await reply_text.edit(f"<b>Here is your link</b>\n\n{link}", reply_markup=reply_markup, disable_web_page_preview = True)

    if not DISABLE_CHANNEL_BUTTON:
        await post_message.edit_reply_markup(reply_markup)

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
