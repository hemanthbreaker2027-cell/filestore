# OTAKULUX File Sharing Bot

OTAKULUX is a high-speed, secure Telegram bot designed for seamless file sharing and streaming. It allows administrators to store files in a private database channel and generate unique, trackable links for users to access them.

## 🚀 Key Features

- **Concurrent File Delivery**: Optimized for speed using asynchronous semaphore-based delivery.
- **Premium Streaming & Download**:
  - Integrated high-quality web player with glassmorphism UI.
  - Direct support for external Android players: **VLC, MX Player, PLAYit, and KMPlayer**.
  - unbypassable security timers and verification system.
- **Advanced Metadata Parsing**: Automatically extracts Quality (4K-360p), Season, and Episode from filenames.
- **Flexible Management**:
  - Multi-channel Force Subscription (Join Verification).
  - Auto-deletion of delivered files to keep user chats clean.
  - Comprehensive admin dashboard for user and channel management.
  - /batch and /genlink commands for instant link generation.

## ⚙️ Administrative Commands

| Command | Description |
|:---|:---|
| `/start` | Initial interaction with the bot |
| `/batch` | Generate a link for a range of files |
| `/genlink` | Generate a link for a single file |
| `/auto_delete` | Set the auto-deletion timer (in seconds) |
| `/add_admin` | (Owner Only) Add new administrators |
| `/broadcast` | Send messages to all bot users |
| `/dbroadcast` | Broadcast with auto-deletion |
| `/ban` / `/unban` | Manage user access |

## 🛠 Setup & Installation

### Prerequisites
- Python 3.9+
- MongoDB Database
- Telegram API Credentials (API_ID, API_HASH, BOT_TOKEN)

### Deployment
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/OTAKULUX/OTAKULUX-Bot.git
   cd OTAKULUX-Bot
   ```
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment Variables**:
   Create a `.env` file or set variables directly:
   - `TG_BOT_TOKEN`: Your Telegram Bot Token
   - `APP_ID`: Telegram API ID
   - `API_HASH`: Telegram API Hash
   - `DATABASE_URL`: MongoDB Connection URI
   - `CHANNEL_ID`: Database Channel ID
   - `OWNER_ID`: Your Telegram User ID
   - `WEBSITE_URL`: Your public domain (for streaming/verification)

4. **Run the Bot**:
   ```bash
   python3 bot.py
   ```

## 🤝 Support
Join our Telegram channel for updates and support: [@OTAKULUX](https://t.me/OTAKULUX)

---
© 2025 OTAKULUX. Released under the MIT License.
