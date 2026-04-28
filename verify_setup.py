
import asyncio
from bot import Bot
from plugins.route import routes
from aiohttp import web
import os

async def verify_frontend():
    # This is a manual check script
    print("Checking templates...")
    for t in ['safe', 'verify', 'banned']:
        if os.path.exists(f"templates/{t}.html"):
            print(f"✅ {t}.html exists")
        else:
            print(f"❌ {t}.html missing")

if __name__ == "__main__":
    asyncio.run(verify_frontend())
