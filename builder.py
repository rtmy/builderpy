import http.server
import os
import sys
import subprocess
import time
import json
import git
import re
import postgresql

class RequestHandler(http.server.CGIHTTPRequestHandler):
	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()

		self.wfile.write(bytes('{"status":"error", "content":{"text":"Please send POST"}}', "utf8"))
	def do_POST(self):
		self.send_response(200)		

		self.send_header('Content-type','application/json')
		self.end_headers()

		data = self.rfile.read(65535).decode()
		print(data)
		
		contents = json.loads(data)

		action = contents["type-action"]
		repository = contents["repository"]

		if not action or not repository:
			self.wfile.write(bytes('{"status":"error", "content":{"text":"post, please"}}', "utf8"))
			return

		print(repository)
		pattern = re.compile("https:\/\/github\.com\/(?P<user>[A-z]+)\/(?P<repo>[A-z]+)")

		match = pattern.match(repository)

		if not match:
			self.wfile.write(bytes('{"status":"error", "content":{"text":"repo not compatible"}}', "utf8"))
			return

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

		encoder = json.JSONEncoder()
		output = encoder.encode(output)

		self.wfile.write(bytes(output, "utf8"))
		print('sent')
		return

def run(server_class=http.server.HTTPServer, handler_class=RequestHandler):
	server_address = ('', 8000)
	httpd = server_class(server_address, handler_class)
	httpd.serve_forever()

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
		return '{"status":"error", "content":{"text":"repo not compatible"}}'

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

if len(sys.argv) < 2:
        print("{} pq://<username>:<password>@<host>/<db_name>".format(sys.argv[0]))
        exit()
db = postgresql.open(sys.argv[1])
loginsert = db.prepare("INSERT INTO logs (repoid, datetime, log) VALUES ($1, to_timestamp($2), $3)")
repoinsert = db.prepare("insert into repositories (url) values ($1) returning id")
run()
