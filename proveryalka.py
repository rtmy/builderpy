import git
import json
import os
import time
import subprocess

def gitget(url):
	'''Загрузка содержимого репозитория.

	Создаёт папку и клонирует в неё
	репозиторий по URL-у.
	Возвращает путь до папки'''

	if not os.path.exists('build'):
		os.makedirs('build')
	reponame = os.path.basename(url)
	repodir = os.path.join(os.getcwd(), 'build', reponame + time.strftime("%Y%m%d%H%M%S"))
	repo = git.Repo.init(repodir)
	origin = repo.create_remote('origin', url)
	origin.fetch()
	repo.create_head('master', origin.refs.master).set_tracking_branch(origin.refs.master).checkout()
	origin.pull()
	print("git got", url)
	return repodir # путь до папки

def check(repodir):
	'''Проверка репозитория.

	Вовзвращает результат проверки'''
	print("checking", repodir)
	cflags = ['--std=c89', '-Wall', '-Werror']
	dirs =  set(next(os.walk(repodir))[1])
	try:
		username = (dirs - {'.git'}).pop()
	except KeyError:	
		return error('username folder not found')

	with open(os.path.join(repodir, username, 'build.json')) as data_file:  # проверяем наличие build.json
		if data_file:   
			data = json.load(data_file)
		else:
			return error('automatic check is not supported by this repo')

	lang = data["lang"] # определяем язык сборки
	if lang == "lang_C":
		gcc = 'gcc'
	elif lang == "lang_C++":
		gcc = 'g++'
	else:
		return error('language is not supported')

	flags = data["flags"]
	files = data["files"]
	formatversion = data["format-version"]
	appversion = data["app-version"]
	appbuild = data["app-build"]
	
	for f in next(os.walk(os.path.join(repodir, username)))[1]: # ищем вызовы system() в коде
		with open(f, 'r') as source:
			if re.match("system\d*\(.*\)*", source):
				return error('repo not compatible')

	return {'ok': 'built'}, data, gcc, flags, flags, repodir, username, files

async def build(gcc, cflags, flags, repodir, username, files):
	'''Сборка файлов с исходным кодом.

	Возвращает результат сборки'''
	result = list()
	for f in files:
		filename = os.path.join(repodir, username, f)
		proc = subprocess.Popen( \
                   [gcc, *cflags, *flags, "-o", os.path.join(repodir, "binaries", f.split(".")[0]+".o"),  filename], \
                   stderr=subprocess.PIPE)	
		output = proc.stderr.read().decode()
		result.append({"filename":f, "output":output})
	print("built", username)
	return result

def error(text):
	'''Возвращает ошибку.

	Для внутреннего использования'''
	return ({'error':text}, None, None, None, None, None, None)
