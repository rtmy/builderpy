import os
import sys
import subprocess
import time
import json
import git
import re
import postgresql
from aiohttp import web

async def do_GET(request):
	return web.Response(text='please send post')
async def do_POST(request):
	data = await request.json()
	print(request.headers)
	action = data["type-action"]
	repository = data["repository"]

	if not action or not repository:
		return web.json_response({"status":"error", "content":{"text":"post, please"}})

	print(repository)
	pattern = re.compile("https:\/\/github\.com\/(?P<user>[A-z]+)\/(?P<repo>[A-z]+)")

	match = pattern.match(repository)

	if not match:
		return web.json_response({"status":"error", "content":{"text":"repo not compatible"}})

	user = match.group('user')
	repo = match.group('repo')

	url = 'https://github.com/' + user + '/' + repo
	if not db.query("select id from repositories where url = " + "\'" + url + "\'")[0][0]:
		repoinsert(url)
	 
	repoid = db.query("select id from repositories where url = " + "\'" + url + "\'")[0][0] 
	print(repoid)
	if action == "build":
		repodir = gitget(url)
		result = build(repodir)
		loginsert(repoid, (int(time.time())), result)
		output = {'status':'ok', 'content':{'text':'built'}}
	elif action == "retrieve":
		print('retrieve')
		output = retrieve(repoid)
	else:
		output = {'status':'error', 'content':{'text':'requested action is unknown'}}

	return web.json_response(output)
def gitget(url):
	if not os.path.exists('build'):
		os.makedirs('build')
	reponame = os.path.basename(url)
	repodir = os.path.join(os.getcwd(), 'build', reponame + time.strftime("%Y%m%d%H%M%S"))
	repo = git.Repo.init(repodir)
	origin = repo.create_remote('origin', url)
	origin.fetch()
	repo.create_head('master', origin.refs.master).set_tracking_branch(origin.refs.master).checkout()
	origin.pull()
	return repodir ## where cloned repository

def build(repodir):
	cflags = ['--std=c89', '-Wall', '-Werror']
	username = ''
	for dir in next(os.walk(repodir))[1]: ## должно рабоать по-другому
		if dir != '.git':
			username = dir
	if username == '':
		return {"status":"error", "content":{"text":"repo not compatible"}}

	with open(os.path.join(repodir, username, 'build.json')) as data_file: 
		if data_file:   
			data = json.load(data_file)
		else:
			return {'status':'error', 'content':{'text':'automatic check is not supported by this repo'}}

	lang = data["lang"]
	if lang == "lang_C":
		gcc = 'gcc'
	elif lang == "lang_C++":
		gcc = 'g++'
	else:
		return {'status':'error', 'content':{'text':'language is not supported'}}

	## проверять флаги
	flags = data["flags"]
	for flag in flags:
		if flag not in cflags:
			cflags.append(flag)
		else:
			return {'status':'error', 'content':{'text':'flag overriding is not allowed'}}

	files = data["files"]
	formatversion = data["format-version"]
	appversion = data["app-version"]
	appbuild = data["app-build"]


	result = []
	for f in files:
		proc = subprocess.Popen([gcc, *cflags, os.path.join(repodir, username, f)], stderr=subprocess.PIPE)
		output = proc.stderr.read().decode()
		result.append({"filename":f, "output":output})

	result = json.dumps(result)
	return result

def retrieve(repoid, date='latest'):
	logs = db.query("SELECT log, datetime FROM logs where datetime in \
	(select max (datetime) from logs where repoid = {});".format(str(repoid)))
	if logs == []:
		return {'status':'error', 'content':{'text':'no log for this repo found'}}
	return {'status':'ok', 'content':{'datetime':str(logs[0][1]), 'text':logs[0][0]}}

db = postgresql.open("pq://builderpy:blogger@localhost/logs")
loginsert = db.prepare("INSERT INTO logs (repoid, datetime, log) VALUES ($1, to_timestamp($2), $3)")
repoinsert = db.prepare("insert into repositories (url) values ($1) returning id")
app = web.Application()
app.router.add_get('/', do_GET)
app.router.add_post('/', do_POST)
web.run_app(app)
