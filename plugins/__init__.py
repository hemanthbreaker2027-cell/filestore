#(©)Codexbotz
#@AniZoneFlix





import aiohttp
import aiohttp_jinja2
import jinja2
from aiohttp import web
from web_server import routes as web_routes


async def on_cleanup(app):
    await app['client_session'].close()

async def web_server(bot):
    # client_max_size increased to handle large metadata and optimize for speed
    web_app = web.Application(client_max_size=1024**3) # 1GB limit for headers/meta
    aiohttp_jinja2.setup(web_app, loader=jinja2.FileSystemLoader('templates'))
    web_app['bot'] = bot
    web_app['client_session'] = aiohttp.ClientSession()
    web_app.on_cleanup.append(on_cleanup)
    web_app.add_routes(web_routes)
    return web_app
