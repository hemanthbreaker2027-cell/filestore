import asyncio
import time
import hashlib
import os
from aiohttp import web
from jinja2 import Environment, FileSystemLoader
from config import (
    RECAPTCHA_SITE_KEY, RECAPTCHA_SECRET_KEY, WEBSITE_URL
)
from helper_security import secure_redirect
from database.database import db

routes = web.RouteTableDef()

# Jinja2 Environment
template_env = Environment(loader=FileSystemLoader('templates'))

def get_real_ip(request):
    return request.headers.get('CF-Connecting-IP') or request.headers.get('X-Forwarded-For', request.remote)

def is_bot(request):
    ua = request.headers.get('User-Agent', '').lower()
    if not ua: return True

    # Block known automation tools
    bot_keywords = ['playwright', 'puppeteer', 'headless', 'curl', 'wget', 'python-requests', 'aiohttp', 'bot', 'spider', 'crawler']
    if any(k in ua for k in bot_keywords):
        return True

    # Check headers
    if request.method == 'POST':
        if not request.headers.get('sec-fetch-site') or not request.headers.get('accept-language'):
            return True

    return False

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("OTAKULUX Secure Redirect v3 (Non-Cloudflare)")

@routes.get("/r/{noise}/{token}")
async def intermediate_redirect_handler(request):
    # 1. Anti-Bot: rate limiting
    ip = get_real_ip(request)
    if not await db.check_rate_limit(ip):
        return web.Response(text="Rate limit exceeded. Try again later.", status=429)

    # 2. Anti-Bot: Header validation
    if is_bot(request):
        return web.Response(text="Bot access denied.", status=403)

    token = request.match_info['token']
    noise = request.match_info['noise']

    # 3. Validate token signature and decrypt early
    payload = secure_redirect.decrypt(token)
    if not payload:
        return web.Response(text="Invalid or corrupted security token.", status=403)

    if time.time() > payload.get('exp', 0):
        return web.Response(text="Security token has expired.", status=403)

    template = template_env.get_template('redirect.html')
    html = template.render(
        RECAPTCHA_SITE_KEY=RECAPTCHA_SITE_KEY,
        TOKEN=token,
        NOISE=noise
    )
    return web.Response(text=html, content_type='text/html')

@routes.post("/api/get_redirect")
async def secure_api_redirect(request):
    # 1. Anti-Bot: Rate limiting
    ip = get_real_ip(request)
    if not await db.check_rate_limit(ip, limit=3, window=30): # Stricter for API
        return web.json_response({"success": False, "message": "Too many attempts."}, status=429)

    # 2. Anti-Bot: Header validation
    if is_bot(request) or request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return web.json_response({"success": False, "message": "Access denied."}, status=403)

    try:
        data = await request.json()
        token = data.get('token')
        captcha_token = data.get('captcha')

        if not token or not captcha_token:
            return web.json_response({"success": False, "message": "Missing credentials."}, status=400)

        # 3. Verify reCAPTCHA v3
        client_session = request.app['client_session']
        async with client_session.post('https://www.google.com/recaptcha/api/siteverify', data={
            'secret': RECAPTCHA_SECRET_KEY,
            'response': captcha_token,
            'remoteip': ip
        }) as resp:
            recaptcha_result = await resp.json()

        if not recaptcha_result.get('success') or \
           recaptcha_result.get('score', 0) < 0.5 or \
           recaptcha_result.get('action') != 'redirect_access':
            return web.json_response({"success": False, "message": "High-risk activity detected. Access denied."}, status=403)

        # 4. Validate Token
        payload = secure_redirect.decrypt(token)
        if not payload:
            return web.json_response({"success": False, "message": "Invalid security token."}, status=403)

        if time.time() > payload.get('exp', 0):
            return web.json_response({"success": False, "message": "Security token expired."}, status=403)

        # 5. Optional: Match IP Hash if present
        if payload.get('ip_hash'):
            current_ip_hash = hashlib.sha256(ip.encode()).hexdigest()
            if payload['ip_hash'] != current_ip_hash:
                return web.json_response({"success": False, "message": "Security context mismatch."}, status=403)

        # 6. One-Time Token Check
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        if not await db.use_secure_token(token_hash):
            return web.json_response({"success": False, "message": "This link has already been used."}, status=403)

        # 7. Success - Return Final URL
        return web.json_response({
            "success": True,
            "url": payload['url']
        })

    except Exception as e:
        print(f"Secure API Error: {e}")
        return web.json_response({"success": False, "message": "Internal security error."}, status=500)

@routes.get("/health")
async def health_check(request):
    return web.Response(text="OK")
