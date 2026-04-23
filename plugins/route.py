
from aiohttp import web
import aiohttp
import jwt
import time
import re
import asyncio
from config import JWT_SECRET, WEBSITE_URL
from helper_func import get_shortlink, decode, encode
from database.database import db

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    try:
        with open("templates/index.html", "r") as f:
            content = f.read()
        return web.Response(text=content, content_type='text/html')
    except:
        return web.json_response("OTAKULUX FileStore v2")

@routes.get("/watch/{payload}")
async def watch_page(request):
    payload = request.match_info['payload']
    try:
        with open("templates/watch.html", "r") as f:
            content = f.read()
        content = content.replace("{{ PAYLOAD }}", payload)

        # Try to fetch real metadata
        try:
            bot = request.app['bot']
            decoded_string = await decode(payload)
            if decoded_string.startswith("get-"):
                msg_id = int(int(decoded_string.split("-")[1]) / abs(bot.db_channel.id))
            else:
                msg_id = int(int(decoded_string) / abs(bot.db_channel.id))

            metadata = await db.get_anime_metadata(msg_id)
            if metadata:
                content = content.replace("Solo Leveling", metadata.get('anime_name', 'Unknown Anime'))
                content = content.replace("Season 1", f"Season {metadata.get('season', '--')}")
                content = content.replace("Episode 1", f"Episode {metadata.get('episode', '--')}")

                anilist = metadata.get('anilist', {})
                if anilist:
                    desc = anilist.get('description', 'No description available.')
                    # Strip HTML tags from description if any
                    clean_desc = re.sub('<[^<]+?>', '', desc)
                    content = content.replace("In a world where hunters...", clean_desc)
                    if anilist.get('bannerImage'):
                         content = content.replace('https://vjs.zencdn.net/v/oceans.png', anilist.get('bannerImage'))
        except Exception as meta_e:
            print(f"Metadata fetch error for watch page: {meta_e}")

        return web.Response(text=content, content_type='text/html')
    except Exception as e:
        return web.Response(text=f"Error loading watch page: {e}", status=500)

@routes.get("/health")
async def health_check(request):
    return web.Response(text="OK", status=200)

@routes.get("/api/trending")
async def api_trending(request):
    # Fetch top 10 recent anime for trending
    cursor = db.anime_data.find().sort("_id", -1).limit(10)
    results = await cursor.to_list(length=10)
    data = []
    for res in results:
        bot = request.app['bot']
        converted_id = res['_id'] * abs(bot.db_channel.id)
        payload = await encode(f"get-{converted_id}")

        anilist = res.get('anilist', {})
        img = anilist.get('coverImage', {}).get('extraLarge') or "https://telegra.ph/file/e292b12890b8b4b9dcbd1.jpg"

        data.append({
            "id": payload,
            "title": res.get('anime_name'),
            "ep": res.get('episode'),
            "img": img
        })
    return web.json_response(data)

@routes.get("/api/latest")
async def api_latest(request):
    # Fetch 10 latest anime
    cursor = db.anime_data.find().sort("_id", -1).limit(10)
    results = await cursor.to_list(length=10)
    data = []
    for res in results:
        bot = request.app['bot']
        converted_id = res['_id'] * abs(bot.db_channel.id)
        payload = await encode(f"get-{converted_id}")

        anilist = res.get('anilist', {})
        img = anilist.get('coverImage', {}).get('extraLarge') or "https://telegra.ph/file/e292b12890b8b4b9dcbd1.jpg"

        data.append({
            "id": payload,
            "title": res.get('anime_name'),
            "ep": res.get('episode'),
            "img": img
        })
    return web.json_response(data)

@routes.get("/stream/{payload}")
@routes.get("/stream/{payload}/{token}")
async def stream_handler(request):
    payload = request.match_info['payload']
    token = request.match_info.get('token')

    # We simplified the security, but we can still keep token-based access for player compatibility if needed
    # or just allow access directly. For better compatibility with Video.js/External Players,
    # let's allow access if there's a valid website URL context or token.

    bot = request.app['bot']

    try:
        decoded_string = await decode(payload)
        # Handle both "get-ID" and raw ID if needed
        if decoded_string.startswith("get-"):
            msg_id = int(int(decoded_string.split("-")[1]) / abs(bot.db_channel.id))
        else:
            msg_id = int(int(decoded_string) / abs(bot.db_channel.id))

        message = await bot.get_messages(bot.db_channel.id, msg_id)
        if not message or not message.media:
            return web.HTTPNotFound(text="File not found or not a media file.")

        media = getattr(message, message.media.value)
        file_size = media.file_size
        file_name = getattr(media, 'file_name', 'video.mp4')
        mime_type = getattr(media, 'mime_type', 'video/mp4')

        # Handle Range Requests for Seeking
        range_header = request.headers.get('Range')
        start = 0
        end = file_size - 1

        if range_header:
            try:
                kind, ranges = range_header.split('=')
                if kind == 'bytes':
                    start_str, end_str = ranges.split('-')
                    start = int(start_str) if start_str else 0
                    if end_str:
                        end = int(end_str)
            except:
                pass

        if start >= file_size:
             return web.Response(status=416, text="Requested range not satisfiable")

        response = web.StreamResponse(
            status=206 if range_header else 200,
            reason='Partial Content' if range_header else 'OK',
            headers={
                'Content-Type': mime_type,
                'Content-Disposition': f'attachment; filename="{file_name}"',
                'Content-Length': str(end - start + 1),
                'Content-Range': f'bytes {start}-{end}/{file_size}',
                'Accept-Ranges': 'bytes',
            }
        )

        await response.prepare(request)

        async for chunk in bot.stream_media(message, offset=start, limit=end - start + 1):
            await response.write(chunk)

        await response.write_eof()
        return response

    except Exception as e:
        print(f"Stream Error: {e}")
        return web.HTTPInternalServerError(text=str(e))
