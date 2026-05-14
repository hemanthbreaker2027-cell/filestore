
# AniZoneFlix FileStore Bot v6.0 - Universal Link Protection Flow 🚀

An advanced Telegram FileStore bot with a secure, multi-layer link protection system and a high-performance streaming engine.

## 🛡️ Universal Link Protection Flow

The bot implements a strict, secure gateway for all file access:

1.  **Bot Layer:** Generates a tamper-proof, time-limited protected link using JWT (HS256).
2.  **Protected Link Layer:** `https://yourdomain.com/protect?data=<signed_token>`
3.  **Frontend Verification Layer:** A mandatory 10-second timer page that validates token integrity.
4.  **Backend Verification Layer:** Validates the JWT, expiry, and request authenticity.
5.  **Converted Wrapped URL Layer:** Backend converts the internal code into a "Wrapped URL" (e.g., `theimmigrationworld.com`) ONLY after successful verification.
6.  **Final Destination:** User is redirected to the file or destination.

## 🌟 Key Features

- **Zero-Buffering Engine V6:** High-speed streaming and parallel prefetching.
- **Dynamic Control Panel:** Toggle shortener, streaming, and delivery settings in real-time via `/panel`.
- **JWT Security:** All links are signed and expire after use or timeout.
- **Wrapped URL Masking:** Original mapping logic and shortener links are never exposed to the frontend.
- **Chrome-Only Enforcement:** Optional security layer for browser-specific access.

## 🚀 Deployment Guide

### 1. Render (Recommended)
1.  **Fork** this repository.
2.  Create a new **Web Service** on Render.
3.  **Environment Variables:**
    - `TG_BOT_TOKEN`: Your Telegram Bot Token.
    - `APP_ID` & `API_HASH`: From [my.telegram.org](https://my.telegram.org).
    - `DATABASE_URL`: MongoDB Connection URI.
    - `WEBSITE_URL`: Your Render app URL (e.g., `myapp.onrender.com`).
    - `SECURE_SECRET_KEY`: A long, random string for JWT signing.
    - `WRAPPED_URL_DOMAIN`: The domain for final redirection (e.g., `theimmigrationworld.com`).
4.  **Build Command:** `pip install -r requirements.txt`
5.  **Start Command:** `python3 main.py` (This starts both the Bot and the Web Server).

### 2. Heroku
1.  Click the **Deploy to Heroku** button or use the CLI.
2.  The `app.json` and `Procfile` are pre-configured.
3.  Fill in the Config Vars in the Heroku Dashboard.

## 🛠 Admin Panel Commands

- `/panel` or `/settings`: Open the core control dashboard.
- `/stream on/off`: Globally toggle streaming buttons.
- `/download on/off`: Globally toggle download buttons.
- `/addpremium`: Grant premium (bypass) access to users.

## ⚙️ Core Configuration Variables

| Variable | Description |
| --- | --- |
| `SHORTLINK_URL` | Shortener domain (e.g., `arolinks.com`). |
| `SHORTLINK_API` | API Key for your shortener. |
| `SECURE_SECRET_KEY`| Key used for JWT encryption. **Keep this private.** |
| `WRAPPED_URL_DOMAIN`| The domain used for the final conversion step. |

---
**Developed by [AniZoneFlix](https://t.me/AniZoneFlix)**
