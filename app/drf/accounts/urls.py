from django.urls import path

from rest_framework.routers import DefaultRouter
from .views import UserRegistrationEndpoint, UserUpdateEndpoint, account_activity_view, change_password, \
	subscription_view, NotificationView, \
	CustomTokenObtainPair, activate_account_view, reset_password

app_name = 'accounts'

route = DefaultRouter()
route.register('notifications', NotificationView, basename='notification')

urlpatterns = [
	path('register/', UserRegistrationEndpoint.as_view(), name='register-as-user'),
	path('reset_password/', reset_password, name='reset_password'),
	path('activate/<uid64>/<token>/', activate_account_view, name='activate-user'),
	path('update/', UserUpdateEndpoint.as_view(), name='update-user'),
	path('change-password/', change_password, name='change-user'),
	path('subscription/', subscription_view, name='subscription'),
	path('account-activity/', account_activity_view, name='account-activity'),
	*route.urls
]
