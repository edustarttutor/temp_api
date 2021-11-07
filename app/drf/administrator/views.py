import json

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.core.paginator import Paginator
# from django.db.models import query

from rest_framework import views, viewsets, status, permissions, generics, response, filters, pagination
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.pagination import PageNumberPagination

from accounts.models import Notification, User, SubscriptionPlan
from administrator.pagination import CustomPageNumberPagination
from administrator.serializer import (
	AdminTokenObtainSerializer, PracticeQuestionSerializer, UsersSerializer, DepartmentSerializer,
	SubjectSerializer, SubTopicSerializer, TopicSerializer, SubjectTypeSerializer,
	NotificationSerializer)
from departments.models import Department
from practiceQuestion.models import Questions
from subject_related.models import Subject, Topic, SubTopic, SubjectType


class GeneralModelViewConfig(viewsets.ModelViewSet):
	pagination_class = CustomPageNumberPagination

	def paginate_queryset(self, queryset):
		if 'pagination' in self.request.query_params:
			return None
		return super().paginate_queryset(queryset)


class AdminTokenObtainPairView(TokenObtainPairView):
	serializer_class = AdminTokenObtainSerializer

	def post(self, request, *args, **kwargs):
		serializer = self.serializer_class(data=request.data)

		try:
			serializer.is_valid(raise_exception=True)

			if not serializer.validated_data.get('is_superuser'):
				data = {'detail': "You dont have the right privilege"}
				return Response(data, status=status.HTTP_401_UNAUTHORIZED)
		except TokenError as e:
			raise InvalidToken(e.args[0])

		return Response(serializer.validated_data, status=status.HTTP_200_OK)


class AdminDashboard(generics.GenericAPIView):
	permission_classes = [permissions.IsAdminUser]

	def get(self, request):
		users = get_user_model().objects.filter(is_superuser=False).only('pk')
		resent_users = [
			{'id': x.id, 'full_name': x.full_name, 'email': x.email, 'profile_pic': x.profile_pic.url,
			 'is_active': x.is_active}
			for x in get_user_model().objects.filter(is_staff=False).order_by('-id')[:5]
		]

		data = {
			'total_users': users.count(),
			"free_trial_users": SubscriptionPlan.objects.filter(subscription_status='free-trial').count(),
			"paying_users": SubscriptionPlan.objects.filter(subscription_status='paid').count(),
			"expired_users": SubscriptionPlan.objects.filter(subscription_status='expired').count(),
			"subject_count": Subject.objects.count(),
			"topic_count": Topic.objects.count(),
			"subtopic_count": SubTopic.objects.count(),
			"department_count": Department.objects.count(),
			"resently_registered_users": resent_users,
			"notification": [x for x in Notification.objects.all().values().order_by('-id')[:5]],
			"profile": {'profile_pic': request.user.profile_pic.url, 'full_name': request.user.full_name}
		}
		return response.Response(data)


class UsersView(viewsets.ModelViewSet):
	permission_classes = (permissions.IsAdminUser,)
	queryset = User.objects.filter(is_staff=False)
	serializer_class = UsersSerializer
	pagination_class = CustomPageNumberPagination


class SubjectView(GeneralModelViewConfig):
	permission_classes = (permissions.IsAdminUser,)
	queryset = Subject.objects.all()
	serializer_class = SubjectSerializer
	filter_backends = [filters.SearchFilter, filters.OrderingFilter]
	pagination_class = CustomPageNumberPagination
	ordering_fields = ['id', 'pub_date']


class DepartmentView(viewsets.ModelViewSet):
	permission_classes = (permissions.IsAdminUser,)
	queryset = Department.objects.all()
	serializer_class = DepartmentSerializer
	filter_backends = [filters.SearchFilter]
	search_field = ['name']

	def list(self, request, *args, **kwargs):
		queryset = Department.objects.values().annotate(Count('subject'))
		return response.Response(queryset)


class SubjectTypeView(viewsets.ModelViewSet):
	permission_classes = (permissions.IsAdminUser,)
	queryset = SubjectType.objects.all()
	serializer_class = SubjectTypeSerializer
	filter_backends = [filters.SearchFilter, filters.OrderingFilter]
	search_fields = ['name']
	ordering_fields = ['id', 'pub_date']


class TopicView(viewsets.ModelViewSet):
	permission_classes = (permissions.IsAdminUser,)
	queryset = Topic.objects.all()
	serializer_class = TopicSerializer
	filter_backends = [filters.SearchFilter, filters.OrderingFilter]
	ordering_fields = ['id']
	search_fields = ['subject__name', 'subject__slug', 'subject__id', 'name']
	pagination_class = CustomPageNumberPagination


class SubTopicView(GeneralModelViewConfig):
	permission_classes = [permissions.IsAdminUser]
	queryset = SubTopic.all_objects.all()
	serializer_class = SubTopicSerializer
	filter_backends = [filters.OrderingFilter, filters.SearchFilter]
	search_fields = ['name', 'status', 'topic__id', 'lock']
	ordering_fields = ['id', 'pub_date', 'date_updated', 'ordering']
	pagination_class = CustomPageNumberPagination


class NotificationView(GeneralModelViewConfig):
	permission_classes = [permissions.IsAdminUser]
	queryset = Notification.objects.all()
	serializer_class = NotificationSerializer
	pagination_class = CustomPageNumberPagination


class PracticeQuestionView(viewsets.ModelViewSet):
	permission_classes = [permissions.IsAdminUser]
	queryset = Questions.objects.all()
	serializer_class = PracticeQuestionSerializer
