from hashlib import md5

from django.test import TestCase, SimpleTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse, resolve

from rest_framework.test import APITestCase

from departments.models import Department
from subject_related.models import SubTopic
from .models import AccountActivity, Notification, NotificationUser, SubscriptionActivity, User
from .views import UserRegistrationEndpoint


class TestSetUp:
	def __init__(self, _self):
		self.user = get_user_model().objects.create_user(full_name="Client", email="client@a.com", password='client')
		response = _self.client.post(reverse('token-obtain'), data={'email': 'client@a.com', 'password': 'client'})
		self.access = response.json()['access']


class UserRegistration(APITestCase):
	def test_user_registration(self):
		url = reverse('accounts:register-as-user')
		res = self.client.post(url, data={
			'full_name': 'Test',
			'email': 'ultratot@codk.site',
			'password': 'testing'
		})

		print(res.data)
		self.assertEquals(res.status_code, 201)

	def test_user_activate(self):
		url = reverse('accounts:register-as-user')
		self.client.post(url, data={
			'full_name': 'Test',
			'email': 'ultratot@codk.site',
			'password': 'testing'
		})

		hashed = md5('ultratot@codk.site'.encode('utf-8')).hexdigest()
		url = reverse('accounts:activate-user', args=[1, hashed])
		res = self.client.get(url)

		self.assertEquals(res.status_code, 200)
		self.assertEquals(res.data, 'Account Activated')
		self.assertTrue(User.objects.first().is_active)

	def test_reset_password(self):
		get_user_model().objects.create_user(full_name="Client", email="client@a.com", password='client')
		url = reverse('accounts:reset_password')

		res = self.client.post(url, data={'email': 'client@a.com'})

		print(res.data)

		self.assertEquals(res.status_code, 202)



class CustomTokenView(APITestCase):
	def test_token_obtain_pair_view(self):
		user = get_user_model().objects.create_user(full_name="Client One", email="client@a.com", password="a")
		user.is_active = True
		user.save()

		url = '/token/obtain/'
		res = self.client.post(url, data={"email": "client@a.com", "password": "a"})

		print(res.data)


class AccountsModelTest(TestCase):
	def test_default_user_model(self):
		db = get_user_model()
		db.objects.create_user(email="a@a.com", full_name="Dean Derry", password="salvor")

		self.assertEqual(db.objects.count(), 1)
		self.assertEqual(db.objects.first().email, "a@a.com")
		self.assertEqual(db.objects.first().is_active, False)

	def test_super_user_model(self):
		db = get_user_model()
		db.objects.create_superuser(email="a@a.com", full_name="Dean Derry", password="salvor")

		self.assertEqual(db.objects.count(), 1)
		self.assertEqual(db.objects.first().email, "a@a.com")
		self.assertEqual(db.objects.first().is_active, True)
		self.assertEqual(db.objects.first().is_superuser, True)


class AccountUrlTest(SimpleTestCase):
	def test_register_as_a_user_resolve(self):
		url = reverse('accounts:register-as-user')
		self.assertEquals(resolve(url).func.__name__, UserRegistrationEndpoint.as_view().__name__)


class AccountViewTest(APITestCase):
	def test_create_new_user_POST(self):
		_ = self.client
		url = reverse('accounts:register-as-user')

		res = _.post(url, data={'email': 'a@a.com', 'full_name': 'New User', 'password': 'deanderry'})

		self.assertEquals(res.status_code, 201)
		self.assertEquals(get_user_model().objects.first().email, "a@a.com")
		self.assertEquals(get_user_model().objects.first().is_active, False)


class TestNotification(APITestCase):
	def setUp(self):
		db = get_user_model()
		d1 = Department.objects.create(name='Department One', slug='department-one')
		d2 = Department.objects.create(name='Department Two', slug='department-two')

		db.objects.create(email="a@a.com", full_name="Dean Derry", department=d1)
		db.objects.create(email="b@a.com", full_name="Dean Trazzy", department=d2)

		user2 = get_user_model().objects.create_user(full_name="Client Two", email="client2@a.com", password='client')
		user2.is_active = True
		user2.save()

		self.user2 = user2

		response2 = self.client.post(reverse('token-obtain'), data={'email': 'client2@a.com', 'password': 'client'})

		self.access_1 = response2.json()['access']

	def test_notification_model_add_all_user(self):
		Notification.add_notification(to='all-users', title='First Notification', content='This is to notifi the gen')

		self.assertEquals(Notification.objects.count(), 1)
		self.assertEquals(NotificationUser.objects.count(), 2)
		self.assertQuerysetEqual(
			NotificationUser.objects.all(),
			['<NotificationUser: b@a.com>', '<NotificationUser: a@a.com>']
		)

	def test_notification_model_add_by_department(self):
		Notification.add_notification(
			to='by-department', title='First Notification',
			content='This is to notifi the gen', department='department-one'
		)

		self.assertEquals(Notification.objects.count(), 1)
		self.assertEquals(NotificationUser.objects.count(), 1)
		self.assertQuerysetEqual(NotificationUser.objects.all(), ['<NotificationUser: a@a.com>'])

	def test_notification_model_add_selected_users(self):
		Notification.add_notification(
			to='selected-users', title='First Notification',
			content='This is to notifi the gen', users_list=[1, 2]
		)

		self.assertEquals(Notification.objects.count(), 1)
		self.assertEquals(NotificationUser.objects.count(), 2)
		self.assertQuerysetEqual(
			NotificationUser.objects.all(),
			['<NotificationUser: b@a.com>', '<NotificationUser: a@a.com>']
		)

	def test_notification_model_delete(self):
		Notification.add_notification(
			to='selected-users', title='First Notification',
			content='This is to notifi the gen', users_list=[1, 2]
		)
		Notification.remove_notification(pk=1)

		self.assertEquals(Notification.objects.count(), 0)
		self.assertEquals(NotificationUser.objects.count(), 0)

	def test_notification_model_delete_another_test(self):
		Notification.add_notification(
			to='selected-users', title='First Notification',
			content='This is to notifi the gen', users_list=[1, 2]
		)
		Notification.add_notification(
			to='by-department', title='First Notification',
			content='This is to notifi the gen', department='department-one'
		)

		Notification.remove_notification(pk=2)

		self.assertEquals(Notification.objects.count(), 1)
		self.assertEquals(NotificationUser.objects.count(), 2)

	def test_subscription_POST(self):
		url = '/accounts/subscription/'
		res = self.client.post(
			url,
			HTTP_AUTHORIZATION='JWT ' + self.access_1,
			data={
				"reference": '00aada',
				'status': 'approved',
				'transaction': '002',
				'plan': 'premuim',
				'trxref': '002',
			}
		)

		self.assertEquals(SubscriptionActivity.objects.count(), 1)
		self.assertEquals(SubscriptionActivity.objects.first().user.email, "client2@a.com")

	def test_notifications_GET(self):
		Notification.add_notification(to='all-users', title='First Notification', content='This is to notifi the gen')

		url = '/accounts/notifications/'
		# res = self.client.post(
		# 	url,
		# 	HTTP_AUTHORIZATION='JWT '+self.access_1,
		# 	data={
		# 		"reference": '00aada',
		# 		'status': 'approved',
		# 		'transaction': '002',
		# 		'plan': 'premuim',
		# 		'trxref': '002',
		# 	}
		# )
		res = self.client.get(url, HTTP_AUTHORIZATION='JWT ' + self.access_1, )

		print(res.data)

	# self.assertEquals(SubscriptionActivity.objects.count(), 1)
	# self.assertEquals(SubscriptionActivity.objects.first().user.email, "client2@a.com")


class TestAccountActivity(APITestCase):
	def test_activity_for_create_user(self):
		url = '/accounts/'
		User.objects.create_user('a@a.com', 'Dean', 'a')
		# res = self.client
		self.assertEquals(AccountActivity.objects.count(), 1)
		self.assertEquals(AccountActivity.objects.first().user.email, 'a@a.com')
		self.assertEquals(AccountActivity.objects.first().activity_type, 'Account Created')

	def test_activity_for_update_user(self):
		user_obj = TestSetUp(self)
		url = '/accounts/update/'
		res = self.client.patch(url, data={'full_name': 'Oya Na'}, HTTP_AUTHORIZATION='JWT ' + user_obj.access)

		self.assertEquals(User.objects.get(email='client@a.com').full_name, 'Oya Na')
		self.assertEquals(AccountActivity.objects.count(), 2)
		self.assertEquals(AccountActivity.objects.filter(
			user__email='client@a.com', activity_type='Profile Updated').count(), 1)

	def test_activity_for_payment_made_by_user(self):
		user_obj = TestSetUp(self)
		url = '/accounts/subscription/'
		res = self.client.post(url, data=dict(
			reference="a",
			status="b",
			trxref="a",
			transaction="100",
			amount="100",
			plan="Paid",

		), HTTP_AUTHORIZATION='JWT ' + user_obj.access)

		self.assertEquals(AccountActivity.objects.count(), 3)
		self.assertEquals(AccountActivity.objects.filter(
			user__email='client@a.com', activity_type='Subcription Plan Updated').count(), 1)
		self.assertEquals(AccountActivity.objects.filter(
			user__email='client@a.com', activity_type='Profile Updated').count(), 1)

	def test_activity_view(self):
		user_obj = TestSetUp(self)
		url = '/accounts/update/'
		self.client.patch(url, data={'full_name': 'Oya Na'}, HTTP_AUTHORIZATION='JWT ' + user_obj.access)
		res = self.client.get('/accounts/account-activity/', HTTP_AUTHORIZATION='JWT ' + user_obj.access)

		self.assertEquals(res.status_code, 200)
		self.assertEquals(res.data[0]['message'], 'Your profile has been updated')
		self.assertEquals(res.data[0]['user'], 1)
		self.assertEquals(res.data[1]['message'], 'Your edustart account has been created')
