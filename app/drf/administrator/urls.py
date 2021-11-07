from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'edustart_admin'

route = DefaultRouter()
route.register('users', views.UsersView)
route.register('department', views.DepartmentView)
route.register('subject', views.SubjectView)
route.register('subject-type', views.SubjectTypeView)
route.register('topic', views.TopicView)
route.register('subtopic', views.SubTopicView)
route.register('notification', views.NotificationView)
route.register('practice-questions', views.PracticeQuestionView)

urlpatterns = [
	path('token/obtain/', views.AdminTokenObtainPairView.as_view(), name='admin_token_obtain_pair'),
	path('dashboard/', views.AdminDashboard.as_view(), name='admin_dashboard'),
	*route.urls
]
