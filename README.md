# 🛡️ AniZoneFlix: STRICT SECURITY FILE STORE ENGINE

Welcome to the **Supreme Version** of the AniZoneFlix File Store Bot. This system has been upgraded with **Government-Grade Security**, Anti-Bypass logic, and advanced Owner Controls.

---

## ⚡ Key Features

- **Maximum Security:** Google reCAPTCHA v3 (Strict Score 0.5+) validation.
- **Anti-Automation:** Advanced detection for bots, scripts, and headless browsers.
- **Controlled Delivery:** Toggleable Shortener System with multiple modes.
- **Dynamic Modes:**
    - **ONE PER TIME:** Verification required for every single request.
    - **BASED TIME:** Verification grants a time-limited access window (e.g., 1 hour).
- **AniZoneFlix UI/UX:** Premium Glassmorphism design with Zoro-themed aesthetics.
- **Reliable Media Delivery:** Guaranteed support for Videos, Photos, Stickers, and Emojis.

---

## 🛠️ Owner Control Panel

Accessible via `/panel` or `/settings`.

- **Shortener System Toggle:** Globally enable/disable the verification flow.
- **Mode Selection:**
    - `ONE PER TIME`: Strict verification for every file.
    - `BASED TIME`: Time-gated verification (User inputs validity in seconds).
- **File Delivery Toggle:** Stop/Resume all file delivery services.
- **Core Features:** Toggle bot maintenance mode.

---

## 🔒 Security Implementation

1. **reCAPTCHA v3 Strict Mode:** Requests with scores below `0.5` are automatically rejected to prevent automation.
2. **Backend Validation:** Server-side verification of User-Agents, IP identification, and one-time tokens.
3. **Wrapped URL System:** All shortlinks are wrapped in an additional security layer (`/protect` -> `/verify`) to prevent direct access to final destinations.
4. **Anti-Bypass Headers:** Checks for `webdriver` and browser environment consistency to block Tampermonkey/automation scripts.

---

## 🚀 Deployment Guide

### Environment Variables

| Variable | Description |
|----------|-------------|
| `TG_BOT_TOKEN` | Your Telegram Bot Token |
| `APP_ID` / `API_HASH` | Telegram API Credentials |
| `DATABASE_URL` | MongoDB Connection URI |
| `WEBSITE_URL` | Your Frontend Domain (e.g. `https://my-bot.render.com`) |
| `RECAPTCHA_SITE_KEY` | Google reCAPTCHA v3 Site Key |
| `RECAPTCHA_SECRET_KEY` | Google reCAPTCHA v3 Secret Key |
| `SHORTLINK_URL` | Primary Shortener Domain (e.g. `arolinks.com`) |
| `SHORTLINK_API` | Primary Shortener API Key |

---

## 💎 Commands

- `/start` - Ignite the engine.
- `/panel` - Owner-only Core Control Panel.
- `/add_admin` - Add a supreme administrator.
- `/addpremium` - Grant elite access to users (Bypasses Shortener).
- `/auto_delete` - Set the self-destruct timer for files.

---

**© 2025 AniZoneFlix. All Rights Reserved.**
