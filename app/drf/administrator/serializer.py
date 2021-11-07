import json

from practiceQuestion.models import Questions
from django.contrib.auth.models import update_last_login
from django.db.models import Count
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework.serializers import ModelSerializer, Serializer

from accounts.models import User, Notification
from departments.models import Department
from subject_related.models import Subject, SubjectType, Topic, SubTopic


class AdminTokenObtainSerializer(TokenObtainPairSerializer):
	def validate(self, attrs):
		data = super().validate(attrs)

		refresh = self.get_token(self.user)

		data['refresh'] = str(refresh)
		data['access'] = str(refresh.access_token)
		data['is_superuser'] = self.user.is_superuser

		if api_settings.UPDATE_LAST_LOGIN:
			update_last_login(None, self.user)

		return data


class UsersSerializer(ModelSerializer):
	class Meta:
		model = User
		# fields = '__all__'
		exclude = ['user_permissions', 'groups', 'is_staff', 'password']

	def to_representation(self, instance):
		data = super().to_representation(instance)
		data['subscription_status'] = instance.subscriptionplan.subscription_status
		data['department__name'] =  instance.department.name if instance.department else 'Not yet picked'
		return data


class DepartmentSerializer(ModelSerializer):
	class Meta:
		model = Department
		fields = '__all__'


class SubjectSerializer(ModelSerializer):
	class Meta:
		model = Subject
		fields = '__all__'

	def to_representation(self, instance, *args, **kwargs):
		result = super().to_representation(instance, *args, **kwargs)
		result['type__name'] = instance.type.name
		result['department__name'] = instance.department.name
		result['topic_count'] = instance.topic_set.count()
		return result


class TopicSerializer(ModelSerializer):
	class Meta:
		model = Topic
		fields = '__all__'

	def create(self, validated_data):
		"""
		Get validated data
		Get all ordering with subject == validated_data.subject
		Update all gotten gotten data ordering is >= validated_data ordering
		After update, create the new instance
		:param validated_data:
		:return: Created instance of validated_data
		"""
		# print(validated_data)
		if validated_data.get('ordering'):
			def fix(x):
				x.ordering = x.ordering + 1
				x.save()
				return x

			tuple(fix(x) for x in validated_data.get('subject').topic_set.filter() if x.ordering >= validated_data['ordering'])
			topic = self.Meta.model.objects.create(**validated_data)
		else:
			if validated_data.get('subject').topic_set.all().count():
				last_ordering = validated_data.get('subject').topic_set.all().order_by('-ordering')[0].ordering
			else:
				last_ordering = 0
			topic = self.Meta.model.objects.create(**validated_data, ordering=last_ordering+1)
		return topic

	def to_representation(self, instance):
		rep = super().to_representation(instance)
		rep['subject__name'] = instance.subject.name
		rep['subtopic_count'] = instance.subtopic_set.count()
		return rep


class SubjectTypeSerializer(ModelSerializer):
	class Meta:
		model = SubjectType
		fields = '__all__'


class SubTopicSerializer(ModelSerializer):
	class Meta:
		model = SubTopic
		fields = '__all__'

	def to_representation(self, instance):
		data = super().to_representation(instance)
		data['topic__name'] = instance.topic.name
		data['subject__name'] = instance.topic.subject.name
		return data

	def create(self, validated_data):
		"""
		Get validated data
		Get all ordering with topic == validated_data.subject
		Update all gotten gotten data ordering is >= validated_data ordering
		After update, create the new instance
		:param validated_data:
		:return: Created instance of validated_data
		"""
		# print(validated_data)
		if validated_data.get('ordering'):
			def fix(x):
				x.ordering = x.ordering + 1
				x.save()
				return x

			tuple(fix(x) for x in validated_data.get('topic').subtopic_set.filter() if x.ordering >= validated_data['ordering'])
			subtopic = self.Meta.model.objects.create(**validated_data)
		else:
			if validated_data.get('topic').subtopic_set.all():
				last_ordering = validated_data.get('topic').subtopic_set.all().order_by('-ordering')[0].ordering
			else:
				last_ordering = 0
			subtopic = self.Meta.model.objects.create(**validated_data, ordering=last_ordering+1)
		return subtopic


class NotificationSerializer(ModelSerializer):
	class Meta:
		model = Notification
		fields = '__all__'

	def create(self, validated_data):
		to = validated_data.get('to')
		title = validated_data.get('title')
		content = validated_data.get('content')
		department = validated_data.get('department')
		users_list = validated_data.get('users_list')
		notify = self.Meta.model.add_notification(to, title, content)

		return notify



class PracticeQuestionSerializer(ModelSerializer):
	class Meta:
		model = Questions
		fields = '__all__'

	def create(self, validated_data):
		item, data = self.Meta.model.objects.get_or_create(topic=validated_data.get('topic'))
		item.questions = validated_data.get('questions')
		item.save()
		return item
	
	def to_representation(self, instance):
		data = super().to_representation(instance)
		data['questions_count'] = len(json.loads(instance.questions))
		data['name'] = instance.topic.name
		data['topic_id'] = instance.topic.id
		return data
