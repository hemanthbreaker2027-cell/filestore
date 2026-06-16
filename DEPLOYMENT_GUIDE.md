# Secure Link System Deployment Guide 🚀

This guide explains how to deploy the new Chrome-only, same-tab secure link system.

## 🏗 Stack Overview
- **Bot**: Python (Pyrogram/Pyrofork)
- **Web Protection**: Next.js (TypeScript)
- **Streaming Engine**: Node.js (Fastify + GramJS)
- **Database**: MongoDB
- **Session Cache**: Redis (Optional but recommended for strict tab locking)

---

## 🚀 Step-by-Step Deployment

### 1. Environment Variables
Configure the following variables in your hosting provider (Render, Vercel, Railway, etc.):

#### 🤖 Bot & Common
- `TG_BOT_TOKEN`: Your Telegram Bot Token.
- `APP_ID` & `API_HASH`: From my.telegram.org.
- `DATABASE_URL`: MongoDB connection string.
- `REDIS_URL`: (Optional) Redis connection string for same-tab enforcement.
- `SECURE_SECRET_KEY`: A long random string for JWT signing.
- `WEBSITE_URL`: Your web deployment domain (e.g., `https://secure.yourdomain.com`).

#### 🌐 Web (Next.js)
- `DATABASE_URL`: Same as above.
- `SECURE_SECRET_KEY`: Same as above.

#### 🎥 Streaming Server
- `STREAM_PORT`: Port for the streaming server (default: 8080).
- `CHANNEL_ID`: Your database channel ID.

---

### 2. Deployment Platforms

#### Vercel (Web Frontend only)
1. Point Vercel to the `web-node` directory.
2. Add the environment variables.
3. Vercel will automatically build and deploy the Next.js app.

#### Render / Docker (Full Stack)
1. Use the provided `Dockerfile`.
2. For the streaming server, run:
   ```bash
   cd web-node && npm install && npm run stream
   ```
3. For the Bot:
   ```bash
   pip install -r requirements.txt && python3 main.py
   ```

---

### 🛡 Security Features
- **Chrome-Only**: Blocks Firefox, Safari, Edge, and other browsers via User-Agent and Feature Detection.
- **Same-Tab Lock**: Uses `BroadcastChannel` and `localStorage` (frontend) + Redis (backend) to prevent multi-tab access.
- **No CAPTCHA**: Replaced with behavioral checks and signed JWT payloads.
- **Link Wrapping**: Automatically converts shortener links to `theimmigrationworld.com` wrapped format.

---

## 🛠 Maintenance & Cleanup
- To update the secret key, change `SECURE_SECRET_KEY` in both Bot and Web environments. This will invalidate all active sessions.
- Logs for the streaming engine are handled by Fastify and can be viewed in your process manager.
