from datetime import timezone, date, timedelta, datetime

import django
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext as _
from django.db.models.signals import post_save

from departments.models import Department


class CustomUserObject(BaseUserManager):
	def create_user(self, email, full_name, password, **other_fields):
		email = self.normalize_email(email)
		user = self.model(email=email, full_name=full_name, **other_fields)
		if password:
			user.set_password(password)
		user.save()
		return user

	def create_superuser(self, email, full_name, password, **other_fields):
		other_fields.setdefault('is_staff', True)
		other_fields.setdefault('is_superuser', True)
		other_fields.setdefault('is_active', True)

		return self.create_user(email, full_name, password, **other_fields)


class User(AbstractBaseUser, PermissionsMixin):
	full_name = models.CharField(_("Full Name"), max_length=50)
	email = models.EmailField(_("Email Address"), unique=True)
	phone = models.IntegerField(_("Phone Number"), default=0)
	about = models.TextField(_("About You"), default="", blank=True)
	# subscription_status = models.CharField(
	# 	max_length=50,
	# 	choices=[
	# 		('free-trial', "Free Trial"),
	# 		('paid', "Paid"),
	# 		('expired', 'Expired'),
	# 		('no-plan', 'No Plan')
	# 	],
	# 	default='no-plan'
	# )
	# subscription_expiry = models.DateField(auto_now_add=True)
	department = models.ForeignKey(Department, on_delete=models.PROTECT, blank=True, null=True)
	profile_pic = models.ImageField(blank=True, default='default_profile.png')
	is_active = models.BooleanField(default=False)
	is_staff = models.BooleanField(default=False)
	date_joined = models.DateTimeField(auto_now_add=True)
	objects = CustomUserObject()

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['full_name']

	def __str__(self):
		return self.email


class SubscriptionPlan(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	subscription_status = models.CharField(
		max_length=50,
		choices=[
			('free-trial', "Free Trial"),
			('paid', "Paid"),
			('no-plan', 'No Plan')
		],
		default='no-plan'
	)
	expiry_date = models.DateTimeField(default=django.utils.timezone.now)

	def save(self, *args, **kwargs):
		# print(self.subscription_status)
		if self.subscription_status == 'free-trial':
			self.expiry_date = datetime.now() + timedelta(days=3)
		elif self.subscription_status == 'paid':
			self.expiry_date = datetime.now() + timedelta(days=30)
		super().save(*args, **kwargs)

	def __str__(self):
		return self.user.email


def create_sub_user(instance, **kwargs):
	if kwargs['created']:
		SubscriptionPlan.objects.create(user=instance)


post_save.connect(create_sub_user, User)


class Notification(models.Model):
	title = models.CharField(max_length=50)
	content = models.TextField()
	to = models.CharField(max_length=500)
	date_created = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.title

	class Meta:
		ordering = ('-id',)

	@classmethod
	def add_notification(cls, to, title, content, **kwargs):
		notification = cls.objects.create(title=title, content=content, to=to)
		if to == 'all-users':
			users = User.objects.filter(is_staff=False)
		elif to == 'by-department':
			users = Department.objects.get(slug=kwargs.get('department')).user_set.all()
		elif to == 'free-trial':
			users = User.objects.filter(subscription_status='free-trial').all()
		elif to == 'paid':
			users = User.objects.filter(subscription_status='paid').all()
		elif to == 'expired':
			users = User.objects.filter(subscription_status='expired').all()
		elif to == 'no-plan':
			users = User.objects.filter(subscription_status='no-plan').all()
		elif to == 'selected-users':
			users = (User.objects.get(pk=pk) for pk in kwargs.get('users_list'))
		else:
			raise ValueError("No Valid to was entered")

		for user in users:
			NotificationUser.objects.create(user=user, notification=notification)

		return notification

	@classmethod
	def remove_notification(cls, pk):
		notification = cls.objects.get(pk=pk).delete()


class NotificationUser(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
	read = models.BooleanField(default=False)

	class Meta:
		ordering = ('-id',)

	def __str__(self):
		return self.user.email


class SubscriptionActivity(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	reference = models.CharField(max_length=200)
	status = models.CharField(max_length=200)
	trxref = models.CharField(max_length=200)
	transaction = models.CharField(max_length=200)
	amount = models.IntegerField(default=0)
	plan = models.CharField(max_length=50)
	date_created = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-id']

	def __str__(self):
		return self.user.email


class AccountActivity(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	message = models.TextField()
	activity_type = models.CharField(max_length=50, default='')
	date_created = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-id']

	def __str__(self):
		return self.user.email


def user_signal(instance, **kwargs):
	if kwargs['created']:
		AccountActivity.objects.create(
			user=instance, activity_type='Account Created',
			message="Your edustart account has been created"
		)
	else:
		AccountActivity.objects.create(
			user=instance, activity_type='Profile Updated',
			message="Your profile has been updated"
		)


post_save.connect(user_signal, User)


def subscription_signal(instance, **kwargs):
	if kwargs['created']:
		AccountActivity.objects.create(
			user=instance.user, activity_type='Subcription Plan Updated',
			message=f"Your subscription plan has been updated to {instance.plan}"
		)


post_save.connect(subscription_signal, SubscriptionActivity)

