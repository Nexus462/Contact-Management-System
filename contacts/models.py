"""
Contact model — stores each contact linked to the user who created it.
"""

from django.db import models
from django.contrib.auth.models import User


class Contact(models.Model):
    # Each contact belongs to one user
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')

    # Contact info fields
    name    = models.CharField(max_length=100)
    phone   = models.CharField(max_length=20)
    email   = models.EmailField(blank=True)
    address = models.TextField(blank=True)

    # Optional profile image
    image   = models.ImageField(upload_to='profiles/', blank=True, null=True)

    # Favorite flag
    is_favorite = models.BooleanField(default=False)

    # Category/Group (e.g., Family, Friend, Work, etc.)
    category = models.CharField(max_length=50, blank=True, default='')

    # Notes field for additional information
    notes = models.TextField(blank=True, default='')

    # Emergency contact flag
    is_emergency = models.BooleanField(default=False)

    # Reminder fields
    has_reminder = models.BooleanField(default=False)
    reminder_date = models.DateTimeField(blank=True, null=True)
    reminder_note = models.CharField(max_length=200, blank=True, default='')

    # Additional smart fields
    birthday = models.DateField(blank=True, null=True)
    last_contacted = models.DateTimeField(blank=True, null=True)
    website = models.URLField(blank=True, default='')
    company = models.CharField(max_length=100, blank=True, default='')
    job_title = models.CharField(max_length=100, blank=True, default='')
    
    # Social media
    whatsapp = models.CharField(max_length=20, blank=True, default='')
    linkedin = models.URLField(blank=True, default='')
    twitter = models.CharField(max_length=50, blank=True, default='')
    facebook = models.URLField(blank=True, default='')
    instagram = models.CharField(max_length=50, blank=True, default='')

    # Auto timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_emergency', '-is_favorite', 'name']  # Emergency first, then favorites, then alphabetically

    def __str__(self):
        return self.name

    def get_initials(self):
        """Returns initials for avatar placeholder (e.g. 'John Doe' → 'JD')"""
        parts = self.name.strip().split()
        if len(parts) >= 2:
            return parts[0][0].upper() + parts[-1][0].upper()
        return self.name[0].upper() if self.name else '?'
