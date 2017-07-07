import git
import json
import os
import time
import subprocess

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
	return repodir # path to cloned repository

def build(repodir):
	'''Repository basic check and build routines.
	This function checks specifications file
	options and tries to build each file.
	Returns status and additional stuff.'''

	cflags = ['--std=c89', '-Wall', '-Werror']
	for dir in next(os.walk(repodir))[1]:
		if dir != '.git':
			username = dir
			break

	with open(os.path.join(repodir, username, 'build.json')) as data_file: 
		if data_file:   
			data = json.load(data_file)
		else:
			return {'error':'automatic check is not supported by this repo'}

	lang = data["lang"]
	if lang == "lang_C":
		gcc = 'gcc'
	elif lang == "lang_C++":
		gcc = 'g++'
	else:
		return {'error':'language is not supported'}

	flags = data["flags"]
	files = data["files"]
	formatversion = data["format-version"]
	appversion = data["app-version"]
	appbuild = data["app-build"]
	
	for f in next(os.walk(os.path.join(repodir, username)))[1]:
		with open(f, 'r') as source:
			if re.match("system\d*\(.*\)*", source):
				return {'error':'repo not compatible'}

	result = list()
	for f in files:
		filename = os.path.join(repodir, username, f)
		proc = subprocess.Popen( \
                   [gcc, *cflags, "-o", os.path.join(repodir, "binaries", f.split(".")[0]+".o"),  filename], \
                   stderr=subprocess.PIPE)	
		output = proc.stderr.read().decode()
		result.append({"filename":f, "output":output})

	return {'ok': 'built'}, result, data
