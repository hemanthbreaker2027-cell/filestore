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

        # STICKER LOGIC MAPPINGS
        sticker_mappings = {}
        try:
            sticker_mappings = await db.get_all_stickers()
        except Exception as e:
            print(f"Error fetching sticker mappings: {e}")

        # SEQUENTIAL DELIVERY (V9 Interleaved Engine)
        # Optimized for Sticker -> Media sequence with enhanced resilience
        semaphore = asyncio.Semaphore(10)

        async def deliver_item(msg):
            if not msg or msg.empty: return None
            async with semaphore:
                # 1. ADMIN PANEL STICKERS (If enabled)
                if settings.get('stickers_enabled', True):
                    # We can send a default sticker or one from sticker_mappings if keyword matches
                    sent_panel_sticker = False
                    try:
                        caption_text = (msg.caption or "").lower()
                        for keyword, sticker_id in sticker_mappings.items():
                            if keyword in caption_text:
                                await client.send_sticker(chat_id=user_id, sticker=sticker_id)
                                sent_panel_sticker = True
                                break
                    except: pass

                    if not sent_panel_sticker:
                        # Fallback default sticker if desired, or skip.
                        # User requested "send stickers (if enabled)"
                        pass

                original_caption = msg.caption.html if msg.caption else ""
                caption = f"{original_caption}\n\n{CUSTOM_CAPTION}" if CUSTOM_CAPTION else original_caption

                # Default reply markup: Keep original buttons if any
                reply_markup = msg.reply_markup

                # STREAM & DOWNLOAD BUTTONS
                is_video = False
                file_name = "Requested File"
                file_size = 0
                mime_type = "video/mp4"

                if msg.video:
                    is_video = True
                    file_name = msg.video.file_name or "video.mp4"
                    file_size = msg.video.file_size
                    mime_type = msg.video.mime_type or "video/mp4"
                elif msg.document and msg.document.mime_type:
                    if msg.document.mime_type.startswith('video/') or (msg.document.file_name and msg.document.file_name.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.webm'))):
                        is_video = True
                        file_name = msg.document.file_name or "file.mkv"
                        file_size = msg.document.file_size
                        mime_type = msg.document.mime_type or "video/mp4"

                if is_video and (settings.get('stream_enabled', False) or settings.get('download_enabled', False)):
                    file_obj = msg.video or msg.document
                    code = getattr(file_obj, 'file_unique_id', None)
                    if not code:
                        import secrets
                        code = secrets.token_hex(4)

                    file_link = f"https://t.me/{client.username}?start=get-{msg.id * abs(client.db_channel.id)}"

                    await db.shortener_verifications.update_one(
                        {'_id': code},
                        {'$set': {
                            'user_id': str(user_id),
                            'original_url': file_link,
                            'file_name': file_name,
                            'file_size': file_size,
                            'mime_type': mime_type,
                            'verified_at': time.time(),
                            'expires_at': time.time() + 86400
                        }},
                        upsert=True
                    )

                    buttons = []
                    base_web_url = settings.get('website_url', WEBSITE_URL)
                    if settings.get('stream_enabled', False):
                        buttons.append([InlineKeyboardButton("▶ STREAM", url=f"https://{base_web_url}/watch?path={code}")])
                    if settings.get('download_enabled', False):
                        buttons.append([InlineKeyboardButton("⬇ DOWNLOAD", url=f"https://{base_web_url}/download/{code}")])

                    if reply_markup and reply_markup.inline_keyboard:
                        new_kb = list(reply_markup.inline_keyboard)
                        new_kb.extend(buttons)
                        reply_markup = InlineKeyboardMarkup(new_kb)
                    else:
                        reply_markup = InlineKeyboardMarkup(buttons)

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
    settings = await db.get_settings()
    shortener_enabled = settings.get('shortener_system', True)

    if not shortener_enabled:
        return await send_files(client, user_id, base64_string)

    try:
        # ULTRA STRICT FLOW
        # 1. Generate local verification token (GXC8A format)
        token = await db.create_strict_verification(user_id, base64_string)

        # 2. Construct Protected URL (Bot Layer: Bot never exposes original URLs)
        web_domain = settings.get('website_url', WEBSITE_URL)
        base_url = web_domain if web_domain.startswith("http") else f"https://{web_domain}"
        short_link = f"{base_url}/protect?data={token}"

        buttons = [
            [
                InlineKeyboardButton(text="⚡️ ˹ ᴅᴏᴡɴʟᴏᴀᴅ ˼ ⚡️", url=short_link),
                InlineKeyboardButton(text="🛡 ˹ ᴛᴜᴛᴏʀɪᴀʟ ˼ 🛡", url=TUT_VID)
            ],
            [
                InlineKeyboardButton(text="💎 ˹ ᴘʀᴇᴍɪᴜᴍ ˼ 💎", callback_data="premium")
            ]
        ]

        try:
            await message.reply_photo(
                photo=random.choice(ANIME_BANNERS),
                caption=SHORT_MSG,
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        except Exception as photo_err:
            print(f"Photo reply failed: {photo_err}, falling back to text")
            await message.reply_text(
                text=SHORT_MSG + f"\n\n🔗 <b>Verification Link:</b> {short_link}",
                reply_markup=InlineKeyboardMarkup(buttons),
                disable_web_page_preview=True
            )

    except Exception as e:
        print(f"CRITICAL ERROR in short_url: {e}")
        # If shortener fails, we MUST decide: bypass or tell user?
        # User said "fix it", so if it fails, maybe tell them why or fallback.
        # Fallback to direct delivery to ensure "sending anything"
        await send_files(client, user_id, base64_string)


async def handle_payload(client: Client, message: Message, basic_payload: str):
    user_id = message.from_user.id
    settings = await db.get_settings()
    shortener_enabled = settings.get('shortener_system', True)

    # Clean payload and get base64 string
    is_verified_payload = basic_payload.startswith("yu3elk")
    if is_verified_payload:
        base64_string = basic_payload[6:-1]
    else:
        base64_string = basic_payload

    # REQUIRED CORRECT BEHAVIOR: WHEN SHORTNER_ENABLED = false
    if not shortener_enabled:
        return await send_files(client, user_id, base64_string)

    # REQUIRED CORRECT BEHAVIOR: WHEN SHORTNER_ENABLED = true
    is_premium = await is_premium_user(user_id)
    is_admin = await db.admin_exist(user_id) or user_id == OWNER_ID

    shorten_admins = settings.get('shorten_admins', True)

    shortener_mode = settings.get('shortener_mode', 'one_per_time')
    shortener_time = settings.get('shortener_time', 0)

    # STRICT CONFIG CHECK
    can_shorten = all([
        bool(WEBSITE_URL),
        bool(SHORTLINK_URL),
        bool(SHORTLINK_API)
    ])

    # Check actual verification state from database
    actual_verified = False
    verify_status = await db.get_verify_status(user_id)

    if verify_status.get('is_verified'):
        if shortener_mode == 'based_time':
            verified_time = verify_status.get('verified_time', 0)
            if (time.time() - verified_time) < shortener_time:
                # Based Time Verification: Link must ALSO match or be a direct verified click
                # However, usually based_time implies session-wide bypass.
                # To be strict, we check if they are verified.
                actual_verified = True
            else:
                # Time expired, reset status in real-time
                await db.update_verify_status(user_id, is_verified=False)
        else:
            # ONE PER TIME Mode: Verification token MUST match base64_string
            if is_verified_payload and verify_status.get('verify_token') == base64_string:
                actual_verified = True
                # Consume verification if one_per_time (optional, but requested strict)
                # await db.update_verify_status(user_id, is_verified=False)

    # Final Bypass Determination
    is_bypassed_admin = is_admin and not shorten_admins

    # Logic: If Shortener is OFF, bypass immediately.
    if not shortener_enabled:
        return await send_files(client, user_id, base64_string)

    # If ON, check other bypasses
    if is_premium or is_bypassed_admin or actual_verified:
        return await send_files(client, user_id, base64_string)

    # Check if we CAN shorten
    if not can_shorten:
        print(f"[CONFIG ERROR] Shortener enabled but credentials missing: URL={SHORTLINK_URL}, API={bool(SHORTLINK_API)}")
        if is_admin:
            await message.reply_text("<b>⚠️ Warning: Shortener enabled but credentials (URL/API) missing in config.py! Delivering files directly.</b>")
        return await send_files(client, user_id, base64_string)

    # Proceed to shortener
    await short_url(client, message, base64_string)

@Bot.on_message(filters.command('start') & filters.private)
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

            # ULTRA STRICT VERIFICATION DEEP LINK
            if basic.startswith("verify_"):
                token = basic.replace("verify_", "")
                record = await db.consume_strict_verification(token)
                if record:
                    # Success! Deliver files
                    await send_files(client, user_id, record['code'])
                else:
                    await message.reply_text("<b>❌ Verification Failed!</b>\n\nYou must complete the full verification flow to access these files.")
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
