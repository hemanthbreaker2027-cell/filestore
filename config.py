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
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "8686791784:AAEx_yNKgwLbSMzL-536sofSPPwEeAV9btw")
APP_ID = int(os.environ.get("APP_ID", "22266643")) #Your API ID from my.telegram.org
API_HASH = os.environ.get("API_HASH", "7d0b85b4146034511b8776ed7ff99de4") #Your API Hash from my.telegram.org
#--------------------------------------------

CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1003967760305")) #Your db channel Id
OWNER = os.environ.get("OWNER", "OTAKULUX") # Owner username without @OTAKULUX
OWNER_ID = int(os.environ.get("OWNER_ID", "8797485479")) # Owner id
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
TURNSTILE_SITE_KEY = os.environ.get("TURNSTILE_SITE_KEY", "0x4AAAAAADAceZFJoAHEh_3r")
TURNSTILE_SECRET_KEY = os.environ.get("TURNSTILE_SECRET_KEY", "0x4AAAAAADAcefAQQ1HVBoYrubzJWrhuRTs")
WEBSITE_URL = os.environ.get("WEBSITE_URL", "https://filestore-1-xme9.onrender.com") # e.g. https://yourdomain.com
JWT_SECRET = os.environ.get("JWT_SECRET", "otakulux_secret_key")
TUT_VID = os.environ.get("TUT_VID","https://t.me/OTAKULUX/3")
SHORT_MSG = "<b>⌯ Here is Your Download Link, Must Watch Tutorial Before Clicking On Download...</b>"

SHORTENER_PIC = random.choice(ANIME_BANNERS)
#--------------------------------------------

#--------------------------------------------
HELP_TXT = "<b><blockquote>ᴛʜɪs ɪs ᴀɴ ғɪʟᴇ ᴛᴏ ʟɪɴᴋ ʙᴏᴛ ᴡᴏʀᴋ ғᴏʀ @OTAKULUX\n\n❏ ʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅs\n├/start : sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ\n├/about : ᴏᴜʀ Iɴғᴏʀᴍᴀᴛɪᴏɴ\n└/help : ʜᴇʟᴘ ʀᴇʟᴀᴛᴇᴅ ʙᴏᴛ\n\n sɪᴍᴘʟʏ ᴄʟɪᴄᴋ ᴏɴ ʟɪɴᴋ ᴀɴᴅ sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ ᴊᴏɪɴ ʙᴏᴛʜ ᴄʜᴀɴɴᴇʟs ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ ᴛʜᴀᴛs ɪᴛ.....!\n\n ᴅᴇᴠᴇʟᴏᴘᴇᴅ ʙʏ <a href=https://t.me/OTAKULUX>OTAKULUX</a></blockquote></b>"
ABOUT_TXT = "<b><blockquote>◈ ᴄʀᴇᴀᴛᴏʀ: <a href=https://t.me/OTAKULUX>OTAKULUX</a>\n◈ ꜰᴏᴜɴᴅᴇʀ ᴏꜰ : <a href=https://t.me/OTAKULUX>OTAKULUX</a>\n◈ ᴀɴɪᴍᴇ ᴄʜᴀɴɴᴇʟ : <a href=https://t.me/OTAKULUX>OTAKULUX</a>\n◈ sᴇʀɪᴇs ᴄʜᴀɴɴᴇʟ : <a href=https://t.me/OTAKULUX>OTAKULUX</a>\n◈ ᴀᴅᴜʟᴛ ᴍᴀɴʜᴡᴀ : <a href=https://t.me/OTAKULUX>OTAKULUX</a>\n◈ ᴅᴇᴠᴇʟᴏᴘᴇʀ : <a href=https://t.me/OTAKULUX>OTAKULUX</a></blockquote></b>"
#--------------------------------------------
#--------------------------------------------
START_MSG = os.environ.get("START_MESSAGE", "<b>ʜᴇʟʟᴏ {mention}\n\n<blockquote> ɪ ᴀᴍ ғɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ, ɪ ᴄᴀɴ sᴛᴏʀᴇ ᴘʀɪᴠᴀᴛᴇ ғɪʟᴇs ɪɴ sᴘᴇᴄɪғɪᴇᴅ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ᴏᴛʜᴇʀ ᴜsᴇʀs ᴄᴀɴ ᴀᴄᴄᴇss ɪᴛ ғʀᴏᴍ sᴘᴇᴄɪᴀʟ ʟɪɴᴋ.</blockquote></b>")
FORCE_MSG = os.environ.get("FORCE_SUB_MESSAGE", "ʜᴇʟʟᴏ {mention}\n\n<b><blockquote>ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ᴀɴᴅ ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ ʀᴇʟᴏᴀᴅ button ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛᴇᴅ ꜰɪʟᴇ.</b></blockquote>")

CMD_TXT = """<blockquote><b>» ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs:</b></blockquote>

<b>›› /auto_delete :</b> sᴇᴛ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇ
<b>›› /check_dlt_time :</b> ᴄʜᴇᴄᴋ ᴄᴜʀʀᴇɴᴛ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇ
<b>›› /dbroadcast :</b> ʙʀᴏᴀᴅᴄᴀsᴛ ᴅᴏᴄᴜᴍᴇɴᴛ / ᴠɪᴅᴇᴏ
<b>›› /ban :</b> ʙᴀɴ ᴀ ᴜꜱᴇʀ
<b>›› /unban :</b> ᴜɴʙᴀɴ ᴀ ᴜꜱᴇʀ
<b>›› /banlist :</b> ɢᴇᴛ ʟɪsᴛ ᴏꜰ ʙᴀɴɴᴇᴅ ᴜꜱᴇʀs
<b>›› /addchnl :</b> ᴀᴅᴅ ꜰᴏʀᴄᴇ sᴜʙ ᴄʜᴀɴɴᴇʟ
<b>›› /delchnl :</b> ʀᴇᴍᴏᴠᴇ ꜰᴏʀᴄᴇ sᴜʙ ᴄʜᴀɴɴᴇʟ
<b>›› /listchnl :</b> ᴠɪᴇᴡ ᴀᴅᴅᴇᴅ ᴄʜᴀɴɴᴇʟs
<b>›› /fsub_mode :</b> ᴛᴏɢɢʟᴇ ꜰᴏʀᴄᴇ sᴜʙ ᴍᴏᴅᴇ
<b>›› /pbroadcast :</b> sᴇɴᴅ ᴘʜᴏᴛᴏ ᴛᴏ ᴀʟʟ ᴜꜱᴇʀs
<b>›› /add_admin :</b> ᴀᴅᴅ ᴀɴ ᴀᴅᴍɪɴ
<b>›› /deladmin :</b> ʀᴇᴍᴏᴠᴇ ᴀɴ ᴀᴅᴍɪɴ
<b>›› /admins :</b> ɢᴇᴛ ʟɪsᴛ ᴏꜰ ᴀᴅᴍɪɴs
<b>›› /addpremium :</b> ᴀᴅᴅ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀ
<b>›› /premium_users :</b> ʟɪsᴛ ᴀʟʟ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀs
<b>›› /remove_premium :</b> ʀᴇᴍᴏᴠᴇ ᴘʀᴇᴍɪᴜᴍ ꜰʀᴏᴍ ᴀ ᴜꜱᴇʀ
<b>›› /myplan :</b> ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ sᴛᴀᴛᴜs
<b>›› /count :</b> ᴄᴏᴜɴᴛ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴs
<b>›› /delreq :</b> Rᴇᴍᴏᴠᴇᴅ ʟᴇғᴛᴏᴠᴇʀ ɴᴏɴ-ʀᴇǫᴜᴇsᴛ ᴜsᴇʀs
"""
#--------------------------------------------
CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", "<b>• ʙʏ @OTAKULUX</b>") #set your Custom Caption here, Keep None for Disable Custom Caption
PROTECT_CONTENT = True if os.environ.get('PROTECT_CONTENT', "False") == "True" else False #set True if you want to prevent users from forwarding files from bot
#--------------------------------------------
#Set true if you want Disable your Channel Posts Share button
DISABLE_CHANNEL_BUTTON = os.environ.get("DISABLE_CHANNEL_BUTTON", None) == 'True'
#--------------------------------------------
BOT_STATS_TEXT = "<b>BOT UPTIME</b>\n{uptime}"
USER_REPLY_TEXT = "ʙᴀᴋᴋᴀ ! ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴍʏ ꜱᴇɴᴘᴀɪ!!"

#==========================(BUY PREMIUM)====================#

OWNER_TAG = os.environ.get("OWNER_TAG", "OTAKULUX")
UPI_ID = os.environ.get("UPI_ID", "OTAKULUX@OTAKULUX")
QR_PIC = random.choice(ANIME_BANNERS)
SCREENSHOT_URL = os.environ.get("SCREENSHOT_URL", f"t.me/OTAKULUX")
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
   
