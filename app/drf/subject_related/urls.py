from rest_framework import routers

from . import views

app_name = 'subject_related'

route = routers.DefaultRouter()
route.register('dashboard', views.DashboardView, basename='dashboard')
route.register('subjects', views.SubjectsView, basename='subject')
route.register('departments', views.DepartmentView, basename='department')
route.register('sub-topics', views.SubTopicView, basename='subtopic')
route.register('bookmark', views.BookmarkView, basename='bookmark')
route.register('watch-history', views.WatchHistoryView, basename='watch_history')

urlpatterns = [
	*route.urls,
]
