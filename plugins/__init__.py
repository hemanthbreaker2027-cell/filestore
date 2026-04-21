#(©)Codexbotz
#@OTAKULUX





from aiohttp import web
from .route import routes


async def on_cleanup(app):
    await app['client_session'].close()

async def web_server(bot):
    web_app = web.Application(client_max_size=30000000)
    web_app['bot'] = bot
    web_app['client_session'] = aiohttp.ClientSession()
    web_app.on_cleanup.append(on_cleanup)
    web_app.add_routes(routes)
    return web_app
