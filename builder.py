import http.server
import os
import subprocess
import time
import json
import git
import re

class RequestHandler(http.server.BaseHTTPRequestHandler):
	def do_GET(self):
		# Send response status code
		self.send_response(200)
		# Send headers
		self.send_header('Content-type','text/html')
		self.end_headers()
		
		path = self.path
		pattern = re.compile("https:\/\/github\.com\/(?P<user>[A-z]+)\/(?P<repo>[A-z]+)")

		match = pattern.match(path, 1)
		if not match:
			html_code = "<head> <meta charset=\"UTF-8\"> </head> \
<body><p>Введите адрес на GitHub</p></body>"
			self.wfile.write(bytes(html_code, "utf8"))
			return

		user = match.group('user')
		repo = match.group('repo')

		url = 'https://github.com/' + user + '/' + repo 
		repodir =  gitget(url)
		message = trytobuild(repodir)
		
		html_code = "<head> <meta charset=\"UTF-8\"> </head> \
<body>"
		self.wfile.write(bytes(html_code, "utf8"))

		for entry in message:
			self.wfile.write(bytes("<p>" + entry + "</p>", "utf8"))
		html_code = "</body>"
		self.wfile.write(bytes(html_code, "utf8"))
		return

def run(server_class=http.server.HTTPServer, handler_class=RequestHandler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

def gitget(url):
	reponame = os.path.basename(url)
	repodir = os.path.join(os.getcwd(), reponame + time.strftime("%Y%m%d%H%M%S"))
	repo = git.Repo.init(repodir)
	origin = repo.create_remote('origin', url)
	origin.fetch()
	repo.create_head('master', origin.refs.master).set_tracking_branch(origin.refs.master).checkout()
	origin.pull()
	return repodir

def trytobuild(repodir):
	cflags = ['--std=c89', '-Wall', '-Werror']

	for dir in next(os.walk(repodir))[1]:
		if dir != '.git':
			username = dir

	with open(os.path.join(repodir, username, 'build.json')) as data_file: 
		if data_file:   
			data = json.load(data_file)
		else:
			return 1 ## automatic check is not supported by this repo

	lang = data["lang"]
	if not lang in ["lang_C", "lang_C++"]:
		return 2 ## language is not supported

	## проверять флаги
	flags = data["flags"]
	files = data["files"]
	formatversion = data["format-version"]
	appversion = data["app-version"]
	appbuild = data["app-build"]

	result = []
	for f in files:
		proc = subprocess.Popen(['gcc', *cflags, os.path.join(repodir, username, f)], stderr=subprocess.PIPE)
		output = proc.stderr.read().decode()
		result.append(f + ' ' + output)

	return result

run()