from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model

from departments.models import Department


class SubjectType(models.Model):
	name = models.CharField(max_length=20, choices=[('olvevel', 'OLevel/Waec/Jamb')])
	date_created = models.DateTimeField(auto_now_add=True)
	date_updated = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.name


class Subject(models.Model):
	department = models.ForeignKey(Department, on_delete=models.PROTECT)
	type = models.ForeignKey(SubjectType, on_delete=models.SET_DEFAULT, default=1)
	name = models.CharField(max_length=50)
	slug = models.SlugField(max_length=50, unique=True)
	description = models.TextField()
	objectives = models.TextField(default='')
	subject_image = models.ImageField(default="default.png")
	lecturer = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, default=1)
	pub_date = models.DateTimeField(auto_now=True)
	date_updated = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['name']

	def __str__(self):
		return self.name


class PubObject(models.Manager):
	def get_queryset(self, *args, **kwargs):
		return super().get_queryset(*args, **kwargs).filter(status='published')


class Topic(models.Model):
	ordering = models.IntegerField(default=1, blank=True, null=True)
	subject = models.ForeignKey(Subject, on_delete=models.PROTECT)
	name = models.CharField(max_length=500)
	slug = models.SlugField(max_length=50, unique=True)
	topic_thumbnail = models.ImageField(default="default_thumbnail.png")
	status = models.CharField(
		max_length=50,
		choices=[('published', 'Publish'), ('draft', 'Drafted')],
		default='published'
	)
	pub_date = models.DateTimeField(auto_now_add=True)
	date_updated = models.DateTimeField(auto_now=True)
	objects = PubObject()
	all_objects = models.Manager()

	class Meta:
		ordering = ['ordering']

	def __str__(self):
		return self.name


class SubTopic(models.Model):
	topic = models.ForeignKey(Topic, on_delete=models.PROTECT)
	ordering = models.IntegerField(default=1, blank=True, null=True)
	name = models.CharField(max_length=500)
	video_link = models.URLField()
	slug = models.SlugField(max_length=50, unique=True)
	description = models.TextField()
	topic_thumbnail = models.ImageField(default="default_thumbnail.png")
	status = models.CharField(
		max_length=50,
		choices=[('published', 'Publish'), ('draft', 'Drafted')],
		default='published'
	)
	lock = models.BooleanField(default=True)
	pub_date = models.DateTimeField(auto_now_add=True)
	date_updated = models.DateTimeField(auto_now=True)
	objects = PubObject()
	all_objects = models.Manager()

	class Meta:
		ordering = ['-id']

	def __str__(self):
		return self.name


class Bookmark(models.Model):
	user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
	topics = models.ManyToManyField(SubTopic)

	def __str__(self):
		return self.user

	@classmethod
	def add_bookmark(cls, current_user, subtopic):
		_subtopic, action = cls.objects.get_or_create(user=current_user)
		_subtopic.topics.add(subtopic)

	@classmethod
	def remove_bookmark(cls, current_user, subtopic):
		_subtopic, action = cls.objects.get_or_create(user=current_user)
		_subtopic.topics.remove(subtopic)


class WatchHistory(models.Model):
	user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
	subtopic = models.ForeignKey(SubTopic, on_delete=models.CASCADE)
	percentage = models.IntegerField(default=0, blank=True, null=True)
	date_updated = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-date_updated']

	def __str__(self):
		return "{} - {}".format(self.user.full_name, self.subtopic.name)
