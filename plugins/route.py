import asyncio
import jwt
import time
import hashlib
import uuid
import os
from aiohttp import web
from jinja2 import Environment, FileSystemLoader
from config import (
    TURNSTILE_SITE_KEY, TURNSTILE_SECRET_KEY, JWT_SECRET, WEBSITE_URL,
    SHORTLINK_URL, SHORTLINK_API
)
from plugins.turnstile_html import TURNSTILE_HTML, BANNED_HTML, BOT_DETECTED_HTML
from helper_func import get_shortlink, decode
from database.database import db

routes = web.RouteTableDef()

# Jinja2 Environment
template_env = Environment(loader=FileSystemLoader('templates'))

# Configuration
TIMER_THRESHOLD = 100 # 100 seconds

def is_external_player(ua):
    if not ua:
        return False
    ua = ua.lower()
    external_players = [
        'vlc', 'mxplayer', 'playit', 'dalvik', 'mpv', 'stagefright',
        'lavf', 'lua-resty-http', 'okhttp', 'gstreamer', 'androidplayer',
        'com.mxtech.videoplayer', 'org.videolan.vlc', 'com.playit.videoplayer'
    ]
    return any(player in ua for player in external_players)

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
            if attempts >= 10: # BAN_STRIKE_3
                await db.ban_user_bypass(identifier, -1) # Permanent
                return web.json_response({"success": False, "message": "Bypass detected. Permanent block issued.", "banned": True}, status=403)
            elif attempts == 5: # BAN_STRIKE_2
                await db.ban_user_bypass(identifier, 24)
                return web.json_response({"success": False, "message": "Bypass detected. 24h block issued.", "banned": True}, status=403)
            elif attempts == 3: # BAN_STRIKE_1
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
    bot = request.app.get('bot')
    decoded = await decode(payload)
    msg_id = int(int(decoded.split("-")[1]) / abs(bot.db_channel.id))
    msg = await bot.get_messages(bot.db_channel.id, msg_id)
    media = msg.video or msg.document or msg.audio
    file_name = media.file_name or "video.mp4"

    # Use WEBSITE_URL if set, else fallback to request host
    domain = WEBSITE_URL.rstrip('/') if WEBSITE_URL else f"{request.scheme}://{request.host}"
    stream_url = f"{domain}/file/{payload}/{file_name}"
    watch_url = f"{domain}/watch/{payload}/{file_name}"

    # VLC Intent formatting - using both vlc:// and intent:// for max compatibility
    intent_url = f"intent://{stream_url.replace('https://','').replace('http://','')}/#Intent;scheme={domain.split(':')[0]};package=org.videolan.vlc;S.browser_fallback_url={watch_url};end"

    html = f"""
    <html>
    <head>
        <title>OTAKULUX | Opening VLC...</title>
        <script>
            window.onload = function() {{
                window.location.href = "vlc://{stream_url}";
                setTimeout(() => {{ window.location.href = "{intent_url}"; }}, 500);
                setTimeout(() => {{ window.location.href = "{watch_url}"; }}, 3000);
            }};
        </script>
    </head>
    <body style="background:#000;color:#fff;display:flex;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;">
        <div style="text-align:center;">
            <h3>Redirecting to VLC...</h3>
            <p>If it doesn't open, <a href="{watch_url}" style="color:#00d2ff;">click here</a></p>
        </div>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')

@routes.get("/mx/{payload}")
async def mx_redirect(request):
    payload = request.match_info['payload']
    bot = request.app.get('bot')
    decoded = await decode(payload)
    msg_id = int(int(decoded.split("-")[1]) / abs(bot.db_channel.id))
    msg = await bot.get_messages(bot.db_channel.id, msg_id)
    media = msg.video or msg.document or msg.audio
    file_name = media.file_name or "video.mp4"

    domain = WEBSITE_URL.rstrip('/') if WEBSITE_URL else f"{request.scheme}://{request.host}"
    stream_url = f"{domain}/file/{payload}/{file_name}"
    watch_url = f"{domain}/watch/{payload}/{file_name}"

    # MX Player Intent formatting - try Pro first, then Ad-supported
    intent_pro = f"intent:{stream_url}#Intent;package=com.mxtech.videoplayer.pro;S.title={file_name};S.browser_fallback_url={watch_url};end"
    intent_ad = f"intent:{stream_url}#Intent;package=com.mxtech.videoplayer.ad;S.title={file_name};S.browser_fallback_url={watch_url};end"

    html = f"""
    <html>
    <head>
        <title>OTAKULUX | Opening MX Player...</title>
        <script>
            window.onload = function() {{
                window.location.href = "{intent_pro}";
                setTimeout(() => {{ window.location.href = "{intent_ad}"; }}, 800);
                setTimeout(() => {{ window.location.href = "{watch_url}"; }}, 3000);
            }};
        </script>
    </head>
    <body style="background:#000;color:#fff;display:flex;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;">
        <div style="text-align:center;">
            <h3>Redirecting to MX Player...</h3>
            <p>If it doesn't open, <a href="{watch_url}" style="color:#00d2ff;">click here</a></p>
        </div>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')

@routes.get("/playit/{payload}")
async def playit_redirect(request):
    payload = request.match_info['payload']
    bot = request.app.get('bot')
    decoded = await decode(payload)
    msg_id = int(int(decoded.split("-")[1]) / abs(bot.db_channel.id))
    msg = await bot.get_messages(bot.db_channel.id, msg_id)
    media = msg.video or msg.document or msg.audio
    file_name = media.file_name or "video.mp4"

    domain = WEBSITE_URL.rstrip('/') if WEBSITE_URL else f"{request.scheme}://{request.host}"
    stream_url = f"{domain}/file/{payload}/{file_name}"
    watch_url = f"{domain}/watch/{payload}/{file_name}"

    intent_url = f"intent:{stream_url}#Intent;package=com.playit.videoplayer;S.title={file_name};S.browser_fallback_url={watch_url};end"
    html = f"""
    <html>
    <head>
        <title>OTAKULUX | Opening PLAYit...</title>
        <script>
            window.onload = function() {{
                window.location.href = "{intent_url}";
                setTimeout(() => {{ window.location.href = "{watch_url}"; }}, 3000);
            }};
        </script>
    </head>
    <body style="background:#000;color:#fff;display:flex;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;">
        <div style="text-align:center;">
            <h3>Redirecting to PLAYit...</h3>
            <p>If it doesn't open, <a href="{watch_url}" style="color:#00d2ff;">click here</a></p>
        </div>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')

@routes.get("/km/{payload}")
async def km_redirect(request):
    payload = request.match_info['payload']
    bot = request.app.get('bot')
    decoded = await decode(payload)
    msg_id = int(int(decoded.split("-")[1]) / abs(bot.db_channel.id))
    msg = await bot.get_messages(bot.db_channel.id, msg_id)
    media = msg.video or msg.document or msg.audio
    file_name = media.file_name or "video.mp4"

    domain = WEBSITE_URL.rstrip('/') if WEBSITE_URL else f"{request.scheme}://{request.host}"
    stream_url = f"{domain}/file/{payload}/{file_name}"
    watch_url = f"{domain}/watch/{payload}/{file_name}"

    intent_url = f"intent:{stream_url}#Intent;package=com.kmplayer;S.title={file_name};S.browser_fallback_url={watch_url};end"
    html = f"""
    <html>
    <head>
        <title>OTAKULUX | Opening KMPlayer...</title>
        <script>
            window.onload = function() {{
                window.location.href = "{intent_url}";
                setTimeout(() => {{ window.location.href = "{watch_url}"; }}, 3000);
            }};
        </script>
    </head>
    <body style="background:#000;color:#fff;display:flex;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;">
        <div style="text-align:center;">
            <h3>Redirecting to KMPlayer...</h3>
            <p>If it doesn't open, <a href="{watch_url}" style="color:#00d2ff;">click here</a></p>
        </div>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')

@routes.get("/best/{payload}")
async def best_redirect(request):
    payload = request.match_info['payload']
    bot = request.app.get('bot')
    decoded = await decode(payload)
    msg_id = int(int(decoded.split("-")[1]) / abs(bot.db_channel.id))
    msg = await bot.get_messages(bot.db_channel.id, msg_id)
    media = msg.video or msg.document or msg.audio
    file_name = media.file_name or "video.mp4"

    domain = WEBSITE_URL.rstrip('/') if WEBSITE_URL else f"{request.scheme}://{request.host}"
    stream_url = f"{domain}/file/{payload}/{file_name}"
    watch_url = f"{domain}/watch/{payload}/{file_name}"

    # Sequential player attempt logic with premium UI
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>OTAKULUX | Detecting Best Player...</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script>
        function tryPlayers() {{
            const streamUrl = "{stream_url}";
            const watchUrl = "{watch_url}";
            const title = "{file_name}";

            // 1. Try VLC (Direct URI)
            window.location.href = "vlc://" + streamUrl;

            // 2. Try MX Player Pro
            setTimeout(() => {{
                window.location.href = "intent:" + streamUrl + "#Intent;package=com.mxtech.videoplayer.pro;S.title=" + title + ";S.browser_fallback_url=" + watchUrl + ";end";
            }}, 800);

            // 3. Try MX Player (Free)
            setTimeout(() => {{
                window.location.href = "intent:" + streamUrl + "#Intent;package=com.mxtech.videoplayer.ad;S.title=" + title + ";S.browser_fallback_url=" + watchUrl + ";end";
            }}, 1600);

            // 4. Try PLAYit
            setTimeout(() => {{
                window.location.href = "intent:" + streamUrl + "#Intent;package=com.playit.videoplayer;S.title=" + title + ";S.browser_fallback_url=" + watchUrl + ";end";
            }}, 2400);

            // 5. Final Fallback to Web
            setTimeout(() => {{
                window.location.href = watchUrl;
            }}, 3500);
        }}
        window.onload = tryPlayers;
    </script>
</head>
<body style="background:#050505;color:#fff;font-family:'Segoe UI',sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;">
    <div style="text-align:center;padding:20px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.1);border-radius:20px;backdrop-filter:blur(10px);box-shadow:0 10px 30px rgba(0,0,0,0.5);">
        <h2 style="color:#00d2ff;margin:0 0 10px 0;letter-spacing:1px;">Detecting Best Player</h2>
        <p style="color:#888;font-size:0.9rem;">Launching external application...</p>
        <div style="margin-top:20px;width:40px;height:40px;border:4px solid rgba(255,0,127,0.1);border-top-color:#ff007f;border-radius:50%;animation:spin 0.8s linear infinite;display:inline-block;"></div>
    </div>
    <style>@keyframes spin {{ to {{ transform:rotate(360deg); }} }}</style>
</body>
</html>
"""
    return web.Response(text=html, content_type='text/html')

async def stream_controller(request, payload):
    bot = request.app.get('bot')
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
        file_name = media.file_name or "video.mp4"
        file_size = media.file_size

        # Enhanced MIME type detection for mobile players
        mime_type = media.mime_type or "application/octet-stream"
        if "video" in mime_type or file_name.lower().endswith((".mp4", ".mkv", ".mov", ".webm", ".avi", ".ts")):
            if not mime_type or mime_type == "application/octet-stream":
                if file_name.lower().endswith(".mkv"):
                    mime_type = "video/x-matroska"
                elif file_name.lower().endswith(".mp4"):
                    mime_type = "video/mp4"
                else:
                    mime_type = "video/webm"

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
            'Content-Disposition': f'inline; filename="{file_name}"',
            'Accept-Ranges': 'bytes',
            'Content-Length': str(end - start + 1),
            'Content-Range': f'bytes {start}-{end}/{file_size}',
            'Cache-Control': 'public, max-age=3600',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, HEAD, OPTIONS',
            'Access-Control-Allow-Headers': 'Range, Content-Type, Accept-Ranges, Origin',
            'Access-Control-Expose-Headers': 'Content-Range, Content-Length, Accept-Ranges, Content-Type',
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'ALLOWALL',
            'Connection': 'keep-alive',
        }

        res = web.StreamResponse(status=206 if range_header else 200, headers=headers)
        await res.prepare(request)

        try:
            async for chunk in bot.stream_media(media, offset=start, limit=end-start+1):
                await res.write(chunk)
        except Exception:
            pass # Connection reset by player is common

        return res
    except Exception as e:
        print(f"Stream Controller Error: {e}")
        return web.Response(text=f"Stream Error: {e}", status=500)

@routes.get("/watch/{payload}/{file_name}")
@routes.get("/watch/{payload}")
@routes.get("/watch")
async def watch_route_handler(request):
    payload = request.match_info.get('payload') or request.query.get('path')
    if not payload:
        return web.Response(text="Payload missing", status=400)

    ua = request.headers.get('User-Agent', '')
    if is_external_player(ua):
        return await stream_controller(request, payload)

    bot = request.app.get('bot')

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
        stream_url = f"/file/{payload}"
        mime_type = getattr(media, 'mime_type', 'video/mp4')

        template = template_env.get_template('watch.html')
        html = template.render(
            file_name=file_name,
            stream_url=stream_url,
            mime_type=mime_type,
            payload=payload
        )
        return web.Response(text=html, content_type='text/html')

    except Exception as e:
        print(f"Watch Page Error: {e}")
        return web.Response(text=f"Error loading stream page: {e}", status=500)

@routes.get("/file/{payload}/{file_name}")
@routes.get("/file/{payload}")
async def direct_download(request):
    payload = request.match_info['payload']
    bot = request.app.get('bot')

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

        # Optimize for PLAYit and some picky players
        mime_type = media.mime_type or "application/octet-stream"
        if "video" in mime_type or file_name.endswith((".mp4", ".mkv", ".mov", ".webm", ".avi")):
            if not mime_type or mime_type == "application/octet-stream":
                mime_type = "video/mp4" if file_name.endswith(".mp4") else "video/x-matroska"

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
            'Content-Disposition': f'inline; filename="{file_name}"',
            'Accept-Ranges': 'bytes',
            'Content-Length': str(end - start + 1),
            'Content-Range': f'bytes {start}-{end}/{file_size}',
            'Cache-Control': 'public, max-age=3600',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, HEAD, OPTIONS',
            'Access-Control-Allow-Headers': 'Range, Content-Type, Accept-Ranges, Origin',
            'Access-Control-Expose-Headers': 'Content-Range, Content-Length, Accept-Ranges, Content-Type',
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'ALLOWALL',
            'Connection': 'keep-alive',
        }

        res = web.StreamResponse(status=206 if range_header else 200, headers=headers)
        await res.prepare(request)

        try:
            async for chunk in bot.stream_media(media, offset=start, limit=end-start+1):
                await res.write(chunk)
        except Exception:
            pass

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
            except Exception:
                pass

            return res

        except Exception as e:
            print(f"Streaming Error: {e}")
            # Fallback to bot redirect if streaming fails critically
            username = bot.username if bot else "OTAKULUX"
            return web.HTTPFound(f"https://t.me/{username}?start=yu3elk{payload}7")

    except Exception as e:
        print(f"JWT/Session Error: {e}")
        return web.HTTPFound(f"/verify/{payload}")
