
from aiohttp import web
import os

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_handler(request):
    return web.Response(text="ᴀɴɪᴢᴏɴᴇꜰʟɪx ꜱᴇᴄᴜʀᴇ ꜱᴛʀᴇᴀᴍ ᴇɴɢɪɴᴇ ᴠ11.0 [STABLE]", content_type="text/plain")

@routes.get("/health")
async def health(request):
    return web.Response(text="OK")

async def web_server(bot):
    app = web.Application()
    app['bot'] = bot
    app.add_routes(routes)
    return app
