from datetime import datetime, timedelta

from rest_framework import test
from django.urls import reverse
from django.contrib.auth import get_user_model

from accounts.models import User, SubscriptionPlan
from subject_related.models import WatchHistory
from .test_setup import TestSetUp


class TestSubTopic(test.APITestCase):

    def test_single_subtopic_expired_subscription_GET(self):
        _ = TestSetUp(self)
        url = '/sub-topics/sub-topic-one/'

        res = self.client.get(url, HTTP_AUTHORIZATION=f'JWT {_.access_1}')
        self.assertEquals(res.status_code, 401)
        self.assertEquals(res.data['msg'], 'Current Subscription has Expired')

    # def test_single_subtopic_subscription_GET(self):
    #     _ = TestSetUp(self)
    #     user = SubscriptionPlan.objects.get(user__email="client@a.com")
    #     user.expiry_date = "datetime.now() + timedelta(days=3)"
    #     d = user.save()
    #
    #     print(user)
    #     print(d)
    #     print(datetime.now() + timedelta(days=3))
    #
    #     print(User.objects.get(email="client@a.com").subscriptionplan.expiry_date)
    #     url = '/sub-topics/sub-topic-one/'
    #
    #     res = self.client.get(url, HTTP_AUTHORIZATION=f'JWT {_.access_1}')
    #     self.assertEquals(res.status_code, 401)
    #     self.assertEquals(res.data['msg'], 'Current Subscription has Expired')
