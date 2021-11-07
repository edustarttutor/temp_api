from django.db import models

from accounts.models import User
from subject_related.models import Topic


class Questions(models.Model):
	topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
	questions = models.TextField(default="")
	date = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.topic.name


class UserAnswers(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
	score = models.CharField(max_length=50)
	date_created = models.DateField(auto_now_add=True)
