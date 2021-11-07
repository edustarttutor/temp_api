from rest_framework import test

from .test_setup import TestSetUp
from ..models import WatchHistory


class TestSubject(test.APITestCase):
	def test_subject_list_with_limit_as_params(self):
		_ = TestSetUp(self)
		url = "/subjects/"

		res = self.client.get(url+'?limit= 3', HTTP_AUTHORIZATION='JWT '+_.access_1)

		print(res.data)

		self.assertEquals(res.status_code, 200)
		self.assertEquals(len(res.data['results']), 3)
		self.assertEquals(
			len(
				self.client.get('/subjects/?limit= 2', HTTP_AUTHORIZATION='JWT '+_.access_1).data['results']
			), 2
		)

	def test_subject_retrieve(self):
		_ = TestSetUp(self)
		url = "/subjects/subject-1/"
		res = self.client.get(url, HTTP_AUTHORIZATION='JWT '+_.access_1)

		self.assertEquals(res.status_code, 200)

	def test_subject_retrieve_with_bookmark(self):
		_ = TestSetUp(self)
		self.client.post('/bookmark/', data={"pk": '1'}, HTTP_AUTHORIZATION='JWT ' + _.access_1)
		url = "/subjects/subject-1/"

		res = self.client.get(url, HTTP_AUTHORIZATION='JWT '+_.access_1)

		self.assertEquals(res.status_code, 200)
		self.assertEquals(len(res.data['topics'][0]['sub_topics']), 3)
		self.assertTrue(res.data['topics'][0]['sub_topics'][0].get('bookmarked'))
		self.assertFalse(res.data['topics'][0]['sub_topics'][1].get('bookmarked'))
		self.assertFalse(res.data['topics'][0]['sub_topics'][2].get('bookmarked'))

	def test_subject_retrieve_with_watchlist_check(self):
		_ = TestSetUp(self)
		self.client.get('/sub-topics/sub-topic-two/', HTTP_AUTHORIZATION=f'JWT {_.access_1}')
		# self.client.get('/sub-topics/sub-topic-one/', HTTP_AUTHORIZATION=f'JWT {_.access_1}')
		url = "/subjects/subject-1/"

		res = self.client.get(url, HTTP_AUTHORIZATION='JWT '+_.access_1)

		print(res.data['topics'][0]['sub_topics'])
		self.assertEquals(res.status_code, 200)
		# self.assertEquals(len(res.data['topics'][0]['sub_topics']), 3)
		# self.assertTrue(res.data['topics'][0]['sub_topics'][0].get('bookmarked'))
		# self.assertFalse(res.data['topics'][0]['sub_topics'][1].get('bookmarked'))
		# self.assertFalse(res.data['topics'][0]['sub_topics'][2].get('bookmarked'))
