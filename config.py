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

import os
import random
from os import environ,getenv
import logging
from logging.handlers import RotatingFileHandler

#OTAKULUX on Tg
#--------------------------------------------
#Bot token @OTAKULUX
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "8710949806:AAEnxn2AcaC09GoUWK_mLqLiV9Dt3M79zi8")
APP_ID = int(os.environ.get("APP_ID", "22266643")) #Your API ID from my.telegram.org
API_HASH = os.environ.get("API_HASH", "7d0b85b4146034511b8776ed7ff99de4") #Your API Hash from my.telegram.org
#--------------------------------------------

CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1003748914288")) #Your db channel Id
OWNER = os.environ.get("OWNER", "alonekingstarback") # Owner username without @OTAKULUX
OWNER_ID = int(os.environ.get("OWNER_ID", "8646416973")) # Owner id
#--------------------------------------------
PORT = os.environ.get("PORT", "8001")
#--------------------------------------------
DB_URI = os.environ.get("DATABASE_URL", "mongodb+srv://hemanthbreaker2027:9550399779htr@cluster0.haybbxg.mongodb.net/?appName=Cluster0")
DB_NAME = os.environ.get("DATABASE_NAME", "Cluster0")
#--------------------------------------------
FSUB_LINK_EXPIRY = int(os.getenv("FSUB_LINK_EXPIRY", "10"))  # 0 means no expiry
BAN_SUPPORT = os.environ.get("BAN_SUPPORT", "https://t.me/OTAKULUX")
TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "200"))
#--------------------------------------------
# Random Anime Banners (Neon / Dark Theme)
ANIME_BANNERS = [
    "https://telegra.ph/file/ec17880d61180d3312d6a.jpg", # Zoro
    "https://telegra.ph/file/e292b12890b8b4b9dcbd1.jpg", # Solo Leveling
    "https://telegra.ph/file/3e83c69804826b3cba066-16cffa90cd682570da.jpg", # Naruto
    "https://telegra.ph/file/ec17880d61180d3312d6a.jpg", # Add more
    "https://telegra.ph/file/e292b12890b8b4b9dcbd1.jpg"
]

START_PIC = random.choice(ANIME_BANNERS)
FORCE_PIC = random.choice(ANIME_BANNERS)

#--------------------------------------------
SHORTLINK_URL = os.environ.get("SHORTLINK_URL", "arolinks.com")
SHORTLINK_API = os.environ.get("SHORTLINK_API", "e49643875c2fa34dd6087254e58283d65ffc7748")
RECAPTCHA_SITE_KEY = os.environ.get("RECAPTCHA_SITE_KEY", "6LfvWswsAAAAADgpyWripb1IZSbBjlniKAmdBjSv")
RECAPTCHA_SECRET_KEY = os.environ.get("RECAPTCHA_SECRET_KEY", "6LfvWswsAAAAAEwc1yAjAVX0IXPsxIe1FHNtwVco")
SECURE_SECRET_KEY = os.environ.get("SECURE_SECRET_KEY", "HJjdgddjdodkdbdbdmdksksiwkwoahsbdndododjdndndmdkdjdbdmdosjsbsbwkwkwjsbdbdndkdkdkdjdbdbdndndndndna amalapapaksbsbsn")
WEBSITE_URL = os.environ.get("WEBSITE_URL", "filestore-1-9iz2.onrender.com") # e.g. https://yourdomain.com
JWT_SECRET = os.environ.get("JWT_SECRET", "anizoneflix_secret_key")
TUT_VID = os.environ.get("TUT_VID","https://t.me/anizoneflix")
WRAPPED_URL_DOMAIN = os.environ.get("WRAPPED_URL_DOMAIN", "theimmigrationworld.com")
WHITELISTED_DOMAINS = ["arolinks.com", "vshort.in", "gplinks.in"] # Add more as needed

SHORT_MSG = "<b>⚡️ <blockquote>˹ ʜᴇʀᴇ ɪs ʏᴏᴜʀ sᴇᴄᴜʀᴇ ʟɪɴᴋ ˼\n\n🛡 sᴏʟᴠᴇ ᴛʜᴇ sʜᴏʀᴛɴᴇʀ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ᴛᴏ ᴜɴʟᴏᴄᴋ ʏᴏᴜʀ ꜰɪʟᴇs. ᴍᴜsᴛ ᴡᴀᴛᴄʜ ᴛᴜᴛᴏʀɪᴀʟ ɪꜰ ʏᴏᴜ ᴀʀᴇ sᴛᴜᴄᴋ! 💫</blockquote></b>"

SHORTENER_PIC = random.choice(ANIME_BANNERS)
#--------------------------------------------

#--------------------------------------------
HELP_TXT = "<b>⚡️ <blockquote>˹ ᴀɴɪᴢᴏɴᴇꜰʟɪx ʜᴇʟᴘ ᴄᴇɴᴛᴇʀ ˼\n\n💎 ᴛʜɪs ɪs ᴀɴ ᴜʟᴛʀᴀ-ꜰᴀsᴛ ꜰɪʟᴇ ᴛᴏ ʟɪɴᴋ ʙᴏᴛ ᴘᴏᴡᴇʀᴇᴅ ʙʏ @AniZoneFlix\n\n📜 ᴄᴏᴍᴍᴀɴᴅ ʟɪsᴛ:\n├ /start : ɪɢɴɪᴛᴇ ᴛʜᴇ ʙᴏᴛ 🔥\n├ /about : ᴅɪsᴄᴏᴠᴇʀ ᴏᴜʀ ʟᴇɢᴀᴄʏ 🛡\n└ /help : sᴇᴇᴋ ɢᴜɪᴅᴀɴᴄᴇ ✨\n\n🚀 sɪᴍᴘʟʏ ᴄʟɪᴄᴋ ᴀɴʏ ʟɪɴᴋ, ᴊᴏɪɴ ᴛʜᴇ ꜰᴏʀᴄᴇ sᴜʙ ᴄʜᴀɴɴᴇʟs, ᴀɴᴅ ʏᴏᴜ ᴀʀᴇ ʀᴇᴀᴅʏ ᴛᴏ ɢᴏ...!\n\n👑 ᴅᴇᴠᴇʟᴏᴘᴇᴅ ᴡɪᴛʜ ❤️ ʙʏ <a href=https://t.me/AniZoneFlix>ᴀɴɪᴢᴏɴᴇꜰʟɪx</a></blockquote></b>"
ABOUT_TXT = "<b>🛡 <blockquote>˹ ᴀɴɪᴢᴏɴᴇꜰʟɪx ʟᴇɢᴀᴄʏ ˼\n\n👤 ᴄʀᴇᴀᴛᴏʀ: <a href=https://t.me/AniZoneFlix>ᴀɴɪᴢᴏɴᴇꜰʟɪx</a>\n💎 ꜰᴏᴜɴᴅᴇʀ: @AniZoneFlix\n🌀 ᴀɴɪᴍᴇ: @AniZoneFlix\n🎬 sᴇʀɪᴇs: @AniZoneFlix\n🔞 ᴀᴅᴜʟᴛ: @AniZoneFlix\n🛠 ᴅᴇᴠᴇʟᴏᴘᴇʀ: @AniZoneFlix</blockquote></b>"
#--------------------------------------------
#--------------------------------------------
START_MSG = os.environ.get("START_MESSAGE", "<b>⚡️ ʜᴇʟʟᴏ {mention} ˼\n\n<blockquote>💎 ɪ ᴀᴍ ᴛʜᴇ ᴍᴏsᴛ ᴘᴏᴡᴇʀꜰᴜʟ ꜰɪʟᴇ sᴛᴏʀᴇ ᴇɴɢɪɴᴇ. ɪ ᴄᴀɴ sᴛᴏʀᴇ ʏᴏᴜʀ ᴘʀɪᴠᴀᴛᴇ ꜰɪʟᴇs sᴇᴄᴜʀᴇʟʏ ᴡɪᴛʜ ᴜʟᴛʀᴀ-ꜰᴀsᴛ sᴘᴇᴇᴅ. ⚡️</blockquote></b>")
FORCE_MSG = os.environ.get("FORCE_SUB_MESSAGE", "⚡️ ʜᴇʟʟᴏ {mention}\n\n<b><blockquote>🛡 ˹ ᴀᴄᴄᴇss ᴅᴇɴɪᴇᴅ ˼\n\n💎 ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ᴀɴᴅ ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ ʀᴇʟᴏᴀᴅ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴜɴʟᴏᴄᴋ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛᴇᴅ ꜰɪʟᴇ. 🚀</b></blockquote>")

CMD_TXT = """🛡 <b><blockquote>˹ ᴀᴅᴍɪɴ ᴄᴏʀᴇ ᴄᴏɴᴛʀᴏʟ ˼</blockquote></b>

💎 <b>›› /auto_delete :</b> sᴇᴛ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇ 🕒
💎 <b>›› /check_dlt_time :</b> ᴄʜᴇᴄᴋ ᴄᴜʀʀᴇɴᴛ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇ 🔍
💎 <b>›› /dbroadcast :</b> ʙʀᴏᴀᴅᴄᴀsᴛ ᴍᴇᴅɪᴀ 📢
💎 <b>›› /ban :</b> ʀᴇsᴛʀɪᴄᴛ ᴀ ᴜsᴇʀ 🚫
💎 <b>›› /unban :</b> ʟɪꜰᴛ ʀᴇsᴛʀɪᴄᴛɪᴏɴ 🔓
💎 <b>›› /banlist :</b> sʜᴏᴡ ʙʟᴏᴄᴋᴇᴅ ᴇɴᴛɪᴛɪᴇs 💀
💎 <b>›› /addchnl :</b> ᴀᴅᴅ ꜰᴏʀᴄᴇ sᴜʙ 🔗
💎 <b>›› /delchnl :</b> ʀᴇᴍᴏᴠᴇ ꜰᴏʀᴄᴇ sᴜʙ ❌
💎 <b>›› /listchnl :</b> ᴠɪᴇᴡ ᴀʟʟ ᴄʜᴀɴɴᴇʟs 📋
💎 <b>›› /fsub_mode :</b> ᴛᴏɢɢʟᴇ ꜰsᴜʙ ᴍᴏᴅᴇ ⚙️
💎 <b>›› /pbroadcast :</b> sᴇɴᴅ ᴘʜᴏᴛᴏ ʙʀᴏᴀᴅᴄᴀsᴛ 🖼
💎 <b>›› /add_admin :</b> ᴇʟᴇᴠᴀᴛᴇ ᴛᴏ ᴀᴅᴍɪɴ 👑
💎 <b>›› /deladmin :</b> ʀᴇᴠᴏᴋᴇ ᴀᴅᴍɪɴ ᴘᴏᴡᴇʀ 📉
💎 <b>›› /admins :</b> ʟɪsᴛ ᴀʟʟ ᴀᴅᴍɪɴs 👥
💎 <b>›› /addpremium :</b> ɢʀᴀɴᴛ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss 💎
💎 <b>›› /premium_users :</b> sʜᴏᴡ ᴇʟɪᴛᴇ ᴜsᴇʀs ⭐
💎 <b>›› /remove_premium :</b> ʀᴇᴍᴏᴠᴇ ᴘʀᴇᴍɪᴜᴍ ᴛɪᴇʀ 📉
💎 <b>›› /myplan :</b> ᴠɪᴇᴡ ʏᴏᴜʀ ᴅᴇsᴛɪɴʏ 📜
💎 <b>›› /count :</b> sᴛᴀᴛɪsᴛɪᴄs 📊
💎 <b>›› /delreq :</b> ᴄʟᴇᴀɴᴜᴘ ᴅᴀᴛᴀʙᴀsᴇ 🧹
"""
#--------------------------------------------
CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", "<b>• ʙʏ @AniZoneFlix</b>") #set your Custom Caption here, Keep None for Disable Custom Caption
PROTECT_CONTENT = True if os.environ.get('PROTECT_CONTENT', "False") == "True" else False #set True if you want to prevent users from forwarding files from bot
#--------------------------------------------
#Set true if you want Disable your Channel Posts Share button
DISABLE_CHANNEL_BUTTON = os.environ.get("DISABLE_CHANNEL_BUTTON", None) == 'True'
#--------------------------------------------
BOT_STATS_TEXT = "<b>BOT UPTIME</b>\n{uptime}"
USER_REPLY_TEXT = "ʙᴀᴋᴋᴀ ! ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴍʏ ꜱᴇɴᴘᴀɪ!!"

#==========================(BUY PREMIUM)====================#

OWNER_TAG = os.environ.get("OWNER_TAG", "ᴀɴɪᴢᴏɴᴇꜰʟɪx")
UPI_ID = os.environ.get("UPI_ID", "AniZoneFlix@AniZoneFlix")
QR_PIC = random.choice(ANIME_BANNERS)
SCREENSHOT_URL = os.environ.get("SCREENSHOT_URL", f"t.me/AniZoneFlix")
#--------------------------------------------
#Time and its price
#7 Days
PRICE1 = os.environ.get("PRICE1", "0 rs")
#1 Month
PRICE2 = os.environ.get("PRICE2", "60 rs")
#3 Month
PRICE3 = os.environ.get("PRICE3", "150 rs")
#6 Month
PRICE4 = os.environ.get("PRICE4", "280 rs")
#1 Year
PRICE5 = os.environ.get("PRICE5", "550 rs")

#===================(END)========================#

LOG_FILE_NAME = "filesharingbot.txt"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME,
            maxBytes=50000000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
