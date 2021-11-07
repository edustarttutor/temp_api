from django.urls import reverse
from django.contrib.auth import get_user_model

from accounts.models import Notification
from subject_related.models import SubTopic, Bookmark, Subject, Topic, Department, SubjectType


class TestSetUp:
	def __init__(self, _self):
		"""
		Create Two Users for authentication purposes
		"""
		user = get_user_model().objects.create_user(full_name="Client", email="client@a.com", password='client')
		user.is_active = True
		user.subscriptionplan.subscription_status = 'paid'
		user.save()
		user.subscriptionplan.save()

		user2 = get_user_model().objects.create_user(full_name="Client Two", email="client2@a.com", password='client')
		user2.is_active = True
		# user2.subscriptionplan.subscription_status = 'paid'
		user2 = user2.save()

		self.user = user
		self.user2 = user2

		response = _self.client.post(reverse('token-obtain'), data={'email': 'client@a.com', 'password': 'client'})
		response2 = _self.client.post(reverse('token-obtain'), data={'email': 'client2@a.com', 'password': 'client'})

		self.access_1 = response.json()['access']
		# self.access_2 = response2.json()['access']

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
		self.subtopic3 = SubTopic.objects.create(name="Sub Topic Three", slug="sub-topic-three", ordering=3, topic=topic)

		"""
		Setting up notification
		"""
		Notification.add_notification(to='all-users', title='First Notification', content='This is to notifi the gen')