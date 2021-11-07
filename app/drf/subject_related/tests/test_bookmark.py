from rest_framework import test
from django.urls import reverse
from django.contrib.auth import get_user_model

from subject_related.models import SubTopic, Bookmark, Subject, Topic, Department, SubjectType


class TestSetUp:
    def __init__(self, _self):
        user = get_user_model().objects.create_user(full_name="Client", email="client@a.com", password='client')
        user.is_active = True
        user.save()

        user2 = get_user_model().objects.create_user(full_name="Client Two", email="client2@a.com", password='client')
        user2.is_active = True
        user2.save()
        
        
        self.user = user
        self.user2 = user2

        res = _self.client.post(reverse('token-obtain'), data={'email':'client@a.com', 'password': 'client'})
        res2 = _self.client.post(reverse('token-obtain'), data={'email':'client2@a.com', 'password': 'client'})
        
        self.res = res.json()['access']
        self.res2 = res2.json()['access']

        department = Department.objects.create(name='art')
        subject_type = SubjectType.objects.create(name='olevel')
        subject = Subject.objects.create(name='Subject', department=department, lecturer=user)
        topic = Topic.objects.create(name="Topic One", subject=subject, ordering=1)
        self.subtopic1 = SubTopic.objects.create(name="Sub Topic One", ordering=1, topic=topic)
        self.subtopic2 = SubTopic.objects.create(name="Sub Topic Two", ordering=2, topic=topic)
        self.subtopic3 = SubTopic.objects.create(name="Sub Topic Three", ordering=2, topic=topic)


class TestBookmarkView(test.APITestCase):
    def test_list_bookmarks(self):
        data = TestSetUp(self)


        # Add to bookmark
        self.client.post('/bookmark/', data={"pk":'1'}, HTTP_AUTHORIZATION='JWT '+ data.res)
        self.client.post('/bookmark/', data={"pk":'2'}, HTTP_AUTHORIZATION='JWT '+ data.res)
        self.client.post('/bookmark/', data={"pk":'3'}, HTTP_AUTHORIZATION='JWT '+ data.res2)

        res = self.client.get('/bookmark/', HTTP_AUTHORIZATION='JWT '+ data.res)
        
        self.assertEquals(res.status_code, 200)
        self.assertEquals(len(res.data), 2)
        self.assertEquals(res.data[0]['subtopic'], 'Sub Topic One')
        self.assertEquals(res.data[1]['subtopic'], 'Sub Topic Two')


    def test_add_to_bookmark(self):
        data = TestSetUp(self)

        res = self.client.post('/bookmark/', data={"pk":'1'}, HTTP_AUTHORIZATION='JWT '+ data.res)
        
        self.assertEquals(res.status_code, 201)
        self.assertEquals(Bookmark.objects.count(), 1)
        self.assertEquals(Bookmark.objects.first().user.email, 'client@a.com')
        self.assertEquals(Bookmark.objects.first().topics.count(), 1)

    
    def test_remove_from_bookmark(self):
        data = TestSetUp(self)

        self.client.post('/bookmark/', data={"pk":1}, HTTP_AUTHORIZATION='JWT '+data.res, HTTP_ACCEPT='application/json')
        self.client.post('/bookmark/', data={"pk":2}, HTTP_AUTHORIZATION='JWT '+data.res, HTTP_ACCEPT='application/json')

        res = self.client.delete('/bookmark/1/', HTTP_AUTHORIZATION='JWT '+data.res, HTTP_ACCEPT='application/json')

        self.assertEquals(res.status_code, 200)
        self.assertEquals(Bookmark.objects.count(), 1)
        self.assertEquals(Bookmark.objects.first().user.email, 'client@a.com')
        self.assertEquals(Bookmark.objects.first().topics.count(), 1)
        



class TestBookmarkModel(test.APITestCase):
    def test_add_new_bookmark(self):
        data = TestSetUp(self)
        Bookmark.add_bookmark(data.user, data.subtopic1)

        self.assertEquals(Bookmark.objects.all().count(), 1)
        self.assertEquals(str(Bookmark.objects.first().user), 'client@a.com')
        self.assertEquals(Bookmark.objects.first().topics.count(), 1)
        self.assertEquals(Bookmark.objects.first().topics.first().name, 'Sub Topic One')
    
    def test_remove_bookmark(self):
        data = TestSetUp(self)
        Bookmark.add_bookmark(data.user, data.subtopic1)
        Bookmark.remove_bookmark(data.user, data.subtopic1)

        self.assertEquals(Bookmark.objects.all().count(), 1)
        self.assertEquals(Bookmark.objects.first().topics.count(), 0)

        

