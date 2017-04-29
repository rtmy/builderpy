import socket
import git
import os
import json
import subprocess
import time
import zipfile

HOST, PORT = '', 8888
listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind((HOST, PORT))
listen_socket.listen(1)
gitrepo = []

cflags = '--std=c89 -Wall -Werror'

print('Serving HTTP on port', PORT)

while True:
	client_connection, client_address = listen_socket.accept()
	request = client_connection.recv(1024).decode()
	print(request)
	i = 5

	while (request[i] != ' '):
		gitrepo.append(request[i])
		i += 1

	gitrepo = ''.join(gitrepo)

	reponame = os.path.basename(gitrepo)
	print(gitrepo)

	repodir = os.path.join(os.getcwd(), reponame + time.strftime("%Y%m%d%H%M%S"))

	repo = git.Repo.init(repodir)
	origin = repo.create_remote('origin', gitrepo)
	origin.fetch()
	repo.create_head('master', origin.refs.master).set_tracking_branch(origin.refs.master).checkout()
	origin.pull()

	http_response = """\
HTTP/1.1 200 OK

Hello, world!
Exploring the repository
"""
	client_connection.sendto(http_response.encode(),(HOST, PORT))

	for userdirs, _, _ in os.walk(repodir):
		userdir = userdirs

	username = os.path.basename(userdir)

	with open(os.path.join(userdir, 'build.json')) as data_file: 
		if data_file:   
			data = json.load(data_file)
		else:
			client_connection.sendto("automatic check is not supported by this repo".encode(),(HOST, PORT))
			exit	

	lang = data["lang"]
	if not lang in ["lang_C", "lang_C++"]:
		print("language is not supported")

	## проверять флаги
	flags = data["flags"]
	files = data["files"]
	formatversion = data["format-version"]
	appversion = data["app-version"]
	appbuild = data["app-build"]

	os.makedirs(os.path.join(userdir, 'logs'))

	zipf = zipfile.ZipFile(username + '.zip', 'w', zipfile.ZIP_DEFLATED)
	http_response = ''
	for f in files:	
		logfile = open(os.path.join(userdir, f) + '.log', 'w+')
		subprocess.run(['gcc', cflags.split(' '), flags, os.path.join(userdir, f)], stdout=logfile, stderr=logfile)
		http_response = http_response + f + ' compiled'
		logfile.close()
		zipf.write(os.path.join(userdir, f))

	zipf.close()
	print(http_response)
	client_connection.sendto(http_response.encode(),(HOST, PORT))
	client_connection.close()
	i = 0
	gitrepo = []