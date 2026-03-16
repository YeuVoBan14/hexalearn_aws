from .models import Level, Source, UserProfile
from rest_framework import serializers
from django.contrib.auth.models import User


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = '__all__'
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = '__all__'
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']


class UserProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', required=False)
    first_name = serializers.CharField(
        source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)

    reading_level_name = serializers.CharField(
        source='reading_level.name', read_only=True)
    reading_level_color = serializers.CharField(
        source='reading_level.color', read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'user_id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'address', 'date_of_birth',
            'profile_picture', 'image_url',
            'native_language', 'daily_ai_limit',
            'reading_level_name', 'reading_level_color',
            'created_at',
        ]
        read_only_fields = [
            'user_id', 'email', 'created_at',
            'image_url', 'daily_ai_limit',
            'reading_level_name', 'reading_level_color',
        ]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.profile_picture and hasattr(obj.profile_picture, 'url'):
            return request.build_absolute_uri(obj.profile_picture.url)
        return None

    def validate_username(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError(
                "Username has already been taken.")
        return value

    def update(self, instance, validated_data):
        if 'profile_picture' in validated_data and instance.profile_picture:
            instance.profile_picture.delete(save=False)
            
        user_data = validated_data.pop('user', {})
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        # Update UserProfile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class RegisterSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    phone_number = serializers.CharField(
        max_length=15, required=False, allow_blank=True)
    address = serializers.CharField(
        max_length=255, required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False)
    native_language = serializers.CharField(max_length=10, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'confirm_password',
                  'phone_number', 'address', 'date_of_birth', 'native_language']
        
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs
    
    def create(self, validated_data):
        profile_data = {
            'phone_number':    validated_data.pop('phone_number', ''),
            'address':         validated_data.pop('address', ''),
            'date_of_birth':   validated_data.pop('date_of_birth', None),
            'native_language': validated_data.pop('native_language', ''),
        }

        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)

        # Signal đã tạo UserProfile rồi, chỉ cần update thêm data
        profile = user.profile
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return user
