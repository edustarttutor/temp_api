from django.db import models


class Department(models.Model):
	name = models.CharField(max_length=50, unique=True)
	slug = models.SlugField(max_length=50, unique=True)
	pub_date = models.DateTimeField(auto_now_add=True)
	date_updated = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['name']

	def __str__(self):
		return self.name
