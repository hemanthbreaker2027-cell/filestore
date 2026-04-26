
from aiohttp import web
import aiohttp
import jwt
import time
import hashlib
import uuid
import asyncio
from config import TURNSTILE_SITE_KEY, TURNSTILE_SECRET_KEY, JWT_SECRET, WEBSITE_URL, SHORTLINK_URL, SHORTLINK_API
from plugins.turnstile_html import TURNSTILE_HTML, BANNED_HTML, BOT_DETECTED_HTML
from helper_func import get_shortlink
from database.database import db

routes = web.RouteTableDef()

# Configuration
TIMER_THRESHOLD = 100 # 100 seconds
BAN_STRIKE_1 = 3   # 1 hour ban
BAN_STRIKE_2 = 5   # 24 hour ban
BAN_STRIKE_3 = 10  # Permanent ban

def get_real_ip(request):
    return request.headers.get('CF-Connecting-IP') or request.headers.get('X-Forwarded-For', request.remote)

def get_identifier(request):
    ip = get_real_ip(request)
    ua = request.headers.get('User-Agent', '')
    return hashlib.sha256(f"{ip}{ua}".encode()).hexdigest()

async def check_ban(identifier):
    record = await db.get_bypass_record(identifier)
    if record and record.get('ban_status'):
        if time.time() < record.get('ban_expiry'):
            return record
        else:
            await db.reset_bypass_attempts(identifier)
    return None

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("OTAKULUX FileStore Secure v2")

@routes.get("/verify/{payload}")
async def turnstile_page(request):
    identifier = get_identifier(request)
    ban_record = await check_ban(identifier)
    if ban_record:
        return web.HTTPFound("/banned")

    payload = request.match_info['payload']
    session_id = str(uuid.uuid4())

    # Create initial session JWT with server-side start_time
    init_token = jwt.encode({
        'session_id': session_id,
        'start_time': time.time(),
        'ip': get_real_ip(request),
        'ua': request.headers.get('User-Agent', ''),
        'payload': payload
    }, JWT_SECRET, algorithm='HS256')

    html = TURNSTILE_HTML.replace("{{ SITE_KEY }}", TURNSTILE_SITE_KEY) \
                        .replace("{{ PAYLOAD }}", payload) \
                        .replace("{{ SESSION_ID }}", session_id)

    response = web.Response(text=html, content_type='text/html')
    # Set a short-lived cookie for verification context
    response.set_cookie('v_session', init_token, httponly=True, secure=True, samesite='Lax', max_age=600)
    return response

@routes.post("/verify_token")
async def verify_turnstile(request):
    identifier = get_identifier(request)
    ban_record = await check_ban(identifier)
    if ban_record:
        return web.json_response({"success": False, "message": "You are banned.", "banned": True}, status=403)

    ip = get_real_ip(request)
    try:
        data = await request.json()
        token = data.get('token')
        payload = data.get('payload')
        session_id = data.get('session_id')
        v_session = request.cookies.get('v_session')

        if not v_session:
            return web.json_response({"success": False, "message": "Session expired. Refreshing..."}, status=400)

        try:
            decoded_v = jwt.decode(v_session, JWT_SECRET, algorithms=['HS256'])
        except:
            return web.json_response({"success": False, "message": "Invalid session. Refreshing..."}, status=400)

        # Validate session integrity
        if decoded_v.get('session_id') != session_id or \
           decoded_v.get('ip') != ip or \
           decoded_v.get('payload') != payload:
            return web.json_response({"success": False, "message": "Security mismatch. Refreshing..."}, status=403)

        # ⏳ unbypassable Backend Timer Enforcement
        elapsed = time.time() - decoded_v.get('start_time')
        if elapsed < TIMER_THRESHOLD:
            # 🔁 BYPASS DETECTED -> LOOP SYSTEM
            await db.increment_bypass_attempt(identifier)
            record = await db.get_bypass_record(identifier)
            attempts = record.get('attempts_count', 0)

            # Progressive Banning
            if attempts >= BAN_STRIKE_3:
                await db.ban_user_bypass(identifier, -1) # Permanent
                return web.json_response({"success": False, "message": "Bypass detected. Permanent block issued.", "banned": True}, status=403)
            elif attempts == BAN_STRIKE_2:
                await db.ban_user_bypass(identifier, 24)
                return web.json_response({"success": False, "message": "Bypass detected. 24h block issued.", "banned": True}, status=403)
            elif attempts == BAN_STRIKE_1:
                await db.ban_user_bypass(identifier, 1)
                return web.json_response({"success": False, "message": "Bypass detected. 1h block issued.", "banned": True}, status=403)

            # If not banned, generate new shortlink loop
            new_verify_link = f"{WEBSITE_URL}/verify/{payload}"
            new_short_link = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, new_verify_link)

            return web.json_response({
                "success": False,
                "loop": True,
                "message": "Bypass detected. Security timer was not completed. Solve again using the new link.",
                "new_link": new_short_link
            }, status=403)

        # Verify token with Cloudflare
        client_session = request.app['client_session']
        async with client_session.post('https://challenges.cloudflare.com/turnstile/v0/siteverify', data={
            'secret': TURNSTILE_SECRET_KEY,
            'response': token,
            'remoteip': ip
        }) as resp:
            result = await resp.json()

        if result.get('success'):
            # Success -> Reset attempts and allow redirect
            await db.reset_bypass_attempts(identifier)

            # Optional: small security delay
            await asyncio.sleep(1.5)

            final_token = jwt.encode({
                'payload': payload,
                'iat': int(time.time()),
                'exp': int(time.time()) + 3600
            }, JWT_SECRET, algorithm='HS256')

            final_dest = f"{WEBSITE_URL}/f/{payload}"
            short_url_result = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, final_dest)

            response = web.json_response({"success": True, "redirect": short_url_result})
            response.set_cookie('session', final_token, httponly=True, secure=True, samesite='Lax')
            response.del_cookie('v_session')
            return response
        else:
            return web.json_response({"success": False, "message": "Turnstile verification failed. Please try again."}, status=403)

    except Exception as e:
        print(f"Error in verify: {e}")
        return web.json_response({"success": False, "message": "Internal security error."}, status=500)

@routes.get("/banned")
async def banned_page(request):
    identifier = get_identifier(request)
    ban_record = await check_ban(identifier)
    if not ban_record:
        return web.HTTPFound("/")

    expiry = ban_record.get('ban_expiry')
    if expiry >= 9999999999:
        msg = "You are permanently blocked from using this system due to repeated bypass attempts."
        time_str = None
    else:
        msg = "You are temporarily blocked due to repeated bypass attempts."
        remaining = int(expiry - time.time())
        hours, remainder = divmod(remaining, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str = f"{hours}h {minutes}m {seconds}s"

    html = BANNED_HTML.replace("{{ MESSAGE }}", msg)
    if time_str:
        html = html.replace("{{ TIME_LEFT }}", time_str).replace("{{ TIME_BOX_CLASS }}", "")
    else:
        html = html.replace("{{ TIME_LEFT }}", "").replace("{{ TIME_BOX_CLASS }}", "hidden")

    return web.Response(text=html, content_type='text/html')

@routes.get("/bot-detected")
async def bot_detected(request):
    return web.Response(text=BOT_DETECTED_HTML, content_type='text/html')

@routes.get("/vlc/{payload}")
async def vlc_redirect(request):
    payload = request.match_info['payload']
    stream_url = f"{request.scheme}://{request.host}/file/{payload}"
    vlc_url = f"vlc://{stream_url}"
    html = f"<html><head><script>window.location.replace('{vlc_url}');</script></head><body>Redirecting to VLC...</body></html>"
    return web.Response(text=html, content_type='text/html')

@routes.get("/mx/{payload}")
async def mx_redirect(request):
    payload = request.match_info['payload']
    stream_url = f"{request.scheme}://{request.host}/file/{payload}"
    mx_url = f"intent://{stream_url}#Intent;package=com.mxtech.videoplayer.ad;end"
    html = f"<html><head><script>window.location.replace('{mx_url}');</script></head><body>Redirecting to MX Player...</body></html>"
    return web.Response(text=html, content_type='text/html')

@routes.get("/playit/{payload}")
async def playit_redirect(request):
    payload = request.match_info['payload']
    stream_url = f"{request.scheme}://{request.host}/file/{payload}"
    playit_url = f"intent://{stream_url}#Intent;package=com.playit.videoplayer;end"
    html = f"<html><head><script>window.location.replace('{playit_url}');</script></head><body>Redirecting to PLAYit...</body></html>"
    return web.Response(text=html, content_type='text/html')

@routes.get("/watch/{payload}")
async def watch_page(request):
    payload = request.match_info['payload']
    bot = request.app.get('bot')
    from helper_func import decode

    try:
        decoded_payload = await decode(payload)
        argument = decoded_payload.split("-")
        if len(argument) < 2:
             return web.Response(text="Invalid Payload", status=400)

        msg_id = int(int(argument[1]) / abs(bot.db_channel.id))
        msg = await bot.get_messages(bot.db_channel.id, msg_id)

        if not msg or not (msg.video or msg.document):
            return web.Response(text="Video not found.", status=404)

        media = msg.video or msg.document
        file_name = media.file_name or "video"

        # Use relative paths for the stream URL
        stream_url = f"/file/{payload}"

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Streaming: {file_name} - OTAKULUX</title>
    <style>
        body {{ background-color: #0f0f12; color: #fff; font-family: 'Segoe UI', sans-serif; margin: 0; display: flex; flex-direction: column; align-items: center; min-height: 100vh; }}
        .header {{ width: 100%; padding: 1rem; text-align: center; background: #1a1a24; border-bottom: 1px solid #333; }}
        .player-container {{ width: 100%; max-width: 900px; margin-top: 2rem; background: #000; border-radius: 8px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
        video {{ width: 100%; display: block; }}
        .controls {{ margin-top: 2rem; display: flex; flex-wrap: wrap; justify-content: center; gap: 1rem; padding: 0 1rem 3rem; }}
        .btn {{ text-decoration: none; padding: 0.8rem 1.5rem; border-radius: 5px; font-weight: bold; transition: 0.2s; color: #000; background: #00ffcc; text-align: center; min-width: 150px; }}
        .btn:hover {{ transform: scale(1.05); opacity: 0.9; }}
        .vlc {{ background: #ff9900; }}
        .mx {{ background: #0088cc; color: #fff; }}
        .playit {{ background: #ff4d4d; color: #fff; }}
        .title {{ margin: 1rem; color: #00ffcc; font-size: 1.2rem; text-align: center; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>OTAKULUX Stream</h1>
    </div>
    <div class="title">{file_name}</div>
    <div class="player-container">
        <video controls autoplay>
            <source src="{stream_url}" type="video/mp4">
            Your browser does not support the video tag.
        </video>
    </div>
    <div class="controls">
        <a href="{stream_url}" class="btn">📥 Download</a>
        <a href="vlc://{request.scheme}://{request.host}{stream_url}" class="btn vlc">▶️ Play in VLC</a>
        <a href="intent://{request.scheme}://{request.host}{stream_url}#Intent;package=com.mxtech.videoplayer.ad;end" class="btn mx">▶️ Play in MX Player</a>
        <a href="intent://{request.scheme}://{request.host}{stream_url}#Intent;package=com.playit.videoplayer;end" class="btn playit">▶️ Play in PLAYit</a>
    </div>
</body>
</html>
"""
        return web.Response(text=html, content_type='text/html')

    except Exception as e:
        print(f"Watch Page Error: {e}")
        return web.Response(text=f"Error loading stream page: {e}", status=500)

@routes.get("/file/{payload}")
async def direct_download(request):
    payload = request.match_info['payload']
    bot = request.app.get('bot')
    from helper_func import decode

    try:
        decoded_payload = await decode(payload)
        argument = decoded_payload.split("-")
        if len(argument) < 2:
             return web.Response(text="Invalid Payload", status=400)

        msg_id = int(int(argument[1]) / abs(bot.db_channel.id))
        msg = await bot.get_messages(bot.db_channel.id, msg_id)

        if not msg or not (msg.document or msg.video or msg.audio):
            return web.Response(text="File not found or not a media file.", status=404)

        media = msg.document or msg.video or msg.audio
        file_name = media.file_name or "file"
        file_size = media.file_size
        mime_type = media.mime_type or "application/octet-stream"

        # Basic Range support
        range_header = request.headers.get('Range')
        start = 0
        end = file_size - 1

        if range_header:
            ranges = range_header.replace('bytes=', '').split('-')
            start = int(ranges[0]) if ranges[0] else 0
            end = int(ranges[1]) if len(ranges) > 1 and ranges[1] else file_size - 1

        if start >= file_size:
            return web.Response(status=416)

        headers = {
            'Content-Type': mime_type,
            'Content-Disposition': f'attachment; filename="{file_name}"',
            'Accept-Ranges': 'bytes',
            'Content-Length': str(end - start + 1),
            'Content-Range': f'bytes {start}-{end}/{file_size}',
        }

        res = web.StreamResponse(status=206 if range_header else 200, headers=headers)
        await res.prepare(request)

        try:
            async for chunk in bot.stream_media(media, offset=start, limit=end-start+1):
                await res.write(chunk)
        except Exception as e:
            print(f"Error during streaming: {e}")

        return res

    except Exception as e:
        print(f"Direct Download Error: {e}")
        return web.Response(text=f"Download Error: {e}", status=500)

@routes.get("/f/{payload}")
async def final_redirect(request):
    payload = request.match_info['payload']
    session_cookie = request.cookies.get('session')

    if not session_cookie:
        return web.HTTPFound(f"/verify/{payload}")

    try:
        decoded = jwt.decode(session_cookie, JWT_SECRET, algorithms=['HS256'])
        if decoded.get('payload') != payload:
            return web.HTTPFound(f"/verify/{payload}")

        bot = request.app.get('bot')
        from helper_func import decode

        try:
            decoded_payload = await decode(payload)
            argument = decoded_payload.split("-")
            if len(argument) < 2:
                 return web.Response(text="Invalid Payload", status=400)

            msg_id = int(int(argument[1]) / abs(bot.db_channel.id))
            msg = await bot.get_messages(bot.db_channel.id, msg_id)

            if not msg or not (msg.document or msg.video or msg.audio):
                return web.Response(text="File not found or not a media file.", status=404)

            media = msg.document or msg.video or msg.audio
            file_name = media.file_name or "file"
            file_size = media.file_size
            mime_type = media.mime_type or "application/octet-stream"

            # Basic Range support
            range_header = request.headers.get('Range')
            start = 0
            end = file_size - 1

            if range_header:
                ranges = range_header.replace('bytes=', '').split('-')
                start = int(ranges[0]) if ranges[0] else 0
                end = int(ranges[1]) if len(ranges) > 1 and ranges[1] else file_size - 1

            if start >= file_size:
                return web.Response(status=416)

            chunk_size = 1024 * 1024 # 1MB
            headers = {
                'Content-Type': mime_type,
                'Content-Disposition': f'attachment; filename="{file_name}"',
                'Accept-Ranges': 'bytes',
                'Content-Length': str(end - start + 1),
                'Content-Range': f'bytes {start}-{end}/{file_size}',
            }

            res = web.StreamResponse(status=206 if range_header else 200, headers=headers)
            await res.prepare(request)

            try:
                async for chunk in bot.stream_media(media, offset=start, limit=end-start+1):
                    await res.write(chunk)
            except Exception as e:
                print(f"Error during streaming: {e}")

            return res

        except Exception as e:
            print(f"Streaming Error: {e}")
            # Fallback to bot redirect if streaming fails critically
            username = bot.username if bot else "OTAKULUX"
            return web.HTTPFound(f"https://t.me/{username}?start=yu3elk{payload}7")

    except Exception as e:
        print(f"JWT/Session Error: {e}")
        return web.HTTPFound(f"/verify/{payload}")
