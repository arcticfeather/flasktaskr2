<<<<<<< HEAD
from project import db

db.create_all()
db.session.commit()
=======
from views import db
from models import FTasks
from datetime import date

# create the database and db table
db.create_all()

# insert data
db.session.add(FTasks("Finish this tutorial", date(2014,9,13),10,1))
db.session.add(FTasks("Finish Real Python", date(2014,9,20),10,1))

db.session.commit()

	
>>>>>>> 4a19f85f75cb5013e7c7d72ca685d6f61b254e0c
