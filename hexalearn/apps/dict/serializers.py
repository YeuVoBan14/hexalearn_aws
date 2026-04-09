from rest_framework import serializers
from .models import (Kanji, KanjiMeaning, KanjiWord, PartOfSpeech,
                     Word, WordImage, WordMeaning, WordPronunciation, Example,
                     UserPinnedWord, SavedWordList, SavedWordListItem)
from apps.home.models import MediaFile
from drf_spectacular.utils import extend_schema_field
# ---------------------------------------------------------------------------
# PART OF SPEECH
# ---------------------------------------------------------------------------


class PartOfSpeechSerializer(serializers.ModelSerializer):
    language_name = serializers.CharField(
        source='language.name', read_only=True)

    class Meta:
        model = PartOfSpeech
        fields = ['id', 'name', 'code', 'language',
                  'language_name', 'created_at']
        read_only_fields = ['id', 'created_at']

# ---------------------------------------------------------------------------
# WORD GET & UPDATE — basic fields only
# ---------------------------------------------------------------------------


class WordMeaningSerializer(serializers.ModelSerializer):
    language_name = serializers.CharField(
        source='language.name', read_only=True)

    class Meta:
        model = WordMeaning
        fields = ['id', 'language', 'language_name',
                  'short_definition', 'full_definition', 'created_at']
        read_only_fields = ['id', 'created_at']


class WordPronunciationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordPronunciation
        fields = ['id', 'type', 'pronunciation', 'created_at']
        read_only_fields = ['id', 'created_at']


class WordImageSerializer(serializers.ModelSerializer):
    file_url = serializers.CharField(
        source='media_file.file_url',  read_only=True)
    file_name = serializers.CharField(
        source='media_file.file_name', read_only=True)
    alt_text = serializers.CharField(
        source='media_file.alt_text',  read_only=True)
    mime_type = serializers.CharField(
        source='media_file.mime_type', read_only=True)

    class Meta:
        model = WordImage
        fields = ['id', 'media_file', 'file_url', 'file_name',
                  'alt_text', 'mime_type', 'created_at']
        read_only_fields = ['id', 'created_at']


class KanjiWordInlineSerializer(serializers.ModelSerializer):
    character = serializers.CharField(source='kanji.character', read_only=True)
    kanji_onyomi = serializers.CharField(
        source='kanji.onyomi',    read_only=True)
    kanji_kunyomi = serializers.CharField(
        source='kanji.kunyomi',   read_only=True)

    class Meta:
        model = KanjiWord
        fields = ['id', 'kanji', 'character', 'kanji_onyomi',
                  'kanji_kunyomi', 'position', 'reading_in_word']
        read_only_fields = ['id']


class ExampleSerializer(serializers.ModelSerializer):
    language_name = serializers.CharField(
        source='language.name', read_only=True)
    translation_language_name = serializers.CharField(
        source='language_of_translation.name', read_only=True)

    class Meta:
        model = Example
        fields = [
            'id', 'sentence',
            'language', 'language_name',
            'translation',
            'language_of_translation', 'translation_language_name',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class WordSerializer(serializers.ModelSerializer):
    """
    GET  — return all fields, including nested meanings/pronunciations/images (read-only)
    PUT/PATCH — only allow updating basic fields (lemma, language, level, part_of_speech),
                other fields managed via their own endpoints (meanings, pronunciations, images)
    """
    # Read-only display fields
    language_name = serializers.CharField(
        source='language.name', read_only=True)
    level_name = serializers.CharField(source='level.name', read_only=True)
    part_of_speech_name = serializers.CharField(
        source='part_of_speech.name', read_only=True)

    # Nested — read-only, managed via their own endpoints
    meanings = WordMeaningSerializer(many=True, read_only=True)
    pronunciations = WordPronunciationSerializer(many=True, read_only=True)
    word_images = WordImageSerializer(many=True, read_only=True)
    kanji_words = KanjiWordInlineSerializer(many=True, read_only=True)
    examples = ExampleSerializer(many=True, read_only=True)

    class Meta:
        model = Word
        fields = [
            'id', 'lemma',
            'language', 'language_name',
            'level', 'level_name',
            'part_of_speech', 'part_of_speech_name',
            'meanings', 'pronunciations', 'word_images', 'kanji_words', 'examples',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at',
            'meanings', 'pronunciations', 'word_images', 'kanji_words', 'examples',
        ]

# ---------------------------------------------------------------------------
# KANJI GET & UPDATE — basic fields only
# ---------------------------------------------------------------------------


class KanjiMeaningSerializer(serializers.ModelSerializer):
    language_name = serializers.CharField(
        source='language.name', read_only=True)

    class Meta:
        model = KanjiMeaning
        fields = ['id', 'language', 'language_name',
                  'meaning', 'created_at']
        read_only_fields = ['id', 'created_at']


class KanjiSerializer(serializers.ModelSerializer):
    level_name = serializers.CharField(source='level.name', read_only=True)

    meanings = KanjiMeaningSerializer(many=True, read_only=True)
    examples = ExampleSerializer(many=True, read_only=True)

    class Meta:
        model = Kanji
        fields = ['id', 'character', 'onyomi', 'kunyomi', 'stroke_count',
                  'level', 'level_name',
                  'meanings', 'examples',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at',
                            'meanings', 'examples']

# ---------------------------------------------------------------------------
# WORD Write Serializer — with nested meanings, pronunciations, and images
# ---------------------------------------------------------------------------


class WordMeaningWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordMeaning
        fields = ['language', 'short_definition', 'full_definition']


class WordPronunciationWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordPronunciation
        fields = ['type', 'pronunciation']


class WordImageWriteSerializer(serializers.Serializer):
    """get metadata after client upload to Cloudinary/S3."""
    file_url = serializers.URLField()
    file_path = serializers.CharField(
        help_text="public_id from Cloudinary or key from S3")
    file_name = serializers.CharField(max_length=255)
    mime_type = serializers.CharField(max_length=100)
    alt_text = serializers.CharField(
        max_length=255, required=False, allow_blank=True)
    file_size = serializers.IntegerField(required=False)


class ExampleWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Example
        fields = [
            'sentence', 'language',
            'translation', 'language_of_translation',
        ]


class KanjiWordWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = KanjiWord
        fields = ['kanji', 'position', 'reading_in_word']


class WordWriteSerializer(serializers.ModelSerializer):
    meanings = WordMeaningWriteSerializer(many=True, required=False)
    pronunciations = WordPronunciationWriteSerializer(
        many=True, required=False)
    word_images = WordImageWriteSerializer(many=True, required=False)
    examples = ExampleWriteSerializer(many=True, required=False)
    kanji_words = KanjiWordWriteSerializer(many=True, required=False)

    class Meta:
        model = Word
        fields = [
            'id', 'lemma', 'language', 'level', 'part_of_speech',
            'meanings', 'pronunciations', 'word_images',
            'examples', 'kanji_words',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        meanings_data = validated_data.pop('meanings', [])
        pronunciations_data = validated_data.pop('pronunciations', [])
        word_images_data = validated_data.pop('word_images', [])
        examples_data = validated_data.pop('examples', [])
        kanji_words_data = validated_data.pop('kanji_words', [])

        word = Word.objects.create(**validated_data)

        for item in meanings_data:
            WordMeaning.objects.create(word=word, **item)

        for item in pronunciations_data:
            WordPronunciation.objects.create(word=word, **item)

        for item in word_images_data:
            # Client đã upload lên Cloudinary/S3, chỉ cần lưu metadata
            media_file = MediaFile.objects.create(
                file_url=item['file_url'],
                file_path=item['file_path'],
                file_name=item['file_name'],
                mime_type=item['mime_type'],
                alt_text=item.get('alt_text', ''),
                file_size=item.get('file_size'),
                upload_by=self.context['request'].user,
            )
            WordImage.objects.create(word=word, media_file=media_file)

        for item in examples_data:
            Example.objects.create(word=word, **item)

        for item in kanji_words_data:
            KanjiWord.objects.create(word=word, **item)

        return word

# ----------------------------------------------------------------------------
# KANJI Write Serializer — with nested meanings and examples
# ----------------------------------------------------------------------------


class KanjiMeaningWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = KanjiMeaning
        fields = ['language', 'meaning']


class KanjiWriteSerializer(serializers.ModelSerializer):
    meanings = KanjiMeaningWriteSerializer(many=True, required=False)
    examples = ExampleWriteSerializer(many=True, required=False)

    class Meta:
        model = Kanji
        fields = ['id', 'character', 'onyomi', 'kunyomi', 'stroke_count', 'level',
                  'meanings', 'examples']
        read_only_fields = ['id']

    def create(self, validated_data):
        meanings_data = validated_data.pop('meanings', [])
        examples_data = validated_data.pop('examples', [])

        kanji = Kanji.objects.create(**validated_data)

        for item in meanings_data:
            KanjiMeaning.objects.create(kanji=kanji, **item)

        for item in examples_data:
            Example.objects.create(kanji=kanji, **item)

        return kanji

# ----------------------------------------------------------------------------
# KANJI AND WORD SERIALIZER for search realtime
# ----------------------------------------------------------------------------


class WordSuggestSerializer(serializers.ModelSerializer):
    language_name = serializers.CharField(
        source='language.name', read_only=True)
    part_of_speech_name = serializers.CharField(
        source='part_of_speech.name', read_only=True)
    short_definition = serializers.SerializerMethodField()

    class Meta:
        model = Word
        fields = ['id', 'lemma', 'language_name',
                  'part_of_speech_name', 'short_definition']

    def get_short_definition(self, obj):
        meanings = getattr(obj, 'filtered_meanings', None)
        if meanings:
            return meanings[0].short_definition

        request = self.context.get('request')

        # Ưu tiên native_language của user nếu đã đăng nhập
        lang = 'vi'  # fallback default
        if request and request.user.is_authenticated:
            try:
                native = request.user.userprofile.native_language
                if native:
                    lang = native.code
            except Exception:
                pass
        else:
            lang = request.query_params.get('language', 'vi') if request else 'vi'

        meaning = obj.meanings.filter(language__code=lang).first()
        return meaning.short_definition if meaning else None


class KanjiSuggestSerializer(serializers.ModelSerializer):
    level_name = serializers.CharField(source='level.name', read_only=True)
    short_meaning = serializers.SerializerMethodField()

    class Meta:
        model = Kanji
        fields = ['id', 'character', 'onyomi',
                  'kunyomi', 'level_name', 'short_meaning']

    def get_short_meaning(self, obj):
        meanings = getattr(obj, 'filtered_meanings', None)
        if meanings:
            return meanings[0].meaning
        
        request = self.context.get('request')
        lang = 'vi'  # fallback default
        if request and request.user.is_authenticated:
            try:
                native = request.user.userprofile.native_language
                if native:
                    lang = native.code
            except Exception:
                pass
        else:
            lang = request.query_params.get('language', 'vi') if request else 'vi'
        meaning = obj.meanings.filter(language__code=lang).first()
        return meaning.meaning if meaning else None

# ----------------------------------------------------------------------------
# USER PINNED WORD & SAVED WORD LIST
# ----------------------------------------------------------------------------


class UserPinnedWordSerializer(serializers.ModelSerializer):
    word_detail = WordSerializer(source="word", read_only=True)

    class Meta:
        model = UserPinnedWord
        fields = ["id", "word", "word_detail"]
        read_only_fields = ["id"]
        
class SavedWordListItemSerializer(serializers.ModelSerializer):
    word_id = serializers.IntegerField(source="word.id", read_only=True)
    lemma = serializers.CharField(source="word.lemma", read_only=True)
    language = serializers.CharField(source="word.language.name", read_only=True)

    class Meta:
        model = SavedWordListItem
        fields = ['id', 'word_id', 'lemma', 'language', 'position']
        read_only_fields = ['id', 'position']
        
class SavedWordListSerializer(serializers.ModelSerializer):
    items = SavedWordListItemSerializer(many=True, read_only=True)
    word_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SavedWordList
        fields = ['id', 'name', 'description', 'is_public', 'word_count', 'items', 'created_at']
        read_only_fields = ['id', 'created_at', 'word_count']
        
    @extend_schema_field(serializers.IntegerField())
    def get_word_count(self, obj) -> int:
        return obj.items.count()
        
class SavedWordListWriteSerializer(serializers.ModelSerializer):
    #For crud savedwordlist
    class Meta:
        model = SavedWordList
        fields = ['id', 'name', 'description', 'is_public']
        read_only_fields = ['id']

class PinWordSerializer(serializers.Serializer):
    # Use to pin word in WordViewSet
    # Able to add to already existed list or create a new list with name
    list_id = serializers.IntegerField(required =False)
    list_name = serializers.CharField(required = False, allow_blank=True)
    
    def validate(self, attrs):
        if not attrs.get('list_id') and not attrs.get('list_name', '').strip():
            pass
        # if doesn't have list_id or name, it's will automatically created list with the name "New List"
        return attrs
    
    
class WordAIRequestSerializer(serializers.Serializer):
    MODE_CHOICE = ['analyze', 'relations']
    
    mode = serializers.ChoiceField(
        choices = MODE_CHOICE,
        default = 'analyze',
        help_text = "analyze | relations",
    )
    
class KanjiAIRequestSerializer(serializers.Serializer):
    MODE_CHOICE = ['analyze', 'relations']
    
    mode = serializers.ChoiceField(
        choices = MODE_CHOICE,
        default = 'analyze',
        help_text = "analyze | relations",
    )