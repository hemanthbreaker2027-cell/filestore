
from aiohttp import web
import time
import os
import hashlib
import asyncio
from config import WEBSITE_URL, SHORTLINK_URL, SHORTLINK_API, WRAPPED_URL_DOMAIN, RECAPTCHA_SITE_KEY
from database.database import db
from services.security import SecurityService, SecureRedirect

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

async def check_ban_status(request):
    identifier = SecurityService.get_identifier(request)
    record = await db.get_bypass_record(identifier)
    if record and record.get('ban_status'):
        if time.time() < record.get('ban_expiry'):
            return True, record
        else:
            await db.reset_bypass_attempts(identifier)
    return False, None

@routes.get("/", allow_head=True)
async def root_handler(request):
    return web.Response(text="ᴀɴɪᴢᴏɴᴇꜰʟɪx sᴇᴄᴜʀᴇ ᴇɴɢɪɴᴇ ᴠ𝟻.𝟶 - Online", content_type="text/plain")

@routes.get("/r2/{userId}/{token}")
async def r2_landing_page(request):
    is_banned, record = await check_ban_status(request)
    if is_banned:
        return web.HTTPFound("/banned")

    user_id = request.match_info['userId']
    token = request.match_info['token']

    # Pre-validate token
    data = SecureRedirect.decrypt(token)
    if not data:
        return web.Response(text="Invalid or Expired Security Token", status=403)

    html = await get_template("safe") # We reuse safe.html but it will be updated for /r2/
    if not html: return web.Response(text="Template Error", status=500)

    html = html.replace("{{ RECAPTCHA_SITE_KEY }}", RECAPTCHA_SITE_KEY)
    html = html.replace("{{ USER_ID }}", user_id)
    html = html.replace("{{ TOKEN }}", token)

    return web.Response(text=html, content_type="text/html")

@routes.post("/r2/verify")
async def r2_verify(request):
    is_banned, _ = await check_ban_status(request)
    if is_banned:
        return json_response(False, "Access Denied", status=403)

    try:
        # STRICT SECURITY: Check headers
        user_agent = request.headers.get('User-Agent', '')
        if not user_agent or 'bot' in user_agent.lower() or 'python' in user_agent.lower():
             return json_response(False, "Automation Detected", status=403)

        data = await request.json()
        recaptcha_token = data.get('recaptchaToken')
        link_token = data.get('linkToken')

        ip = SecurityService.get_client_ip(request)
        identifier = SecurityService.get_identifier(request)

        if not all([recaptcha_token, link_token]):
            return json_response(False, "Missing required parameters", status=400)

        # 1. Verify reCAPTCHA v3
        client_session = request.app['client_session']
        success, score = await SecurityService.verify_recaptcha(recaptcha_token, ip, client_session)

        # Check for specific configuration error score
        if score == -1:
             return json_response(False, "Bot configuration error (Invalid reCAPTCHA Secret). Please contact admin.", status=500)

        # STRICT SECURITY: Score must be >= 0.3 (Dynamic for mobile)
        from services.security import MIN_SCORE
        if not success or score < MIN_SCORE:
            await db.increment_bypass_attempt(identifier)
            return json_response(False, f"Security check failed (Score: {score}). Please disable your VPN/Ad-blocker and try again.", status=403)

        # 2. Decrypt and validate link token again
        token_data = SecureRedirect.decrypt(link_token)
        if not token_data:
            return json_response(False, "Invalid or Expired Link", status=403)

        # 3. Check if token was already used
        token_hash = hashlib.sha256(link_token.encode()).hexdigest()
        if not await db.validate_and_use_token(token_hash):
            return json_response(False, "Link Already Used", status=403)

        # 4. Success -> Reset attempts
        await db.reset_bypass_attempts(identifier)

        # 5. Return final destination (Direct link to bot)
        payload = token_data.get('payload')
        bot = request.app['bot']
        final_redirect = f"https://t.me/{bot.username}?start=yu3elk{payload}7"

        # Update BASED TIME status if applicable
        settings = await db.get_settings()
        if settings.get('shortener_mode') == 'based_time':
             # We need user_id here. Decrypt link_token usually contains it in r2 flow
             user_id = request.match_info.get('userId') # available in r2 flow
             if user_id:
                 await db.update_verify_status(int(user_id), is_verified=True, verified_time=time.time())

        return json_response(True, "Verified successfully", {"redirect": final_redirect})

    except Exception as e:
        print(f"Web API Error: {e}")
        return json_response(False, "Internal Server Error", status=500)

@routes.get("/banned")
async def banned_route(request):
    is_banned, record = await check_ban_status(request)
    if not is_banned:
        return web.HTTPFound("/")

    expiry = record.get('ban_expiry')
    time_left = ""
    is_permanent = True

    if expiry < 9999999999:
        is_permanent = False
        remaining = int(expiry - time.time())
        h, rem = divmod(remaining, 3600)
        m, s = divmod(rem, 60)
        time_left = f"{h}h {m}m {s}s"

    html = await get_template("banned")
    if not html: return web.Response(text="Template Error", status=500)

    html = html.replace("{{ MESSAGE }}", "Multiple bypass attempts detected. Your access has been restricted.")

    if is_permanent:
        import re
        html = re.sub(r"<!-- TIME_BOX_START -->.*?<!-- TIME_BOX_END -->", "", html, flags=re.DOTALL)
    else:
        html = html.replace("{{ TIME_LEFT }}", time_left)
        html = html.replace("<!-- TIME_BOX_START -->", "").replace("<!-- TIME_BOX_END -->", "")

    return web.Response(text=html, content_type="text/html")

@routes.get("/protect")
async def protect_landing_page(request):
    url = request.query.get('url')
    if not url:
        return web.Response(text="Missing target URL", status=400)

    html = await get_template("protect")
    if not html: return web.Response(text="Template Error", status=500)

    html = html.replace("{{ RECAPTCHA_SITE_KEY }}", RECAPTCHA_SITE_KEY)
    html = html.replace("{{ ENCODED_URL }}", url)

    return web.Response(text=html, content_type="text/html")

@routes.post("/verify")
async def verify_shortener(request):
    from plugins.start import send_files
    try:
        # STRICT SECURITY: Check headers
        user_agent = request.headers.get('User-Agent', '')
        if not user_agent or 'bot' in user_agent.lower() or 'python' in user_agent.lower():
             return json_response(False, "Automation Detected", status=403)

        data = await request.json()
        recaptcha_token = data.get('recaptchaToken')
        encrypted_payload = data.get('url')

        if not recaptcha_token or not encrypted_payload:
            return json_response(False, "Missing parameters", status=400)

        # 1. Verify reCAPTCHA
        ip = SecurityService.get_client_ip(request)
        client_session = request.app['client_session']
        success, score = await SecurityService.verify_recaptcha(recaptcha_token, ip, client_session)

        if score == -1:
            return json_response(False, "Bot configuration error (Invalid reCAPTCHA Secret).", status=500)

        # STRICT SECURITY: Score >= 0.3
        from services.security import MIN_SCORE
        if not success or score < MIN_SCORE:
            return json_response(False, f"Security check failed (Score: {score}). Please disable your VPN/Ad-blocker and try again.", status=403)

        # 2. Retrieve destination using the code (encrypted_payload contains the code)
        code = encrypted_payload
        record = await db.verify_shortener_code(code)
        if not record:
            return json_response(False, "Invalid or Expired Session", status=403)

        original_url = record.get('original_url')
        user_id = int(record.get('user_id'))

        # 3. Mark as verified in database for bot check
        payload = ""
        from urllib.parse import urlparse, parse_qs
        parsed_url = urlparse(original_url)
        start_param = parse_qs(parsed_url.query).get('start', [''])[0]

        # Determine the pure payload (base64 part)
        if start_param.startswith("yu3elk") and start_param.endswith("7"):
            payload = start_param[6:-1]
        elif start_param.startswith("yu3elk"):
            payload = start_param[6:]
        else:
            payload = start_param

        # Ensure final_url has verified markers so bot recognizes it
        final_param = start_param if start_param.startswith("yu3elk") else f"yu3elk{start_param}7"
        final_url = original_url.replace(f"start={start_param}", f"start={final_param}")

        settings = await db.get_settings()
        if settings.get('shortener_mode') == 'based_time':
            await db.update_verify_status(user_id, is_verified=True, verified_time=time.time())
        else:
            # ONE PER TIME - mark this specific payload as verified
            await db.update_verify_status(user_id, verify_token=payload, is_verified=True, verified_time=time.time())

        # 4. Instant File Delivery (Telegram side)
        # We deliver files immediately to satisfy the "instant" requirement
        from helper_func import is_subscribed
        bot = request.app['bot']

        if user_id and payload:
            if await is_subscribed(bot, user_id):
                asyncio.create_task(send_files(bot, user_id, payload))

        # 5. Return redirection back to bot (Browser side)
        return json_response(True, "Verified", {"redirect": final_url})

    except Exception as e:
        print(f"API Error: {e}")
        return json_response(False, "Server Error", status=500)

@routes.get("/eductionssstudiess/")
async def wrapped_url_handler(request):
    code = request.query.get('eductionstudiess')
    if not code:
        return web.Response(text="Missing Code", status=400)

    html = await get_template("protect")
    if not html: return web.Response(text="Template Error", status=500)

    html = html.replace("{{ RECAPTCHA_SITE_KEY }}", RECAPTCHA_SITE_KEY)
    html = html.replace("{{ ENCODED_URL }}", code) # We pass code instead of URL

    return web.Response(text=html, content_type="text/html")

@routes.get("/watch")
async def watch_handler(request):
    code = request.query.get('path')
    record = await db.verify_shortener_code(code)
    if not record:
        return web.Response(text="Invalid or Expired Link", status=403)

    # In a real scenario, you'd have a direct stream link.
    # For now, we'll use a placeholder or derived link logic if possible.
    # The requirement asks for same type as demo links: https://cdn2.linkforge.xyz/watch/AgADKS23981
    # We will assume a service or endpoint provides the raw stream.

    # We will use the 'code' to generate the STREAM_URL
    # For demo purposes, we will assume the STREAM_URL is derived from some internal logic or service.
    # In this bot's context, let's use the code to construct a temporary stream URL.

    file_name = record.get('file_name', 'video.mp4')
    from urllib.parse import quote
    encoded_name = quote(file_name)
    stream_url = f"https://{request.host}/stream/file/{code}/{encoded_name}"
    download_url = f"https://{request.host}/download/{code}"

    html = await get_template("watch")
    if not html: return web.Response(text="Template Error", status=500)

    html = html.replace("{{ STREAM_URL }}", stream_url)
    html = html.replace("{{ STREAM_URL_NO_PROTO }}", stream_url.replace("https://", "").replace("http://", ""))
    html = html.replace("{{ DOWNLOAD_URL }}", download_url)
    html = html.replace("{{ FILE_NAME }}", record.get('file_name', 'Requested File'))

    return web.Response(text=html, content_type="text/html")

@routes.get("/download/{code}")
async def download_handler(request):
    code = request.match_info['code']
    record = await db.verify_shortener_code(code)
    if not record:
        return web.Response(text="Invalid or Expired Link", status=403)

    # Redirect to the actual file or bot
    return web.HTTPFound(record.get('original_url'))

@routes.get("/stream/file/{code}")
@routes.get("/stream/file/{code}/{filename}")
async def stream_file_handler(request):
    code = request.match_info['code']
    record = await db.verify_shortener_code(code)
    if not record:
        return web.Response(text="Invalid or Expired Link", status=403)

    # Extract message ID from original_url
    # original_url format: https://t.me/botname?start=get-MSGID
    import re
    match = re.search(r"get-(\d+)", record.get('original_url', ''))
    if not match:
        return web.Response(text="Source Not Found", status=404)

    msg_id = int(int(match.group(1)) / abs(request.app['bot'].db_channel.id))
    bot = request.app['bot']

    try:
        msg = await bot.get_messages(bot.db_channel.id, msg_id)
        if not msg or msg.empty:
            return web.Response(text="File Not Found", status=404)

        file_obj = msg.video or msg.document
        if not file_obj:
            return web.Response(text="Invalid Media", status=400)

        # Refined Stream delivery with proper headers
        range_header = request.headers.get('Range', None)
        start = 0
        end = file_obj.file_size - 1

        if range_header:
             # Basic Range parsing
             try:
                 range_val = range_header.replace('bytes=', '').split('-')
                 start = int(range_val[0])
                 if range_val[1]:
                     end = int(range_val[1])
             except: pass

        response = web.StreamResponse(status=206 if range_header else 200)
        response.headers['Content-Type'] = file_obj.mime_type or 'video/mp4'
        response.headers['Content-Length'] = str(end - start + 1)
        response.headers['Content-Range'] = f'bytes {start}-{end}/{file_obj.file_size}'
        response.headers['Accept-Ranges'] = 'bytes'
        response.headers['Access-Control-Allow-Origin'] = '*' # Critical for some players

        await response.prepare(request)

        # We need an optimized stream that supports offset if possible
        # bot.stream_media doesn't take offset easily in pyro, but for small chunks it works
        async for chunk in bot.stream_media(file_obj, offset=start, limit=end-start+1):
            await response.write(chunk)

        await response.write_eof()
        return response

    except Exception as e:
        print(f"Streaming Error: {e}")
        return web.Response(text="Streaming Failed", status=500)

@routes.get("/health")
async def health_check(request):
    return web.Response(text="OK", status=200)
