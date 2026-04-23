# OTAKULUX - Premium Anime Streaming Ecosystem 🚀

A comprehensive solution for anime communities, combining a high-performance **Pyrogram Telegram Bot** for file storage and a **Premium Dark-Theme Website** for seamless streaming.

## 🌟 Key Features

### 🤖 Telegram Bot (Backend)
- **Advanced FileStore:** Interactive metadata collection (Anime Name, Season, Episode, Quality).
- **Auto-Enrichment:** Automatically fetches plots, ratings, and banners using the **Anilist API**.
- **Alphabetical Index:** User-friendly `/index` command to browse the entire library (A-Z).
- **Auto-Delete:** configurable timer to delete files from users' chats after delivery.
- **Force Subscribe:** Multi-channel join verification before file access.
- **Premium System:** Built-in subscription management for bypassing restrictions.

### 🌐 Streaming Website (Frontend)
- **Dynamic Homepage:** Real-time "Trending" and "Latest" grids synced with the bot's database.
- **Neon Aesthetic:** Premium dark mode UI with backdrop blurs and glowing accents.
- **Built-in Player:** Integrated **Video.js** player with support for seeking (HTTP Range requests).
- **External Player Support:** One-click links for **VLC**, **MX Player**, and **PlayIt**.
- **Security:** Cloudflare Turnstile protection with a mandatory backend security timer.

---

## 🛠️ Deployment Guide

### 1. Prerequisites
- **Telegram:** Get `APP_ID` and `API_HASH` from [my.telegram.org](https://my.telegram.org) and a `TG_BOT_TOKEN` from [@BotFather](https://t.me/BotFather).
- **Database:** A free cluster from [MongoDB Atlas](https://www.mongodb.com/cloud/atlas). Use the `DATABASE_URL` (SRV connection string).
- **Cloudflare:** Create a [Turnstile](https://dash.cloudflare.com/?to=/:account/turnstile) widget. Note the `SITE_KEY` and `SECRET_KEY`.

### 2. Environment Variables

| Variable | Description | Example |
| :--- | :--- | :--- |
| `TG_BOT_TOKEN` | Your Bot Token | `123456:ABCDE...` |
| `APP_ID` | Telegram App ID | `22266643` |
| `API_HASH` | Telegram API Hash | `7d0b85b41...` |
| `DATABASE_URL` | MongoDB Connection URI | `mongodb+srv://...` |
| `CHANNEL_ID` | Database Channel ID | `-100123456789` |
| `OWNER_ID` | Your Telegram User ID | `8797485479` |
| `WEBSITE_URL` | Your deployed website URL | `https://your-app.onrender.com` |
| `TURNSTILE_SITE_KEY` | Cloudflare Turnstile Site Key | `0x4AAAAAA...` |
| `TURNSTILE_SECRET_KEY` | Cloudflare Turnstile Secret Key | `0x4AAAAAA...` |
| `JWT_SECRET` | Secret for session tokens | `your_random_secret` |

### 3. Deploy to Render / Heroku / VPS

#### Option A: VPS (Docker)
```bash
git clone https://github.com/OTAKULUX/Bot.git
cd Bot
# Edit .env with your variables
docker build -t otakulux-bot .
docker run -p 8001:8001 otakulux-bot
```

#### Option B: Render / Heroku
1. Create a new Web Service.
2. Connect your GitHub repository.
3. Add all the environment variables listed above.
4. Set the build command: `pip install -r requirements.txt`
5. Set the start command: `python3 bot.py`

---

## 📖 Admin Usage

1. **Adding Anime:** Simply send a file to the bot. It will ask for details interactively.
2. **Setup Channels:** Use `/addchnl <channel_id>` to add force-subscription requirements.
3. **Manage Admins:** Use `/add_admin <user_id>` to authorize other users to add anime.
4. **Auto-Delete:** Use `/auto_delete <seconds>` to set the global file deletion timer.

## 🤝 Support
Join our Telegram channel for updates and support: [@OTAKULUX](https://t.me/OTAKULUX)

---
*Created with ❤️ by **OTAKULUX***
