
from aiohttp import web
import os
import secrets
import json
import aiohttp
from config import BASE_URL, VERIFY_BOT_USERNAME
from database.database import db

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_handler(request):
    return web.Response(text="ᴀɴɪᴢᴏɴᴇꜰʟɪx CODEFLIX NETWORK NODE ᴠ11.0", content_type="text/plain")

@routes.get("/v/{secure_token}")
async def codeflix_return_handler(request):
    # This route handles the return from Verification Bot to Main Bot
    secure_token = request.match_info.get('secure_token')
    if not secure_token: return web.Response(text="Missing Secure Token", status=400)

    # 1. Look up session by secure_token
    session = await db.get_session_by_token(secure_token)
    if not session:
        return web.Response(text="Invalid or Expired Token", status=403)

    # 2. Redirect back to Main Bot with the deep link
    main_bot_username = session.get('bot_username')
    return_url = f"https://t.me/{main_bot_username}?start=verify_{secure_token}"

    # 3. Simple Redirect UI
    html = f"""
    <html>
    <head>
        <title>Codeflix Verification | Redirecting</title>
        <style>
            body {{ background: #020617; color: #38bdf8; display: flex; align-items: center; justify-content: center; height: 100vh; font-family: sans-serif; margin: 0; }}
            .loader {{ border: 3px solid rgba(56, 189, 248, 0.1); border-left-color: #38bdf8; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin-bottom: 20px; }}
            @keyframes spin {{ 100% {{ transform: rotate(360deg); }} }}
            .container {{ text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="loader" style="margin: 0 auto 20px;"></div>
            <p>Verification Success. Returning to Bot...</p>
            <script>setTimeout(() => {{ window.location.href = "{return_url}"; }}, 1500);</script>
        </div>
    </body>
    </html>
    """
    return web.Response(text=html, content_type="text/html")

@routes.get("/health")
async def health(request): return web.Response(text="OK")

async def web_server(bot):
    app = web.Application()
    app['bot'] = bot
    app.add_routes(routes)
    return app
