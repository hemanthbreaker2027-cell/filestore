from aiohttp import web

routes = web.RouteTableDef()

@OTAKULUX.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("OTAKULUX FileStore")
