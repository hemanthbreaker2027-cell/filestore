
from aiohttp import web
import aiohttp
import jwt
import time
import re
from config import TURNSTILE_SITE_KEY, TURNSTILE_SECRET_KEY, JWT_SECRET, WEBSITE_URL, SHORTLINK_URL, SHORTLINK_API
from plugins.turnstile_html import TURNSTILE_HTML
from helper_func import get_shortlink

routes = web.RouteTableDef()

# Simple IP-based rate limiting
ip_requests = {}

def get_real_ip(request):
    return request.headers.get('CF-Connecting-IP') or request.headers.get('X-Forwarded-For', request.remote)

def is_rate_limited(ip):
    current_time = time.time()
    if ip not in ip_requests:
        ip_requests[ip] = []

    # Remove requests older than 1 minute
    ip_requests[ip] = [t for t in ip_requests[ip] if current_time - t < 60]

    if len(ip_requests[ip]) > 30: # 30 requests per minute
        return True

    ip_requests[ip].append(current_time)
    return False

def is_proxy(request):
    # Check for common proxy headers and Cloudflare indicators
    if request.headers.get('CF-IPCountry') in ['T1', 'XX']: # Tor or unknown
        return True

    # Check if we should block common proxies/VPNs by header
    if request.headers.get('X-Proxy-ID') or request.headers.get('Via'):
        return True

    return False

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("OTAKULUX FileStore")

@routes.get("/verify/{payload}")
async def turnstile_page(request):
    payload = request.match_info['payload']

    if is_proxy(request):
        return web.Response(text="VPN/Proxy not allowed. Please disable it to proceed.", status=403)

    # Site key and payload injection
    html = TURNSTILE_HTML.replace("{{ SITE_KEY }}", TURNSTILE_SITE_KEY).replace("{{ PAYLOAD }}", payload)
    return web.Response(text=html, content_type='text/html')

@routes.post("/verify_token")
async def verify_turnstile(request):
    ip = get_real_ip(request)
    if is_rate_limited(ip):
        return web.json_response({"success": False, "message": "Too many requests. Slow down!"}, status=429)

    try:
        data = await request.json()
        token = data.get('token')
        payload = data.get('payload')

        if not token:
            return web.json_response({"success": False, "message": "Missing token"}, status=400)

        # Verify token with Cloudflare
        # Reusing session from app state
        client_session = request.app['client_session']
        async with client_session.post('https://challenges.cloudflare.com/turnstile/v0/siteverify', data={
            'secret': TURNSTILE_SECRET_KEY,
            'response': token,
            'remoteip': ip
        }) as resp:
            result = await resp.json()

        if result.get('success'):
            # Security: Hostname validation
            expected_hostname = WEBSITE_URL.replace("https://", "").replace("http://", "").split(":")[0]
            if result.get('hostname') != expected_hostname:
                # If we are in local dev, allow localhost
                if result.get('hostname') not in ['localhost', '127.0.0.1', expected_hostname]:
                    return web.json_response({"success": False, "message": "Hostname mismatch. Unauthorized domain."}, status=403)

            # Generate session JWT
            session_token = jwt.encode({
                'payload': payload,
                'iat': int(time.time()),
                'exp': int(time.time()) + 3600 # 1 hour expiry
            }, JWT_SECRET, algorithm='HS256')

            # Create destination URL for shortener
            final_dest = f"{WEBSITE_URL}/f/{payload}"

            # Use shortener
            short_url_result = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, final_dest)

            response = web.json_response({
                "success": True,
                "redirect": short_url_result
            })

            # Set secure session cookie
            response.set_cookie('session', session_token, httponly=True, secure=True, samesite='Lax')
            return response
        else:
            return web.json_response({"success": False, "message": "Verification failed"}, status=403)

    except Exception as e:
        print(f"Error in verify: {e}")
        return web.json_response({"success": False, "message": f"Internal server error: {str(e)}"}, status=500)

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
        if bot:
            username = bot.username
        else:
            username = "OTAKULUX"

        # Ensure we use the format the bot expects to avoid re-shortening loop
        # The bot expects start payload or yu3elk{payload}7
        return web.HTTPFound(f"https://t.me/{username}?start=yu3elk{payload}7")

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return web.HTTPFound(f"/verify/{payload}")
    except Exception as e:
        print(f"Error in final_redirect: {e}")
        return web.HTTPFound(f"/verify/{payload}")
