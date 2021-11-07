from django.core.serializers import serialize
from rest_framework import serializers

from .models import Subject, SubTopic, WatchHistory


class SerializedSubjects(serializers.ModelSerializer):
	class Meta:
		model = Subject
		fields = ['id', 'department', 'type', 'name', 'description', 'objectives', 'subject_image', 'lecturer', 'slug']

	def to_representation(self, instance):
		queryset = super().to_representation(instance)

		"""
		Add to returned subject results
		"""
		queryset["lecturer"] = instance.lecturer.full_name
		queryset["image"] = instance.subject_image.url
		queryset["department"] = instance.department.name
		queryset["type__name"] = instance.type.name
		queryset["lectures"] = instance.topic_set.count()

		return queryset


class SerializedSubTopic(serializers.ModelSerializer):
	class Meta:
		model = SubTopic
		fields = ['id', 'video_link', 'lock']


class WatchHistorySerializer(serializers.ModelSerializer):
	class Meta:
		model = WatchHistory
		fields = [
			'id',
			'subtopic',
			'percentage',
			'date_updated'
		]

	def to_representation(self, instance):
		queryset = super().to_representation(instance)
		queryset['subtopic'] = instance.subtopic.name
		queryset['subject'] = instance.subtopic.topic.subject.name
		queryset['subject_slug'] = instance.subtopic.topic.subject.slug
		queryset['tumbnail'] = instance.subtopic.topic_thumbnail.url
		return queryset
