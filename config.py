
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
