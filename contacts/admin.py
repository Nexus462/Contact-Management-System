"""
Django admin configuration for Contact model.
Allows managing contacts through the /admin interface.
"""

from django.contrib import admin
from .models import Contact
from .profile_models import UserProfile


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'user', 'created_at']
    list_filter = ['user', 'created_at']
    search_fields = ['name', 'phone', 'email']
    readonly_fields = ['created_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'location']
    search_fields = ['user__username', 'phone', 'location']

