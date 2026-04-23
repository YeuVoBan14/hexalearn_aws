from django.utils import timezone

from apps.account.storage import delete_media_file
from apps.dict.models import Word

from .models import Topic, Passage, Paragraph, ParagraphTranslation, ReadingNote, UserReadingProgress
from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import transaction
from drf_spectacular.utils import extend_schema_field, OpenApiTypes

from apps.home.models import Language, MediaFile

from .tasks import async_detect_paragraph, async_detect_passage
class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = '__all__'
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']
        
# ----------------------------------------------------------------------------
# READ NESTED PASSAGE, PARAGRAPH AND TRANSLATIONS
# ----------------------------------------------------------------------------

class UserReadingProgressReadSerializer(serializers.ModelSerializer):
    passage_title = serializers.CharField(source='passage.title', read_only=True)
    class Meta:
        model = UserReadingProgress
        fields = ['id','passage_title', 'status', 'percentage_read', 
                  'last_paragraph_index', 'last_read_at',
                  'complete_at']
        read_only_fields = fields

class ReadingNoteReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingNote
        fields = ['id', 'selected_text', 'note', 'created_at']

class ParagraphTranslationReadSerializer(serializers.ModelSerializer):
    language_code = serializers.CharField(source='language.code', read_only=True)
    language_name = serializers.CharField(source='language.name', read_only=True)
 
    class Meta:
        model  = ParagraphTranslation
        fields = ['id', 'language', 'language_code', 'language_name', 'translation', 'created_at']
        
class ParagraphReadSerializer(serializers.ModelSerializer):
    translations = ParagraphTranslationReadSerializer(many=True, read_only=True)
    image_url    = serializers.SerializerMethodField()
    notes        = serializers.SerializerMethodField()
    vocabulary = serializers.SerializerMethodField()
    class Meta:
        model  = Paragraph
        fields = [
            'id', 'index', 'content', 'note',
            'image_url', 'translations', 'notes',
            'vocabulary',
            'created_at', 'updated_at',
        ]
    @extend_schema_field(OpenApiTypes.URI)
    def get_image_url(self, obj) -> str | None:
        return obj.image_url
    
    @extend_schema_field(ReadingNoteReadSerializer(many=True))
    def get_notes(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return []
        qs = obj.user_notes.filter(user=request.user).order_by('created_at')
        return ReadingNoteReadSerializer(qs, many=True).data
    
    @extend_schema_field({
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "lemma": {"type": "string"},
            },
        },
    })
    def get_vocabulary(self, obj):
        return list(obj.vocabulary.values('id', 'lemma'))
 
class PassageReadSerializer(serializers.ModelSerializer):
    paragraphs    = ParagraphReadSerializer(many=True, read_only=True)
    language_name = serializers.CharField(source='language.name', read_only=True)
    level_name    = serializers.CharField(source='level.name',    read_only=True)
    topic_name    = serializers.CharField(source='topic.name',    read_only=True)
    image_url     = serializers.SerializerMethodField()
    reading_progress = serializers.SerializerMethodField()
 
    class Meta:
        model  = Passage
        fields = [
            'id', 'title', 'description',
            'language', 'language_name',
            'level', 'level_name',
            'topic', 'topic_name',
            'source', 'estimated_read_time',
            'reading_progress',
            'image_url', 'paragraphs',
            'created_at', 'updated_at',
        ]
 
    @extend_schema_field(OpenApiTypes.URI)
    def get_image_url(self, obj) -> str | None:
        return obj.image_url
    
    @extend_schema_field(UserReadingProgressReadSerializer(many=False))
    def get_reading_progress(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        progresses = getattr(obj, 'user_progresses', None)
        if progresses is not None:
            progress = progresses[0] if progresses else None
        else:
            progress = obj.user_reading_progresses.filter(user=request.user).first()
        if not progress:
            return None
        return UserReadingProgressReadSerializer(progress).data
   
# ----------------------------------------------------------------------------
# WRITE NESTED PASSAGE
# ---------------------------------------------------------------------------- 

class MediaFileWriteSerializer(serializers.Serializer):
    file_url  = serializers.CharField()
    file_path = serializers.CharField()
    file_name = serializers.CharField(max_length=255)
    mime_type = serializers.CharField(max_length=100)
    alt_text  = serializers.CharField(max_length=255, required=False, allow_blank=True)
    file_size = serializers.IntegerField(required=False, allow_null=True)
    
def _create_media_file(image_data: dict, request) -> MediaFile:
    """Tạo MediaFile record từ dict data."""
    return MediaFile.objects.create(
        file_url  = image_data['file_url'],
        file_path = image_data['file_path'],
        file_name = image_data['file_name'],
        mime_type = image_data['mime_type'],
        alt_text  = image_data.get('alt_text', ''),
        file_size = image_data.get('file_size'),
        upload_by = request.user if request and request.user.is_authenticated else None,
    )
    
def _delete_media_file_if_exists(media_file) -> None:
    """Xóa MediaFile record + file trên cloud nếu tồn tại."""
    if not media_file:
        return
    try:
        delete_media_file(media_file)
    except Exception:
        media_file.delete()

class ParagraphTranslationWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ParagraphTranslation
        fields = ['language', 'translation']

class ParagraphWriteSerializer(serializers.ModelSerializer):
    """
    Dùng cho standalone create/update paragraph.
    Nếu muốn tạo kèm translation:
        { "content": "...", "translation": { "language": 1, "translation": "..." } }
    """
    image = MediaFileWriteSerializer(required=False, allow_null=True, write_only=True)
    translation = ParagraphTranslationWriteSerializer(
        write_only=True, required=False, allow_null=True
    )
    
    class Meta:
        model  = Paragraph
        fields = ['image', 'content', 'note', 'translation']
        
    def create(self, validated_data):
        image_data       = validated_data.pop('image', None)
        translation_data = validated_data.pop('translation', None)
        request          = self.context.get('request')

        media_file = _create_media_file(image_data, request) if image_data else None
        paragraph = Paragraph.objects.create(**validated_data, image=media_file)

        # Tạo translation được cung cấp
        provided_language_id = None
        if translation_data:
            provided_language_id = translation_data['language'].pk
            ParagraphTranslation.objects.create(
                paragraph=paragraph,
                **translation_data,
            )

        # Tìm các language còn thiếu trong passage → tạo placeholder
        existing_languages = Language.objects.filter(
            paragraphtranslation__paragraph__passage=paragraph.passage
        ).distinct()

        for language in existing_languages:
            if language.pk == provided_language_id:
                continue
            ParagraphTranslation.objects.get_or_create(
                paragraph=paragraph,
                language=language,
                defaults={'translation': f"No translation in {language.name} yet"},
            )

        transaction.on_commit(
            lambda: async_detect_paragraph(paragraph.pk)
        )
        return paragraph

    def update(self, instance, validated_data):
        image_data = validated_data.pop('image', None)
        validated_data.pop('translation', None)
        request = self.context.get('request')
 
        content_changed = (
            'content' in validated_data and
            validated_data['content'] != instance.content
        )
 
        # image_data = None  → không đổi ảnh
        # image_data = {}    → gửi lên nhưng rỗng, bỏ qua
        # image_data = {...} → có data mới → xóa cũ, tạo mới
        if image_data:
            old_media  = instance.image
            instance.image = _create_media_file(image_data, request)
            _delete_media_file_if_exists(old_media)
 
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
 
        if content_changed:
            transaction.on_commit(
                lambda: async_detect_paragraph(instance.pk, replace=True)
            )
        return instance
    
class _ParagraphInPassageSerializer(serializers.ModelSerializer):
    """
    local serializer ussed for nested create paragraphs in passage.
    translation is only a string because the language is provided at the passage level.
    """
    image       = MediaFileWriteSerializer(required=False, allow_null=True, write_only=True)
    translation = serializers.CharField(write_only=True, required=False, allow_null=True)
 
    class Meta:
        model  = Paragraph
        fields = ['image', 'content', 'note', 'translation']
        
class PassageWriteSerializer(serializers.ModelSerializer):
    """
    - Obtain 'translation_language' at passsage level, apply to all paragraphs.
    - Which any paragraph has translation provided, it will be created. For those don't have, a placeholder will be created with "No translation in {language.name} yet".
    - Update only updates the basic information of the passage, not the paragraphs.
    """
    cover_image = MediaFileWriteSerializer(required=False, allow_null=True, write_only=True)
    paragraphs = _ParagraphInPassageSerializer(
        many=True, required=False, write_only=True
    )
    translation_language = serializers.PrimaryKeyRelatedField(
        queryset=Language.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    class Meta:
        model  = Passage
        fields = [
            'title', 'language', 'description', 'cover_image',
            'level', 'topic', 'source', 'estimated_read_time',
            'paragraphs', 'translation_language',
        ]
        
    @transaction.atomic
    def create(self, validated_data):
        cover_image_data     = validated_data.pop('cover_image', None)
        paragraphs_data      = validated_data.pop('paragraphs', [])
        translation_language = validated_data.pop('translation_language', None)
        request              = self.context.get('request')
 
        cover_media = _create_media_file(cover_image_data, request) if cover_image_data else None
        passage     = Passage.objects.create(**validated_data, cover_image=cover_media)
 
        for para_data in paragraphs_data:
            para_image_data  = para_data.pop('image', None)
            translation_text = para_data.pop('translation', None)
 
            para_media = _create_media_file(para_image_data, request) if para_image_data else None
            paragraph  = Paragraph.objects.create(passage=passage, image=para_media, **para_data)
 
            if translation_language:
                ParagraphTranslation.objects.create(
                    paragraph=paragraph,
                    language=translation_language,
                    translation=translation_text or f"No translation in {translation_language.name} yet",
                )
 
        if paragraphs_data:
            transaction.on_commit(
                lambda: async_detect_passage(passage.pk)
            )
 
        return passage
 
    @transaction.atomic
    def update(self, instance, validated_data):
        cover_image_data = validated_data.pop('cover_image', None)
        validated_data.pop('paragraphs', None)
        validated_data.pop('translation_language', None)
        request = self.context.get('request')
 
        if cover_image_data:
            old_cover        = instance.cover_image
            instance.cover_image = _create_media_file(cover_image_data, request)
            _delete_media_file_if_exists(old_cover)
 
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
            
        
# ----------------------------------------------------------------------------
# READING NOTE FOR WRITING
# ----------------------------------------------------------------------------  
      
class ReadingNoteWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingNote
        fields = ['selected_text', 'note']
        
    def validate_selected_text(self, value):
        paragraph = self.context.get('paragraph')
        if paragraph and value not in paragraph.content:
            raise serializers.ValidationError(
                "selected_text must be a substring of paragraph content."
            )
        return value

# ----------------------------------------------------------------------------
# USER READING PROGRESS FOR WRITING
# ----------------------------------------------------------------------------  

class UserReadingProgressWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = UserReadingProgress
        fields = ['last_paragraph_index', 'status', 'complete_at']
        extra_kwargs = {
            'status'      : {'required': False},
            'complete_at' : {'required': False},
        }
        
    def validate_last_paragraph_index(self, value):
        passage = self.context.get('passage')
        if passage:
            total = passage.paragraphs.count()
            if value < 1 or value > total:
                raise serializers.ValidationError(
                    f"last_paragraph_index must be between 1 and {total}."
                )
        return value
    
    def validate(self, attrs):
        passage = self.context.get('passage')
        index   = attrs.get('last_paragraph_index')

        if passage and index is not None:
            total = passage.paragraphs.count()
            if index >= total:
                attrs['status']      = 'finished'
                attrs['complete_at'] = timezone.now()  
            elif index >= 2:
                attrs['status'] = 'in_progress'
            else:
                attrs['status'] = 'started'

        return attrs
    
# ----------------------------------------------------------------------------
# AI REQUEST SERIALIZERS
# ----------------------------------------------------------------------------

class ReadingAIRequestSerializer(serializers.Serializer):
    #Serializer for AI requests, explain/summarize/vocabulary
    MODE_CHOICES = ['explain', 'summarize', 'vocabulary']
    
    mode = serializers.ChoiceField(
        choices=MODE_CHOICES,
        default='explain',
        help_text="Mode of AI request: explain, summarize, or vocabulary"
        )
    
    selected_text = serializers.CharField(
        required=False, allow_blank=True,
        allow_null=True,
        help_text="The specific text the user wants explained. Optional for summarize modes."
    )
    
    def validate(self, attrs):
        mode = attrs.get('mode')
        selected_text = attrs.get('selected_text', '').strip()
        
        if mode == 'explain' and not selected_text:
            raise serializers.ValidationError({
                'selected_text': '`selected_text` is required for explain mode.'
            })
        return attrs