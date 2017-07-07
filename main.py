from aiohttp import web
from routes import setup_routes
import db
import pathlib
import yaml

app = web.Application()
with open('config.yaml', 'r') as config: # открытие конфигурационного файла
	try:
        	conf = yaml.load(config)
	except yaml.YAMLError as exc:
		print(exc)
print(conf) # для отладки
app['config'] = conf
app.on_startup.append(db.init_pg)
app.on_startup.append(db.create_tables)
app.on_cleanup.append(db.close_pg)
setup_routes(app)
web.run_app(app, port=conf['proveryalka-port'], host=conf['proveryalka-host'])
