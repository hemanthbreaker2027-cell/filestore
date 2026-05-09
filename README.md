
# AniZoneFlix FileStore Bot v6.0 - Zero Buffering Edition 🚀

An advanced Telegram FileStore bot with a high-performance streaming engine designed for zero buffering, instant playback, and seamless external player integration.

## 🌟 Key Features

- **Zero-Buffering Engine V6:** Rewritten from the ground up to eliminate delays.
- **Instant Seeking:** Skip through videos without loading loops.
- **Parallel Prefetching:** Pre-fetches chunks from Telegram while streaming to ensure constant data flow.
- **External Player Support:** Optimized intents for MX Player, VLC, and PLAYit.
- **Modular Design:** Independent Web (Streaming/Download) and Bot services.
- **Mobile First:** Minimalist UI designed for high-speed mobile browsing.
- **Multi-Cloud Support:** Ready to deploy on Vercel, Render, Koyeb, and Heroku.

## 🚀 Deployment Guide

### 1. Vercel (Web Service Only)
To deploy the streaming engine on Vercel:
1. Fork this repository.
2. In Vercel, create a new project and select your fork.
3. Add the following Environment Variables:
   - `DATABASE_URL`: Your MongoDB Connection String.
   - `APP_ID`, `API_HASH`, `TG_BOT_TOKEN`.
   - `RECAPTCHA_SITE_KEY`, `RECAPTCHA_SECRET_KEY`.
4. Deploy! Vercel will handle the `web/` directory automatically.

### 2. Koyeb / Render / Railway
Recommended for the Full Bot + Web service:
1. Create a new service from your fork.
2. Use the provided `Procfile` for the run command.
3. Configure all Environment Variables from `config.py`.
4. Koyeb/Render will detect the `web` process and expose the streaming port.

### 3. Heroku
1. Click the "Deploy to Heroku" button or use the Heroku CLI.
2. The `app.json` is pre-configured with all required fields.

## 🛠 Repository Structure

- `/web`: Core high-speed streaming and download engine.
- `/plugins`: Bot commands and handlers.
- `/templates`: Ultra-fast minimalist UI templates.
- `/database`: MongoDB abstraction layer.

## ⚙️ Environment Variables

| Variable | Description |
| --- | --- |
| `TG_BOT_TOKEN` | Your Telegram Bot Token. |
| `DATABASE_URL` | MongoDB Connection URI. |
| `WEBSITE_URL` | Your deployment domain (without https://). |
| `CHANNEL_ID` | Telegram Channel ID for file storage. |
| `RECAPTCHA_SITE_KEY` | Google reCAPTCHA v3 Site Key. |

## ❤️ Credits
- Developed by [AniZoneFlix](https://t.me/AniZoneFlix)
- Inspired by FileToLink and TG-FileStreamBot architectures.

---
**Disclaimer:** This bot is for educational purposes only. Always comply with Telegram's Terms of Service.
