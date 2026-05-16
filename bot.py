
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

from aiohttp import web
import asyncio
import pyromod.listen
from pyrogram import Client
from pyrogram.types import BotCommand
from pyrogram.enums import ParseMode
import sys
import pytz
from datetime import datetime
#ᴀɴɪᴢᴏɴᴇꜰʟɪx on ᴛɢ
from config import *
from database.db_premium import *
from database.database import *
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

# Suppress APScheduler logs below WARNING level
logging.getLogger("apscheduler").setLevel(logging.WARNING)

scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
scheduler.add_job(remove_expired_users, "interval", seconds=10)

# Reset verify count for all users daily at 00:00 IST
async def daily_reset_task():
    try:
        await db.reset_all_verify_counts()
    except Exception:
        pass  

async def token_cleanup_task():
    try:
        await db.cleanup_tokens()
        await db.cleanup_strict_verifications()
    except Exception:
        pass

scheduler.add_job(daily_reset_task, "cron", hour=0, minute=0)
scheduler.add_job(token_cleanup_task, "interval", hours=1)
# scheduler.start() is called inside Bot.start() to ensure an active event loop


def get_indian_time():
    """Returns the current time in IST."""
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist)


name = """
 BY AniZoneFlix BOTS
"""

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={
                "root": "plugins"
            },
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        scheduler.start()
        # Automatically unblock all users on restart
        try:
            await db.clear_all_bans()
            self.LOGGER(__name__).info("All users have been unblocked successfully on startup.")
        except Exception as e:
            self.LOGGER(__name__).error(f"Failed to unblock users: {e}")
        usr_bot_me = await self.get_me()
        self.uptime = get_indian_time()

        # Set Bot Commands Automatically
        try:
            await self.set_bot_commands([
                BotCommand("start", "🚀 Start the bot"),
                BotCommand("ping", "🏓 Check responsiveness"),
                BotCommand("myplan", "🎖️ Check your premium status"),
                BotCommand("about", "⚠️ About the bot"),
                BotCommand("help", "❓ Help and commands"),
                BotCommand("commands", "⚙️ Admin commands list"),
                BotCommand("auto_delete", "🕒 Set file auto-delete timer (Admin)"),
                BotCommand("check_auto_delete", "🔍 Check auto-delete timer (Admin)"),
                BotCommand("batch", "📦 Create a batch link (Admin)"),
                BotCommand("genlink", "🔗 Generate a single link (Admin)"),
                BotCommand("panel", "🛠️ Owner Control Panel"),
                BotCommand("stats", "📊 Bot Statistics (Admin)"),
                BotCommand("users", "👥 Total Users (Admin)"),
                BotCommand("admins", "👥 List Admins (Admin)"),
                BotCommand("add_admin", "👑 Add Admin (Owner)"),
                BotCommand("deladmin", "📉 Remove Admin (Owner)"),
                BotCommand("addpremium", "💎 Add Premium User (Admin)"),
                BotCommand("remove_premium", "📉 Remove Premium User (Admin)"),
                BotCommand("premium_users", "⭐ List Premium Users (Admin)"),
                BotCommand("count", "📊 Total Verified Tokens Today (Admin)")
            ])
        except Exception as e:
            self.LOGGER(__name__).error(f"Failed to set bot commands: {e}")

        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id = db_channel.id, text = "Test Message")
            await test.delete()
        except Exception as e:
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).warning(f"Make Sure bot is Admin in DB Channel, and Double check the CHANNEL_ID Value, Current Value {CHANNEL_ID}")
            self.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/AniZoneFlix for support")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info(f"Bot Running..!\n\nCreated by \nhttps://t.me/AniZoneFlix")
        self.LOGGER(__name__).info(r"""


  ___ ___  ___  ___ ___ _    _____  _____  ___ _____ ___ 
 / __/ _ \|   \| __| __| |  |_ _\ \/ / _ )/ _ \_   _/ __|
| (_| (_) | |) | _|| _|| |__ | | >  <| _ \ (_) || | \__ \
 \___\___/|___/|___|_| |____|___/_/\_\___/\___/ |_| |___/
                                                         
 
                                          """)

        self.set_parse_mode(ParseMode.HTML)
        self.username = usr_bot_me.username
        self.LOGGER(__name__).info(f"Bot Running..! Made by @AniZoneFlix")

        # Start Web Server (Late Import to avoid circular dependency)
        from plugins import web_server
        app = web.AppRunner(await web_server(self))
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", PORT).start()


        try: await self.send_message(OWNER_ID, text = f"<b><blockquote> Bᴏᴛ Rᴇsᴛᴀʀᴛᴇᴅ by @AniZoneFlix</blockquote></b>")
        except: pass

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")

    def run(self):
        """Run the bot."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.start())
        self.LOGGER(__name__).info("Bot is now running. Thanks to @AniZoneFlix")
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            self.LOGGER(__name__).info("Shutting down...")
        finally:
            loop.run_until_complete(self.stop())

#
# Copyright (C) 2025 by AniZoneFlix@AniZoneFlix, < https://github.com/AniZoneFlix >.
#
# This file is part of < https://t.me/AniZoneFlix > project,
# and is released under the MIT License.
# Please see < https://t.me/AniZoneFlix/blob/master/LICENSE >
#
# All rights reserved.