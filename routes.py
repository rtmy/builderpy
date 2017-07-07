from views import index
def setup_routes(app):
	resource = app.router.add_resource('/{name}')
	resource.add_route('GET', repository_handler)

async def repository_handler(request):
	return web.Response(text="Hello, {}".format(request.match_info['name']))

# This is used to server handle POST
async def do_POST(request):

	print(repository)
	pattern = re.compile("https:\/\/github\.com\/(?P<user>[A-z]+)\/(?P<repo>[A-z]+)")

	match = pattern.match(repository)

	if not match:
		return web.json_response({"status":"error", "content":{"text":"request is incompatible"}})

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
	return web.json_response(output)
