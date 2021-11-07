from django.contrib.auth import get_user_model
from django.urls import reverse, resolve
from rest_framework import test

from accounts.models import Notification, NotificationUser, User
from administrator.views import AdminDashboard
from practiceQuestion.models import Questions
from subject_related.models import Department, SubjectType, Subject, Topic, SubTopic


class SetUpTest:
	def __init__(self, _self):
		"""
		Create Two Users for authentication purposes
		"""
		user = get_user_model().objects.create_superuser(full_name="Admin One", email="admin@a.com", password='admin')
		user.save()

		user2 = get_user_model().objects.create_user(full_name="Client Two", email="client2@a.com", password='client')
		user2.is_active = True
		user2.subscription_status = 'free-trial'
		user2.save()

		user3 = get_user_model().objects.create_user(full_name="Client Three", email="client3@a.com", password='client')
		user3.is_active = True
		user3.subscription_status = 'paid'
		user3.save()

		user4 = get_user_model().objects.create_user(full_name="Client Four", email="client4@a.com", password='client')
		user4.is_active = True
		user4.save()

		response = _self.client.post(reverse('token-obtain'), data={'email': 'admin@a.com', 'password': 'admin'})
		self.admin_access = response.json()['access']

		"""
		Setting up the Subjects, Topics, Subtopics, Department and Subject type
		"""
		department = Department.objects.create(name='art', slug='art')
		department2 = Department.objects.create(name='science', slug='science')

		subject_type = SubjectType.objects.create(name='olevel')

		subject = Subject.objects.create(name='Subject', department=department, lecturer=user, slug="subject-1")
		Subject.objects.create(name='Subject Two', department=department2, lecturer=user, slug="subject-2")
		Subject.objects.create(name='Subject Three', department=department, lecturer=user, slug="subject-3")
		Subject.objects.create(name='Subject Four', department=department2, lecturer=user, slug="subject-4")

		topic = Topic.objects.create(name="Topic One", slug='topic-one', subject=subject, ordering=1)
		topic2 = Topic.objects.create(name="Topic Two", slug='topic-two', subject=subject, ordering=2)

		self.subtopic1 = SubTopic.objects.create(name="Sub Topic One", slug="sub-topic-one", ordering=1, topic=topic)
		self.subtopic2 = SubTopic.objects.create(name="Sub Topic Two", slug="sub-topic-two", ordering=2, topic=topic)
		self.subtopic3 = SubTopic.objects.create(name="Sub Topic Three", slug="sub-topic-three", ordering=3,
		                                         topic=topic)

		"""
		Setting up notification
		"""
		Notification.add_notification(to='all-users', title='First Notification', content='This is to notifi the gen')


class TestAdministrator(test.APITestCase):
	def test_admin_login(self):
		user = get_user_model().objects.create_superuser(full_name="Admin One", email="admin@a.com", password='admin')
		user2 = get_user_model().objects.create_user(full_name="Client One", email="client@a.com", password='client')
		url = '/edustart_admin/token/obtain/'
		res = self.client.post(url, data={'email': 'admin@a.com', 'password': 'admin'})

		self.assertEquals(res.status_code, 200)
		self.assertEquals(self.client.post(url, data={'email': 'client@a.com', 'password': 'client'}).status_code, 401)

	def test_admin_dashboard(self):
		data = SetUpTest(self)
		url = '/edustart_admin/dashboard/'
		res = self.client.get(url, HTTP_AUTHORIZATION='JWT ' + data.admin_access)

		self.assertEquals(res.status_code, 200)
		self.assertEquals(resolve(url).func.__name__, AdminDashboard.as_view().__name__)
		self.assertEquals(res.data['total_users'], 3)
		self.assertEquals(res.data['free_trial_users'], 1)
		self.assertEquals(res.data['paying_users'], 1)
		self.assertEquals(res.data['subject_count'], 4)
		self.assertEquals(res.data['topic_count'], 1)
		self.assertEquals(res.data['subtopic_count'], 3)
		self.assertEquals(res.data['notification'],
		                  [{'content': 'This is to notifi the gen', 'id': 1, 'title': 'First Notification'}])

	def test_admin_department(self):
		data = SetUpTest(self)
		url = '/edustart_admin/department/'
		res = self.client.get(url, HTTP_AUTHORIZATION='JWT ' + data.admin_access)

		print(res.data)

	def test_admin_topic(self):
		data = SetUpTest(self)
		url = '/edustart_admin/topic/?order_by=-ordering'
		res = self.client.get(url, HTTP_AUTHORIZATION='JWT ' + data.admin_access)

		print(res.data)

	def test_admin_topic_add_before_a_value(self):
		data = SetUpTest(self)
		url = '/edustart_admin/topic/'
		res = self.client.post(url, HTTP_AUTHORIZATION='JWT ' + data.admin_access, data={
			'name': 'Topic on', "slug": "topic-on", "subject": 1, "ordering": "1"
		})

		self.assertEqual(res.status_code, 201)
		self.assertEquals(Topic.objects.count(), 3)
		self.assertEquals(Topic.objects.get(slug='topic-on').ordering, 1)
		self.assertEquals(Topic.objects.get(slug='topic-two').ordering, 3)
		self.assertEquals(Topic.objects.get(slug='topic-one').ordering, 2)

	def test_admin_topic_add_before_two_value(self):
		data = SetUpTest(self)
		url = '/edustart_admin/topic/'
		res = self.client.post(url, HTTP_AUTHORIZATION='JWT ' + data.admin_access, data={
			'name': 'Topic on', "slug": "topic-on", "subject": 1, "ordering": "2"
		})

		self.assertEqual(res.status_code, 201)
		self.assertEquals(Topic.objects.count(), 3)
		self.assertEquals(Topic.objects.get(slug='topic-on').ordering, 2)
		self.assertEquals(Topic.objects.get(slug='topic-two').ordering, 3)
		self.assertEquals(Topic.objects.get(slug='topic-one').ordering, 1)

	def test_admin_topic_add_last(self):
		data = SetUpTest(self)
		url = '/edustart_admin/topic/'
		res = self.client.post(url, HTTP_AUTHORIZATION='JWT ' + data.admin_access, data={
			'name': 'Topic on', "slug": "topic-on", "subject": 1
		})

		self.assertEqual(res.status_code, 201)
		self.assertEquals(Topic.objects.count(), 3)
		self.assertEquals(Topic.objects.get(slug='topic-on').ordering, 3)
		self.assertEquals(Topic.objects.get(slug='topic-two').ordering, 2)
		self.assertEquals(Topic.objects.get(slug='topic-one').ordering, 1)

	def test_admin_subject_get_no_pagination(self):
		data = SetUpTest(self)
		url = '/edustart_admin/subject/?pagination=all'
		res = self.client.get(url, HTTP_AUTHORIZATION='JWT ' + data.admin_access)

		self.assertEqual(res.status_code, 200)
		self.assertEquals(len(res.data), 4)
		self.assertEquals(res.data[0]['id'], 1)

	def test_admin_subject_POST(self):
		data = SetUpTest(self)
		url = '/edustart_admin/subject/'
		subject_data = {
			'department': 1,
			'type': 1,
			'name': 'Subject Post',
			'slug': 'subject-post',
			'description': "Com to datay",
			'objectives': "<ul><li>Dean Derry</li></ul>",
			'lecturer': 1,
		}
		res = self.client.post(url, data=subject_data, HTTP_AUTHORIZATION='JWT ' + data.admin_access)

		print(res.data)
		self.assertEqual(res.status_code, 201)

	# self.assertEquals(len(res.data), 4)
	# self.assertEquals(res.data[0]['id'], 1)

	def test_admin_subtopic_add_before_a_value(self):
		data = SetUpTest(self)
		url = '/edustart_admin/subtopic/'
		res = self.client.post(url, HTTP_AUTHORIZATION='JWT ' + data.admin_access, data={
			'name': 'Sub Topic on', "slug": "sub-topic-on", "topic": 1,
			"ordering": "1", "video_link": 'http://www.add.cm', 'description': "only"
		})

		# print(res.data)
		self.assertEqual(res.status_code, 201)
		self.assertEquals(SubTopic.objects.count(), 4)
		self.assertEquals(SubTopic.objects.get(slug='sub-topic-on').ordering, 1)
		self.assertEquals(SubTopic.objects.get(slug='sub-topic-one').ordering, 2)
		self.assertEquals(SubTopic.objects.get(slug='sub-topic-two').ordering, 3)
		self.assertEquals(SubTopic.objects.get(slug='sub-topic-three').ordering, 4)

	def test_admin_subtopic_add_before_two_value(self):
		data = SetUpTest(self)
		url = '/edustart_admin/subtopic/'
		res = self.client.post(url, HTTP_AUTHORIZATION='JWT ' + data.admin_access, data={
			'name': 'Sub Topic on', "slug": "sub-topic-on", "topic": 1,
			"ordering": 3, "video_link": 'http://www.add.cm', 'description': "only"
		})

		# print(res.data)
		self.assertEqual(res.status_code, 201)
		self.assertEquals(SubTopic.objects.count(), 4)
		self.assertEquals(SubTopic.objects.get(slug='sub-topic-on').ordering, 3)
		self.assertEquals(SubTopic.objects.get(slug='sub-topic-one').ordering, 1)
		self.assertEquals(SubTopic.objects.get(slug='sub-topic-two').ordering, 2)
		self.assertEquals(SubTopic.objects.get(slug='sub-topic-three').ordering, 4)

	def test_admin_subtopic_add_last(self):
		data = SetUpTest(self)
		url = '/edustart_admin/subtopic/'
		res = self.client.post(url, HTTP_AUTHORIZATION='JWT ' + data.admin_access, data={
			'name': 'Sub Topic on', "slug": "sub-topic-on", "topic": 1,
			"video_link": 'http://www.add.cm', 'description': "only"
		})

		# print(res.data)
		self.assertEqual(res.status_code, 201)
		self.assertEquals(SubTopic.objects.count(), 4)
		self.assertEquals(SubTopic.objects.get(slug='sub-topic-on').ordering, 4)
		self.assertEquals(SubTopic.objects.get(slug='sub-topic-one').ordering, 1)
		self.assertEquals(SubTopic.objects.get(slug='sub-topic-two').ordering, 2)
		self.assertEquals(SubTopic.objects.get(slug='sub-topic-three').ordering, 3)

	def test_admin_notifications_add(self):
		data = SetUpTest(self)
		url = '/edustart_admin/notification/'
		res = self.client.post(url, HTTP_AUTHORIZATION='JWT ' + data.admin_access, data={
			'title': 'Testing Notification', "content": "Small Content", "to": "all-users"
		})

		print(res.data)
		self.assertEqual(res.status_code, 201)
		self.assertEquals(len(Notification.objects.filter(title='Testing Notification')), 1)
		self.assertEquals(
			len(NotificationUser.objects.filter(notification=Notification.objects.get(title='Testing Notification'))),
			3)

	def test_topic_level_questions_GET(self):
		data = SetUpTest(self)
		question = Questions(
			topic=Topic.objects.first(), questions="[{}, {}, {}]",
		).save()

		url = '/edustart_admin/practice-questions/'
		res = self.client.get(url, HTTP_AUTHORIZATION='JWT ' + data.admin_access)

		print(res.data['results'])
		self.assertEqual(res.status_code, 200)
		self.assertEqual(len(res.data['results']), 1)
	
	def test_practice_question_POST(self):
		import json
		data = SetUpTest(self)

		url = '/edustart_admin/practice-questions/'
		form_data = (
			{
				"id":1,
				"question": "What is your name?",
				"answers": (
					{ "id":1, "answer":"Derry", "correct":False },
					{ "id":2, "answer":"Dean", "correct":True },
					{ "id":3, "answer":"Kuammy", "correct":False },
					{ "id":4, "answer":"Pade", "correct":False }
				)
			},
			{
				"id":2,
				"question": "What is your age?",
				"answers": (
					{ "id":1, "answer":11, "correct":False },
					{ "id":2, "answer":22, "correct":False },
					{ "id":3, "answer":44, "correct":True },
					{ "id":4, "answer":55, "correct":False }
				)
			}
		)
		res = self.client.post(url, HTTP_AUTHORIZATION='JWT ' + data.admin_access, data={
			"topic":1,
			"lecturer":1,
			"questions":json.dumps(form_data)

		})

		print(res.data)
		self.assertEqual(res.status_code, 201)
		# self.assertEqual(len(res.data['results']), 1)
