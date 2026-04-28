
from aiohttp import web
import aiohttp
import time
import uuid
import os
import hashlib
from config import JWT_SECRET, WEBSITE_URL, SHORTLINK_URL, SHORTLINK_API
from database.database import db
from services.security import SecurityService, SecureRedirect

routes = web.RouteTableDef()

# reCAPTCHA Site Key from Env
RECAPTCHA_SITE_KEY = os.environ.get("RECAPTCHA_SITE_KEY", "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI")

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
    return web.Response(text="OTAKULUX Secure Engine v4.0 - Online", content_type="text/plain")

@routes.get("/safe/{payload}")
async def safe_landing_page(request):
    is_banned, record = await check_ban_status(request)
    if is_banned:
        return web.HTTPFound("/banned")

    payload = request.match_info['payload']

    html = await get_template("safe")
    if not html: return web.Response(text="Template Error", status=500)

    html = html.replace("{{ RECAPTCHA_SITE_KEY }}", RECAPTCHA_SITE_KEY)
    html = html.replace("{{ PAYLOAD }}", payload)

    return web.Response(text=html, content_type="text/html")

@routes.post("/api/verify_safe")
async def api_verify_safe(request):
    is_banned, _ = await check_ban_status(request)
    if is_banned:
        return json_response(False, "Access Denied", status=403)

    try:
        data = await request.json()
        token = data.get('token')
        payload = data.get('payload')
        ip = request.headers.get('X-Forwarded-For', request.remote)
        identifier = SecurityService.get_identifier(request)

        if not all([token, payload]):
            return json_response(False, "Missing required parameters", status=400)

        # 1. Verify reCAPTCHA v3
        client_session = request.app['client_session']
        success, score = await SecurityService.verify_recaptcha(token, ip, client_session)

        if not success:
            await db.increment_bypass_attempt(identifier)
            return json_response(False, f"Security check failed (Score: {score}). Please try again.", status=403)

        # 2. Generate Secure One-Time Token
        uid = str(uuid.uuid4())
        secure_token = SecureRedirect.encrypt({"payload": payload, "uid": uid})

        # Hash the token for DB storage (one-time use)
        token_hash = hashlib.sha256(secure_token.encode()).hexdigest()
        await db.store_secure_token(token_hash, int(time.time()) + 300) # 5 min expiry

        # 3. Final Destination URL (Google Redirect Method for obfuscation)
        google_redirect = f"https://www.google.com/url?q={WEBSITE_URL}/r2/{uid}/{secure_token}"

        return json_response(True, "Verified successfully", {"redirect": google_redirect})

    except Exception as e:
        print(f"Web API Error: {e}")
        return json_response(False, "Internal Server Error", status=500)

@routes.get("/r2/{uid}/{token}")
async def secure_redirect_handler(request):
    uid = request.match_info['uid']
    token = request.match_info['token']

    # 1. Check if token was already used
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    if not await db.validate_and_use_token(token_hash):
        return web.Response(text="Link Expired or Already Used", status=403)

    # 2. Decrypt Token
    data = SecureRedirect.decrypt(token)
    if not data or data.get('uid') != uid:
        return web.Response(text="Invalid Security Token", status=403)

    payload = data.get('payload')

    # 3. Final Redirect to Bot
    bot = request.app['bot']
    return web.HTTPFound(f"https://t.me/{bot.username}?start=yu3elk{payload}7")

@routes.get("/verify/{payload}")
async def legacy_verify_page(request):
    # Redirect legacy links to new safe page
    return web.HTTPFound(f"/safe/{request.match_info['payload']}")

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

@routes.get("/health")
async def health_check(request):
    return web.Response(text="OK", status=200)
