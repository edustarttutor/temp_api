from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from departments.models import Department
from practiceQuestion.models import Questions, UserAnswers
from subject_related.models import Subject, Topic, SubjectType


class QuestionsTest(APITestCase):
	def setUp(self):
		user = get_user_model().objects.create_user(full_name="Client", email="client@a.com", password='client')
		user.is_active = True
		user.subscriptionplan.subscription_status = 'paid'
		user.save()
		user.subscriptionplan.save()
		response = self.client.post(reverse('token-obtain'), data={'email': 'client@a.com', 'password': 'client'})
		self.access = response.json()['access']

		subject_type = SubjectType.objects.create(name='olevel')
		department = Department.objects.create(name='art', slug='art')
		subject = Subject.objects.create(name='Subject', department=department, lecturer=user, slug="subject-1")
		self.topic = Topic.objects.create(name="Topic One", slug='topic-one', subject=Subject.objects.first(), ordering=1)
		self.question = Questions.objects.create(topic=self.topic, questions="ada")

	def test_answer_POST(self):
		url = '/practice/user-answers/'
		res = self.client.post(url, HTTP_AUTHORIZATION='JWT '+self.access, data={'score':5, 'topic':1})

		print(res.data)
		self.assertEquals(res.status_code, 201)

	def test_answer_GET(self):
		url = '/practice/user-answers/'
		self.client.post(url, HTTP_AUTHORIZATION='JWT ' + self.access, data={'score': 5, 'topic': 1})
		res = self.client.get(url, HTTP_AUTHORIZATION='JWT '+self.access)

		print(res.data)
		self.assertEquals(res.status_code, 200)
		self.assertEquals(res.data.get('count'), 1)
