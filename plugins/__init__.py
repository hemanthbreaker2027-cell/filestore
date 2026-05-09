#(©)Codexbotz
#@AniZoneFlix





import aiohttp
from aiohttp import web
from .route import routes


async def on_cleanup(app):
    await app['client_session'].close()

async def web_server(bot):
    # client_max_size increased to handle large metadata and optimize for speed
    web_app = web.Application(client_max_size=1024**3) # 1GB limit for headers/meta
    web_app['bot'] = bot
    web_app['client_session'] = aiohttp.ClientSession()
    web_app.on_cleanup.append(on_cleanup)
    web_app.add_routes(routes)
    return web_app
