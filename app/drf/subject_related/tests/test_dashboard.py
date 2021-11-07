from rest_framework.test import APITestCase
from .test_setup import TestSetUp


class DashboardTest(APITestCase):
	def testDashboard_GET(self):
		_ = TestSetUp(self)
		url = ('/dashboard/')
		res = self.client.get(url, HTTP_AUTHORIZATION='JWT '+_.access_1)

		self.assertEquals(res.status_code, 200)
		self.assertEquals(res.data['my_subjects'], 0)
		self.assertEquals(res.data['completed_subjects'], 0)
		self.assertEquals(res.data['bookmarks'], 0)
		self.assertEquals(res.data['questions_completed'], 0)
		self.assertQuerysetEqual(res.data['watch_list'], [])
		self.assertEquals(res.data['activities'], [])
