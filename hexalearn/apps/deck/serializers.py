from rest_framework import serializers
from .models import Deck, Card, Folder, StudyState

#FOLDER

class DeckInFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deck
        fields = ['id', 'title', 'is_public', 'created_at']


class FolderSerializer(serializers.ModelSerializer):
    decks = DeckInFolderSerializer(many=True, read_only=True)
    total_decks = serializers.IntegerField(source='decks.count', read_only=True)

    class Meta:
        model = Folder
        fields = ['id', 'name', 'description', 'total_decks', 'created_at', 'updated_at', 'decks']
        read_only_fields = ['id', 'total_decks', 'created_at', 'updated_at']

class DeckOverviewSerializer(serializers.Serializer):
    folders = FolderSerializer(many=True)
    unorganized_decks = DeckInFolderSerializer(many=True)
    
#DECK
class CardSerializer(serializers.ModelSerializer):
    front_image = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    back_image = serializers.URLField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Card
        fields = ['id', 'front_text', 'back_text', 'hint', 'front_image', 'back_image']
        read_only_fields = ['id']

class DeckListSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source.name', read_only=True)
    estimated_level_name = serializers.CharField(
        source='estimated_level.name', read_only=True)
    total_cards = serializers.IntegerField(
        source='cards.count', read_only=True)

    class Meta:
        model = Deck
        fields = [
            'id', 'title', 'description',
            'source', 'source_name',
            'estimated_level', 'estimated_level_name',
            'is_public', 'total_cards',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class DeckDetailSerializer(serializers.ModelSerializer):
    cards = CardSerializer(many=True, read_only=True)
    source_name = serializers.CharField(source='source.name', read_only=True)
    estimated_level_name = serializers.CharField(
        source='estimated_level.name', read_only=True)
    total_cards = serializers.IntegerField(
        source='cards.count', read_only=True)

    class Meta:
        model = Deck
        fields = [
            'id', 'title', 'description',
            'source', 'source_name',
            'estimated_level', 'estimated_level_name',
            'is_public', 'total_cards',
            'created_at', 'updated_at',
            'cards',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        
# CREATE DECK AND CARDS

class DeckCreateSerializer(serializers.ModelSerializer):
    cards = CardSerializer(many=True, write_only=True, required=True)

    class Meta:
        model = Deck
        fields = [
            'id', 'title', 'description',
            'source', 'estimated_level',
            'is_public', 'cards',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_cards(self, value):
        if len(value) == 0:
            raise serializers.ValidationError("Deck must have at least 1 card.")
        return value
    
    def create(self, validated_data):
        cards_data = validated_data.pop('cards', [])
        deck = Deck.objects.create(**validated_data)
        Card.objects.bulk_create([
            Card(deck=deck, **card_data) for card_data in cards_data
        ])
        return deck

# UPDATE DECK basic info (not including cards)
class DeckUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deck
        fields = [
            'title', 'description', 'is_public','folder',
        ]

class StudyStateSerializer(serializers.ModelSerializer):
    card_front_text = serializers.CharField(source='card.front_text', read_only=True)
    card_back_text = serializers.CharField(source='card.back_text', read_only=True)
    class Meta:
        model = StudyState
        fields = [
            'id', 'card',
            'card_front_text', 'card_back_text',
            'repetition', 'interval_days',
            'last_reviewed', 'last_result',
            'next_review', 'review_count',
        ]
        read_only_fields = [
            'id', 'repetition', 'interval_days',
            'last_reviewed', 'next_review', 'review_count',
        ]