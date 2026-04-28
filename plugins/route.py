import asyncio
import time
import hashlib
import os
from aiohttp import web
from jinja2 import Environment, FileSystemLoader
from config import (
    RECAPTCHA_SITE_KEY, RECAPTCHA_SECRET_KEY, WEBSITE_URL,
    SHORTLINK_URL, SHORTLINK_API
)
from helper_security import secure_redirect
from helper_func import get_shortlink
from database.database import db

routes = web.RouteTableDef()

# Jinja2 Environment
template_env = Environment(loader=FileSystemLoader('templates'))

def get_real_ip(request):
    return request.headers.get('CF-Connecting-IP') or request.headers.get('X-Forwarded-For', request.remote)

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("OTAKULUX Secure Redirect v3 (Non-Cloudflare)")

@routes.get("/safe")
async def safe_page_handler(request):
    link = request.query.get('link')
    if not link:
        return web.Response(text="Missing link parameter.", status=400)

    # Anti-Bot: rate limiting
    ip = get_real_ip(request)
    if not await db.check_rate_limit(ip):
        return web.Response(text="Rate limit exceeded.", status=429)

    template = template_env.get_template('safe.html')
    html = template.render(
        RECAPTCHA_SITE_KEY=RECAPTCHA_SITE_KEY,
        LINK=link
    )
    return web.Response(text=html, content_type='text/html')

@routes.post("/api/verify_safe")
async def verify_safe_handler(request):
    ip = get_real_ip(request)

    # 1. Anti-Bot: Rate limiting (Increased for user convenience)
    if not await db.check_rate_limit(ip, limit=10, window=30):
        return web.json_response({"success": False, "message": "Please slow down."}, status=429)

    # 2. Enhanced API Security: Header key check
    # This prevents direct automated POSTs without passing through the frontend landing page
    sec_key = request.headers.get('X-Security-Key')
    if not sec_key or len(sec_key) < 32:
        return web.json_response({"success": False, "message": "Access denied."}, status=403)

    # 3. Throttling: Small server-side delay to stop rapid mining
    await asyncio.sleep(1.2)

    # 4. Relaxed Header validation (Bypass detection removed)
    try:
        data = await request.json()
        link_id = data.get('link')
        captcha_token = data.get('captcha')

        if not link_id or not captcha_token:
            return web.json_response({"success": False, "message": "Invalid request."}, status=400)

        # 3. Verify reCAPTCHA v3
        client_session = request.app['client_session']
        async with client_session.post('https://www.google.com/recaptcha/api/siteverify', data={
            'secret': RECAPTCHA_SECRET_KEY,
            'response': captcha_token,
            'remoteip': ip
        }) as resp:
            recaptcha_result = await resp.json()

        if not recaptcha_result.get('success') or recaptcha_result.get('score', 0) < 0.5:
            return web.json_response({"success": False, "message": "High-risk activity detected."}, status=403)

        # 4. Generate signed redirect token (One-time use, 60s expiry)
        payload = {
            'link': link_id,
            'exp': int(time.time()) + 60,
            'iat': int(time.time())
        }
        # Generate extreme long link
        signed_token = secure_redirect.encrypt(payload, min_length=120000)

        # 5. Construct verification URL and shorten it
        verify_url = f"{WEBSITE_URL}/verify?token={signed_token}"
        shortlink = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, verify_url)

        # 6. Return Google-style redirect method
        google_redirect = f"https://www.google.com/url?q={shortlink}"

        return web.json_response({
            "success": True,
            "redirect": google_redirect
        })

    except Exception as e:
        print(f"Verify Safe Error: {e}")
        return web.json_response({"success": False, "message": "Internal error."}, status=500)

@routes.get("/verify")
async def final_verify_handler(request):
    token = request.query.get('token')
    if not token:
        return web.HTTPFound("/safe")

    # 1. Validate Token
    payload = secure_redirect.decrypt(token)
    if not payload:
        return web.HTTPFound("/safe")

    # 2. Integrity checks (Expiry and One-time use)
    if time.time() > payload.get('exp', 0):
        return web.HTTPFound("/safe")

    token_hash = hashlib.sha256(token.encode()).hexdigest()
    if not await db.use_secure_token(token_hash):
        return web.HTTPFound("/safe")

    # 4. Final Redirect to Bot
    bot = request.app.get('bot')
    username = bot.username if bot else "OTAKULUX"
    final_payload = payload['link']

    return web.HTTPFound(f"https://t.me/{username}?start=yu3elk{final_payload}7")

@routes.get("/watch/{payload}")
async def watch_page_handler(request):
    payload = request.match_info.get('payload')
    if not payload:
        return web.Response(text="Invalid payload.", status=400)

    from helper_func import decode
    try:
        decoded = await decode(payload)
        # payload format is "get-{msg_id}"
        msg_id = int(decoded.split("-")[1])
    except Exception:
        return web.Response(text="Invalid link.", status=400)

    bot = request.app['bot']
    db_id = abs(bot.db_channel.id)
    real_msg_id = msg_id // db_id

    try:
        msg = await bot.get_messages(bot.db_channel.id, real_msg_id)
        if not msg or msg.empty:
            return web.Response(text="File not found or deleted.", status=404)

        # Determine file name and size
        file = msg.document or msg.video or msg.audio
        file_name = getattr(file, 'file_name', 'Unnamed File')
        file_size = getattr(file, 'file_size', 0)

        def get_readable_size(size):
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size < 1024:
                    return f"{size:.2f} {unit}"
                size /= 1024

        template = template_env.get_template('watch.html')
        html = template.render(
            file_name=file_name,
            file_size=get_readable_size(file_size),
            payload=payload
        )
        return web.Response(text=html, content_type='text/html')
    except Exception as e:
        print(f"Watch Error: {e}")
        return web.Response(text="Error fetching file details.", status=500)

@routes.get("/stream/{payload}")
async def stream_handler(request):
    payload = request.match_info.get('payload')
    from helper_func import decode
    try:
        decoded = await decode(payload)
        msg_id = int(decoded.split("-")[1])
    except Exception:
        return web.Response(text="Invalid link.", status=400)

    bot = request.app['bot']
    db_id = abs(bot.db_channel.id)
    real_msg_id = msg_id // db_id

    try:
        msg = await bot.get_messages(bot.db_channel.id, real_msg_id)
        if not msg or msg.empty:
            return web.Response(text="File not found.", status=404)

        file = msg.document or msg.video or msg.audio
        if not file:
            return web.Response(text="No media found.", status=404)

        # Support Range Requests
        range_header = request.headers.get('Range')
        offset = 0
        limit = file.file_size

        if range_header:
            # Simple Range Parser
            try:
                kind, range_val = range_header.split('=')
                if kind == 'bytes':
                    start, end = range_val.split('-')
                    offset = int(start)
                    if end:
                        limit = int(end) + 1
            except:
                pass

        # Use bot.stream_media if available, else standard delivery
        async def file_sender():
            async for chunk in bot.stream_media(file, offset=offset, limit=limit):
                yield chunk

        resp = web.StreamResponse(status=206 if range_header else 200)
        resp.headers['Content-Type'] = getattr(file, 'mime_type', 'application/octet-stream')
        resp.headers['Content-Disposition'] = f'attachment; filename="{getattr(file, "file_name", "file")}"'
        resp.headers['Accept-Ranges'] = 'bytes'

        if range_header:
            resp.headers['Content-Range'] = f'bytes {offset}-{limit-1}/{file.file_size}'
            resp.content_length = limit - offset
        else:
            resp.content_length = file.file_size

        await resp.prepare(request)
        async for chunk in file_sender():
            await resp.write(chunk)
        return resp

    except Exception as e:
        print(f"Stream Error: {e}")
        return web.Response(text="Streaming error.", status=500)

@routes.get("/health")
async def health_check(request):
    return web.Response(text="OK")
