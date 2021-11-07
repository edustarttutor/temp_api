from django.contrib import admin

# Register your models here.
from accounts.models import Notification, NotificationUser

admin.site.register(Notification)
admin.site.register(NotificationUser)
