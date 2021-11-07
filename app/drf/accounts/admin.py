from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, SubscriptionPlan

admin.site.register(User)


class SubAdmin(admin.ModelAdmin):
	list_display = ['user', 'subscription_status', 'expiry_date']


admin.site.register(SubscriptionPlan, SubAdmin)
