
from aiohttp import web
import jinja2
import aiohttp_jinja2
import os

async def protect(request):
    context = {
        'RECAPTCHA_SITE_KEY': '6LfvWswsAAAAADgpyWripb1IZSbBjlniKAmdBjSv',
        'ENCODED_URL': 'V3V0T0tLejV6dnI2...' # Example token
    }
    with open('templates/protect.html', 'r') as f:
        template = f.read()

    html = template.replace('{{ RECAPTCHA_SITE_KEY }}', context['RECAPTCHA_SITE_KEY'])
    html = html.replace('{{ ENCODED_URL }}', context['ENCODED_URL'])
    return web.Response(text=html, content_type='text/html')

async def safe(request):
    context = {
        'RECAPTCHA_SITE_KEY': '6LfvWswsAAAAADgpyWripb1IZSbBjlniKAmdBjSv',
        'TOKEN': 'some_token'
    }
    with open('templates/safe.html', 'r') as f:
        template = f.read()

    html = template.replace('{{ RECAPTCHA_SITE_KEY }}', context['RECAPTCHA_SITE_KEY'])
    html = html.replace('{{ TOKEN }}', context['TOKEN'])
    return web.Response(text=html, content_type='text/html')

async def banned(request):
    with open('templates/banned.html', 'r') as f:
        html = f.read()
    html = html.replace('{{ TIME_LEFT }}', '23h 59m 59s')
    html = html.replace('{{ MESSAGE }}', 'Multiple bypass attempts detected.')
    return web.Response(text=html, content_type='text/html')

app = web.Application()
app.router.add_get('/protect', protect)
app.router.add_get('/safe', safe)
app.router.add_get('/banned', banned)

if __name__ == '__main__':
    web.run_app(app, port=8001)
