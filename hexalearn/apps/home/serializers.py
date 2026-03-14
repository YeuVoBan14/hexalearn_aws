from .models import Level, Source
from rest_framework import serializers

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