
from aiohttp import web
import asyncio
import mimetypes
import re
from urllib.parse import quote
from config import WEBSITE_URL, WHITELISTED_DOMAIN, WRAP_URL
from database.database import db
from helper_func import decode

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_handler(request):
    return web.Response(text="ᴀɴɪᴢᴏɴᴇꜰʟɪx ꜱᴇᴄᴜʀᴇ ꜱᴛʀᴇᴀᴍ ᴇɴɢɪɴᴇ ᴠ6.0", content_type="text/plain")

@routes.get("/protect")
async def protect_landing_page(request):
    code = request.query.get('code')
    if not code: return web.Response(text="Invalid Token", status=400)

    record = await db.get_strict_verification(code)
    if not record: return web.Response(text="Verification Link Expired", status=403)

    # STEP 2: 5-second frontend delay (Redesigned Glassmorphism)
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AniZoneFlix | Secure Gateway</title>
        <script src="https://cdn.tailwindcss.com"></script>
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
            .neon-text {
                text-shadow: 0 0 10px rgba(56, 189, 248, 0.3);
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            .anim-pulse { animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
        </style>
    </head>
    <body class="p-4">
        <div class="glass max-w-md w-full p-8 rounded-3xl text-center relative overflow-hidden">
            <div class="absolute top-0 left-0 w-full h-1 bg-white/5">
                <div class="progress-bar" id="progressBar"></div>
            </div>

            <div class="mb-6 inline-flex p-4 rounded-2xl bg-sky-500/10 text-sky-400">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
            </div>

            <h1 class="text-2xl font-semibold text-white mb-2 neon-text">Secure Verification</h1>
            <p class="text-slate-400 mb-8 text-sm leading-relaxed">We are securing your request. Please wait a moment while we redirect you to the final destination.</p>

            <div class="flex items-center justify-center space-x-3 mb-4">
                <div class="text-4xl font-bold text-sky-400" id="timer">5</div>
                <div class="text-slate-500 text-sm font-medium tracking-widest uppercase">Seconds Left</div>
            </div>

            <div class="flex justify-center space-x-1 anim-pulse">
                <div class="w-1.5 h-1.5 rounded-full bg-sky-400/40"></div>
                <div class="w-1.5 h-1.5 rounded-full bg-sky-400/60"></div>
                <div class="w-1.5 h-1.5 rounded-full bg-sky-400"></div>
            </div>
        </div>

        <script>
            let timeLeft = 5;
            const timer = document.getElementById('timer');
            const progressBar = document.getElementById('progressBar');

            const countdown = setInterval(() => {
                timeLeft--;
                timer.textContent = timeLeft;
                progressBar.style.width = ((5 - timeLeft) * 20) + '%';

                if (timeLeft <= 0) {
                    clearInterval(countdown);
                    // STEP 3: Redirect to WRAP URL with CODE
                    window.location.href = "{wrap_url}" + "{code}";
                }
            }, 1000);
        </script>
    </body>
    </html>
    """.replace("{code}", code).replace("{wrap_url}", WRAP_URL)
    return web.Response(text=html, content_type="text/html")

@routes.get("/universtiesstudiess/")
async def wrapped_url_handler(request):
    code = request.query.get('studiessinsurancess')
    if not code: return web.Response(text="Invalid Request", status=400)

    stage = request.query.get('stage', '1')
    if stage == '1':
        # STEP 4: 2-second backend verification UI
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Finalizing Verification</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');
                body {
                    font-family: 'Outfit', sans-serif;
                    background: #0f172a;
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0;
                }
                .loader {
                    border: 3px solid rgba(56, 189, 248, 0.1);
                    border-top: 3px solid #38bdf8;
                    border-radius: 50%;
                    width: 48px;
                    height: 48px;
                    animation: spin 1s linear infinite;
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        </head>
        <body>
            <div class="text-center">
                <div class="loader mb-6 mx-auto"></div>
                <h1 class="text-xl font-medium text-white mb-2">Finalizing Verification</h1>
                <p class="text-slate-400 text-sm">Please wait while we confirm your request...</p>
            </div>
            <script>
                setTimeout(() => {
                    const url = new URL(window.location.href);
                    url.searchParams.set('stage', '2');
                    window.location.href = url.toString();
                }, 2000);
            </script>
        </body>
        </html>
        """
        return web.Response(text=html, content_type="text/html")

    success = await db.mark_strict_verified(code)
    if success:
        bot = request.app.get('bot')
        bot_username = bot.username if bot else "bot"
        return web.HTTPFound(location=f"https://t.me/{bot_username}?start=verify_{code}")

    return web.Response(text="Link Expired or Invalid", status=403)

@routes.get("/watch")
async def watch_handler(request):
    code = request.query.get('path')
    record = await db.verify_shortener_code(code)
    if not record: return web.Response(text="Invalid Link", status=403)
    file_name = record.get('file_name', 'video.mp4')
    stream_url = f"https://{request.host}/stream/file/{code}/{quote(file_name)}"
    return web.Response(text=f"Stream URL: {stream_url}")

@routes.get("/download/{code}")
async def download_handler(request):
    return await stream_file_handler(request, is_download=True)

@routes.get("/stream/file/{code}")
@routes.get("/stream/file/{code}/{filename}")
async def stream_file_handler(request, is_download=False):
    code = request.match_info.get('code')
    record = await db.verify_shortener_code(code)
    if not record: return web.Response(text="Forbidden", status=403)
    bot = request.app.get('bot')
    if not bot: return web.Response(text="Bot Not Found", status=500)
    original_url = record.get('original_url', '')
    match = re.search(r"get-(\d+)", original_url)
    if not match: return web.Response(text="Media Not Found", status=404)
    msg_id = int(int(match.group(1)) / abs(bot.db_channel.id))
    try:
        msg = await bot.get_messages(bot.db_channel.id, msg_id)
        file_obj = msg.video or msg.document
        if not file_obj: return web.Response(text="No Streamable Media", status=404)
        file_size = file_obj.file_size
        resp = web.StreamResponse(status=200)
        resp.headers.update({'Content-Type': file_obj.mime_type or 'video/mp4', 'Content-Length': str(file_size)})
        if is_download: resp.headers['Content-Disposition'] = f'attachment; filename="{quote(file_obj.file_name)}"'
        await resp.prepare(request)
        async for chunk in bot.stream_media(file_obj):
            await resp.write(chunk)
        return resp
    except: return web.Response(text="Error", status=500)

@routes.get("/health")
async def health(request): return web.Response(text="OK")
