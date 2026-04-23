from django.shortcuts import get_object_or_404, render
from django.db.models import Q, F, Prefetch
from django.db import transaction

from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.http import StreamingHttpResponse


from .ai_client import stream_gemini_response

from .serializers import (ReadingNoteReadSerializer, ReadingNoteWriteSerializer, TopicSerializer, PassageWriteSerializer, PassageReadSerializer,
                          ParagraphWriteSerializer, ParagraphReadSerializer,
                          ParagraphTranslationReadSerializer, ParagraphTranslationWriteSerializer, UserReadingProgressReadSerializer, UserReadingProgressWriteSerializer,
                          ReadingAIRequestSerializer)
from .serializers import _delete_media_file_if_exists

from .models import ReadingNote, Topic, Passage, Paragraph, ParagraphTranslation, UserReadingProgress
from .docs import *

from apps.home.pagination import CustomPagination
from apps.home.models import Language
from .tasks import async_detect_passage
import logging
from .ai_prompts import build_explain_prompt, build_summarize_prompt, build_vocabulary_prompt
# Create your views here.


@topic_schema
class TopicViewSet(viewsets.ModelViewSet):
    serializer_class = TopicSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]

    def get_queryset(self):
        queryset = Topic.objects.order_by('-created_at')

        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search)
            )

        return queryset


@passage_schema
class PassageViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return PassageWriteSerializer
        return PassageReadSerializer

    def get_queryset(self):
        filters = Q()

        search = self.request.query_params.get('search', '').strip()
        language = self.request.query_params.get('language')
        level = self.request.query_params.get('level')
        topic = self.request.query_params.get('topic')
        estimated_read_time = self.request.query_params.get(
            'estimated_read_time')

        if search:
            filters &= Q(title__icontains=search) | Q(
                description__icontains=search)
        if language:
            filters &= Q(language__code=language)
        if level:
            filters &= Q(level__code=level)
        if topic:
            filters &= Q(topic__code=topic)
        if estimated_read_time:
            filters &= Q(estimated_read_time__lte=estimated_read_time)
        progress_prefetch = Prefetch(
            'user_reading_progresses',
            queryset=UserReadingProgress.objects.filter(
                user=self.request.user
            ) if self.request.user.is_authenticated else UserReadingProgress.objects.none(),
            to_attr='user_progresses',
        )
        return (
            Passage.objects
            .select_related('language', 'level', 'topic', 'source')
            .prefetch_related('paragraphs__translations__language', progress_prefetch)
            .filter(filters)
            .order_by('-created_at')
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        passage = serializer.save()
        return Response(
            PassageReadSerializer(passage).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)
        passage = serializer.save()
        return Response(PassageReadSerializer(passage).data)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        passage = self.get_object()

        media_to_delete = []
        if passage.cover_image:
            media_to_delete.append(passage.cover_image)

        para_images = [
            p.image for p in passage.paragraphs.select_related('image').all()
            if p.image
        ]

        media_to_delete.extend(para_images)

        passage.delete()

        for media in media_to_delete:
            _delete_media_file_if_exists(media)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @detect_vocabulary_schema
    @action(detail=True, methods=['post'], url_path='detect_vocabulary',
            permission_classes=[IsAuthenticated, IsAdminUser])
    def detect_vocabulary(self, request, pk=None):
        """Run vocabulary detection for all paragraphs in the passage. If 'replace' is true, it will replace the existing detected vocabulary."""
        passage = self.get_object()
        replace = request.data.get('replace', False)

        transaction.on_commit(
            lambda: async_detect_passage(passage.pk, replace=replace)
        )
        return Response(
            {'detail': f'Vocabulary detection started for passage #{passage.pk}.'},
            status=status.HTTP_202_ACCEPTED,
        )

    @add_translation_schema
    @action(detail=True, methods=['post'], url_path='add_translation',
            permission_classes=[IsAuthenticated, IsAdminUser])
    @transaction.atomic
    def add_translation(self, request, pk=None):
        """
        Thêm bản dịch cho toàn bộ paragraphs trong passage.

        Body:
        {
            "translation_language": <language_id>,
            "translations": [
                {"index": 1, "translation": "..."},
                {"index": 3, "translation": "..."}
            ]
        }

        - Paragraph nào có index trong `translations` → dùng text đó.
        - Paragraph nào không có trong list → placeholder tự động.
        - Nếu translation cho language đó đã tồn tại → update.
        """
        passage = self.get_object()
        language_id = request.data.get('translation_language')
        translations_in = request.data.get('translations', [])

        if not language_id:
            return Response(
                {'detail': '`translation_language` is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        language = get_object_or_404(Language, pk=language_id)

        # Build map { index → translation_text }
        translation_map = {
            item['index']: item.get('translation', '').strip()
            for item in translations_in
            if 'index' in item
        }

        paragraphs = passage.paragraphs.all()
        updated = created = 0

        for paragraph in paragraphs:
            text = translation_map.get(
                paragraph.index) or f"No translation in {language.name} yet"
            _, is_created = ParagraphTranslation.objects.update_or_create(
                paragraph=paragraph,
                language=language,
                defaults={'translation': text},
            )
            if is_created:
                created += 1
            else:
                updated += 1

        return Response({
            'detail': f'Done for passage #{passage.pk}.',
            'created': created,
            'updated': updated,
        })

    @remove_language_translation_schema
    @action(
        detail=True, methods=['delete'], url_path=r'translations/(?P<language_id>[^/.]+)',
        permission_classes=[IsAuthenticated, IsAdminUser],)
    def remove_language_translation(self, request, pk=None, language_id=None):
        """
        Xoá toàn bộ translations của một language khỏi passage.
        Ví dụ: xoá toàn bộ bản dịch tiếng Việt của passage này.
        """
        passage = self.get_object()
        language = get_object_or_404(Language, pk=language_id)

        deleted_count, _ = ParagraphTranslation.objects.filter(
            paragraph__passage=passage,
            language=language,
        ).delete()

        return Response({
            'detail': f'Removed all {language.name} translations from passage #{passage.pk}.',
            'deleted': deleted_count,
        })


@paragraph_schema
class ParagraphViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return ParagraphWriteSerializer
        return ParagraphReadSerializer

    def get_passage(self):
        return get_object_or_404(Passage, pk=self.kwargs['passage_pk'])

    def get_queryset(self):
        passage = self.get_passage()
        return (
            Paragraph.objects
            .filter(passage=passage)
            .prefetch_related(
                'translations__language',
                'vocabulary',
            )
            .order_by('index')
        )

    def perform_create(self, serializer):
        serializer.save(passage=self.get_passage())

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            ParagraphReadSerializer(serializer.instance).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ParagraphReadSerializer(instance).data)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """
        When delete a paragraph, we need to update the index of the following paragraphs to maintain the correct order.
        Example: [1,2,,3,4], delete index 2 -> [1,2,3]
        """
        paragraph = self.get_object()
        passage = paragraph.passage
        deleted_index = paragraph.index
        old_image = paragraph.image

        paragraph.delete()

        Paragraph.objects.filter(
            passage=passage,
            index__gt=deleted_index,
        ).update(index=F('index') - 1)

        _delete_media_file_if_exists(old_image)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @reorder_schema
    @action(detail=True, methods=['post'], url_path='reorder', permission_classes=[IsAuthenticated, IsAdminUser])
    def reorder(self, request, passage_pk=None, pk=None):
        """Reorder paragraph within the passage. The request body should contain the new index for the paragraph.   
        Example: { "new_index": 2 }
        [1,2,3,4,5], reorder index 1 to index 3
        -Paragraph 2, 3 move up to index 1, 2
        -Paragraph 1 move to index 3
        Result: [2,3,1,4,5] following the new content but the index is [1,2,3,4,5]
        """

        new_index = int(request.data.get('new_index'))
        paragraph = self.get_object()
        passage = paragraph.passage
        old_index = paragraph.index

        if new_index == old_index:
            return Response(ParagraphReadSerializer(paragraph).data)

        total = Paragraph.objects.filter(passage=passage).count()
        if not (1 <= new_index <= total):
            return Response({'detail': f'new_index must be 1-{total}'}, status=400)

        with transaction.atomic():
            # BƯỚC 1: Dọn chỗ cũ - shift ngược về
            paragraph.index = 0  # Tạm set index về 0 để tránh xung đột unique constraint
            paragraph.save()
            if new_index > old_index:
                # Di chuyển từ old+1 đến new_index xuống 1
                paragraphs_to_shift = Paragraph.objects.filter(
                    passage=passage,
                    index__lte=new_index,
                    index__gt=old_index
                ).order_by('index')

                for p in paragraphs_to_shift:
                    p.index -= 1
                    p.save()
            else:
                # Di chuyển từ new_index đến old-1 lên 1
                paragraphs_to_shift = Paragraph.objects.filter(
                    passage=passage,
                    index__gte=new_index,
                    index__lt=old_index,
                ).order_by('-index')  # 4, 3 — lớn trước

                for p in paragraphs_to_shift:
                    p.index += 1
                    p.save()

            # BƯỚC 2: Set index mới cho paragraph (KHÔNG set = 0 nữa)
            paragraph.index = new_index
            paragraph.save()

        return Response(ParagraphReadSerializer(paragraph).data)

    @translations_list_schema
    @action(detail=True, methods=['get'], url_path='translations')
    def translations_list(self, request, passage_pk=None, pk=None):
        """List all translations of the paragraph."""
        paragraph = self.get_object()
        qs = ParagraphTranslation.objects.filter(
            paragraph=paragraph
        ).select_related('language')

        return Response(ParagraphTranslationReadSerializer(qs, many=True).data)

    @translation_update_schema
    @action(detail=True, methods=['patch'], url_path=r'translations/(?P<translation_pk>[^/.]+)/update')
    def translation_update(self, request, passage_pk=None, pk=None, translation_pk=None):
        """PATCH — edit a translation."""
        paragraph = self.get_object()
        translation = get_object_or_404(
            ParagraphTranslation, pk=translation_pk, paragraph=paragraph
        )
        serializer = ParagraphTranslationWriteSerializer(
            translation, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ParagraphTranslationReadSerializer(translation).data)

    @translation_delete_schema
    @action(detail=True, methods=['delete'],
            url_path=r'translations/(?P<translation_pk>[^/.]+)',)
    def translation_delete(self, request, passage_pk=None, pk=None, translation_pk=None):
        """Reset a translation to its default value."""
        paragraph = self.get_object()
        translation = get_object_or_404(
            ParagraphTranslation, pk=translation_pk, paragraph=paragraph
        )
        translation.translation = f"No translation in {translation.language.name} yet"
        translation.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @reading_ai_schema
    @action(detail=True, methods=['post'], url_path='ai', permission_classes=[IsAuthenticated],)
    def ai_explain(self, request, passage_pk=None, pk=None):
        """
        POST /passages/{pid}/paragraphs/{id}/ai/
    
        Stream AI response về client theo chuẩn SSE (Server-Sent Events).
    
        Body:
        {
            "mode": "explain" | "summarize" | "vocabulary",
            "selected_text": "食べます"   ← optional
        }
    
        Response: text/event-stream
            data: chunk1
            data: chunk2
            ...
            data: [DONE]
        """
        # ── Check user profile ─────────────────────────────────────────────
        try:
            profile = request.user.profile
        except Exception:
            return Response(
            {'detail': 'User profile not found.'}, status=status.HTTP_400_BAD_REQUEST,)
            
        if profile.daily_ai_limit <= 0:
            return Response(
                {
                    'detail': 'Daily AI limit reached. Resets at midnight UTC.',
                    'daily_ai_limit': 0,
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
            
        # ── Validate request body ─────────────────────────────────────────────
        serializer = ReadingAIRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        mode          = serializer.validated_data['mode']
        selected_text = serializer.validated_data.get('selected_text', '').strip()
        
        # ── Get paragraph and validate selected text ─────────────────────────────────────────────
        paragraph = self.get_object()
        if selected_text and selected_text not in paragraph.content:
            return Response(
                {'detail': 'selected_text must be a substring of the paragraph content.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        # ── Build prompt based on mode ─────────────────────────────────────────────
        if mode == 'explain':
            user_prompt = build_explain_prompt(
                paragraph, selected_text, request.user
            )
        elif mode == 'summarize':
            user_prompt = build_summarize_prompt(
                paragraph, request.user
            )
        else:  # vocabulary
            user_prompt = build_vocabulary_prompt(
                paragraph, selected_text, request.user
            )
            
        # ── Stream response from Gemini API ─────────────────────────────────────────────
        def generate():
            """
            Generator cho StreamingHttpResponse.
            Format SSE: mỗi chunk là "data: <text>\n\n"
            Client parse bằng cách split theo "\n\n" và remove "data: " prefix.
            """
            try:
                for chunk in stream_gemini_response(user_prompt):
                    safe_chunk = chunk.replace('\n', '\\n')
                    yield f"data: {safe_chunk}\n\n"
                    
                yield "data: [DONE]\n\n"
                
                profile.daily_ai_limit = max(0, profile.daily_ai_limit - 1)
                profile.save(update_fields=['daily_ai_limit'])
                
            except Exception as e:

                logging.getLogger(__name__).error("AI stream error: %s", e)
                yield f"data: [ERROR] {str(e)}\n\n"
        response = StreamingHttpResponse(
            generate(),
            content_type = 'text/event-stream',
        )
        
        response['Cache-Control']       = 'no-cache'
        response['X-Accel-Buffering']   = 'no'  # tắt nginx buffering
        response['Access-Control-Allow-Origin'] = '*'
    
        # Trả về remaining limit trong header để client biết
        response['X-AI-Limit-Remaining'] = str(profile.daily_ai_limit - 1)
    
        return response
                    
@reading_note_schema
class ReadingNoteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    
    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return ReadingNoteWriteSerializer
        return ReadingNoteReadSerializer
    
    def get_paragraph(self):
        return get_object_or_404(
            Paragraph, 
            pk=self.kwargs['paragraph_pk'],
            passage_id=self.kwargs['passage_pk']
        )
        
    def get_queryset(self):
        return ReadingNote.objects.filter(
            paragraph=self.get_paragraph(),
            user=self.request.user,
        ).order_by('created_at')
        
    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        # Truyền paragraph vào context để validate selected_text
        if not getattr(self, 'swagger_fake_view', False):
            ctx['paragraph'] = self.get_paragraph()
        return ctx
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user, paragraph=self.get_paragraph())
        
    def get_object(self):
        return get_object_or_404(
            ReadingNote,
            pk=self.kwargs['pk'],
            paragraph=self.get_paragraph(),
            user=self.request.user,
        )
@reading_progress_schema
class UserReadingProgressViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_passage(self):
        return get_object_or_404(Passage, pk=self.kwargs['passage_pk'])
    
    def get_queryset(self):
        return UserReadingProgress.objects.filter(
            user = self.request.user,
            passage = self.get_passage(),
        ).select_related('passage')
        
    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return UserReadingProgressWriteSerializer
        return UserReadingProgressReadSerializer
        
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['passage'] = self.get_passage()
        return context
    
    def get_object(self):
        passage = self.get_passage()
        return get_object_or_404(
            UserReadingProgress,
            user=self.request.user,
            passage=passage,
        )
        
    def perform_create(self, serializer):
        serializer.save(user=self.request.user, passage=self.get_passage(), status='started',)
        
    def partial_update(self, request, *args, **kwargs):
        passage = self.get_passage()
        progress, _ = UserReadingProgress.objects.get_or_create(
            user = self.request.user,
            passage = passage,
            defaults={'status': 'started', 'percentage_read': 0, 'last_paragraph_index': 1},
        )
        serializer = self.get_serializer(progress, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserReadingProgressReadSerializer(progress).data)
        
    