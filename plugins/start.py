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
import os
import random
import sys
import re
import string 
import string
import time
import traceback
from datetime import datetime, timedelta
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode, ChatAction
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, ChatInviteLink, ChatPrivileges
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserNotParticipant, MessageNotModified
from config import *
from pytz import timezone
from helper_func import *
from database.database import *
from database.db_premium import *


BAN_SUPPORT = f"{BAN_SUPPORT}"
TUT_VID = f"{TUT_VID}"

async def send_files(client: Client, user_id: int, base64_string, messages=None):
    settings = await db.get_settings()

    if not settings.get('file_delivery', True) and user_id != OWNER_ID:
        try:
            await client.send_message(
                chat_id=user_id,
                text="<b>⚡️ <blockquote>˹ ᴀᴄᴄᴇss ᴅᴇɴɪᴇᴅ ˼\n\n🛡 ꜰɪʟᴇ ᴅᴇʟɪᴠᴇʀʏ ɪs ᴄᴜʀʀᴇɴᴛʟʏ ᴅɪsᴀʙʟᴇᴅ ʙʏ ᴛʜᴇ sᴜᴘʀᴇᴍᴇ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ. 💤</blockquote></b>"
            )
        except: pass
        return

    try:
        # Instant delivery: Skip processing message to reduce roundtrips and latency
        temp_msg = None
        string = await decode(base64_string)
        argument = string.split("-")

        ids = []
        if len(argument) == 3:
            try:
                start = int(argument[1]) // abs(client.db_channel.id)
                end = int(argument[2]) // abs(client.db_channel.id)
                ids = list(range(start, end + 1)) if start <= end else list(range(start, end - 1, -1))
            except Exception as e:
                print(f"Error decoding IDs: {e}")
                return

        elif len(argument) == 2:
            try:
                ids = [int(argument[1]) // abs(client.db_channel.id)]
            except Exception as e:
                print(f"Error decoding ID: {e}")
                return

        try:
            if not messages:
                messages = await get_messages(client, ids)
        except Exception as e:
            try:
                await client.send_message(chat_id=user_id, text="Something went wrong!")
            except: pass
            print(f"Error getting messages: {e}")
            return
        finally:
            if temp_msg:
                try:
                    await temp_msg.delete()
                except:
                    pass

        # REQUIRED correct initialization for message tracking
        AniZoneFlix_msgs = []
        # File auto-delete time in seconds
        FILE_AUTO_DELETE = await db.get_del_timer()

        # SEQUENTIAL DELIVERY (V9 Engine)
        semaphore = asyncio.Semaphore(10)

        async def deliver_item(msg):
            if not msg or msg.empty: return None
            async with semaphore:
                original_caption = msg.caption.html if msg.caption else ""
                caption = f"{original_caption}\n\n{CUSTOM_CAPTION}" if CUSTOM_CAPTION else original_caption

                # Default reply markup: Keep original buttons if any
                reply_markup = msg.reply_markup

                while True:
                    try:
                        sent = await msg.copy(
                            chat_id=user_id,
                            caption=caption,
                            parse_mode=ParseMode.HTML,
                            reply_markup=reply_markup,
                            protect_content=PROTECT_CONTENT
                        )
                        return sent
                    except FloodWait as e:
                        await asyncio.sleep(e.value)
                    except Exception as e:
                        print(f"Error delivering item: {e}")
                        return None

        # Delivery loop
        for msg in messages:
            sent = await deliver_item(msg)
            if sent: AniZoneFlix_msgs.append(sent)

        if not AniZoneFlix_msgs:
            try:
                await client.send_message(chat_id=user_id, text="<b>⚠️ requested files not found or deleted from our database.</b>")
            except: pass
            return

        try:
            # ULTRA STRICT HASH APPEND - Monospace at the very end of delivery
            hash_code = base64_string[-5:].upper() if len(base64_string) >= 5 else "GXC8A"
            last_msg = AniZoneFlix_msgs[-1]
            if last_msg.caption:
                current_cap = last_msg.caption.html if hasattr(last_msg.caption, 'html') else last_msg.caption
                await last_msg.edit_caption(
                    caption=f"{current_cap}\n\n<code>{hash_code}</code>",
                    reply_markup=last_msg.reply_markup
                )
            else:
                # If last message has no caption (like a sticker), send hash separately or on the message before if possible
                # For simplicity, send a small text message
                await client.send_message(chat_id=user_id, text=f"<code>{hash_code}</code>")
        except Exception as e:
            print(f"Error appending hash: {e}")

        if FILE_AUTO_DELETE > 0:
            notification_msg = await client.send_message(
                chat_id=user_id,
                text=f"<b>⚡️ <blockquote>˹ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀʟᴇʀᴛ ˼\n\n🛡 ᴛʜɪs ꜰɪʟᴇ ᴡɪʟʟ ʙᴇ ᴛᴇʀᴍɪɴᴀᴛᴇᴅ ɪɴ {get_exp_time(FILE_AUTO_DELETE)}.\n\n💎 ᴘʟᴇᴀsᴇ sᴀᴠᴇ ᴏʀ ꜰᴏʀᴡᴀʀᴅ ɪᴛ ᴛᴏ ʏᴏᴜʀ sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs ʙᴇꜰᴏʀᴇ ɪᴛ ɪs ɢᴏɴᴇ! 💫</blockquote></b>"
            )

            await asyncio.sleep(FILE_AUTO_DELETE)

            for snt_msg in AniZoneFlix_msgs:
                if snt_msg:
                    try:    
                        await snt_msg.delete()  
                    except Exception as e:
                        print(f"Error deleting message {snt_msg.id}: {e}")

            try:
                reload_url = f"https://t.me/{client.username}?start={base64_string}"
                keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("⚡️ ˹ ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ ˼ ⚡️", url=reload_url)]]
                )

                await notification_msg.edit(
                    f"<b>🛡 <blockquote>˹ ꜰɪʟᴇ ᴛᴇʀᴍɪɴᴀᴛᴇᴅ ˼\n\n💎 ʏᴏᴜʀ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ ɪs sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ !!\n\n🚀 ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴛᴏ ʀᴇᴄᴏᴠᴇʀ ʏᴏᴜʀ ᴅᴇʟᴇᴛᴇᴅ ᴀssᴇᴛ 👇\n\n<code>{reload_url}</code></blockquote></b>",
                    reply_markup=keyboard
                )
            except Exception as e:
                print(f"Error updating notification with 'Get File Again' button: {e}")

    except Exception as e:
        print(f"Final Error in send_files: {e}")

async def short_url(client: Client, message: Message, base64_string):
    user_id = message.from_user.id

    # Create verification session in shared DB via API context
    session_id = await db.create_verification_session(user_id, client.username, context="api")

    # Construct verification link via the API redirector
    # Using BASE_URL for the frontend entry point
    verify_link = f"{BASE_URL}/api/r/{session_id}?redirect=true"

    buttons = [
        [
            InlineKeyboardButton(text="⚡️ ˹ ᴠᴇʀɪꜰʏ ᴛᴏ ᴜɴʟᴏᴄᴋ ˼ ⚡️", url=verify_link),
            InlineKeyboardButton(text="🛡 ˹ ᴛᴜᴛᴏʀɪᴀʟ ˼ 🛡", url=TUT_VID)
        ]
    ]

    await message.reply_photo(
        photo=random.choice(ANIME_BANNERS),
        caption=SHORT_MSG.format(mention=message.from_user.mention),
        reply_markup=InlineKeyboardMarkup(buttons),
    )

async def handle_payload(client: Client, message: Message, basic_payload: str):
    user_id = message.from_user.id
    settings = await db.get_settings()
    shortener_enabled = settings.get('shortener_system', True)

    # Clean payload and get base64 string
    base64_string = basic_payload

    if not shortener_enabled:
        return await send_files(client, user_id, base64_string)

    is_premium = await is_premium_user(user_id)
    is_admin = await db.admin_exist(user_id) or user_id == OWNER_ID
    shorten_admins = settings.get('shorten_admins', True)

    if is_premium or (is_admin and not shorten_admins):
        return await send_files(client, user_id, base64_string)

    # CHECK DEALS SYSTEM
    can_access, deals = await db.check_daily_limit(user_id)
    if can_access:
        # Use a deal and send file
        await db.use_deal(user_id)
        return await send_files(client, user_id, base64_string)
    else:
        # No deals left, send verification prompt
        return await short_url(client, message, base64_string)

@Client.on_message(filters.command('ping') & filters.private)
async def ping_command(client: Client, message: Message):
    start_time = time.time()
    reply = await message.reply_text("<b>⚡ ᴘɪɴɢɪɴɢ...</b>")
    end_time = time.time()
    ping_time = round((end_time - start_time) * 1000, 2)
    await reply.edit_text(f"<b>🏓 ᴘᴏɴɢ!</b>\n\n⏱️ <code>{ping_time} ms</code>")

@Client.on_message(filters.command('help') & filters.private)
async def help_command(client: Client, message: Message):
    # help_command logic
    buttons = [
        [InlineKeyboardButton('ʜᴏᴍᴇ', callback_data='start'),
         InlineKeyboardButton("ᴄʟᴏꜱᴇ", callback_data='close')]
    ]
    await message.reply_text(
        text=HELP_TXT.format(first=message.from_user.first_name),
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_message(filters.command('start') & filters.private)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id

    if not await is_subscribed(client, user_id):
        return await not_joined(client, message)

    settings = await db.get_settings()

    # Add user if not already present
    if not await db.present_user(user_id):
        try:
            await db.add_user(user_id)
        except:
            pass

    # Check if user is banned
    banned_users = await db.get_ban_users()
    if user_id in banned_users:
        return await message.reply_text(
            "<b>💀 <blockquote>˹ ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ˼\n\n🚫 ʏᴏᴜʀ ᴀᴄᴄᴇss ʜᴀs ʙᴇᴇɴ ᴛᴇʀᴍɪɴᴀᴛᴇᴅ ғʀᴏᴍ ᴛʜɪs ᴇɴɢɪɴᴇ.\n\n🛡 ᴄᴏɴᴛᴀᴄᴛ sᴜᴘᴘᴏʀᴛ ɪꜰ ʏᴏᴜ ʙᴇʟɪᴇᴠᴇ ᴛʜɪs ɪs ᴀ ꜰᴀᴛᴀʟ ᴇʀʀᴏʀ. 💫</blockquote></b>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🛡 ᴄᴏɴᴛᴀᴄᴛ sᴜᴘᴘᴏʀᴛ 🛡", url=BAN_SUPPORT)]]
            )
        )

    # Handle normal message flow
    text = message.text

    if len(text) > 7:
        try:
            basic = text.split(" ", 1)[1]

            # CODEFLIX NETWORK DEEP LINK
            if basic.startswith("verify_"):
                token = basic.replace("verify_", "")
                session = await db.get_session_by_token(token)

                if session and session['user_id'] == str(user_id):
                    # Refill deals for the user
                    await db.refill_deals(user_id)

                    await message.reply_text(
                        "<b>✅ Verification Success!\n\n🛡 Your daily verification deals have been refilled. You can now access your files. ⚡️</b>"
                    )

                    # Mark session as used
                    await db.mark_session_used(session['session_id'])
                else:
                    await message.reply_text("<b>❌ Verification Failed!</b>\n\nSecurity Error: Session invalid, expired, or belongs to another user.")
                return

            await handle_payload(client, message, basic)
            return

        except Exception as e:
            print(f"Error processing start payload: {e}")
            return
    else:
        if not settings.get('core_features', True) and user_id != OWNER_ID:
            return await message.reply_text("<b>⚠️ Bot is under maintenance. Please try again later.</b>")

        # Premium Start UI Redesign
        buttons = [
            [InlineKeyboardButton("📢 ˹ ᴍᴀɪɴ ᴄʜᴀɴɴᴇʟ ˼", url="https://t.me/AniZoneFlix")],
            [InlineKeyboardButton("🌀 ˹ ᴏɴɢᴏɪɴɢ ᴀɴɪᴍᴇ ˼", url="https://t.me/AniZoneFlix/50")],
            [InlineKeyboardButton("⚪ ˹ ᴀɴɪᴍᴇ ɪɴᴅᴇx ˼", url="https://t.me/AniZoneFlix/51")],
            [
                InlineKeyboardButton("⚙️ ˹ ᴀʙᴏᴜᴛ ˼", callback_data="about"),
                InlineKeyboardButton("💎 ˹ ᴘʀᴇᴍɪᴜᴍ ˼", callback_data="premium")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(buttons)

        # Premium Welcome Message
        caption = (
            "━━━━━━━━━━━━━━━━━━━\n"
            f"⚡️ <b>˹ ʜᴇʏ, {message.from_user.first_name} ˼</b>\n\n"
            "💎 ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ ᴍᴏsᴛ ᴘᴏᴡᴇʀꜰᴜʟ ꜰɪʟᴇ sᴛᴏʀᴇ ᴇɴɢɪɴᴇ.\n"
            "ɪ ᴄᴀɴ sᴛᴏʀᴇ ᴀɴᴅ sʜᴀʀᴇ ꜰɪʟᴇs sᴇᴄᴜʀᴇʟʏ ᴡɪᴛʜ ᴜʟᴛʀᴀ-ꜰᴀsᴛ sᴘᴇᴇᴅ. 😈\n\n"
            "<i>🛡 ᴜɴʟᴏᴄᴋ ᴛʜᴇ ꜰᴜʟʟ ᴘᴏᴛᴇɴᴛɪᴀʟ ʙʏ ᴊᴏɪɴɪɴɢ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ʙᴇʟᴏᴡ.</i>\n"
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
# Don't Remove Credit @AniZoneFlix, @AniZoneFlix
# Ask Doubt on telegram @AniZoneFlix



async def not_joined(client: Client, message: Message):
    user_id = message.from_user.id

    # Get detailed subscription status
    status_list = await get_sub_status(client, user_id)

    buttons = []
    status_text = ""

    for i, status in enumerate(status_list, 1):
        icon = "✅" if status['is_joined'] else "❌"
        status_text += f"💎 {i}. {icon} {status['name']} ⚡️ {'ᴊᴏɪɴᴇᴅ' if status['is_joined'] else 'ɴᴏᴛ ᴊᴏɪɴᴇᴅ'}\n"

        if not status['is_joined']:
            buttons.append([InlineKeyboardButton(text=f"📢 ˹ {status['name']} ˼", url=status['link'])])

    # Add Try Again button
    try_again_data = "ck"
    if hasattr(message, 'command') and len(message.command) > 1:
        try_again_data = f"ck_{message.command[1]}"

    buttons.append([InlineKeyboardButton("🔄 ˹ ᴛʀʏ ᴀɢᴀɪɴ ˼", callback_data=try_again_data)])

    caption = (
        "━━━━━━━━━━━━━━━━━━━\n"
        "✨ ˹ ʜᴇʏ sᴀᴍᴀ × ᴀɴɪᴢᴏɴᴇꜰʟɪx ˼ ✨\n\n"
        "🎉 <b>˹ ᴀɴɪᴍᴇ ꜰɪʟᴇs ᴀʀᴇ ʀᴇᴀᴅʏ ˼ !!</b>\n\n"
        "⚠️ ʜᴇʏ! ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ ᴊᴏɪɴᴇᴅ ᴀʟʟ ʀᴇǫᴜɪʀᴇᴅ ᴄʜᴀɴɴᴇʟs.\n"
        "ᴊᴏɪɴ ɴᴏᴡ ᴛᴏ ᴜɴʟᴏᴄᴋ ʏᴏᴜʀ ꜰɪʟᴇs ɪɴsᴛᴀɴᴛʟʏ! ⚡️\n\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "📊 <b>˹ sᴜʙsᴄʀɪᴘᴛɪᴏɴ sᴛᴀᴛᴜs ˼:</b>\n\n"
        f"{status_text}\n"
        "━━━━━━━━━━━━━━━━━━━"
    )

    await message.reply_photo(
        photo=random.choice(ANIME_BANNERS),
        caption=caption,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

#=====================================================================================##

@Client.on_message(filters.command('myplan') & filters.private)
async def check_plan(client: Client, message: Message):
    user_id = message.from_user.id  # Get user ID from the message

    # Get the premium status of the user
    status_message = await check_user_plan(user_id)

    # Send the response message to the user
    await message.reply(status_message)

#=====================================================================================##
# Command to add premium user
@Client.on_message(filters.command('addpremium') & filters.private & admin)
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
@Client.on_message(filters.command('remove_premium') & filters.private & admin)
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
@Client.on_message(filters.command('premium_users') & filters.private & admin)
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
                f"User: @AniZoneFlix{username}\n"
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



#=====================================================================================##

@Client.on_message(filters.command("count") & filters.private & admin)
async def total_verify_count_cmd(client, message: Message):
    total = await db.get_total_verify_count()
    await message.reply_text(f"Tᴏᴛᴀʟ ᴠᴇʀɪғɪᴇᴅ ᴛᴏᴋᴇɴs ᴛᴏᴅᴀʏ: <b>{total}</b>")

@Client.on_message(filters.command('commands') & filters.private & admin)
async def bcmd(client: Client, message: Message):
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("• ᴄʟᴏsᴇ •", callback_data = "close")]])
    await message.reply(text=CMD_TXT, reply_markup = reply_markup, quote= True)


@Client.on_message(filters.private, group=-1)
async def monitor_all(client: Client, message: Message):
    # Print every message received for debugging
    print(f"[MONITOR] user={message.from_user.id}, text={message.text or 'MEDIA'}")
