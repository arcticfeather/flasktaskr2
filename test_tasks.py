import os
import unittest
from project import app, db, bcrypt
from project.models import Task, User
from config import basedir

TEST_DB = 'test.db'

class Tasks(unittest.TestCase):
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
		return self.app.post('users/', data=dict(
		name=name, password=password), follow_redirects=True)

	def logout(self):
		return self.app.get('users/logout/', follow_redirects=True)

	def register(self, name, email, password, confirm):
		return self.app.post('users/register/', data=dict(
		name=name, email=email, password=password, confirm=confirm), follow_redirects=True)

	def create_user(self, name, email, password):
		new_user = User(name=name, email=email, password=bcrypt.generate_password_hash(password))
		db.session.add(new_user)
		db.session.commit()

	def create_admin_user(self):
		new_user = User(
			name = 'Admin',
			email = 'admin@admin.com',
			password = bcrypt.generate_password_hash('admin'),
			role = 'admin')
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

	def test_logged_in_users_can_access_tasks_page(self):
		self.register_test_user_and_login()
		response = self.app.get('tasks/tasks/', follow_redirects=True)
		self.assertEquals(response.status_code, 200)
		self.assertIn('Add a new task', response.data)

	def test_not_logged_in_users_cannot_access_tasks_page(self):
		response = self.app.get('tasks/tasks/', follow_redirects=True)
		self.assertIn('You need to login first', response.data)

	def test_users_can_add_tasks(self):
		self.register_test_user_and_login()
		self.app.get('tasks/tasks/', follow_redirects=True)
		response = self.create_task()
		self.assertIn('New entry was successfully posted', response.data)

	def test_users_cannot_add_tasks_when_error(self):
		self.register_test_user_and_login()
		self.app.get('tasks/tasks/', follow_redirects=True)
		response = self.app.post('tasks/add/', data=dict(
			name='Go to the bank',
			due_date='',
			priority='1',
			posted_date='02/05/2014',
			status='1'), follow_redirects=True)
		self.assertIn('This field is required', response.data)

	def test_users_can_complete_tasks(self):
		self.register_test_user_and_login()
		self.app.get('tasks/tasks/', follow_redirects=True)
		self.create_task()
		response = self.app.get('tasks/complete/1/', follow_redirects=True)
		self.assertIn('The task was marked as complete', response.data)

	def test_users_can_delete_tasks(self):
		self.register_test_user_and_login()
		self.app.get('tasks/tasks/', follow_redirects=True)
		self.create_task()
		response = self.app.get('tasks/delete/1/', follow_redirects=True)
		self.assertIn('The task was deleted', response.data)

	def test_users_cannot_cannot_complete_other_users_tasks(self):
		self.create_user('Test user', 'test@testing.com', 'password')
		self.login('Test user', 'password')
		self.app.get('tasks/tasks/', follow_redirects=True)
		self.create_task()
		self.logout()
		self.create_user('Test user 2', 'fake@email.com', 'password')
		self.login('Test user 2', 'password')
		self.app.get('tasks/tasks/',follow_redirects=True)
		response = self.app.get('tasks/complete/1/', follow_redirects=True)
		self.assertNotIn('The task was marked as complete', response.data)

	def test_users_cannot_complete_other_users_tasks(self):
		self.create_user('Test user', 'test@testing.com', 'password')
		self.login('Test user', 'password')
		self.app.get('tasks/tasks/', follow_redirects=True)
		self.create_task()
		self.logout()
		self.create_user('Test user 2', 'fake@email.com', 'password')
		self.login('Test user 2', 'password')
		self.app.get('tasks/tasks/', follow_redirects=True)
		response = self.app.get('tasks/complete/1/', follow_redirects=True)
		self.assertIn('You can only update tasks that belong to you', response.data)

	def test_users_cannot_delete_other_users_tasks(self):
		self.create_user('Test user', 'test@testing.com', 'password')
		self.login('Test user', 'password')
		self.app.get('tasks/tasks/', follow_redirects=True)
		self.create_task()
		self.logout()
		self.create_user('Test user 2', 'fake@email.com', 'password')
		self.login('Test user 2', 'password')
		self.app.get('tasks/tasks/', follow_redirects=True)
		response = self.app.get('tasks/delete/1/', follow_redirects=True)
		self.assertIn('You can only delete tasks that belong to you', response.data)

	def test_admin_users_can_complete_other_users_tasks(self):
		self.create_user('Test user', 'test@testing.com', 'password')
		self.login('Test user', 'password')
		self.app.get('tasks/', follow_redirects=True)
		self.create_task()
		self.logout()
		self.create_admin_user()
		self.login('Admin', 'admin')
		self.app.get('tasks/', follow_redirects=True)
		response = self.app.get('complete/1/', follow_redirects=True)
		self.assertNotIn('You can only update tasks that belong to you', response.data)

	def test_admin_users_can_delete_other_users_tasks(self):
		self.create_user('Test user', 'test@testing.com', 'password')
		self.login('Test user', 'password')
		self.app.get('tasks/', follow_redirects=True)
		self.create_task()
		self.logout()
		self.create_admin_user()
		self.login('Admin', 'admin')
		self.app.get('tasks/', follow_redirects=True)
		response = self.app.get('delete/1/', follow_redirects=True)
		self.assertNotIn('You can only delete tasks that belong to you', response.data)

	def test_users_cannot_see_task_modify_links_for_other_users_tasks(self):
		self.register_test_user_and_login()
		self.app.get('tasks/tasks/', follow_redirects=True)
		self.create_task()
		self.logout()
		self.register('Test user 2', 'fake@email.com', 'password', 'password')
		response = self.login('Test user 2', 'password')
		self.app.get('tasks/tasks/', follow_redirects=True)
		self.assertNotIn('Mark as complete', response.data)
		self.assertNotIn('Delete', response.data)

	def test_users_can_see_task_modify_links_for_their_tasks(self):
		self.register_test_user_and_login()
		self.app.get('tasks/tasks/', follow_redirects=True)
		self.create_task()
		self.logout()
		self.register('Test user 2', 'fake@email.com', 'password', 'password')
		response = self.login('Test user 2', 'password')
		self.app.get('tasks/tasks/', follow_redirects=True)
		response = self.create_task()
		self.assertIn('tasks/complete/2/', response.data)
		self.assertIn('tasks/delete/2/', response.data)

	def test_admin_users_can_see_task_modify_links_for_all_tasks(self):
		self.register_test_user_and_login()
		self.app.get('tasks/tasks/', follow_redirects=True)
		self.create_task()
		self.logout()
		self.create_admin_user()
		self.login('Admin', 'admin')
		self.app.get('tasks/tasks/', follow_redirects=True)
		response = self.create_task()
		self.assertIn('tasks/complete/1/', response.data)
		self.assertIn('tasks/complete/2/', response.data)
		self.assertIn('tasks/delete/1/', response.data)
		self.assertIn('tasks/delete/2/', response.data)

if __name__ == "__main__":
	unittest.main()