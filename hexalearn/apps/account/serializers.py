# apps/accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from apps.home.models import UserProfile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        if self.user.profile.is_deleted:
            raise serializers.ValidationError(
                "This account has been deleted."
            )
        
        return data
    
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'username', 'email',
            'first_name', 'last_name',
        ]