# apps/accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from apps.home.models import UserProfile

class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source='profile.phone_number', read_only=True)
    address = serializers.CharField(source='profile.address', read_only=True)
    date_of_birth = serializers.DateField(source='profile.date_of_birth', read_only=True)
    avatar_url = serializers.SerializerMethodField()
    native_language = serializers.CharField(source='profile.native_language', read_only=True)
    daily_ai_limit = serializers.IntegerField(source='profile.daily_ai_limit', read_only=True)
    reading_level_name = serializers.CharField(source='profile.reading_level.name', read_only=True)
    reading_level_color = serializers.CharField(source='profile.reading_level.color', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email',
            'phone_number', 'address', 'date_of_birth',
            'avatar_url', 'native_language', 'daily_ai_limit',
            'reading_level_name', 'reading_level_color',
        ]

    def get_avatar_url(self, obj):
        try:
            return obj.profile.avatar_url
        except AttributeError:
            return None