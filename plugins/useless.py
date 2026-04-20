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
import os
import random
import sys
import time
from datetime import datetime, timedelta
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode, ChatAction
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, ChatInviteLink, ChatPrivileges
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserNotParticipant
from bot import Bot
from config import *
from helper_func import *
from database.database import *

#=====================================================================================##

@Bot.on_message(filters.command('stats') & admin)
async def stats(bot: Bot, message: Message):
    now = datetime.now()
    delta = now - bot.uptime
    time = get_readable_time(delta.seconds)
    await message.reply(BOT_STATS_TEXT.format(uptime=time))


#=====================================================================================##

WAIT_MSG = "<b>Working....</b>"

#=====================================================================================##


@Bot.on_message(filters.command('users') & filters.private & admin)
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
    users = await db.full_userbase()
    await msg.edit(f"{len(users)} users are using this bot")

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

#=====================================================================================##

#AUTO-DELETE

@Bot.on_message(filters.private & filters.command(['dlt_time', 'auto_delete', 'autodelete']) & admin)
async def set_delete_time(client: Bot, message: Message):
    try:
        if len(message.command) < 2:
            return await message.reply("<b>⚠️ Usᴀɢᴇ:</b> <code>/auto_delete <seconds></code>")

        duration = int(message.command[1])
        await db.set_del_timer(duration)

        await message.reply(
            f"<b>✅ Dᴇʟᴇᴛᴇ Tɪᴍᴇʀ sᴇᴛ sᴜᴄᴄᴇssғᴜʟʟʏ!</b>\n\n"
            f"Fɪʟᴇs ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇᴅ ᴀғᴛᴇʀ <blockquote><b>{duration} sᴇᴄᴏɴᴅs.</b></blockquote>",
            quote=True
        )

    except ValueError:
        await message.reply("<b>❌ Eʀʀᴏʀ:</b> Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ ᴏғ sᴇᴄᴏɴᴅs.")

@Bot.on_message(filters.private & filters.command(['check_dlt_time', 'check_auto_delete', 'checkautodelete']) & admin)
async def check_delete_time(client: Bot, message: Message):
    duration = await db.get_del_timer()
    await message.reply(
        f"<b>🔍 Cᴜʀʀᴇɴᴛ Dᴇʟᴇᴛᴇ Tɪᴍᴇʀ:</b>\n\n"
        f"<blockquote><b>{duration} sᴇᴄᴏɴᴅs</b></blockquote>",
        quote=True
    )

#=====================================================================================##

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