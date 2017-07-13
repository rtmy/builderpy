## методы для показа 

from aiohttp import web
from proveryalka import check, build, gitget
from datetime import timedelta, timezone
import asyncio
import db
import json
import re

async def index(request):
	return web.Response(text='Hello Aiohttp!')

async def build_handler(request):
        url = request.query['url']
        engine = request.app['db']
        await db.add_repository(engine, url)
        
        print(url)
        pattern = re.compile("(?P<s>[A-z]+\.[A-z]+)\/(?P<u>[A-z]+)\/(?P<r>[A-z]+)")
        s, u, r = pattern.match(url).group('s', 'u', 'r')	
        resp, config, *args = check(gitget(s, u, r))
        if resp == {'ok':'built'}:
              request.app.loop.create_task(db.add_run( \
                        engine, url, config, *args))
        print(resp)
        print("printed response")
        return web.json_response(resp)

async def recent_handler(request):
        response = list()
        engine = request.app['db']
        async with engine.acquire() as conn:
                async with conn.execute(db.run.select()) as rp:
                      for res in await rp.fetchall():
                             response.append({'url': res.rep_url, \
           'log': res.log, 'config': res.config, 'time': res.time.strftime("%c")})
        return web.json_response(response)

async def repository_handler(request):
	pass

async def config_handler(request):
	pass
async def log_handler(request):
	pass


