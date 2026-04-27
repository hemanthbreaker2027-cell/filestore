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
from helper_func import is_subscribed, decode, encode, get_messages, get_exp_time, get_sub_status, admin
from helper_security import secure_redirect
from database.database import *
from database.db_premium import *


BAN_SUPPORT = f"{BAN_SUPPORT}"
TUT_VID = f"{TUT_VID}"

async def auto_delete_task(client, message, OTAKULUX_msgs, FILE_AUTO_DELETE, base64_string):
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

async def send_files(client: Client, message: Message, base64_string):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Handle yu3elk stripping if passed directly (e.g. from callback)
    if base64_string.startswith("yu3elk"):
        base64_string = base64_string[6:-1]

    temp_msg = await message.reply_photo(
        photo=random.choice(ANIME_BANNERS),
        caption="━━━━━━━━━━━━━━━━━━━\n🔍 Checking Subscription...\n━━━━━━━━━━━━━━━━━━━"
    )

    if not await is_subscribed(client, user_id):
        await temp_msg.delete()
        return await not_joined(client, message, base64_string)

    try:
        string = await decode(base64_string)
        argument = string.split("-")

        ids = []
        db_id = abs(client.db_channel.id)
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) // db_id)
                end = int(int(argument[2]) // db_id)
                ids = range(start, end + 1) if start <= end else list(range(start, end - 1, -1))
            except Exception as e:
                print(f"Error decoding IDs: {e}")
                await message.reply_text("<b>❌ Error: Invalid link format.</b>")
                return

        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) // db_id)]
            except Exception as e:
                print(f"Error decoding ID: {e}")
                await message.reply_text("<b>❌ Error: Invalid link format.</b>")
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

        # Speed Boost: Concurrent Delivery with Semaphore
        sem = asyncio.Semaphore(3)
        OTAKULUX_msgs = []
        FILE_AUTO_DELETE = await db.get_del_timer()

        async def deliver_file(msg, index):
            nonlocal OTAKULUX_msgs
            if not msg or msg.empty: return

            async with sem:
                try:
                    original_caption = msg.caption.html if msg.caption else ""
                    caption = f"{original_caption}\n\n{CUSTOM_CAPTION}" if CUSTOM_CAPTION else original_caption

                    # UI Upgrade: Premium Buttons
                    reply_markup = None if DISABLE_CHANNEL_BUTTON else msg.reply_markup

                    # Delivery
                    snt_msg = await msg.copy(
                        chat_id=chat_id,
                        caption=caption,
                        parse_mode=ParseMode.HTML,
                        reply_markup=reply_markup,
                        protect_content=PROTECT_CONTENT
                    )
                    OTAKULUX_msgs.append((index, snt_msg))

                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    return await deliver_file(msg, index)
                except Exception as e:
                    print(f"Error delivering message {msg.id}: {e}")

        # Dispatch tasks
        tasks = [deliver_file(msg, i) for i, msg in enumerate(messages)]
        await asyncio.gather(*tasks)

        # Re-sort messages to maintain order for auto-delete logic
        OTAKULUX_msgs.sort(key=lambda x: x[0])
        final_msgs = [m[1] for m in OTAKULUX_msgs]

        if final_msgs:
            asyncio.create_task(auto_delete_task(client, message, final_msgs, FILE_AUTO_DELETE, base64_string))
        else:
            await message.reply_text("<b>❌ Error: No files were found or could be delivered. Please check the link or contact admin.</b>")

    except Exception as e:
        print(f"Final Error in send_files: {e}")

async def secure_redirect_url(client: Client, message: Message, base64_string):
    try:
        user_id = message.from_user.id
        # Final destination URL back to bot with verified payload
        final_url = f"https://t.me/{client.username}?start=yu3elk{base64_string}7"

        # Token Payload
        payload = {
            'url': final_url,
            'exp': int(time.time()) + 3600, # 1 hour expiry
            'uid': user_id,
            'ip_hash': None # We can add IP binding here if we had user IP, but in bot we don't easily get user's public IP
        }

        # Generate Long Token
        token = secure_redirect.encrypt(payload)
        noise = secure_redirect.generate_random_noise(12)

        if WEBSITE_URL:
            secure_link = f"{WEBSITE_URL}/r/{noise}/{token}"
        else:
            # Fallback if WEBSITE_URL is missing
            secure_link = final_url

        buttons = [
            [
                InlineKeyboardButton(text="📥 Gᴇᴛ Fɪʟᴇs", url=secure_link),
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
        print(f"Error generating secure redirect: {e}")


@Bot.on_message(filters.command('start') & filters.private)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    is_premium = await is_premium_user(user_id)

    # Add user if not already present
    if not await db.present_user(user_id):
        try:
            await db.add_user(user_id)
        except:
            pass

    # Handle start payload
    text = message.text
    if len(text) > 7:
        try:
            basic = text.split(" ", 1)[1]
            if basic.startswith("yu3elk"):
                base64_string = basic[6:-1]
            else:
                base64_string = basic

            # ✅ Check Force Subscription
            if not await is_subscribed(client, user_id):
                return await not_joined(client, message, base64_string)

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

            # --- SAFE BLOCK START ---
            try:
                conf_list = [
                    SHORTLINK_URL,
                    SHORTLINK_API,
                    WEBSITE_URL,
                    TURNSTILE_SITE_KEY,
                    TURNSTILE_SECRET_KEY
                ]
                is_incomplete = any(not x or str(x).strip() == "" for x in conf_list)
            except:
                is_incomplete = True

            # Direct send logic
            if is_premium or user_id == OWNER_ID or basic.startswith("yu3elk") or is_incomplete:
                await send_files(client, message, base64_string)
                return
            
            # Secure Redirect logic
            await secure_redirect_url(client, message, base64_string)
            return
            # --- SAFE BLOCK END ---
        

        except Exception as e:
            print(f"Error processing start payload: {e}")
            return

    # Normal start (no payload)
    if not await is_subscribed(client, user_id):
        return await not_joined(client, message)

    else:
        # Premium Start UI Redesign
        buttons = [
            [InlineKeyboardButton("📢 Main Channel", url="https://t.me/OTAKULUX")],
            [InlineKeyboardButton("🌀 Ongoing Anime", url="https://t.me/OTAKULUX/50")],
            [InlineKeyboardButton("⚪ Anime Index", url="https://t.me/OTAKULUX/51")],
            [
                InlineKeyboardButton("⚠️ About", callback_data="about"),
                InlineKeyboardButton("💰 Promo", callback_data="premium")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(buttons)

        # Typing Simulation Lines
        line1 = "━━━━━━━━━━━━━━━━━━━\n"
        line2 = f"Hey, {message.from_user.first_name} ✌🏻 ✨\n"
        line3 = "I hope you're feeling the power of <b>Shadow Monarch</b> 😈\n\n"
        line4 = "⚡ I'm The Ultimate File Sharing Bot... 🎉\n"
        line5 = "━━━━━━━━━━━━━━━━━━━"

        # Send initial message with first few lines
        msg = await message.reply_photo(
            photo=random.choice(ANIME_BANNERS),
            caption=line1 + line2,
            message_effect_id=5104841245755180586 # 🔥
        )

        try:
            await asyncio.sleep(0.5)
            await msg.edit_caption(line1 + line2 + line3)

            await asyncio.sleep(0.5)
            await msg.edit_caption(
                caption=line1 + line2 + line3 + line4 + line5,
                reply_markup=reply_markup
            )
        except MessageNotModified:
            pass
        except Exception as e:
            print(f"Error in typing simulation: {e}")
        return



#=====================================================================================##
# Don't Remove Credit @OTAKULUX, @OTAKULUX
# Ask Doubt on telegram @OTAKULUX



async def not_joined(client: Client, message: Message, payload=None):
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
    if payload:
        try_again_data = f"ck_{payload}"
    elif hasattr(message, 'command') and len(message.command) > 1:
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
