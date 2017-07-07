from aiohttp import web
from routes import setup_routes
from staticconf import load_config
from db import init_pg, close_pg

app = web.Application()
app.on_startup.append(init_pg)
app.on_cleanup.append(close_pg)
setup_routes(app)
web.run_app(app)
