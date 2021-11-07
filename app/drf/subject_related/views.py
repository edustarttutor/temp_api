from datetime import datetime

from django.shortcuts import get_object_or_404
from django.utils.datetime_safe import datetime as d_datetime


from rest_framework import viewsets, permissions, response, status, filters, pagination
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Subject, Topic, SubTopic, Department, Bookmark, WatchHistory
from .serializer import SerializedSubjects, SerializedSubTopic, WatchHistorySerializer


class DashboardView(viewsets.ViewSet):
	permission_classes = [permissions.IsAuthenticated]

	def list(self, request):
		bookmark = Bookmark.objects.filter(user=request.user)

		my_subjects = 0
		completed_subjects = 0
		bookmarks = bookmark[0].topics.count() if bookmark.count() else 0
		questions_completed = 0
		activities = request.user.accountactivity_set.values()[:5]
		watch_list = request.user.watchhistory_set.values('id', 'subtopic__name', 'subtopic__slug')[:5]

		data = dict(
			my_subjects=my_subjects,
			completed_subjects=completed_subjects,
			bookmarks=bookmarks,
			questions_completed=questions_completed,
			watch_list=watch_list,
			activities=activities
		)

		return response.Response(data)


class SubjectsView(viewsets.ModelViewSet):
	permission_classes = [permissions.AllowAny]
	serializer_class = SerializedSubjects
	queryset = Subject.objects.all()
	filter_backends = [filters.SearchFilter]
	search_fields = ['department__slug']
	pagination_class = pagination.LimitOffsetPagination

	def retrieve(self, request, pk):

		queryset = get_object_or_404(Subject, slug=pk)
		serializer = SerializedSubjects(queryset).data

		"""
		Get three related subjects
		"""
		related_subjects_queryset = Subject.objects.filter(department=queryset.department).exclude(id=queryset.id)[:3]
		related_subject_serializer = SerializedSubjects(related_subjects_queryset, many=True)
		serializer['related_subjects'] = related_subject_serializer.data

		user_bookmarks = []
		user_watch_history = []

		if request.user.is_authenticated:
			bookmark_query = Bookmark.objects.filter(user=request.user)
			watchlist_query = request.user.watchhistory_set.all().only('id')

			if bookmark_query:
				user_bookmarks = [x[0] for x in bookmark_query[0].topics.values_list('id')]
			if watchlist_query:
				user_watch_history = [x.subtopic.id for x in watchlist_query]

		serializer['topics'] = tuple(
			{
				**topic,
				'sub_topics': tuple(
					dict(
						id=subtopic.id,
						name=subtopic.name,
						slug=subtopic.slug,
						ordering=subtopic.ordering,
						lock=subtopic.lock,
						bookmarked=subtopic.id in user_bookmarks,
						watched=subtopic.id in user_watch_history,
					) for subtopic in
					SubTopic.objects.filter(topic__name=topic["name"]).order_by('ordering')
				)
			} for topic in
			queryset.topic_set.values("id", "name", "ordering").order_by('ordering')
		)

		return response.Response(serializer, status=status.HTTP_200_OK)

	def update(self, request):
		return response.Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

	def destroy(self, request, *args, **kwargs):
		return response.Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class DepartmentView(viewsets.ViewSet):
	permission_classes = [permissions.AllowAny]

	def list(self, request):
		queryset = Department.objects.values("id", "name", "slug")
		return response.Response(queryset, status=status.HTTP_200_OK)


class SubTopicView(viewsets.ViewSet):
	permission_classes = [permissions.IsAuthenticated]

	def retrieve(self, request, pk):
		data = get_object_or_404(SubTopic, slug=pk)

		if request.user.subscriptionplan.subscription_status in ['free-trial', 'paid']:
			if datetime.now().timetuple() <= request.user.subscriptionplan.expiry_date.timetuple():
				WatchHistory.objects.get_or_create(user=request.user, subtopic=data)
				serializer = SerializedSubTopic(data)
				return response.Response(serializer.data)
			return response.Response({'msg': "Current Subscription has Expired"}, status=status.HTTP_401_UNAUTHORIZED)

		return response.Response({'msg': "Subscribe to watch video"}, status=status.HTTP_401_UNAUTHORIZED)


class BookmarkView(viewsets.ViewSet):
	permission_classes = [permissions.IsAuthenticated]

	def list(self, request):
		data = get_object_or_404(Bookmark, user=request.user)
		data = data.topics.all()
		data = [
			dict(
				id=subtopic.pk, subject=subtopic.topic.subject.name, subject_slug=subtopic.topic.subject.slug,
				subtopic=subtopic.name, completed='40%', tumbnail=subtopic.topic_thumbnail.url,
				slug=subtopic.slug,
			)
			for subtopic in data
		]

		return response.Response(data)

	def create(self, request):
		subtopic = get_object_or_404(SubTopic, pk=request.data['pk'])
		Bookmark.add_bookmark(request.user, subtopic)

		return response.Response(status=status.HTTP_201_CREATED)

	def destroy(self, request, pk):
		subtopic = get_object_or_404(SubTopic, pk=pk)
		Bookmark.remove_bookmark(request.user, subtopic)

		return response.Response(status=status.HTTP_200_OK)


class WatchHistoryView(viewsets.ModelViewSet):
	permission_classes = [permissions.IsAuthenticated]
	queryset = WatchHistory.objects.all()
	serializer_class = WatchHistorySerializer
	pagination_class = pagination.LimitOffsetPagination

	def get_queryset(self):
		queryset = WatchHistory.objects.filter(user=self.request.user)
		return queryset
