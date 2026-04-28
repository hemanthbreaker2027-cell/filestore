
from aiohttp import web
import aiohttp
import time
import uuid
import os
from config import JWT_SECRET, WEBSITE_URL, SHORTLINK_URL, SHORTLINK_API
from database.database import db
from services.security import SecurityService

routes = web.RouteTableDef()

# reCAPTCHA Site Key from Env
RECAPTCHA_SITE_KEY = os.environ.get("RECAPTCHA_SITE_KEY", "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI") # Test key

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
    return web.Response(text="OTAKULUX Secure Engine v3.0 - Online", content_type="text/plain")

@routes.get("/verify/{payload}")
async def verify_page(request):
    is_banned, record = await check_ban_status(request)
    if is_banned:
        return web.HTTPFound("/banned")

    payload = request.match_info['payload']
    session_id = str(uuid.uuid4())

    html = await get_template("verify")
    if not html: return web.Response(text="Template Error", status=500)

    html = html.replace("{{ RECAPTCHA_SITE_KEY }}", RECAPTCHA_SITE_KEY)
    html = html.replace("{{ PAYLOAD }}", payload)
    html = html.replace("{{ SESSION_ID }}", session_id)

    return web.Response(text=html, content_type="text/html")

@routes.post("/api/verify")
async def api_verify(request):
    is_banned, _ = await check_ban_status(request)
    if is_banned:
        return json_response(False, "Access Denied", status=403)

    try:
        data = await request.json()
        token = data.get('token')
        payload = data.get('payload')
        session_id = data.get('session_id')
        ip = request.headers.get('CF-Connecting-IP') or request.headers.get('X-Forwarded-For', request.remote)
        identifier = SecurityService.get_identifier(request)

        if not all([token, payload, session_id]):
            return json_response(False, "Missing required parameters", status=400)

        # 1. Verify reCAPTCHA
        client_session = request.app['client_session']
        success, score = await SecurityService.verify_recaptcha(token, ip, client_session)

        if not success:
            await db.increment_bypass_attempt(identifier)
            record = await db.get_bypass_record(identifier)
            attempts = record.get('attempts_count', 0)

            # Progressive Banning
            if attempts >= 10:
                await db.ban_user_bypass(identifier, -1) # Permanent
            elif attempts >= 5:
                await db.ban_user_bypass(identifier, 24) # 24h
            elif attempts >= 3:
                await db.ban_user_bypass(identifier, 1)  # 1h

            return json_response(False, f"Security check failed (Score: {score}). Please try again.", status=403)

        # 2. Success -> Reset attempts and allow redirect
        await db.reset_bypass_attempts(identifier)

        # 3. Generate Session Cookie
        final_token = SecurityService.generate_session_token(payload, session_id, ip)

        # 4. Get Final Destination (Shortened)
        redirect_url = await SecurityService.get_secure_shortlink(payload)

        response = json_response(True, "Verified successfully", {"redirect": redirect_url})
        response.set_cookie('auth_session', final_token, httponly=True, secure=True, samesite='Lax', max_age=3600)
        return response

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
        # Hide the time box
        import re
        html = re.sub(r"<!-- TIME_BOX_START -->.*?<!-- TIME_BOX_END -->", "", html, flags=re.DOTALL)
    else:
        # Keep it and replace value
        html = html.replace("{{ TIME_LEFT }}", time_left)
        # Clean markers
        html = html.replace("<!-- TIME_BOX_START -->", "").replace("<!-- TIME_BOX_END -->", "")

    return web.Response(text=html, content_type="text/html")

@routes.get("/f/{payload}")
async def final_handler(request):
    payload = request.match_info['payload']
    cookie = request.cookies.get('auth_session')

    if not cookie:
        return web.HTTPFound(f"/verify/{payload}")

    decoded = SecurityService.verify_session_token(cookie)
    if not decoded or decoded.get('payload') != payload:
        return web.HTTPFound(f"/verify/{payload}")

    bot = request.app['bot']
    return web.HTTPFound(f"https://t.me/{bot.username}?start=yu3elk{payload}7")

@routes.get("/health")
async def health_check(request):
    return web.Response(text="OK", status=200)
