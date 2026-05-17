# ˹ ᴀɴɪᴢᴏɴᴇꜰʟɪx ꜱᴇᴄᴜʀᴇ ꜰɪʟᴇ ꜱᴛᴏʀᴇ ᴠ11.0 ˼

A high-performance, secure Telegram File Store Bot with an integrated **Codeflix Verification Network** protocol.

## 🌟 Key Features
- **Codeflix Network Integration:** Centralized verification via a separate bot for maximum security.
- **Dual-Bot Flow:** Secure hand-off between Main Bot and Verification Bot.
- **Daily Verification Deals:** Limit free users to a specific number of verifications per day.
- **Dynamic Control Panel:** Toggle verification and delivery settings in real-time via `/panel`.
- **Auto-Delete Engine:** Automatically terminates shared files after a set timer to prevent leaks.
- **Advanced Batch System:** Generate single or bulk file links with ease.
- **Premium Tier:** Bypass verification for elite users.
- **Forcesub:** Supports multiple channels with join-request validation.

## 🚀 Deployment

### 1. Environment Variables
| Variable | Description |
|----------|-------------|
| `TG_BOT_TOKEN` | Your Telegram Bot Token. |
| `APP_ID` | Your Telegram App ID. |
| `API_HASH` | Your Telegram API Hash. |
| `OWNER_ID` | Your Telegram User ID. |
| `DATABASE_URL` | MongoDB Connection URI. |
| `DATABASE_NAME` | MongoDB Database Name. |
| `CHANNEL_ID` | Telegram Channel ID for file storage. |
| `BASE_URL` | Your deployment URL (e.g. https://your-app.onrender.com). |
| `VERIFY_BOT_USERNAME` | The username of your separate Verification Bot. |

### 2. Fast Deploy
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## 🛠 Commands
- `/start` - Start the engine.
- `/batch` - Create a batch link (Admin).
- `/genlink` - Generate a single link (Admin).
- `/panel` - Owner Control Panel.
- `/stats` - View bot statistics (Admin).
- `/count` - Daily verification count (Admin).

## 🛡 Security
The system uses the **Codeflix Verification Network** protocol. When a user requests content, a unique session is generated in MongoDB. The user is redirected to the Verification Bot, which validates the session and returns a secure token. This ensures that only verified users can access the content, preventing automated scraping and bypasses.

---
**Developed with ❤️ by [AniZoneFlix](https://t.me/AniZoneFlix)**
