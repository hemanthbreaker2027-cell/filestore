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
import re
import string 
import string
import time
from datetime import datetime, timedelta
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode, ChatAction
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, ChatInviteLink, ChatPrivileges
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserNotParticipant, MessageNotModified
from bot import Bot
from config import *
from helper_func import *
from database.database import *
from database.db_premium import *
from services.security import SecurityService


BAN_SUPPORT = f"{BAN_SUPPORT}"
TUT_VID = f"{TUT_VID}"

async def send_files(client: Client, message: Message, base64_string):
    user_id = message.from_user.id

    # We fetch settings here because send_files is called from multiple places
    # (start command, callback query) and might not always have settings passed.
    settings = await db.get_settings()

    if not settings.get('file_delivery', True) and user_id != OWNER_ID:
        return await message.reply_text("<b>⚠️ File delivery is currently disabled by the administrator.</b>")

    temp_msg = await message.reply_photo(
        photo=random.choice(ANIME_BANNERS),
        caption="━━━━━━━━━━━━━━━━━━━\n<b>🔍 Pʀᴏᴄᴇssɪɴɢ Yᴏᴜʀ Rᴇǫᴜᴇsᴛ...</b>\n━━━━━━━━━━━━━━━━━━━"
    )
    await asyncio.sleep(1)

    if not await is_subscribed(client, user_id):
        await temp_msg.delete()
        return await not_joined(client, message)

    try:
        string = await decode(base64_string)
        argument = string.split("-")

        ids = []
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
                ids = range(start, end + 1) if start <= end else list(range(start, end - 1, -1))
            except Exception as e:
                print(f"Error decoding IDs: {e}")
                return

        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except Exception as e:
                print(f"Error decoding ID: {e}")
                return

        try:
            messages = await get_messages(client, ids)
        except Exception as e:
            await message.reply_text("Something went wrong!")
            print(f"Error getting messages: {e}")
            return
        finally:
            try:
                await temp_msg.delete()
            except:
                pass

        OTAKULUX_msgs = []
        # File auto-delete time in seconds
        FILE_AUTO_DELETE = await db.get_del_timer()

        for msg in messages:
            original_caption = msg.caption.html if msg.caption else ""
            caption = f"{original_caption}\n\n{CUSTOM_CAPTION}" if CUSTOM_CAPTION else original_caption
            reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None

            try:
                snt_msg = await msg.copy(
                    chat_id=message.from_user.id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                    protect_content=PROTECT_CONTENT
                )
                OTAKULUX_msgs.append(snt_msg)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                copied_msg = await msg.copy(
                    chat_id=message.from_user.id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                    protect_content=PROTECT_CONTENT
                )
                OTAKULUX_msgs.append(copied_msg)
            except:
                pass

        if FILE_AUTO_DELETE > 0:
            notification_msg = await message.reply(
                f"<b>⚠️ Tʜɪs Fɪʟᴇ ᴡɪʟʟ ʙᴇ Dᴇʟᴇᴛᴇᴅ ɪɴ {get_exp_time(FILE_AUTO_DELETE)}. Pʟᴇᴀsᴇ sᴀᴠᴇ ᴏʀ ғᴏʀᴡᴀʀᴅ ɪᴛ ᴛᴏ ʏᴏᴜʀ sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs ʙᴇғᴏʀᴇ ɪᴛ ɢᴇᴛs Dᴇʟᴇᴛᴇᴅ! ⚡</b>"
            )

            await asyncio.sleep(FILE_AUTO_DELETE)

            for snt_msg in OTAKULUX_msgs:
                if snt_msg:
                    try:    
                        await snt_msg.delete()  
                    except Exception as e:
                        print(f"Error deleting message {snt_msg.id}: {e}")

            try:
                reload_url = f"https://t.me/{client.username}?start={base64_string}"
                keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("ɢᴇᴛ ғɪʟᴇ ᴀɢᴀɪɴ!", url=reload_url)]]
                )

                await notification_msg.edit(
                    f"<b>ʏᴏᴜʀ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ ɪꜱ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ !!\n\nᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ᴅᴇʟᴇᴛᴇᴅ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ 👇\n\n<code>{reload_url}</code></b>",
                    reply_markup=keyboard
                )
            except Exception as e:
                print(f"Error updating notification with 'Get File Again' button: {e}")

    except Exception as e:
        print(f"Final Error in send_files: {e}")

async def short_url(client: Client, message: Message, base64_string):
    user_id = message.from_user.id
    try:
        short_link = None

        # Base destination link (direct bot link)
        destination = f"https://t.me/{client.username}?start=yu3elk{base64_string}7"

        # Check if we should use the new protection flow
        settings = await db.get_settings()
        shortener_enabled = settings.get('shortener_system', True)

        if shortener_enabled:
            # 1. Shorten the link using the configured shortener (e.g. arolinks.com)
            if SHORTLINK_URL and SHORTLINK_API:
                inner_shortlink = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, destination)
            else:
                inner_shortlink = destination

            # 2. Wrap it with our own /protect URL for extra security & reCAPTCHA
            if WEBSITE_URL:
                short_link = SecurityService.get_protection_url(inner_shortlink)
            else:
                short_link = inner_shortlink
        else:
            # If disabled, we probably shouldn't be in short_url, but just in case:
            return await send_files(client, message, base64_string)

        if not short_link:
            # Fallback to direct send if shortening failed
            return await send_files(client, message, base64_string)

        buttons = [
            [
                InlineKeyboardButton(text="ᴅᴏᴡɴʟᴏᴀᴅ", url=short_link),
                InlineKeyboardButton(text="ᴛᴜᴛᴏʀɪᴀʟ", url=TUT_VID)
            ],
            [
                InlineKeyboardButton(text="ᴘʀᴇᴍɪᴜᴍ", callback_data="premium")
            ]
        ]

        await message.reply_photo(
            photo=random.choice(ANIME_BANNERS),
            caption=SHORT_MSG,
            reply_markup=InlineKeyboardMarkup(buttons),
        )

    except Exception as e:
        print(f"Error in short_url: {e}")
        await send_files(client, message, base64_string)


@Bot.on_message(filters.command('start') & filters.private)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    settings = await db.get_settings()
    is_premium = await is_premium_user(user_id)

    # Add user if not already present
    if not await db.present_user(user_id):
        try:
            await db.add_user(user_id)
        except:
            pass

    # ✅ Check Force Subscription
    if not await is_subscribed(client, user_id):
        return await not_joined(client, message)

    # Check if user is banned
    banned_users = await db.get_ban_users()
    if user_id in banned_users:
        return await message.reply_text(
            "<b>⛔️ You are Bᴀɴɴᴇᴅ from using this bot.</b>\n\n"
            "<i>Contact support if you think this is a mistake.</i>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Contact Support", url=BAN_SUPPORT)]]
            )
        )

    # Handle normal message flow
    text = message.text

    if len(text) > 7:
        try:
            basic = text.split(" ", 1)[1]
            is_verified = basic.startswith("yu3elk")

            if is_verified:
                base64_string = basic[6:-1]
            else:
                base64_string = basic

            # Decision logic for shortener
            shortener_enabled = settings.get('shortener_system', True)
            is_admin = await db.admin_exist(user_id) or user_id == OWNER_ID

            # Can we actually shorten?
            can_shorten = bool(WEBSITE_URL) or (bool(SHORTLINK_URL) and bool(SHORTLINK_API))

            # Shortener bypass conditions
            bypass = (
                is_premium or
                is_admin or
                is_verified or
                not shortener_enabled or
                not can_shorten
            )

            if bypass:
                await send_files(client, message, base64_string)
            else:
                await short_url(client, message, base64_string)
            return

        except Exception as e:
            print(f"Error processing start payload: {e}")
            return
    else:
        if not settings.get('core_features', True) and user_id != OWNER_ID:
            return await message.reply_text("<b>⚠️ Bot is under maintenance. Please try again later.</b>")

        # Premium Start UI Redesign
        buttons = [
            [InlineKeyboardButton("📢 Mᴀɪɴ Cʜᴀɴɴᴇʟ", url="https://t.me/OTAKULUX")],
            [InlineKeyboardButton("🌀 Oɴɢᴏɪɴɢ Aɴɪᴍᴇ", url="https://t.me/OTAKULUX/50")],
            [InlineKeyboardButton("⚪ Aɴɪᴍᴇ Iɴᴅᴇx", url="https://t.me/OTAKULUX/51")],
            [
                InlineKeyboardButton("⚙️ Aʙᴏᴜᴛ", callback_data="about"),
                InlineKeyboardButton("💎 Pʀᴇᴍɪᴜᴍ", callback_data="premium")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(buttons)

        # Premium Welcome Message
        caption = (
            "━━━━━━━━━━━━━━━━━━━\n"
            f"⚡ <b>Hᴇʏ, {message.from_user.first_name}!</b>\n\n"
            "Wᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ ᴍᴏsᴛ ᴘᴏᴡᴇʀғᴜʟ ꜰɪʟᴇ sᴛᴏʀᴇ ᴇɴɢɪɴᴇ. "
            "I ᴄᴀɴ sᴛᴏʀᴇ ᴀɴᴅ sʜᴀʀᴇ ꜰɪʟᴇs sᴇᴄᴜʀᴇʟʏ ᴡɪᴛʜ ᴜʟᴛʀᴀ-ꜰᴀsᴛ sᴘᴇᴇᴅ. 😈\n\n"
            "<i>Uɴʟᴏᴄᴋ ᴛʜᴇ ꜰᴜʟʟ ᴘᴏᴛᴇɴᴛɪᴀʟ ʙʏ ᴊᴏɪɴɪɴɢ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ʙᴇʟᴏᴡ.</i>\n"
            "━━━━━━━━━━━━━━━━━━━"
        )

        await message.reply_photo(
            photo=random.choice(ANIME_BANNERS),
            caption=caption,
            reply_markup=reply_markup,
            message_effect_id=5104841245755180586 # 🔥
        )
        return



#=====================================================================================##
# Don't Remove Credit @OTAKULUX, @OTAKULUX
# Ask Doubt on telegram @OTAKULUX



async def not_joined(client: Client, message: Message):
    user_id = message.from_user.id

    # Get detailed subscription status
    status_list = await get_sub_status(client, user_id)

    buttons = []
    status_text = ""

    for i, status in enumerate(status_list, 1):
        icon = "✅" if status['is_joined'] else "❌"
        status_text += f"{i}. {icon} {status['name']} ⚡ {'Joined' if status['is_joined'] else 'Not Joined'}\n"

        if not status['is_joined']:
            buttons.append([InlineKeyboardButton(text=f"📢 {status['name']}", url=status['link'])])

    # Add Try Again button
    try_again_data = "ck"
    if hasattr(message, 'command') and len(message.command) > 1:
        try_again_data = f"ck_{message.command[1]}"

    buttons.append([InlineKeyboardButton("🔄 Try Again", callback_data=try_again_data)])

    caption = (
        "━━━━━━━━━━━━━━━━━━━\n"
        "✨ HEY SAMA × ✨\n\n"
        "🎉 <b>Anime Files Are Ready !!</b>\n\n"
        "⚠️ Hey! You haven't joined all required channels.\n"
        "Join now to unlock your files instantly! ⚡\n\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "📊 <b>SUBSCRIPTION STATUS:</b>\n\n"
        f"{status_text}\n"
        "━━━━━━━━━━━━━━━━━━━"
    )

    await message.reply_photo(
        photo=random.choice(ANIME_BANNERS),
        caption=caption,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

#=====================================================================================##

@Bot.on_message(filters.command('myplan') & filters.private)
async def check_plan(client: Client, message: Message):
    user_id = message.from_user.id  # Get user ID from the message

    # Get the premium status of the user
    status_message = await check_user_plan(user_id)

    # Send the response message to the user
    await message.reply(status_message)

#=====================================================================================##
# Command to add premium user
@Bot.on_message(filters.command('addpremium') & filters.private & admin)
async def add_premium_user_command(client, msg):
    if len(msg.command) != 4:
        await msg.reply_text(
            "Usage: /addpremium <user_id> <time_value> <time_unit>\n\n"
            "Time Units:\n"
            "s - seconds\n"
            "m - minutes\n"
            "h - hours\n"
            "d - days\n"
            "y - years\n\n"
            "Examples:\n"
            "/addpremium 123456789 30 m → 30 minutes\n"
            "/addpremium 123456789 2 h → 2 hours\n"
            "/addpremium 123456789 1 d → 1 day\n"
            "/addpremium 123456789 1 y → 1 year"
        )
        return

    try:
        user_id = int(msg.command[1])
        time_value = int(msg.command[2])
        time_unit = msg.command[3].lower()  # supports: s, m, h, d, y

        # Call add_premium function
        expiration_time = await add_premium(user_id, time_value, time_unit)

        # Notify the admin
        await msg.reply_text(
            f"✅ User `{user_id}` added as a premium user for {time_value} {time_unit}.\n"
            f"Expiration Time: `{expiration_time}`"
        )

        # Notify the user
        await client.send_message(
            chat_id=user_id,
            text=(
                f"🎉 Premium Activated!\n\n"
                f"You have received premium access for `{time_value} {time_unit}`.\n"
                f"Expires on: `{expiration_time}`"
            ),
        )

    except ValueError:
        await msg.reply_text("❌ Invalid input. Please ensure user ID and time value are numbers.")
    except Exception as e:
        await msg.reply_text(f"⚠️ An error occurred: `{str(e)}`")


# Command to remove premium user
@Bot.on_message(filters.command('remove_premium') & filters.private & admin)
async def pre_remove_user(client: Client, msg: Message):
    if len(msg.command) != 2:
        await msg.reply_text("useage: /remove_premium user_id ")
        return
    try:
        user_id = int(msg.command[1])
        await remove_premium(user_id)
        await msg.reply_text(f"User {user_id} has been removed.")
    except ValueError:
        await msg.reply_text("user_id must be an integer or not available in database.")


# Command to list active premium users
@Bot.on_message(filters.command('premium_users') & filters.private & admin)
async def list_premium_users_command(client, message):
    # Define IST timezone
    ist = timezone("Asia/Kolkata")

    # Retrieve all users from the collection
    premium_users_cursor = collection.find({})
    premium_user_list = ['Active Premium Users in database:']
    current_time = datetime.now(ist)  # Get current time in IST

    # Use async for to iterate over the async cursor
    async for user in premium_users_cursor:
        user_id = user["user_id"]
        expiration_timestamp = user["expiration_timestamp"]

        try:
            # Convert expiration_timestamp to a timezone-aware datetime object in IST
            expiration_time = datetime.fromisoformat(expiration_timestamp).astimezone(ist)

            # Calculate remaining time
            remaining_time = expiration_time - current_time

            if remaining_time.total_seconds() <= 0:
                # Remove expired users from the database
                await collection.delete_one({"user_id": user_id})
                continue  # Skip to the next user if this one is expired

            # If not expired, retrieve user info
            user_info = await client.get_users(user_id)
            username = user_info.username if user_info.username else "No Username"
            first_name = user_info.first_name
            mention=user_info.mention

            # Calculate days, hours, minutes, seconds left
            days, hours, minutes, seconds = (
                remaining_time.days,
                remaining_time.seconds // 3600,
                (remaining_time.seconds // 60) % 60,
                remaining_time.seconds % 60,
            )
            expiry_info = f"{days}d {hours}h {minutes}m {seconds}s left"

            # Add user details to the list
            premium_user_list.append(
                f"UserID: <code>{user_id}</code>\n"
                f"User: @OTAKULUX{username}\n"
                f"Name: {mention}\n"
                f"Expiry: {expiry_info}"
            )
        except Exception as e:
            premium_user_list.append(
                f"UserID: <code>{user_id}</code>\n"
                f"Error: Unable to fetch user details ({str(e)})"
            )

    if len(premium_user_list) == 1:  # No active users found
        await message.reply_text("I found 0 active premium users in my DB")
    else:
        await message.reply_text("\n\n".join(premium_user_list), parse_mode=None)


#=====================================================================================##

@Bot.on_message(filters.command("count") & filters.private & admin)
async def total_verify_count_cmd(client, message: Message):
    total = await db.get_total_verify_count()
    await message.reply_text(f"Tᴏᴛᴀʟ ᴠᴇʀɪғɪᴇᴅ ᴛᴏᴋᴇɴs ᴛᴏᴅᴀʏ: <b>{total}</b>")


#=====================================================================================##

@Bot.on_message(filters.command('commands') & filters.private & admin)
async def bcmd(bot: Bot, message: Message):        
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("• ᴄʟᴏsᴇ •", callback_data = "close")]])
    await message.reply(text=CMD_TXT, reply_markup = reply_markup, quote= True)

@Bot.on_message(filters.command('test') & filters.private & filters.user(OWNER_ID))
async def test_shortener(client: Client, message: Message):
    # Test payload for demonstration
    sample_payload = "W3siaWQiOiAxLCAibmFtZSI6ICJUZXN0In1d"
    await short_url(client, message, sample_payload)
