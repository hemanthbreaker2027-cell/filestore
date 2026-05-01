
from aiohttp import web
import time
import os
import hashlib
from config import WEBSITE_URL, SHORTLINK_URL, SHORTLINK_API
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
    return web.Response(text="OTAKULUX Secure Engine v4.1 - Online", content_type="text/plain")

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
        data = await request.json()
        recaptcha_token = data.get('recaptchaToken')
        link_token = data.get('linkToken')

        # Get the real user IP from X-Forwarded-For
        forwarded_for = request.headers.get('X-Forwarded-For', request.remote)
        ip = forwarded_for.split(',')[0].strip()

        identifier = SecurityService.get_identifier(request)

        if not all([recaptcha_token, link_token]):
            return json_response(False, "Missing required parameters", status=400)

        # 1. Verify reCAPTCHA v3
        client_session = request.app['client_session']
        success, score = await SecurityService.verify_recaptcha(recaptcha_token, ip, client_session)

        if not success:
            if score == -1:
                return json_response(False, "Bot configuration error (Invalid reCAPTCHA Secret). Please contact admin.", status=500)

            await db.increment_bypass_attempt(identifier)
            return json_response(False, f"Security check failed (Score: {score}). Please try again.", status=403)

        # 2. Decrypt and validate link token again
        token_data = SecureRedirect.decrypt(link_token)
        if not token_data:
            return json_response(False, "Invalid or Expired Link", status=403)

        # 3. Enforce 180-second wait time
        issued_at = token_data.get('issuedAt', 0)
        time_elapsed = int(time.time()) - issued_at
        if time_elapsed < 180:
            # Bypass Detected!
            await db.ban_user_bypass(identifier, duration_hours=24)
            return json_response(False, "Bypass Detected! Your access has been restricted for 24 hours due to automated activity.", status=403)

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
    try:
        data = await request.json()
        recaptcha_token = data.get('recaptchaToken')
        encoded_url = data.get('url')

        if not recaptcha_token or not encoded_url:
            return json_response(False, "Missing parameters", status=400)

        # 1. Verify reCAPTCHA
        forwarded_for = request.headers.get('X-Forwarded-For', request.remote)
        ip = forwarded_for.split(',')[0].strip()

        client_session = request.app['client_session']
        success, score = await SecurityService.verify_recaptcha(recaptcha_token, ip, client_session)

        if not success:
            return json_response(False, "Security check failed", status=403)

        # 2. Decode the original shortlink
        try:
            original_shortlink = SecurityService.decode_link(encoded_url)
        except:
            return json_response(False, "Invalid URL parameter", status=400)

        # 3. Extract the code from the shortlink
        # Robust extraction: remove query params and trailing slashes
        clean_url = original_shortlink.split('?')[0].rstrip('/')
        code = clean_url.split('/')[-1]

        if not code:
            return json_response(False, "Invalid shortlink format", status=400)

        # 4. Store verification session (Authenticity check)
        identifier = SecurityService.get_identifier(request)
        await db.store_shortener_verification(identifier, code)

        # 5. Return the wrapped URL
        wrapped_url = f"/eductionssstudiess/?eductionstudiess={code}"
        return json_response(True, "Verified", {"redirect": wrapped_url})

    except Exception as e:
        print(f"API Error: {e}")
        return json_response(False, "Server Error", status=500)

@routes.get("/eductionssstudiess/")
async def wrapped_url_handler(request):
    code = request.query.get('eductionstudiess')
    if not code:
        return web.Response(text="Invalid Request", status=400)

    # Security: Verify that this session actually passed reCAPTCHA for this code
    identifier = SecurityService.get_identifier(request)
    if not await db.verify_shortener_code(identifier, code):
        return web.Response(text="Security verification failed or expired. Please go back and try again.", status=403)

    # Reconstruct the original shortlink
    final_url = f"https://{SHORTLINK_URL}/{code}"
    return web.HTTPFound(final_url)

@routes.get("/health")
async def health_check(request):
    return web.Response(text="OK", status=200)
