#(©)Codexbotz
#@AniZoneFlix

from aiohttp import web
from web_server import routes as web_routes

async def web_server(bot):
    web_app = web.Application()
    web_app['bot'] = bot
    web_app.add_routes(web_routes)
    return web_app
