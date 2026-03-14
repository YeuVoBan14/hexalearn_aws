import re
from colorfield.fields import ColorField

from django.db import models
from django.contrib.auth.models import User


LANGUAGE_CHOICES = [
    ("en", "English"),
    ("vi", "Vietnamese"),
    ("jp", "Japanese"),
]


class Level(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20, unique=True)
    color = ColorField(default="#FFFFFF")
    difficulty_rank = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['difficulty_rank']

    def __str__(self):
        return self.name
    
    def _generate_code(self):
        # "N5 - Beginner" → "n5-beginner"
        code = self.name.lower()
        code = re.sub(r'[^\w\s-]', '', code)
        code = re.sub(r'\s+', '-', code.strip())
        return code


class Source(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=50, unique=True)
    color = ColorField(default="#FFFFFF")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def _generate_code(self):
        code = self.name.lower()
        code = re.sub(r'[^\w\s-]', '', code)
        code = re.sub(r'\s+', '-', code.strip())
        return code


class MediaFile(models.Model):
    file_url = models.TextField()
    file_path = models.TextField()
    file_name = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=100)
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    upload_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(
        upload_to="profile_pics/", blank=True, null=True)
    native_language = models.CharField(
        max_length=10, blank=True, choices=LANGUAGE_CHOICES)
    daily_ai_limit = models.PositiveIntegerField(default=20)
    reading_level = models.ForeignKey(
        Level, on_delete=models.SET_NULL, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

    @property
    def avatar_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return None