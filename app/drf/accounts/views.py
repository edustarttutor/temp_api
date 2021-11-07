from datetime import datetime, timedelta
from hashlib import md5
# from multiprocessing import Process
from threading import Thread

from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth.forms import PasswordResetForm

from rest_framework import views, permissions, response, status, decorators, filters
from rest_framework.decorators import api_view
from rest_framework_simplejwt.views import TokenObtainPairView

# Create your views here.
from accounts.models import AccountActivity, SubscriptionActivity, NotificationUser, User
from accounts.serializers import (
	AccountActivitySerializer, UserRegistrationSerializer, UserUpdateSerializer,
	NotificationSerializer, SubscriptionSerializer, CustomTokenObtainPairSerializer, PasswordResetSerializer
)
from administrator.views import GeneralModelViewConfig


class CustomTokenObtainPair(TokenObtainPairView):
	serializer_class = CustomTokenObtainPairSerializer


class UserRegistrationEndpoint(views.APIView):
	permission_classes = [permissions.AllowAny]

	def post(self, request):
		serializer = UserRegistrationSerializer(data=request.data)
		if serializer.is_valid():
			user = serializer.save()

			def send_mail_fnc():
				user_hash = md5(user.email.encode('utf-8')).hexdigest()
				context = {
					'user': user,
					'token': user_hash
				}
				send_mail(
					'Verify your email',
					render_to_string('email.html', context),
					'no_reply@edustart.com',
					[user.email]
				)

			t1 = Thread(target=send_mail_fnc)
			t1.start()

			return response.Response(status=status.HTTP_201_CREATED)
		else:
			return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def activate_account_view(request, uid64, token):
	user = get_object_or_404(User, pk=uid64)
	hashed = md5(user.email.encode('utf-8')).hexdigest()

	if hashed == token:
		if not user.is_active:
			user.is_active = True
			user.subscriptionplan.subscription_status = 'free-trial'
			user.save()
			user.subscriptionplan.save()
		return response.Response(f"Your Email {user.email} has been verified.")
	return response.Response("Invalid Token", status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def reset_password(request):
	print(request.data)
	serializer = PasswordResetSerializer(request.data)
	serializer.is_valid(raise_exception=True)
	serializer.save()
	return response.Response("Done")


class UserUpdateEndpoint(views.APIView):
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request):
		serializer = UserUpdateSerializer(instance=request.user)
		return response.Response(serializer.data)

	def patch(self, request):
		serializer = UserUpdateSerializer(instance=request.user, data=request.data, partial=True)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return response.Response(status=status.HTTP_202_ACCEPTED)


@decorators.api_view(['PUT'])
@decorators.permission_classes([permissions.IsAuthenticated])
def change_password(request):
	old_password = request.data.get('old_password')
	password = request.data.get('password')

	if request.user.check_password(old_password):
		user = request.user
		user.set_password(password)
		user.save()

		return response.Response("Password Updated", status.HTTP_202_ACCEPTED)

	return response.Response("Incorrect password", status.HTTP_400_BAD_REQUEST)


@decorators.api_view(['POST', 'GET'])
@decorators.permission_classes([permissions.IsAuthenticated])
def subscription_view(request):
	if request.method == 'POST':
		data = SubscriptionActivity.objects.create(
			user=request.user,
			reference=request.data['reference'],
			status=request.data['status'],
			transaction=request.data['transaction'],
			plan=request.data['plan'],
			trxref=request.data['trxref'],
			amount=request.data['amount'],
		)
		data.save()

		user = request.user
		user.subscriptionplan.subscription_status = 'paid'
		user.save()
		user.subscriptionplan.save()

		return response.Response(status=status.HTTP_201_CREATED)
	else:
		queryset = SubscriptionActivity.objects.filter(user=request.user.pk)
		if queryset:
			serialized_data = SubscriptionSerializer(queryset, many=True)
			return response.Response(serialized_data.data, status=status.HTTP_200_OK)
		return response.Response("No payment history", status=status.HTTP_200_OK)


class NotificationView(GeneralModelViewConfig):
	queryset = NotificationUser.objects.all()
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = NotificationSerializer
	filter_backends = [filters.SearchFilter]
	search_fields = ['notification__title', 'notification__content', 'read']

	def get_queryset(self):
		queryset = self.request.user.notificationuser_set.all()
		return queryset

	def create(self, request, *args, **kwargs):
		return response.Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

	def destroy(self, request, *args, **kwargs):
		return response.Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@decorators.api_view(['GET'])
@decorators.permission_classes([permissions.IsAuthenticated])
def account_activity_view(request):
	queryset = AccountActivity.objects.filter(user=request.user)
	data = AccountActivitySerializer(instance=queryset, many=True)
	return response.Response(data.data)
