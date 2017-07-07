## методы для показа 

from aiohttp import web
from proveryalka import check, build, gitget
import datetime
import db
import json

async def index(request):
	return web.Response(text='Hello Aiohttp!')

async def build_handler(request):
        url = request.query['url']
        engine = request.app['db']
        await db.add_repository(engine, url)
	
        resp, config, *args = check(gitget(url))
        print(config)
        if resp == {'ok':'built'}:
              result = await build(*args)
              async with engine.acquire() as conn:
                    await conn.execute(db.run.insert().values( \
                      log=str(result), \
                          config=str(config), \
                          time=datetime.datetime.now(), rep_url=url))
        return web.json_response(resp)

async def recent_handler(request):
        response = list()
        engine = request.app['db']
        async with engine.acquire() as conn:
                async with conn.execute(db.run.select()) as rp:
                      for res in await rp.fetchall():
                             response.append({'url': res.rep_url, \
           'log': res.log, 'config': res.config, 'time': res.time.strftime("%c")})
        print(response)
        return web.json_response(response)

async def repository_handler(request):
	pass

async def config_handler(request):
	pass
async def log_handler(request):
	pass


