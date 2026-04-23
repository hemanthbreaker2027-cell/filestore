#(©)Codexbotz

import re
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from pyrogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
import asyncio
from asyncio import TimeoutError
from config import OWNER_ID
from helper_func import encode, get_message_id, admin, get_messages, parse_media_metadata, fetch_anilist_data
from database.database import db

@Bot.on_message(filters.private & admin & filters.command('batch'))
async def batch(client: Client, message: Message):
    # Support for range link format: /batch https://t.me/c/3967760305/274-299
    if len(message.command) > 1:
        link_text = message.command[1]

        # Method 1: Range link selection
        range_pattern = r"https://t.me/(?:c/)?(?:[^/]+)/(\d+)-(\d+)"
        range_match = re.search(range_pattern, link_text)
        if range_match:
            f_msg_id = int(range_match.group(1))
            s_msg_id = int(range_match.group(2))
            string = f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}"
            base64_string = await encode(string)
            link = f"https://t.me/{client.username}?start={base64_string}"
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
            return await message.reply_text(f"<b>Here is your link</b>\n\n<code>{link}</code>", quote=True, reply_markup=reply_markup)

        # Method 2: Owner-only automated batch starting from link
        if message.from_user.id == OWNER_ID:
            single_pattern = r"https://t.me/(?:c/)?(?:[^/]+)/(\d+)"
            single_match = re.search(single_pattern, link_text)
            if single_match:
                start_id = int(single_match.group(1))

                # Check if link belongs to DB channel
                # We do a basic check by trying to fetch the message
                try:
                    test_msg = await client.get_messages(client.db_channel.id, start_id)
                    if not test_msg or test_msg.empty:
                        return await message.reply_text("❌ Error: Message not found in DB channel or inaccessible.")
                except Exception as e:
                    return await message.reply_text(f"❌ Error: {e}")

                # Ask for count
                count_msg = await client.ask(message.chat.id, "How many messages?", filters=filters.text, timeout=60)
                while True:
                    try:
                        num_messages = int(count_msg.text)
                        if num_messages <= 0:
                            count_msg = await client.ask(message.chat.id, "Please send a positive number.", filters=filters.text, timeout=60)
                            continue
                        break
                    except ValueError:
                        count_msg = await client.ask(message.chat.id, "Invalid input. Please send a number (e.g., 25).", filters=filters.text, timeout=60)
                    except Exception:
                        return

                progress = await message.reply_text(f"🔍 Processing 0/{num_messages}...")

                found_ids = []
                current_id = start_id

                while len(found_ids) < num_messages:
                    # Fetch messages in small chunks to avoid rate limits and handle sparse IDs
                    to_fetch = list(range(current_id, current_id + 50))
                    try:
                        msgs = await get_messages(client, to_fetch)
                        for m in msgs:
                            if m and not m.empty:
                                if m.video or m.document:
                                    # Auto-index while batching
                                    media = m.video or m.document
                                    text = m.caption or getattr(media, "file_name", "")
                                    metadata = parse_media_metadata(text)
                                    anilist = await fetch_anilist_data(metadata["anime_name"])
                                    metadata["anilist"] = anilist
                                    metadata["search_name"] = metadata["anime_name"].lower()
                                    await db.save_anime_metadata(m.id, metadata)

                                found_ids.append(m.id)
                                if len(found_ids) == num_messages:
                                    break
                                if len(found_ids) % 5 == 0:
                                    try: await progress.edit_text(f"🔍 Processing {len(found_ids)}/{num_messages}...")
                                    except: pass

                        if not msgs: # Safety break if no messages returned
                            break

                        current_id += 50
                        # If we have reached a very high ID without finding enough, we might want to stop
                        if current_id > start_id + num_messages + 1000:
                            break
                    except Exception as e:
                        print(f"Error in batch scan: {e}")
                        break

                if not found_ids:
                    return await progress.edit_text("❌ No available messages found.")

                last_id = found_ids[-1]
                string = f"get-{start_id * abs(client.db_channel.id)}-{last_id * abs(client.db_channel.id)}"
                base64_string = await encode(string)
                link = f"https://t.me/{client.username}?start={base64_string}"
                reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])

                await progress.delete()
                await message.reply_text("✅ Batch completed successfully")
                return await message.reply_text(f"<b>Here is your link</b>\n\n<code>{link}</code>", quote=True, reply_markup=reply_markup)

    while True:
        try:
            first_message = await client.ask(text = "Forward the First Message from DB Channel (with Quotes)..\n\nor Send the DB Channel Post Link", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        f_msg_id = await get_message_id(client, first_message)
        if f_msg_id:
            break
        else:
            await first_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel", quote = True)
            continue

    while True:
        try:
            second_message = await client.ask(text = "Forward the Last Message from DB Channel (with Quotes)..\nor Send the DB Channel Post link", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id:
            break
        else:
            await second_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel", quote = True)
            continue


    string = f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    await second_message.reply_text(f"<b>Here is your link</b>\n\n<code>{link}</code>", quote=True, reply_markup=reply_markup)


@Bot.on_message(filters.private & admin & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    while True:
        try:
            channel_message = await client.ask(text = "Forward Message from the DB Channel (with Quotes)..\nor Send the DB Channel Post link", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        msg_id = await get_message_id(client, channel_message)
        if msg_id:
            break
        else:
            await channel_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is not taken from DB Channel", quote = True)
            continue

    base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    await channel_message.reply_text(f"<b>Here is your link</b>\n\n<code>{link}</code>", quote=True, reply_markup=reply_markup)


@Bot.on_message(filters.private & admin & filters.command("custom_batch"))
async def custom_batch(client: Client, message: Message):
    collected = []
    STOP_KEYBOARD = ReplyKeyboardMarkup([["STOP"]], resize_keyboard=True)

    await message.reply("Send all messages you want to include in batch.\n\nPress STOP when you're done.", reply_markup=STOP_KEYBOARD)

    while True:
        try:
            user_msg = await client.ask(
                chat_id=message.chat.id,
                text="Waiting for files/messages...\nPress STOP to finish.",
                timeout=60
            )
        except asyncio.TimeoutError:
            break

        if user_msg.text and user_msg.text.strip().upper() == "STOP":
            break

        try:
            sent = await user_msg.copy(client.db_channel.id, disable_notification=True)
            collected.append(sent.id)
        except Exception as e:
            await message.reply(f"❌ Failed to store a message:\n<code>{e}</code>")
            continue

    await message.reply("✅ Batch collection complete.", reply_markup=ReplyKeyboardRemove())

    if not collected:
        await message.reply("❌ No messages were added to batch.")
        return

    start_id = collected[0] * abs(client.db_channel.id)
    end_id = collected[-1] * abs(client.db_channel.id)
    string = f"get-{start_id}-{end_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    await message.reply(f"<b>Here is your custom batch link:</b>\n\n<code>{link}</code>", reply_markup=reply_markup)