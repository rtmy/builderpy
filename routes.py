import views
def setup_routes(app):
	index = app.router.add_resource('/')
	index.add_route('GET', views.index)
	recent = app.router.add_resource('/recent')
	recent.add_route('GET', views.recent_handler)
	repository = app.router.add_resource('/recent/{url}')
	repository.add_route('GET', views.repository_handler)
	config = app.router.add_resource('/recent/{url}/config')
	config.add_route('GET', views.config_handler)
	log = app.router.add_resource('/recent/{url}/log')
	log.add_route('GET', views.log_handler)
	build = app.router.add_resource('/build')
	build.add_route('GET', views.build_handler)
