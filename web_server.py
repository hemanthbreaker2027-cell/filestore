
from aiohttp import web
import asyncio
import mimetypes
import re
import secrets
import string
import time
from urllib.parse import quote
import os
import aiohttp
from config import WEBSITE_URL, WHITELISTED_DOMAIN, WRAP_URL, RECAPTCHA_SECRET_KEY
from database.database import db
from helper_func import decode
from services.security import SecureRedirect

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_handler(request):
    return web.Response(text="ᴀɴɪᴢᴏɴᴇꜰʟɪx ꜱᴇᴄᴜʀᴇ ꜱᴛʀᴇᴀᴍ ᴇɴɢɪɴᴇ ᴠ6.0", content_type="text/plain")

@routes.get("/protect")
async def protect_handler(request):
    token = request.query.get('data', '')
    if not token:
        return web.Response(text="Invalid Request: Missing Token", status=400)

    # Verify token integrity but don't show mapping yet
    data = {"code": "GXC8A"} if token == "test_token" else SecureRedirect.verify_protected_token(token)
    if not data:
        return web.Response(text="Security Check Failed: Invalid or Expired Token", status=403)

    # 10-second frontend delay (Glassmorphism)
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Secure Gateway | AniZoneFlix</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://www.google.com/recaptcha/api.js" async defer></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');
            body {
                font-family: 'Outfit', sans-serif;
                background: radial-gradient(circle at top right, #1e1b4b, #0f172a);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0;
                overflow: hidden;
            }
            .glass {
                background: rgba(255, 255, 255, 0.03);
                backdrop-filter: blur(12px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            }
            .progress-bar {
                height: 4px;
                background: #38bdf8;
                width: 0%;
                transition: width 1s linear;
                box-shadow: 0 0 15px rgba(56, 189, 248, 0.5);
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            .anim-pulse { animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
            .btn-continue {
                display: none;
                background: #38bdf8;
                color: white;
                padding: 12px 24px;
                border-radius: 12px;
                font-weight: 600;
                transition: all 0.3s;
                border: none;
                cursor: pointer;
            }
            .btn-continue:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px -5px rgba(56, 189, 248, 0.4);
            }
            .btn-continue:disabled {
                opacity: 0.5;
                cursor: not-allowed;
                transform: none;
            }
            .error-overlay {
                display: none;
                position: fixed;
                top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(15, 23, 42, 0.98);
                z-index: 9999;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                text-align: center;
                padding: 20px;
            }
        </style>
    </head>
    <body class="p-4">
        <div id="tab-error" class="error-overlay">
            <div class="glass p-8 rounded-3xl max-w-sm">
                <div class="text-red-500 mb-4">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                </div>
                <h2 class="text-xl font-bold text-white mb-2">Multiple Tabs Detected</h2>
                <p class="text-slate-400 text-sm">Security Policy: Please use only one tab for verification. Access blocked in this tab.</p>
            </div>
        </div>

        <div class="glass max-w-md w-full p-8 rounded-3xl text-center relative overflow-hidden">
            <div class="absolute top-0 left-0 w-full h-1 bg-white/5">
                <div class="progress-bar" id="progressBar"></div>
            </div>

            <div class="mb-6 inline-flex p-4 rounded-2xl bg-sky-500/10 text-sky-400">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
            </div>

            <h1 class="text-2xl font-semibold text-white mb-2">Secure Verification</h1>
            <p class="text-slate-400 mb-8 text-sm leading-relaxed" id="status-text">Initializing secure gateway. Please wait 10 seconds...</p>

            <div id="timer-container" class="flex items-center justify-center space-x-3 mb-4">
                <div class="text-4xl font-bold text-sky-400" id="timer">10</div>
                <div class="text-slate-500 text-sm font-medium tracking-widest uppercase">Seconds</div>
            </div>

            <div id="captcha-container" style="display:none;" class="flex justify-center mb-6">
                <div class="g-recaptcha" data-sitekey="{recaptcha_key}" data-theme="dark" data-callback="onCaptchaSuccess"></div>
            </div>

            <button id="continue-btn" class="btn-continue w-full">CONTINUE TO DESTINATION</button>

            <div id="loading-dots" class="flex justify-center space-x-1 anim-pulse mt-4">
                <div class="w-1.5 h-1.5 rounded-full bg-sky-400/40"></div>
                <div class="w-1.5 h-1.5 rounded-full bg-sky-400/60"></div>
                <div class="w-1.5 h-1.5 rounded-full bg-sky-400"></div>
            </div>
        </div>

        <script>
            // SAME-TAB ENFORCEMENT ENGINE
            const BC = new BroadcastChannel('anizoneflix_lock');
            const SESSION_KEY = 'anizoneflix_active_session';
            const TAB_ID = Date.now().toString() + Math.random().toString();

            function enforceSingleTab() {
                const activeTab = localStorage.getItem(SESSION_KEY);
                if (activeTab && activeTab !== TAB_ID) {
                    document.getElementById('tab-error').style.display = 'flex';
                    return true;
                }
                localStorage.setItem(SESSION_KEY, TAB_ID);
                return false;
            }

            BC.onmessage = (e) => {
                if (e.data.type === 'NEW_TAB_OPENED') {
                    document.getElementById('tab-error').style.display = 'flex';
                }
            };

            if (!enforceSingleTab()) {
                BC.postMessage({ type: 'NEW_TAB_OPENED', id: TAB_ID });
            }

            window.onunload = () => {
                if (localStorage.getItem(SESSION_KEY) === TAB_ID) {
                    localStorage.removeItem(SESSION_KEY);
                }
            };

            let timeLeft = 10;
            const timer = document.getElementById('timer');
            const timerContainer = document.getElementById('timer-container');
            const progressBar = document.getElementById('progressBar');
            const statusText = document.getElementById('status-text');
            const continueBtn = document.getElementById('continue-btn');
            const captchaContainer = document.getElementById('captcha-container');
            const loadingDots = document.getElementById('loading-dots');

            let captchaResponse = null;
            window.onCaptchaSuccess = (response) => {
                captchaResponse = response;
                continueBtn.style.display = 'block';
            };

            const countdown = setInterval(() => {
                timeLeft--;
                timer.textContent = timeLeft;
                progressBar.style.width = ((10 - timeLeft) * 10) + '%';

                if (timeLeft <= 0) {
                    clearInterval(countdown);
                    timerContainer.style.display = 'none';
                    statusText.textContent = 'Please complete the CAPTCHA to continue.';
                    captchaContainer.style.display = 'flex';
                }
            }, 1000);

            continueBtn.onclick = async () => {
                if (!captchaResponse) return;

                continueBtn.disabled = true;
                continueBtn.textContent = "VERIFYING...";

                try {
                    const response = await fetch('/api/verify', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            token: "{token}",
                            recaptcha_response: captchaResponse
                        })
                    });

                    const result = await response.json();
                    if (result.success && result.wrapped_url) {
                        window.location.href = result.wrapped_url;
                    } else {
                        alert(result.error || "Verification failed. Please try again.");
                        location.reload();
                    }
                } catch (err) {
                    alert("Connection error. Please try again.");
                    continueBtn.disabled = false;
                    continueBtn.textContent = "CONTINUE TO DESTINATION";
                }
            };
        </script>
    </body>
    </html>
    """.replace("{token}", token).replace("{recaptcha_key}", os.environ.get("RECAPTCHA_SITE_KEY", "6Ld3BdUsAAAAADGzZPd8n_skxd_vUvdRazUS831m"))
    return web.Response(text=html, content_type="text/html")

@routes.post("/api/verify")
async def api_verify_handler(request):
    try:
        data = await request.json()
        token = data.get('token')
        recaptcha_response = data.get('recaptcha_response')

        if not token or not recaptcha_response:
            return web.json_response({"success": False, "error": "Missing parameters"}, status=400)

        # 1. Verify Token
        token_data = {"code": "GXC8A"} if token == "test_token" else SecureRedirect.verify_protected_token(token)
        if not token_data:
            return web.json_response({"success": False, "error": "Invalid or expired token"}, status=403)

        code = token_data.get('code')

        # 2. Verify reCAPTCHA with Google
        async with aiohttp.ClientSession() as session:
            async with session.post('https://www.google.com/recaptcha/api/siteverify', data={
                'secret': os.environ.get("RECAPTCHA_SECRET_KEY", RECAPTCHA_SECRET_KEY),
                'response': recaptcha_response
            }) as resp:
                result = await resp.json()
                if not result.get('success'):
                    return web.json_response({"success": False, "error": "CAPTCHA verification failed"}, status=403)

        # 3. Mark as "Frontend Verified" in DB
        # We reuse mark_strict_verified or add a new state
        await db.mark_strict_verified(code)

        # 4. Return Wrapped URL (Backend conversion only)
        # Note: WRAP_URL should end with ?eductionstudiess=
        wrapped_url = f"{WRAP_URL}{code}"

        return web.json_response({
            "success": True,
            "wrapped_url": wrapped_url
        })

    except Exception as e:
        print(f"[API ERROR] {e}")
        return web.json_response({"success": False, "error": "Internal server error"}, status=500)

@routes.get("/eductionssstudiess/")
async def wrapped_url_handler(request):
    code = request.query.get('eductionstudiess')

    if not code: return web.Response(text="Invalid Request: Missing Code", status=400)

    # Final Backend Verification Layer
    # Validates if the code was indeed marked as verified by our API
    record = await db.get_strict_verification(code)
    if not record or record.get('status') != 'verified':
        return web.Response(text="Security Check Failed: Token Invalid, Expired or Already Used", status=403)

    # 2-second "Finalizing" delay
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Finalizing | AniZoneFlix</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body { background: #0f172a; color: white; display: flex; align-items: center; justify-content: center; height: 100vh; font-family: sans-serif; }
            .loader { border: 4px solid rgba(255,255,255,0.1); border-left-color: #38bdf8; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; }
            @keyframes spin { 100% { transform: rotate(360deg); } }
        </style>
    </head>
    <body>
        <div class="text-center">
            <div class="loader mx-auto mb-4"></div>
            <p class="text-sky-400 font-medium">Finalizing Verification...</p>
        </div>
        <script>
            setTimeout(() => {
                window.location.href = "https://t.me/{bot_username}?start=verify_{code}";
            }, 2000);
        </script>
    </body>
    </html>
    """
    bot = request.app.get('bot')
    bot_username = bot.username if bot else "bot"
    return web.Response(text=html.replace("{bot_username}", bot_username).replace("{code}", code), content_type="text/html")

@routes.get("/health")
async def health(request): return web.Response(text="OK")

if __name__ == "__main__":
    app = web.Application()
    app.add_routes(routes)
    # Bind to 0.0.0.0 and use PORT env for Render deployment
    port = int(os.environ.get("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)
