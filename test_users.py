import os
import unittest
from project import app, db, bcrypt
from project.models import User
from config import basedir

TEST_DB = 'test.db'

class Users(unittest.TestCase):
	# this is a special method that is eecuted prior to each test
	def setUp(self):
		app.config['TESTING'] = True
		app.config['WTF_CSRF_ENABLED'] = False
		app.config['DEBUG'] = False
		app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
				os. path.join(basedir, TEST_DB)
		self.app = app.test_client()
		db.create_all()

		self.assertEquals(app.debug, False)

	# this is a special method that is executed after each test
	def tearDown(self):
		db.drop_all()

	# Helper functions
	def login(self, name, password):
		return self.app.post('/users/', data=dict(
		name=name, password=password), follow_redirects=True)

	def logout(self):
		return self.app.get('users/logout/', follow_redirects=True)

	def register(self, name, email, password, confirm):
		return self.app.post('users/register/', data=dict(
		name=name, email=email, password=password, confirm=confirm), follow_redirects=True)

	def create_user(self, name, email, password):
		new_user = User(name=name, email=email, password=bcrypt.genereate_password_hash(password))
		db.session.add(new_user)
		db.session.commit()

	def register_test_user_and_login(self):
		self.register('Test user', 'test@testing.com', 'password', 'password')
		self.login('Test user', 'password')

	def create_task(self):
		return self.app.post('tasks/add/', data=dict(
			name='Go to the bank',
			due_date='01/12/2014',
			priority='1',
			posted_date='31/08/2014',
			status='1'), follow_redirects=True)

	# Tests

	def test_users_can_register(self):
		new_user = User("newusername", "new@username.com","password")
		db.session.add(new_user)
		db.session.commit()
		test = db.session.query(User).all()
		for t in test:
			t.name
		assert t.name == "newusername"

	def test_form_is_present_on_login_page(self):
		response = self.app.get('users/')
		self.assertEquals(response.status_code, 200)
		self.assertIn('Please login to access your task list', response.data)

	def test_users_cannot_login_unless_registered(self):
		response = self.login('foo', 'bar')
		self.assertIn('Invalid username or password', response.data)

	def test_users_can_login(self):
		self.register('Test user', 'test@testing.com', 'password', 'password')
		response = self.login('Test user', 'password')
		self.assertIn('You are logged in.', response.data)

	def test_invalid_form_data(self):
		self.register('Test user', 'test@testing.com', 'password', 'password')
		response = self.login('alert("alert box!");', 'foo')
		self.assertIn('Invalid username or password', response.data)

	def test_form_is_present_on_register_page(self):
		response = self.app.get('users/register/')
		self.assertEquals(response.status_code, 200)
		self.assertIn('Please register to start a task list', response.data)

	def test_user_registration(self):
		self.app.get('users/register/', follow_redirects=True)
		response = self.register('Test user', 'test@testing.com', 'password', 'password')
		self.assertIn('Thanks for registering', response.data)

	def test_duplicate_user_registration_throws_error(self):
		self.app.get('users/register/', follow_redirects=True)
		self.register('Test user', 'test@testing.com', 'password','password')
		self.app.get('register/', follow_redirects=True)
		response = self.register('Test user', 'test@testing.com', 'password', 'password')
		self.assertIn('That username and/or email already exist', response.data)

	def test_user_registration_field_errors(self):
		response = self.register(
			'Test user', 'test@testing.com', 'password', '')
		self.assertIn('This field is required', response.data)

	def test_logged_in_users_can_logout(self):
		self.register_test_user_and_login()
		response = self.logout()
		self.assertIn('You are logged out', response.data)

	def test_not_logged_in_users_cannot_logout(self):
		response = self.logout()
		self.assertNotIn('You are logged out', response.data)

	def test_default_user_role(self):
		db.session.add(
			User('Test user', 'test@testing.com', 'password')
			)
		db.session.commit()
		users = db.session.query(User).all()
		print users
		for user in users:
			self.assertEquals(user.role, 'user')

	def test_task_template_displays_logged_in_user_name(self):
		self.register_test_user_and_login()
		response = self.app.get('tasks/tasks/', follow_redirects=True)
		self.assertIn('Test user', response.data)

	def test_404_error(self):
		response = self.app.get('/this-route-does-not-exist/')
		self.assertEquals(response.status_code, 404)
		self.assertIn('There\'s nothing here', response.data)

	def test_500_error(self):
		bad_user = User(
			name='Bad user',
			email='baduser@email.com',
			password='password')
		db.session.add(bad_user)
		db.session.commit()
		response = self.login('Bad user', 'password')
		self.assertEquals(response.status_code, 500)
		self.assertNotIn('ValueError: Invalid salt', response.data)
		self.assertIn('Something want terribly wrong', response.data)



if __name__ == "__main__":
	unittest.main()