import os
import sys
import subprocess
import time
import datetime
import json
import git
import re
import postgresql
from aiohttp import web
import control

# This is used by server to handle GET
async def do_GET(request):
	return web.Response(text='please send post')

# This is used to server handle POST
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
		return web.json_response({"status":"error", "content":{"text":"request is incompatible"}})

	user = match.group('user')
	repo = match.group('repo')

	url = 'https://github.com/' + user + '/' + repo
	if not db.query("select id from repositories where url = " + "\'" + url + "\'"):
		repoinsert(url)
	 
	repoid = db.query("select id from repositories where url = " + "\'" + url + "\'")[0][0] 
	print(repoid)
	if action == "build":
		repodir = gitget(url)
		result = json.dumps(build(repodir))
		## directory name where build occured contains date time of git get
		redate = re.compile("(\w*(\d{14}))$")
		dt = re.match(redate, os.path.basename(repodir)).groups()
		currently = time.mktime(time.strptime(dt[1], "%Y%m%d%H%M%S"))

		loginsert(repoid, int(currently), result)
		output = {'status':'ok', 'content':{'text':'built'}}
	elif action == "retrieve":
		print('retrieve')
		output = retrieve(repoid)
	elif action == "try":
		output = run(repoid)
	else:
		output = {'status':'error', 'content':{'text':'requested action is unknown'}}

	return web.json_response(output)

def run(repoid):
	'''Running programs in containers.

	Supposed to return status. Under development'''
	if not os.path.exists('build'):
		return {"status":"error", "content":{"text":"internal error"}}
	datetime = db.query("select max (datetime) from logs where repoid = {}".format(str(repoid)))[0][0].strftime("%Y%m%d%H%M%S")
	url = db.query("select url from repositories where id = {}".format(str(repoid)))[0][0]
	c = control.findnode()
	if not c:
		c = control.initnode()

	output = control.run(c)
	print(output)
	return output		
	
def gitget(url):
	'''Git fetch and pull.

	This function purpose is to download \
	repository content using provided URL.
	Returns path where is repository pulled, \
	string.'''

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
	'''Repository basic check and build routines.

	This function checks specifications file
	options and tries to build each file.
	Returns status and additional stuff.'''

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
	
	for f in next(os.walk(os.path.join(repodir, username)))[1]:
		with open(f, 'r') as source:
			if re.match("system\d*\(.*\)*", source):
				return {"status":"error", "content":{"text":"repo not compatible"}}
	result = []
	for f in files:
		filename = os.path.join(repodir, username, f)
		proc = subprocess.Popen([gcc, *cflags, "-o", os.path.join(repodir, "binaries", f.split(".")[0]+".o"),  filename], stderr=subprocess.PIPE)
		output = proc.stderr.read().decode()
		result.append({"filename":f, "output":output})

	return result

def retrieve(repoid, date='latest'):
	'''Return the log recent build.'''
	logs = db.query("SELECT log, datetime FROM logs where datetime in \
	(select max (datetime) from logs where repoid = {});".format(str(repoid)))
	if logs == []:
		return {'status':'error', 'content':{'text':'no log for this repo found'}}
	return {'status':'ok', 'content':{'datetime':str(logs[0][1]), 'text':logs[0][0]}}

if len(sys.argv) < 2:
	print(sys.argv[0], "pq://<username>:<password>@<host>/<database>")
	sys.exit()

db = postgresql.open(sys.argv[1])
loginsert = db.prepare("INSERT INTO logs (repoid, datetime, log) VALUES ($1, to_timestamp($2), $3)")
repoinsert = db.prepare("insert into repositories (url) values ($1) returning id")
app = web.Application()
app.router.add_get('/', do_GET)
app.router.add_post('/', do_POST)
web.run_app(app)
