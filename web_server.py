
from aiohttp import web
import os
import secrets
import json
import aiohttp
import aiohttp_jinja2
import jinja2
from config import BASE_URL, VERIFY_BOT_USERNAME
from database.database import db

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_handler(request):
    return web.Response(text="ᴀɴɪᴢᴏɴᴇꜰʟɪx API GATEWAY ᴠ11.0 [STABLE]", content_type="text/plain")

@routes.get("/api/check_session/{session_id}")
async def api_check_session(request):
    # Endpoint for Verification Bot to validate a session
    session_id = request.match_info.get('session_id')
    session = await db.sessions.find_one({"session_id": session_id})
    if not session:
        return web.json_response({"success": False, "error": "Invalid session"}, status=404)

    return web.json_response({
        "success": True,
        "user_id": session.get('user_id'),
        "bot_username": session.get('bot_username'),
        "status": session.get('status'),
        "expiry": session.get('expiry')
    })

@routes.post("/api/verify_complete/{session_id}")
async def api_verify_complete(request):
    # Endpoint for Verification Bot to mark verification as done
    session_id = request.match_info.get('session_id')
    try:
        data = await request.json()
        secure_token = data.get('secure_token')

        # Update session status
        result = await db.sessions.update_one(
            {"session_id": session_id, "status": "pending"},
            {"$set": {"status": "verified", "secure_token": secure_token}}
        )

        if result.modified_count > 0:
            return web.json_response({"success": True})
        return web.json_response({"success": False, "error": "Session not found or already verified"}, status=400)
    except:
        return web.json_response({"success": False, "error": "Invalid request"}, status=400)

@routes.get("/v/{secure_token}")
async def user_return_handler(request):
    # This route handles the user redirect from the verification frontend back to the Main Bot
    secure_token = request.match_info.get('secure_token')
    session = await db.get_session_by_token(secure_token)

    if not session:
        return web.Response(text="Verification Error: Session invalid or expired.", status=403)

    bot_username = session.get('bot_username')
    return_url = f"https://t.me/{bot_username}?start=verify_{secure_token}"

    # Simple redirect UI
    html = f"""
    <html><body style="background:#020617;color:#38bdf8;display:flex;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;">
    <div style="text-align:center;">
        <p>Verification Success. Returning to Bot...</p>
        <script>setTimeout(() => {{ window.location.href = "{return_url}"; }}, 1000);</script>
    </div>
    </body></html>
    """
    return web.Response(text=html, content_type="text/html")

@routes.get("/health")
async def health(request): return web.Response(text="OK")

async def web_server(bot):
    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))
    app['bot'] = bot
    app.add_routes(routes)
    return app
