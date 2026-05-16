
from aiohttp import web
import os

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_handler(request):
    return web.Response(text="ᴀɴɪᴢᴏɴᴇꜰʟɪx ꜱᴇᴄᴜʀᴇ ꜱᴛʀᴇᴀᴍ ᴇɴɢɪɴᴇ ᴠ11.0 [STABLE]", content_type="text/plain")

@routes.get("/health")
async def health(request):
    return web.Response(text="OK")
