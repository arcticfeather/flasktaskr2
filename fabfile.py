from fabric.api import local, settings, abort
from fabric.contrib.console import confirm

def test():
	with settings(warn_only=True):
		result = local("nosetests -v", capture=True)

	if result.failed and not confirm("Tests failed. Continute?"):
		abort("Aborted at user request.")

def commit():
	message = raw_input("Enter a git commit message: ")
	local("git add .")
	local('git commit -m "{}"'.format(message))

def push():
	local("git push origin Alpha5")

def prepare():
	test()
	commit()
	push()

def pull():
	local("git pull origin master")

# Heroku

def heroku():
	local("git push heroku master")

def heroku_test():
	local("heroku run nosetests -v")

def deploy():
	pull()
	test()
	commit()
	heroku()
	heroku_test()

def rollback():
	local("heroku rollback")