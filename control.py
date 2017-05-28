import lxc

def findnode():
	'''Looks through list of available containers, returns  \
	container object if found, otherwise None.'''
	for container in lxc.list_containers(as_object=True):
		if container:
			return container
	pass

def initnode():
	'''Initiates a container to work in.

	If settings on host machine are needed to set up
	provides an instruction how to
	Supposed to support different configurations'''
	c = lxc.Container("newcontainer")
	if c.defined:
    		print("Container already exists", file=sys.stderr)
	sys.exit(1)
	
	if not c.create("download", lxc.LXC_CREATE_QUIET, {"dist": "ubuntu", "release": "trusty", "arch": "i386"}):
		print("Failed to create the container rootfs", file=sys.stderr)
		sys.exit(1)
	pass

def run(container):
	'''Runs compiled executables, writes to a log file.

	Not given any argument, executes every binary inside shared directory.'''
	if not container.running:
		container.start()
		container.wait("RUNNING", 3)
	started = 1

	assert(container.init_pid > 1)
	assert(container.running)
	assert(container.state == "RUNNING")

	dir = "/home/binaries"
	container.attach_wait(lxc.attach_run_command, ["for f in `ls {}`;".format(dir), "do $f;", "done"])	

	if started:
		if not container.shutdown(30):
			container.stop()

	return "done"
