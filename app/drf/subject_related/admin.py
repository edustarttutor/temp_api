from django.contrib import admin

from .models import Subject, SubjectType, Department, Topic, SubTopic

admin.site.register(Subject)
admin.site.register(SubjectType)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
	list_display = ['name', 'ordering', 'slug', 'subject']


@admin.register(SubTopic)
class TopicAdmin(admin.ModelAdmin):
	list_display = ['name', 'topic']


admin.site.register(Department)
