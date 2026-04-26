import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot import Bot
from config import (
    HELP_TXT, ABOUT_TXT, START_MSG, PRICE1, PRICE2, PRICE3, PRICE4, PRICE5,
    UPI_ID, SCREENSHOT_URL, OWNER_ID, ANIME_BANNERS
)
from database.database import db
from helper_func import is_subscribed, get_sub_status

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data

    if data == "help":
        await query.message.edit_text(
            text=HELP_TXT.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('ʜᴏᴍᴇ', callback_data='start'),
                 InlineKeyboardButton("ᴄʟᴏꜱᴇ", callback_data='close')]
            ])
        )

    elif data == "about":
        await query.message.edit_text(
            text=ABOUT_TXT.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('ʜᴏᴍᴇ', callback_data='start'),
                 InlineKeyboardButton('ᴄʟᴏꜱᴇ', callback_data='close')]
            ])
        )

    elif data == "start":
        await query.message.edit_text(
            text=START_MSG.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ʜᴇʟᴘ", callback_data='help'),
                 InlineKeyboardButton("ᴀʙᴏᴜᴛ", callback_data='about')]
            ])
        )

    elif data == "premium":
        await query.message.delete()
        await client.send_photo(
            chat_id=query.message.chat.id,
            photo=random.choice(ANIME_BANNERS),
            caption=(
                f"👋 {query.from_user.username}\n\n"
                f"🎖️ Available Plans :\n\n"
                f"● {PRICE1}  For 0 Days Prime Membership\n\n"
                f"● {PRICE2}  For 1 Month Prime Membership\n\n"
                f"● {PRICE3}  For 3 Months Prime Membership\n\n"
                f"● {PRICE4}  For 6 Months Prime Membership\n\n"
                f"● {PRICE5}  For 1 Year Prime Membership\n\n\n"
                f"💵 ASK UPI ID TO ADMIN AND PAY THERE -  <code>{UPI_ID}</code>\n\n\n"
                f"♻️ After Payment You Will Get Instant Membership \n\n\n"
                f"‼️ Must Send Screenshot after payment & If anyone want custom time membrship then ask admin"
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "ADMIN 24/7", url=(SCREENSHOT_URL)
                        )
                    ],
                    [InlineKeyboardButton("🔒 Close", callback_data="close")],
                ]
            )
        )

    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass


    elif data.startswith("rfs_ch_"):
        cid = int(data.split("_")[2])
        try:
            chat = await client.get_chat(cid)
            mode = await db.get_channel_mode(cid)
            status = "🟢 ᴏɴ" if mode == "on" else "🔴 ᴏғғ"
            new_mode = "ᴏғғ" if mode == "on" else "on"
            buttons = [
                [InlineKeyboardButton(f"ʀᴇǫ ᴍᴏᴅᴇ {'OFF' if mode == 'on' else 'ON'}", callback_data=f"rfs_toggle_{cid}_{new_mode}")],
                [InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="fsub_back")]
            ]
            await query.message.edit_text(
                f"Channel: {chat.title}\nCurrent Force-Sub Mode: {status}",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except Exception:
            await query.answer("Failed to fetch channel info", show_alert=True)

    elif data.startswith("rfs_toggle_"):
        cid, action = data.split("_")[2:]
        cid = int(cid)
        mode = "on" if action == "on" else "off"

        await db.set_channel_mode(cid, mode)
        await query.answer(f"Force-Sub set to {'ON' if mode == 'on' else 'OFF'}")

        # Refresh the same channel's mode view
        chat = await client.get_chat(cid)
        status = "🟢 ON" if mode == "on" else "🔴 OFF"
        new_mode = "off" if mode == "on" else "on"
        buttons = [
            [InlineKeyboardButton(f"ʀᴇǫ ᴍᴏᴅᴇ {'OFF' if mode == 'on' else 'ON'}", callback_data=f"rfs_toggle_{cid}_{new_mode}")],
            [InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="fsub_back")]
        ]
        await query.message.edit_text(
            f"Channel: {chat.title}\nCurrent Force-Sub Mode: {status}",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif data == "fsub_back":
        channels = await db.show_channels()
        buttons = []
        for cid in channels:
            try:
                chat = await client.get_chat(cid)
                mode = await db.get_channel_mode(cid)
                status = "🟢" if mode == "on" else "🔴"
                buttons.append([InlineKeyboardButton(f"{status} {chat.title}", callback_data=f"rfs_ch_{cid}")])
            except:
                continue

        await query.message.edit_text(
            "sᴇʟᴇᴄᴛ ᴀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴛᴏɢɢʟᴇ ɪᴛs ғᴏʀᴄᴇ-sᴜʙ ᴍᴏᴅᴇ:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif data.startswith("ck"):
        user_id = query.from_user.id
        if await is_subscribed(client, user_id):
            await query.answer("All channels joined! Delivering files...", show_alert=False)
            await query.message.delete()

            parts = data.split("_", 1)
            # Ensure the message's from_user is the person who clicked the button
            query.message.from_user = query.from_user

            if len(parts) > 1:
                payload = parts[1]
                from plugins.start import send_files
                await send_files(client, query.message, payload)
            else:
                from plugins.start import start_command
                query.message.text = "/start"
                await start_command(client, query.message)
        else:
            await query.answer("You haven't joined all channels yet!", show_alert=True)
            # Refresh the Force Sub UI
            status_list = await get_sub_status(client, user_id)
            buttons = []
            status_text = ""
            for i, status in enumerate(status_list, 1):
                icon = "✅" if status['is_joined'] else "❌"
                status_text += f"{i}. {icon} {status['name']} ⚡ {'Joined' if status['is_joined'] else 'Not Joined'}\n"
                if not status['is_joined']:
                    buttons.append([InlineKeyboardButton(text=f"📢 {status['name']}", url=status['link'])])

            buttons.append([InlineKeyboardButton("🔄 Try Again", callback_data=data)])

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

            # Edit the message to show updated status
            try:
                await query.message.edit_caption(
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
            except Exception as e:
                print(f"Error editing fsub message: {e}")
