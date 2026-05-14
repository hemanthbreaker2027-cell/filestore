
from aiohttp import web
import time
import hashlib
import asyncio
import re
import os
import mimetypes
from urllib.parse import quote, urlparse, parse_qs
from config import WEBSITE_URL, WRAPPED_URL_DOMAIN, RECAPTCHA_SITE_KEY, RECAPTCHA_SECRET_KEY
from database.database import db
from services.security import SecurityService, SecureRedirect
from helper_func import decode, is_subscribed

routes = web.RouteTableDef()

# Template Cache
template_cache = {}

async def get_template(name):
    if name not in template_cache:
        try:
            with open(f"templates/{name}.html", "r") as f:
                template_cache[name] = f.read()
        except FileNotFoundError:
            return None
    return template_cache[name]

def json_response(success=True, message="", data=None, status=200):
    return web.json_response({
        "success": success,
        "message": message,
        "data": data or {}
    }, status=status)

@routes.get("/", allow_head=True)
async def root_handler(request):
    return web.Response(text="ᴀɴɪᴢᴏɴᴇꜰʟɪx ꜱᴇᴄᴜʀᴇ ꜱᴛʀᴇᴀᴍ ᴇɴɢɪɴᴇ ᴠ6.0 - High Speed Active", content_type="text/plain")

@routes.get("/r2/{userId}/{token}")
async def r2_landing_page(request):
    user_id = request.match_info['userId']
    token = request.match_info['token']
    html = await get_template("safe")
    if not html: return web.Response(text="Template Error", status=500)
    html = html.replace("{{ RECAPTCHA_SITE_KEY }}", RECAPTCHA_SITE_KEY).replace("{{ USER_ID }}", user_id).replace("{{ TOKEN }}", token)
    return web.Response(text=html, content_type="text/html")

@routes.post("/r2/verify")
async def r2_verify(request):
    try:
        data = await request.json()
        ip = SecurityService.get_client_ip(request)
        success, score = await SecurityService.verify_recaptcha(data.get('recaptchaToken'), ip, request.app['client_session'])
        if not success or score < 0.3: return json_response(False, "Security check failed", status=403)
        token_data = SecureRedirect.decrypt(data.get('linkToken'))
        if not token_data: return json_response(False, "Invalid Token", status=403)
        bot = request.app['bot']
        final_redirect = f"https://t.me/{bot.username}?start=yu3elk{token_data.get('payload')}7"
        user_id = request.match_info.get('userId')
        if user_id: await db.update_verify_status(int(user_id), is_verified=True, verified_time=time.time())
        return json_response(True, "Verified", {"redirect": final_redirect})
    except Exception: return json_response(False, "Error", status=500)

@routes.get("/protect")
async def protect_landing_page(request):
    token = request.query.get('data')
    if not token: return web.Response(text="Invalid Token", status=400)

    record = await db.get_strict_verification(token)
    if not record: return web.Response(text="Verification Link Expired", status=403)

    # 5-second verification page
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ultra Strict Verification</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: sans-serif; background: #0f172a; color: white; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; text-align: center; }
            .container { background: #1e293b; padding: 2rem; border-radius: 1rem; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }
            .timer { font-size: 3rem; font-weight: bold; color: #38bdf8; margin: 1rem 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Verifying Request...</h1>
            <div class="timer" id="timer">5</div>
            <p>Please wait while we secure your connection.</p>
        </div>
        <script>
            let timeLeft = 5;
            const timer = document.getElementById('timer');
            const countdown = setInterval(() => {
                timeLeft--;
                timer.textContent = timeLeft;
                if (timeLeft <= 0) {
                    clearInterval(countdown);
                    window.location.href = "/wrapped?data=" + "{token}";
                }
            }, 1000);
        </script>
    </body>
    </html>
    """.replace("{token}", token)
    return web.Response(text=html, content_type="text/html")

@routes.get("/wrapped")
async def wrapped_redirect(request):
    token = request.query.get('data')
    record = await db.get_strict_verification(token)
    if not record: return web.Response(text="Link Expired", status=403)

    destination = record.get('shortlink')
    if not destination:
        # Fallback if shortlink was not generated correctly
        code = record.get('code')
        from config import SHORTLINK_URL
        destination = f"https://{SHORTLINK_URL}/{code}"

    return web.HTTPFound(location=destination)

@routes.get("/verify-backend")
async def backend_verify_handler(request):
    token = request.query.get('data')
    if not token: return web.Response(text="Missing Token", status=400)

    success = await db.mark_strict_verified(token)
    if not success: return web.Response(text="Verification Failed or Already Verified", status=403)

    # 1-second verification page
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Verifying...</title>
        <meta http-equiv="refresh" content="1;url=https://t.me/{bot_username}?start=verify_{token}">
        <style>
            body { font-family: sans-serif; background: #0f172a; color: white; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
            .dot { animation: pulse 1s infinite; }
            @keyframes pulse { 0% { opacity: 0.2; } 50% { opacity: 1; } 100% { opacity: 0.2; } }
        </style>
    </head>
    <body>
        <h1>Verifying<span class="dot">...</span></h1>
    </body>
    </html>
    """.replace("{bot_username}", request.app['bot'].username).replace("{token}", token)
    return web.Response(text=html, content_type="text/html")


@routes.get("/eductionssstudiess/")
async def wrapped_url_handler(request):
    code = request.query.get('eductionstudiess')
    if not code: return web.Response(text="Invalid Request", status=400)

    record = await db.verify_shortener_code(code)
    if not record: return web.Response(text="Link Expired or Invalid", status=403)

    user_id, original_url = int(record.get('user_id')), record.get('original_url')
    parsed = urlparse(original_url)
    start_param = parse_qs(parsed.query).get('start', [''])[0]
    payload = start_param[6:-1] if start_param.startswith("yu3elk") else start_param

    # Update verification status in DB
    await db.update_verify_status(user_id, verify_token=payload, is_verified=True, verified_time=time.time())

    return web.HTTPFound(location=original_url)

@routes.post("/verify")
async def verify_protected_token(request):
    try:
        data = await request.json()
        token = data.get('data')

        # 1. Validate JWT
        payload = SecureRedirect.verify_protected_token(token)
        if not payload: return json_response(False, "Invalid or Expired Session", status=403)

        code = payload.get('code')

        # 2. Fetch latest wrapped domain from DB
        settings = await db.get_settings()
        domain = settings.get('wrapped_url_domain', WRAPPED_URL_DOMAIN)

        # 3. Return Converted Wrapped URL
        wrapped_url = f"https://{domain}/eductionssstudiess/?eductionstudiess={code}"
        return json_response(True, "Verified", {"redirect": wrapped_url})
    except Exception as e:
        print(f"[VERIFY ERROR] {e}")
        return json_response(False, "Internal Server Error", status=500)

@routes.get("/watch")
async def watch_handler(request):
    code = request.query.get('path')
    record = await db.verify_shortener_code(code)
    if not record: return web.Response(text="Invalid Link", status=403)
    file_name = record.get('file_name', 'video.mp4')
    stream_url = f"https://{request.host}/stream/file/{code}/{quote(file_name)}"
    html = await get_template("watch")
    if not html: return web.Response(text="Template Error", status=500)
    html = html.replace("{{ STREAM_URL }}", stream_url).replace("{{ FILE_NAME }}", file_name)
    return web.Response(text=html, content_type="text/html")

@routes.get("/download/{code}")
async def download_handler(request):
    return await stream_file_handler(request, is_download=True)

# Optimized Streaming/Download Engine with Parallel Delivery Logic
@routes.get("/stream/file/{code}")
@routes.get("/stream/file/{code}/{filename}")
async def stream_file_handler(request, is_download=False):
    code = request.match_info.get('code')
    record = await db.verify_shortener_code(code)
    if not record: return web.Response(text="Forbidden", status=403)

    bot = request.app['bot']
    original_url = record.get('original_url', '')
    msg_id = None

    match = re.search(r"get-(\d+)", original_url)
    if match: msg_id = int(int(match.group(1)) / abs(bot.db_channel.id))
    else:
        match = re.search(r"start=(?:yu3elk)?([a-zA-Z0-9_-]+)7?", original_url)
        if match:
            try:
                decoded = await decode(match.group(1))
                inner = re.search(r"(?:get-)?(\d+)", decoded)
                if inner: msg_id = int(int(inner.group(1)) / abs(bot.db_channel.id))
            except: pass

    if not msg_id: return web.Response(text="Media Not Found", status=404)

    try:
        msg = await bot.get_messages(bot.db_channel.id, msg_id)
        file_obj = msg.video or msg.document
        if not file_obj: return web.Response(text="No Streamable Media", status=404)

        file_size = file_obj.file_size
        range_header = request.headers.get('Range', 'bytes=0-')

        start, end = 0, file_size - 1
        if range_header:
            try:
                ranges = re.findall(r'(\d+)', range_header)
                start = int(ranges[0])
                if len(ranges) > 1: end = int(ranges[1])
            except: pass

        if start >= file_size: return web.Response(status=416, headers={'Content-Range': f'bytes */{file_size}'})

        mime_type = file_obj.mime_type or mimetypes.guess_type(file_obj.file_name or "")[0] or 'video/mp4'

        status = 206 if range_header else 200
        resp = web.StreamResponse(status=status)
        resp.headers.update({
            'Content-Type': mime_type,
            'Content-Length': str(end - start + 1),
            'Accept-Ranges': 'bytes',
            'Content-Range': f'bytes {start}-{end}/{file_size}',
            'Access-Control-Allow-Origin': '*',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'X-Content-Type-Options': 'nosniff',
            'X-Robots-Tag': 'noindex, nofollow'
        })

        if is_download:
            resp.headers['Content-Disposition'] = f'attachment; filename="{quote(file_obj.file_name or "file")}"'
            resp.headers['Content-Transfer-Encoding'] = 'binary'

        await resp.prepare(request)

        # ENGINE V9: Dynamic High-Throughput Pipe
        # We use larger chunks for high-speed delivery
        chunk_size = 3 * 1024 * 1024 if is_download else 1.5 * 1024 * 1024

        # Parallel Prefetch Optimization
        prefetch_limit = 10 if is_download else 5
        queue = asyncio.Queue(maxsize=prefetch_limit)
        stop_event = asyncio.Event()

        async def prefetcher():
            try:
                async for chunk in bot.stream_media(file_obj, offset=start, limit=end-start+1):
                    if stop_event.is_set(): break
                    await queue.put(chunk)
                await queue.put(None)
            except: await queue.put(None)

        prefetch_task = asyncio.create_task(prefetcher())

        try:
            while True:
                chunk = await queue.get()
                if chunk is None: break
                await resp.write(chunk)
                queue.task_done()
                if not is_download: await resp.drain()
        finally:
            stop_event.set()
            prefetch_task.cancel()
            try: await prefetch_task
            except: pass

        await resp.write_eof()
        return resp
    except Exception as e:
        print(f"Download Error: {e}")
        return web.Response(text="Error", status=500)

@routes.get("/health")
async def health(request): return web.Response(text="OK")
