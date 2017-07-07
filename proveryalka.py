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
