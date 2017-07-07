## методы для показа 

from aiohttp import web
from proveryalka import build, gitget
import datetime
import db
import json

async def index(request):
	return web.Response(text='Hello Aiohttp!')

async def build_handler(request):
        url = request.query['url']
        engine = request.app['db']
        await db.add_repository(engine, url)
	
        resp, result, config = build(gitget(url))
        print(resp, result, config)
        if resp == {'ok':'built'}:
              async with engine.acquire() as conn:
                    await conn.execute(db.run.insert().values( \
                      log=json.dumps(result), config=json.dumps(config), \
                          time=datetime.datetime.now(), rep_url=url))
        return web.json_response(resp)

async def recent_handler(request):
        engine = request.app['db']
        async with engine.acquire() as conn:
                async with conn.execute(db.run.select()) as rp:
                      res = await rp.fetchall()
        return web.Response(text=str(res))

async def repository_handler(request):
	pass

async def config_handler(request):
	pass
async def log_handler(request):
	pass


