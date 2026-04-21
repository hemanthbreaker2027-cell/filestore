
from aiohttp import web
import aiohttp
import jwt
import time
import hashlib
import uuid
from config import TURNSTILE_SITE_KEY, TURNSTILE_SECRET_KEY, JWT_SECRET, WEBSITE_URL, SHORTLINK_URL, SHORTLINK_API
from plugins.turnstile_html import TURNSTILE_HTML, BANNED_HTML, BOT_DETECTED_HTML
from helper_func import get_shortlink
from database.database import db

routes = web.RouteTableDef()

# Configuration
TIMER_THRESHOLD = 100 # 100 seconds
BAN_LIMIT = 3
BAN_DURATION_HOURS = 24

def get_real_ip(request):
    return request.headers.get('CF-Connecting-IP') or request.headers.get('X-Forwarded-For', request.remote)

def get_identifier(request):
    ip = get_real_ip(request)
    ua = request.headers.get('User-Agent', '')
    return hashlib.sha256(f"{ip}{ua}".encode()).hexdigest()

def is_rate_limited(ip):
    # This remains as a simple in-memory check for basic flood protection
    current_time = time.time()
    if not hasattr(is_rate_limited, 'ip_requests'):
        is_rate_limited.ip_requests = {}

    if ip not in is_rate_limited.ip_requests:
        is_rate_limited.ip_requests[ip] = []

    is_rate_limited.ip_requests[ip] = [t for t in is_rate_limited.ip_requests[ip] if current_time - t < 60]

    if len(is_rate_limited.ip_requests[ip]) > 20:
        return True

    is_rate_limited.ip_requests[ip].append(current_time)
    return False

async def check_ban(identifier):
    record = await db.get_bypass_record(identifier)
    if record and record.get('ban_status'):
        if time.time() < record.get('ban_expiry'):
            return record.get('ban_expiry')
        else:
            await db.reset_bypass_attempts(identifier)
    return None

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("OTAKULUX FileStore Secure")

@routes.get("/verify/{payload}")
async def turnstile_page(request):
    identifier = get_identifier(request)
    ban_expiry = await check_ban(identifier)
    if ban_expiry:
        return web.HTTPFound("/banned")

    payload = request.match_info['payload']
    session_id = str(uuid.uuid4())

    # Create initial session JWT to track start time
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
    response.set_cookie('v_session', init_token, httponly=True, secure=True, samesite='Lax', max_age=600)
    return response

@routes.post("/verify_token")
async def verify_turnstile(request):
    identifier = get_identifier(request)
    ban_expiry = await check_ban(identifier)
    if ban_expiry:
        return web.json_response({"success": False, "message": "You are banned.", "banned": True}, status=403)

    ip = get_real_ip(request)
    if is_rate_limited(ip):
        return web.json_response({"success": False, "message": "Slow down!"}, status=429)

    try:
        data = await request.json()
        token = data.get('token')
        payload = data.get('payload')
        session_id = data.get('session_id')
        v_session = request.cookies.get('v_session')

        if not v_session:
            await db.increment_bypass_attempt(identifier)
            return web.json_response({"success": False, "message": "Session missing."}, status=400)

        # Decode initial session
        try:
            decoded_v = jwt.decode(v_session, JWT_SECRET, algorithms=['HS256'])
        except:
            await db.increment_bypass_attempt(identifier)
            return web.json_response({"success": False, "message": "Invalid session."}, status=400)

        # Validate session integrity
        if decoded_v.get('session_id') != session_id or \
           decoded_v.get('ip') != ip or \
           decoded_v.get('payload') != payload:
            await db.increment_bypass_attempt(identifier)
            return web.json_response({"success": False, "message": "Session mismatch."}, status=403)

        # ⏳ Timer Enforcement
        elapsed = time.time() - decoded_v.get('start_time')
        if elapsed < TIMER_THRESHOLD:
            await db.increment_bypass_attempt(identifier)
            record = await db.get_bypass_record(identifier)
            if record.get('attempts_count', 0) >= BAN_LIMIT:
                await db.ban_user_bypass(identifier, BAN_DURATION_HOURS)
                return web.json_response({"success": False, "message": "Timer bypass detected. You are now banned.", "banned": True}, status=403)
            return web.json_response({"success": False, "message": f"Please wait {int(TIMER_THRESHOLD - elapsed)} more seconds."}, status=403)

        # Verify token with Cloudflare
        client_session = request.app['client_session']
        async with client_session.post('https://challenges.cloudflare.com/turnstile/v0/siteverify', data={
            'secret': TURNSTILE_SECRET_KEY,
            'response': token,
            'remoteip': ip
        }) as resp:
            result = await resp.json()

        if result.get('success'):
            # Hostname validation
            expected_hostname = WEBSITE_URL.replace("https://", "").replace("http://", "").split(":")[0]
            if result.get('hostname') != expected_hostname and result.get('hostname') not in ['localhost', '127.0.0.1']:
                return web.json_response({"success": False, "message": "Hostname mismatch."}, status=403)

            # Verification Successful -> Reset attempts and generate final JWT
            await db.reset_bypass_attempts(identifier)

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
            await db.increment_bypass_attempt(identifier)
            return web.json_response({"success": False, "message": "Turnstile failed."}, status=403)

    except Exception as e:
        print(f"Error in verify: {e}")
        return web.json_response({"success": False, "message": "Internal error."}, status=500)

@routes.get("/banned")
async def banned_page(request):
    identifier = get_identifier(request)
    ban_expiry = await check_ban(identifier)
    if not ban_expiry:
        return web.HTTPFound("/")

    remaining = int(ban_expiry - time.time())
    hours, remainder = divmod(remaining, 3600)
    minutes, seconds = divmod(remainder, 60)
    time_str = f"{hours}h {minutes}m {seconds}s"

    return web.Response(text=BANNED_HTML.replace("{{ TIME_LEFT }}", time_str), content_type='text/html')

@routes.get("/bot-detected")
async def bot_detected(request):
    return web.Response(text=BOT_DETECTED_HTML, content_type='text/html')

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
        username = bot.username if bot else "OTAKULUX"
        return web.HTTPFound(f"https://t.me/{username}?start=yu3elk{payload}7")

    except:
        return web.HTTPFound(f"/verify/{payload}")
