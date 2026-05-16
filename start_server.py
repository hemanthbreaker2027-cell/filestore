import asyncio
from aiohttp import web
from web_server import routes

async def run():
    app = web.Application()
    app.add_routes(routes)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "localhost", 8080)
    await site.start()
    print("Server started on http://localhost:8080")
    # Keep it running
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(run())
