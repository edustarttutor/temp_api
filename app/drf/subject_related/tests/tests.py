from django.test import TestCase

from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from accounts.models import User
from .models import Subject, SubjectType, Department, Topic
from .serializer import SerializedSubjects


class TestDepartmentModel(TestCase):
	def test_department_slug_creation(self):
		Department.objects.create(name="Science")
		pass


class TestSubjectRelatedSerializer(TestCase):
	def test_subject_serializer(self):
		pass


class TestSubjectRelatedView(APITestCase):
	def SetUp(self):
		pass

	def test_subject_list_view(self):
		department = Department.objects.create(name="Science")
		_type = SubjectType.objects.create(name='olevel')
		user = User.objects.create(email="a@a.com")
		Subject.objects.create(
			name="Maths",
			slug='math',
			department=department,
			type=_type
		)
		url = '/subjects/'
		c1 = self.client
		res = c1.get(url)

		self.assertEquals(len(res.json()), 1)
		self.assertEquals(res.json()[0]['name'], 'Maths')

	def test_subject_retrieve_and_ony_published_topics_view(self):
		department = Department.objects.create(name="Science")
		_type = SubjectType.objects.create(name='olevel')
		user = User.objects.create(email="a@a.com")
		subject = Subject.objects.create(
			name="Maths",
			slug='math',
			department=department,
			type=_type
		)
		Topic.objects.create(
			subject=subject,
			name="Topic Three",
			ordering=2
		)
		Topic.objects.create(
			subject=subject,
			name="Topic One",
			ordering=1
		)
		Topic.objects.create(
			subject=subject,
			name="Topic Two",
			ordering=3,
			status='draft'
		)
		url = '/subjects/math/'
		c1 = self.client
		res = c1.get(url)

		self.assertEquals(res.json()["name"], "Maths")
		self.assertEquals(len(res.json()["topics"]), 2)
		self.assertEquals(res.json()["topics"][0]["name"], "Topic One")
		self.assertEquals(res.json()["topics"][1]["name"], "Topic Three")
