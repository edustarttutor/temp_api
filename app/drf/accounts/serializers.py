from datetime import datetime

from django.core.mail import EmailMultiAlternatives
from django.template import loader
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import AccountActivity, User, SubscriptionActivity, Notification, NotificationUser, SubscriptionPlan


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
	def validate(self, attrs):

		data = super().validate(attrs)
		user = self.user.email

		user_data = self.user.__dict__
		user_data.pop('_state')
		user_data.pop('id')
		user_data.pop('password')
		user_data.pop('last_login')
		user_data.pop('is_superuser')
		user_data.pop('backend')
		user_data.pop('date_joined')
		user_data['subscription_status'] = SubscriptionPlan.objects.get(user__email=user).subscription_status
		user_data['subscription_expiry'] = str(SubscriptionPlan.objects.get(user__email=user).expiry_date)
		user_data['profile_pic'] = self.user.profile_pic.url
		data['user_data'] = user_data

		return data


class UserRegistrationSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ['email', 'full_name', 'password']

	def create(self, validated_data):
		password = validated_data.pop('password')
		user = self.Meta.model(email=validated_data['email'], full_name=validated_data['full_name'])
		if password:
			user.set_password(password)
		user.save()

		return user


class UserUpdateSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ['email', 'full_name', 'phone', 'about', 'profile_pic', 'is_staff',
		          'date_joined']
		read_only_fields = ['is_staff', 'date_joined']

	def to_representation(self, instance):
		data = super().to_representation(instance)
		data['subscription_status'] = instance.subscriptionplan.subscription_status
		data['subscription_expiry'] = str(instance.subscriptionplan.expiry_date)
		return data


class SubscriptionSerializer(serializers.ModelSerializer):
	class Meta:
		model = SubscriptionActivity
		fields = ['reference', 'status', 'transaction', 'amount', 'plan', 'trxref', 'date_created']
		read_only_fields = ['date_created']


class NotificationSerializer(serializers.ModelSerializer):
	class Meta:
		model = NotificationUser
		fields = ['id', 'notification', 'read']
		read_only_fields = ['notification']

	def to_representation(self, instance):
		rep = super().to_representation(instance)
		rep['notification__title'] = instance.notification.title
		rep['notification__content'] = instance.notification.content
		rep['notification__date'] = instance.notification.date_created
		return rep


class AccountActivitySerializer(serializers.ModelSerializer):
	class Meta:
		model = AccountActivity
		fields = '__all__'


class PasswordResetSerializer(serializers.Serializer):
	email = serializers.CharField(max_length=50)

	def send_mail(self, subject_template_name, email_template_name,
	              context, from_email, to_email, html_email_template_name=None):
		"""
		Send a django.core.mail.EmailMultiAlternatives to `to_email`.
		"""
		subject = loader.render_to_string(subject_template_name, context)
		# Email subject *must not* contain newlines
		subject = ''.join(subject.splitlines())
		body = loader.render_to_string(email_template_name, context)

		email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
		if html_email_template_name is not None:
			html_email = loader.render_to_string(html_email_template_name, context)
			email_message.attach_alternative(html_email, 'text/html')

		email_message.send()



	def save(self, **kwargs):
		pass
