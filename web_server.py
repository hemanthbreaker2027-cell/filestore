
from aiohttp import web
import os
import secrets
import json
import aiohttp
import aiohttp_jinja2
import jinja2
from config import BASE_URL, BACKEND_URL, VERIFY_BOT_USERNAME, RECAPTCHA_SECRET_KEY, RECAPTCHA_SITE_KEY
from database.database import db
from services.security import SecurityService, SecureRedirect

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_handler(request):
    return web.Response(text="ᴀɴɪᴢᴏɴᴇꜰʟɪx API BACKEND ᴠ11.0 [STABLE]", content_type="text/plain")

@routes.get("/api/r/{session_id}")
async def api_r_handler(request):
    session_id = request.match_info.get('session_id')
    if not session_id: return web.json_response({"error": "Missing Session ID"}, status=400)
    target = f"https://t.me/{VERIFY_BOT_USERNAME}?start={session_id}"
    if request.query.get('redirect') == 'true': return web.HTTPFound(target)
    return web.json_response({"target_url": target})

@routes.get("/api/v/{secure_token}")
async def api_v_handler(request):
    secure_token = request.match_info.get('secure_token')
    if not secure_token: return web.json_response({"error": "Missing Token"}, status=400)
    session = await db.get_session_by_token(secure_token)
    if not session: return web.json_response({"error": "Invalid Token"}, status=403)
    bot_username = session.get('bot_username')
    return_url = f"https://t.me/{bot_username}?start=verify_{secure_token}"
    if request.query.get('redirect') == 'true': return web.HTTPFound(return_url)
    return web.json_response({"return_url": return_url, "bot": bot_username})

@routes.get("/health")
async def health(request): return web.Response(text="OK")

async def web_server(bot):
    app = web.Application()
    app['bot'] = bot
    app.add_routes(routes)
    return app
