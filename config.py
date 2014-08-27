import os

# grabs the folder where the script runs
basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE = 'flasktaskr.db'
<<<<<<< HEAD
CSRF_ENABLED = True
SECRET_KEY = 'c8e88e3032ac40'
DEBUG = False
=======
SECRET_KEY = 'c8e88e3032ac40'
>>>>>>> 4a19f85f75cb5013e7c7d72ca685d6f61b254e0c

# defines the full path for the database
DATABASE_PATH = os.path.join(basedir, DATABASE)

# the database URI
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH