import aiopg.sa
import datetime
import sqlalchemy as sa
import json
from proveryalka import build

async def init_pg(app):
    conf = app['config']
    engine = await aiopg.sa.create_engine(
        database=conf['database'],
        user=conf['db-user'],
        password=conf['db-password'],
        host=conf['db-host'],
        port=conf['db-port'])
    app['db'] = engine

async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()

async def create_tables(app):
    engine = app['db']
    async with engine.acquire() as conn:
        await conn.execute('drop table if exists run')
        await conn.execute('drop table if exists repository')
        await conn.execute('create table repository \
        (rep_url text primary key)')
        await conn.execute('create table run \
        (run_id serial primary key, \
        rep_url text references repository(rep_url), \
        time timestamp, \
        log text, \
        config text)')

async def add_run(engine, url, config, *args):
       result = await build(*args)
       async with engine.acquire() as conn:
               await conn.execute(run.insert().values( \
                      log=str(result), \
                          config=str(config), \
                     time=datetime.datetime.now(), rep_url=url))
       print("added run")

# Добавляем запись с URL-ом в БД, если не существует
async def add_repository(engine, url):
	async with engine.acquire() as conn:
                async with conn.execute(repository.select( \
                                 repository.c.rep_url==url)) as rp:
                      res = await rp.fetchone()
                      if not res:
                           await conn.execute(repository.insert().values( \
                                      rep_url=url))


ma = sa.MetaData()
run = sa.Table('run', ma,
    sa.Column('run_id', sa.Integer, primary_key=True),
    sa.Column('rep_url', sa.String(), sa.ForeignKey("repository.rep_url"), \
            nullable=False),
    sa.Column('log', sa.String(), nullable=True),
    sa.Column('config', sa.String(), nullable=False),
    sa.Column('time', sa.DateTime(), nullable=False),
)

repository = sa.Table('repository', ma,
    sa.Column('rep_url', sa.String(), primary_key=True)
)
