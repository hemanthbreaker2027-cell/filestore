# Don't Remove Credit @AniZoneFlix, @AniZoneFlix
# Ask Doubt on telegram @AniZoneFlix
#
# Copyright (C) 2025 by AniZoneFlix@AniZoneFlix, < https://github.com/AniZoneFlix >.
#
# This file is part of < https://t.me/AniZoneFlix > project,
# and is released under the MIT License.
# Please see < https://t.me/AniZoneFlix/blob/master/LICENSE >
#
# All rights reserved.
#

import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from config import *
from helper_func import encode, admin

@Client.on_message(filters.private & admin & ~filters.command(['start', 'help', 'ping', 'commands','users','broadcast','batch', 'custom_batch', 'genlink','stats', 'dlt_time', 'check_dlt_time', 'auto_delete', 'check_auto_delete', 'autodelete', 'checkautodelete', 'dbroadcast', 'ban', 'unban', 'banlist', 'addchnl', 'delchnl', 'listchnl', 'fsub_mode', 'pbroadcast', 'add_admin', 'deladmin', 'admins', 'addpremium', 'premium_users', 'remove_premium', 'myplan', 'count', 'delreq']))
async def channel_post(client: Client, message: Message):
    reply_text = await message.reply_text("Please Wait...!", quote = True)
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

    share_button = [InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]

    # Preserve existing buttons
    buttons = []
    if message.reply_markup and message.reply_markup.inline_keyboard:
        buttons.extend(list(message.reply_markup.inline_keyboard))

    buttons.append(share_button)
    reply_markup = InlineKeyboardMarkup(buttons)

    await reply_text.edit(f"<b>Here is your link</b>\n\n{link}", reply_markup=reply_markup, disable_web_page_preview = True)

    if not DISABLE_CHANNEL_BUTTON:
        try:
            await post_message.edit_reply_markup(reply_markup)
        except Exception as e:
            print(f"Error editing post reply markup: {e}")

# Don't Remove Credit @AniZoneFlix, @AniZoneFlix
# Ask Doubt on telegram @AniZoneFlix
#
# Copyright (C) 2025 by AniZoneFlix@AniZoneFlix, < https://github.com/AniZoneFlix >.
#
# This file is part of < https://t.me/AniZoneFlix > project,
# and is released under the MIT License.
# Please see < https://t.me/AniZoneFlix/blob/master/LICENSE >
#
# All rights reserved.
#
