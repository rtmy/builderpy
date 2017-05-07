import http.server
import os
import subprocess
import time
import json
import git
import re

class RequestHandler(http.server.CGIHTTPRequestHandler):
	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()

		self.wfile.write(bytes('Please send POST', 'utf8'))
	def do_POST(self):
		self.send_response(200)		

		self.send_header('Content-type','application/json')
		self.end_headers()

		action = self.headers["type-action"]
		repository = self.headers["repository"]

		print(repository)
		pattern = re.compile("https:\/\/github\.com\/(?P<user>[A-z]+)\/(?P<repo>[A-z]+)")

		match = pattern.match(repository)

		user = match.group('user')
		repo = match.group('repo')

		if not match:
			output = {'status':'error', 'content':{'text':'repo url is not compatible'}}
		elif action == "build":
			url = 'https://github.com/' + user + '/' + repo 
			repodir = gitget(url)
			output = build(repodir)
		elif action == "retrieve":
			print('retrieve')
			output = retrieve(repo)
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

def gitget(URL):
	'''Git fetch and pull.

       This function purpose is to download \
       repository content using provided URL.
       Returns path where is repository pulled, \
       string.'''
	reponame = os.path.basename(URL)
	repodir = os.path.join(os.getcwd(), reponame + time.strftime("%Y%m%d%H%M%S"))
	repo = git.Repo.init(repodir)
	origin = repo.create_remote('origin', URL)
	origin.fetch()
	repo.create_head('master', origin.refs.master).set_tracking_branch(origin.refs.master).checkout()
	origin.pull()
	return repodir

def build(repodir):
	'''Repository basic check and build routines.

       This function checks specifications file
       options and tries to build each file.
       Returns status and additional stuff.'''
	cflags = ['--std=c89', '-Wall', '-Werror']

	for dir in next(os.walk(repodir))[1]:
		if dir != '.git':
			username = dir

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

	if not os.path.exists('logs'):
		os.makedirs('logs')

	result = []
	logfile = open(os.path.join('logs', os.path.basename(repodir))+'.log', "wb")
	for f in files:
		proc = subprocess.Popen([gcc, *cflags, os.path.join(repodir, username, f)], stderr=subprocess.PIPE)
		output = proc.stderr.read().decode()
		result.append({"filename":f, "output":output})

	result = json.dumps(result)
	logfile.write(bytes(result, "utf8"))
	logfile.close()
	return {'status':'ok', 'content':{'text':'...'}}

def retrieve(reponame, date='latest'):
	'''Returns log.

       This function checks if there is \
       a log file on disk and returns its content \
       as JSON.'''

	if not os.path.exists('logs'):
		return {'status':'error', 'content':{'text':'logfile not found'}}

	for filename in next(os.walk('logs'))[2]:
		print(filename)
		if reponame in filename:
			logfile = filename

	try:
		logfile
	except NameError: ## ??!?
		return {'status':'error', 'content':{'text':'logfile not found'}}

	logfile = open(os.path.join('logs', logfile))
	output =  logfile.read()
	logfile.close()
	return {'status':'ok', 'content':{'filename':filename, 'text':output}}

	pass

run()
