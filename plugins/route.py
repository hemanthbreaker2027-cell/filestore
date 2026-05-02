
from aiohttp import web
import time
import os
import hashlib
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

        # 3. Enforce 8-second wait time
        issued_at = token_data.get('issuedAt', 0)
        time_elapsed = int(time.time()) - issued_at
        if time_elapsed < 8:
            return json_response(False, "Too Fast! Please wait at least 8 seconds before verifying.", status=403)

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

        # 2. Decrypt the original shortlink data
        token_data = SecureRedirect.decrypt(encrypted_payload)
        if not token_data:
            return json_response(False, "Invalid or Expired Security Token", status=403)

        original_shortlink = token_data.get('target')

        # Domain whitelist check
        if not SecurityService.is_domain_whitelisted(original_shortlink):
            return json_response(False, "Access Denied: Domain not whitelisted", status=403)

        # 3. Extract the code from the shortlink
        # Robust extraction: remove query params and trailing slashes
        clean_url = original_shortlink.split('?')[0].rstrip('/')
        code = clean_url.split('/')[-1]

        if not code:
            return json_response(False, "Invalid shortlink format", status=400)

        # 4. Store verification session (Authenticity check)
        identifier = SecurityService.get_identifier(request)

        # Cooldown check
        if not await db.check_cooldown(identifier):
            return json_response(False, "Too many requests. Please wait a moment.", status=429)

        await db.store_shortener_verification(identifier, code, original_shortlink)
        await db.update_cooldown(identifier)

        # 5. Update BASED TIME status if applicable
        settings = await db.get_settings()
        if settings.get('shortener_mode') == 'based_time':
             user_id = token_data.get('user_id')
             if user_id:
                 await db.update_verify_status(int(user_id), is_verified=True, verified_time=time.time())

        # 6. Return the wrapped URL
        wrapped_url = f"https://{WRAPPED_URL_DOMAIN}/eductionssstudiess/?eductionstudiess={code}"
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
    original_url = await db.verify_shortener_code(identifier, code)

    if not original_url:
        return web.Response(text="Security verification failed or expired. Please go back and try again.", status=403)

    # Return the original shortlink
    return web.HTTPFound(original_url)

@routes.get("/health")
async def health_check(request):
    return web.Response(text="OK", status=200)
