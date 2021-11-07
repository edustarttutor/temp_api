from rest_framework import test
from django.urls import reverse
from django.contrib.auth import get_user_model

from subject_related.models import WatchHistory
from .test_setup import TestSetUp


class TestWatchlist(test.APITestCase):
    def test_add_to_watchlist_from_retrieving_a_subtopic(self):
        _ = TestSetUp(self)
        url = '/sub-topics/sub-topic-one/'
        self.client.get('/sub-topics/sub-topic-two/', HTTP_AUTHORIZATION=f'JWT {_.access_1}')
        res = self.client.get(url, HTTP_AUTHORIZATION=f'JWT {_.access_1}')

        print(res.data)
        self.assertEquals(res.status_code, 200)
        self.assertEquals(WatchHistory.objects.count(), 2)
        self.assertEquals(WatchHistory.objects.first().user.email, "client@a.com")

    def test_watchlist_GET(self):
        _ = TestSetUp(self)
        url = '/watch-history/?limit=10'


        self.client.get('/sub-topics/sub-topic-one/', HTTP_AUTHORIZATION=f'JWT {_.access_1}')
        self.client.get('/sub-topics/sub-topic-two/', HTTP_AUTHORIZATION=f'JWT {_.access_1}')
        self.client.get('/sub-topics/sub-topic-two/', HTTP_AUTHORIZATION=f'JWT {_.access_2}')
        res = self.client.get(url, HTTP_AUTHORIZATION=f'JWT {_.access_1}')

        self.assertEquals(res.status_code, 200)
        self.assertEquals(len(res.data['results']), 2)
        # self.assertEquals(WatchHistory.objects.count(), 2)
        # self.assertEquals(WatchHistory.objects.first().user.email, "client@a.com")

    def test_watchlist1_GET(self):
        import os
        print(os.getenv('DEBUG'))
