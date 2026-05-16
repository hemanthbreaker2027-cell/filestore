import asyncio
from aiohttp import web
import jinja2
import aiohttp_jinja2
from playwright.async_api import async_playwright

async def mock_verify(request):
    return aiohttp_jinja2.render_template('secure_verify.html', request, {
        'token': 'MOCK_TOKEN',
        'domain': 'localhost',
        'site_key': '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
    })

async def run_server():
    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))
    app.router.add_get('/', mock_verify)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    return runner

async def capture():
    runner = await run_server()
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('http://localhost:8080')
        await asyncio.sleep(2)  # wait for timer to start
        await page.screenshot(path='/home/jules/verification/secure_verify_screenshot.png')
        await browser.close()
    await runner.cleanup()

if __name__ == '__main__':
    asyncio.run(capture())
