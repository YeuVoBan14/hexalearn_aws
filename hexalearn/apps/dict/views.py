from django.shortcuts import render
from django.db.models import Prefetch
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.decorators import action
from django.db.models import Q
from rest_framework import viewsets, status

from .models import (Kanji, KanjiMeaning, PartOfSpeech, Word, WordMeaning, WordPronunciation, WordImage, KanjiWord, Example,
                     UserPinnedWord, SavedWordList, SavedWordListItem)
from apps.home.pagination import CustomPagination
from .serializers import (KanjiSerializer, KanjiSuggestSerializer, KanjiWriteSerializer, PartOfSpeechSerializer,
                        WordSerializer, WordSuggestSerializer, WordWriteSerializer,
                        WordMeaningWriteSerializer, WordMeaningSerializer,
                        WordPronunciationWriteSerializer, WordPronunciationSerializer,
                        WordImageWriteSerializer, WordImageSerializer,
                        ExampleWriteSerializer, ExampleSerializer,
                        KanjiWordWriteSerializer, KanjiWordInlineSerializer,
                        KanjiMeaningWriteSerializer, KanjiMeaningSerializer,
                        PinWordSerializer, SavedWordListWriteSerializer, SavedWordListSerializer,
                        ReorderItemSerializer)
from .docs import *
from apps.home.models import MediaFile
from apps.account.storage import delete_media_file, delete_media_files_bulk

# Create your views here.
@part_of_speech_schema()
class PartOfSpeechViewSet(viewsets.ModelViewSet):
    queryset = PartOfSpeech.objects.all()
    serializer_class = PartOfSpeechSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomPagination

@word_schema()
class WordViewSet(viewsets.ModelViewSet):
    http_method_names  = ['get', 'post', 'patch', 'delete', 'head', 'options']
    pagination_class   = CustomPagination

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]
    
    def get_queryset(self):
        return Word.objects.prefetch_related(
            'meanings', 'pronunciations', 'word_images__media_file',
            'kanji_words__kanji', 'examples'
        ).select_related('language', 'level', 'part_of_speech')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WordWriteSerializer
        return WordSerializer

    def create(self, request, *args, **kwargs):
        write_serializer = WordWriteSerializer(
            data=request.data,
            context=self.get_serializer_context()
        )
        write_serializer.is_valid(raise_exception=True)
        word = write_serializer.save()

        read_serializer = WordSerializer(
            word,
            context=self.get_serializer_context()
        )
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, *args, **kwargs):
        word = self.get_object()
        media_files = MediaFile.objects.filter(word_images__word=word)
 
        # Delete all files in cloud and related media files
        # WordImage will be automated deleted with Word (CASCADE)
        delete_media_files_bulk(media_files)
 
        word.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @word_suggest_schema()
    @action(detail=False, methods=['get'], url_path='suggest')
    def suggest(self, request):
        search = request.query_params.get('search', '').strip()
        lang   = request.query_params.get('language', 'vi')

        if len(search) < 1:
            return Response([])

        # Tìm word_id từ từng bảng riêng — nhẹ hơn nhiều so với JOIN
        from_lemma = Word.objects.filter(
            lemma__icontains=search
        ).values_list('id', flat=True)

        from_pronunciation = WordPronunciation.objects.filter(
            pronunciation__icontains=search
        ).values_list('word_id', flat=True)

        from_meaning = WordMeaning.objects.filter(
            short_definition__icontains=search
        ).values_list('word_id', flat=True)

        # Gộp ID, lấy tối đa 10
        word_ids = set(list(from_lemma[:10]) + list(from_pronunciation[:10]) + list(from_meaning[:10]))

        words = Word.objects.filter(
            id__in=word_ids
        ).select_related(
            'language', 'part_of_speech'
        ).prefetch_related(
            Prefetch(
                'meanings',
                queryset=WordMeaning.objects.filter(
                    language__code=lang
                ).select_related('language'),
                to_attr='filtered_meanings'
            )
        )[:10]

        serializer = WordSuggestSerializer(words, many=True, context={'request': request})
        return Response(serializer.data)

    @word_pin_schema()
    @action(detail = True, methods = ['post'], url_path='pin', permission_classes=[IsAuthenticated])
    def pin_word(self, request, *args, **kwargs):
        """
        POST /words/{id}/pin/
        BODY:
        - list_id (optional): add to an already existing list
        - list_name (optional): creating new list
        - (none of above): creating new list with name "New List"
        """
        word = self.get_object()
        
        serializer = PinWordSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        pinned_word, pin_created = UserPinnedWord.objects.get_or_create(
            user=request.user,
            word=word,
        )
        
        has_list_id   = 'list_id'   in data and data['list_id']
        has_list_name = 'list_name' in data
        
        if not has_list_id and not has_list_name:
            return Response({
                'pinned_word_id': pinned_word.id,
                'already_pinned': not pin_created,
            }, status=status.HTTP_200_OK if not pin_created else status.HTTP_201_CREATED)
        
        if has_list_id:
            try:
                saved_list = SavedWordList.objects.get(pk=data['list_id'], user=request.user)
            except SavedWordList.DoesNotExist:
                return Response(
                    {'detail': 'List not found or not belong to you'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            saved_list = SavedWordList.objects.create(
                user = request.user,
                name = data.get('list_name', ''),
            )
        
        item, created = SavedWordListItem.objects.get_or_create(
            list = saved_list,
            pinned_word = pinned_word
        )
        
        return Response({
            'pinned_word_id': pinned_word.id,
            'list_id':saved_list.id,
            'list_name':saved_list.name,
            'item_id':item.id,
            'position':item.position,
            'already_in_list': not created,
        }, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)
        
    @word_my_pinned_schema()
    @action(detail=False, methods=['get'], url_path='my-pinned', permission_classes=[IsAuthenticated])
    def my_pinned_words(self, request):
        """
        GET /words/my-pinned/
        """
        pinned_words = UserPinnedWord.objects.filter(
            user=request.user
        ).select_related(
            'word__language', 'word__part_of_speech'
        )

        words = [pw.word for pw in pinned_words]

        serializer = WordSerializer(words, many=True, context={'request': request})
        return Response(serializer.data)
@word_meaning_schema()
class WordMeaningViewSet(viewsets.ModelViewSet):
    """
    GET /words/{word_pk}/meanings/          - list of word meanings
    POST /words/{word__pk}/meanings/        - add new meanings
    PATCH /words/{word__pk}/meanings/{id}/  - edit meaning
    DELETE /words/{word_pk}/meanings{id}/   - delete meaning
    """
    lookup_value_regex = r'\d+'
    http_method_names  = ['get', 'post', 'patch', 'delete', 'head', 'options']
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomPagination
    
    def get_queryset(self):
        return WordMeaning.objects.filter(
            word_id=self.kwargs['word_pk']
        ).select_related('language')
        
    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return WordMeaningWriteSerializer
        return WordMeaningSerializer
    
    def perform_create(self, serializer):
        word = Word.objects.get(pk=self.kwargs['word_pk'])
        serializer.save(word=word)
        
@word_pronunciation_schema()
class WordPronunciationViewSet(viewsets.ModelViewSet):
    """
    GET    /words/{word_pk}/pronunciations/
    POST   /words/{word_pk}/pronunciations/
    PATCH  /words/{word_pk}/pronunciations/{id}/
    DELETE /words/{word_pk}/pronunciations/{id}/
    """
    lookup_value_regex = r'\d+'
    http_method_names  = ['get', 'post', 'patch', 'delete', 'head', 'options']
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomPagination

    def get_queryset(self):
        return WordPronunciation.objects.filter(word_id=self.kwargs['word_pk']).order_by('id')

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return WordPronunciationWriteSerializer
        return WordPronunciationSerializer

    def perform_create(self, serializer):
        word = Word.objects.get(pk=self.kwargs['word_pk'])
        serializer.save(word=word)
        
@word_image_schema()
class WordImageViewSet(viewsets.ModelViewSet):
    """
    GET    /words/{word_pk}/images/
    POST   /words/{word_pk}/images/        — nhận metadata Cloudinary/S3
    DELETE /words/{word_pk}/images/{id}/
    """
    lookup_value_regex = r'\d+'
    http_method_names  = ['get', 'post', 'delete', 'head', 'options']
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomPagination

    def get_queryset(self):
        return WordImage.objects.filter(
            word_id=self.kwargs['word_pk']
        ).select_related('media_file').order_by("id")

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WordImageWriteSerializer
        return WordImageSerializer

    def perform_create(self, serializer):
        word = Word.objects.get(pk=self.kwargs['word_pk'])
        data = serializer.validated_data
        media_file = MediaFile.objects.create(
            file_url  = data['file_url'],
            file_path = data['file_path'],
            file_name = data['file_name'],
            mime_type = data['mime_type'],
            alt_text  = data.get('alt_text', ''),
            file_size = data.get('file_size'),
            upload_by = self.request.user,
        )
        WordImage.objects.create(word=word, media_file=media_file)
        
    def destroy(self, request, *args, **kwargs):
        word_image = self.get_object()
        media_file = word_image.media_file
 
        word_image.delete()
 
        # Xóa file trên cloud + MediaFile trong DB
        delete_media_file(media_file)
 
        return Response(status=status.HTTP_204_NO_CONTENT)
        
@word_example_schema()
class WordExampleViewSet(viewsets.ModelViewSet):
    """
    GET    /words/{word_pk}/examples/
    POST   /words/{word_pk}/examples/
    PATCH  /words/{word_pk}/examples/{id}/
    DELETE /words/{word_pk}/examples/{id}/
    """
    lookup_value_regex = r'\d+'
    http_method_names  = ['get', 'post', 'patch', 'delete', 'head', 'options']
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        return Example.objects.filter(
            word_id=self.kwargs['word_pk']
        ).select_related('language', 'language_of_translation').order_by("id")

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return ExampleWriteSerializer
        return ExampleSerializer

    def perform_create(self, serializer):
        word = Word.objects.get(pk=self.kwargs['word_pk'])
        serializer.save(word=word)
        
@word_kanji_schema()
class WordKanjiWordViewSet(viewsets.ModelViewSet):
    """
    GET    /words/{word_pk}/kanjis/
    POST   /words/{word_pk}/kanjis/
    PATCH  /words/{word_pk}/kanjis/{id}/
    DELETE /words/{word_pk}/kanjis/{id}/
    """
    lookup_value_regex = r'\d+'
    http_method_names  = ['get', 'post', 'patch', 'delete', 'head', 'options']
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomPagination

    def get_queryset(self):
        return KanjiWord.objects.filter(
            word_id=self.kwargs['word_pk']
        ).select_related('kanji').order_by("id")

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return KanjiWordWriteSerializer
        return KanjiWordInlineSerializer

    def perform_create(self, serializer):
        word = Word.objects.get(pk=self.kwargs['word_pk'])
        serializer.save(word=word)

# ---------------------------------------------------------------------------
# KANJI VIEWSET
# ---------------------------------------------------------------------------
@kanji_schema()
class KanjiViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    pagination_class   = CustomPagination
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]
    def get_queryset(self):
        return Kanji.objects.prefetch_related(
            'meanings', 'examples'
        ).select_related('level').order_by("id")

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return KanjiWriteSerializer
        return KanjiSerializer

    @kanji_suggest_schema()
    @action(detail=False, methods=['get'], url_path='suggest')
    def suggest(self, request):
        search = request.query_params.get('search', '').strip()
        lang = request.query_param.get('language', 'vi')
        
        if len(search) < 1:
            return Response([])

        from_character = Kanji.object.filter(
            character__icontains = search
        ).value_list('id', flat = True)
        
        from_onyomi = Kanji.objects.filter(
            onyomi__icontains = search
        ).value_list('id', flat = True)
        
        from_kunyomi = Kanji.objects.filter(
            kunyomi__icontains=search
        ).values_list('id', flat=True)

        from_meaning = KanjiMeaning.objects.filter(
            meaning__icontains=search
        ).values_list('kanji_id', flat=True)
        
        kanji_ids = set(
            list(from_character[:10]) +
            list(from_onyomi[:10])    +
            list(from_kunyomi[:10])   +
            list(from_meaning[:10])
        )
        
        kanjis = Kanji.objects.filter(
            id__in=kanji_ids
        ).select_related(
            'level'
        ).prefetch_related(
            Prefetch(
                'meanings',
                queryset=KanjiMeaning.objects.filter(
                    language__code=lang
                ).select_related('language'),
                to_attr='filtered_meanings'
            )
        )[:10]

        serializer = KanjiSuggestSerializer(kanjis, many=True, context={'request': request})
        return Response(serializer.data)
    
@kanji_meaning_schema()
class KanjiMeaningViewSet(viewsets.ModelViewSet):
    """
    GET    /kanjis/{kanji_pk}/meanings/
    POST   /kanjis/{kanji_pk}/meanings/
    PATCH  /kanjis/{kanji_pk}/meanings/{id}/
    DELETE /kanjis/{kanji_pk}/meanings/{id}/
    """
    lookup_value_regex = r'\d+'
    http_method_names  = ['get', 'post', 'patch', 'delete', 'head', 'options']
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomPagination

    def get_queryset(self):
        return KanjiMeaning.objects.filter(
            kanji_id=self.kwargs['kanji_pk']
        ).select_related('language').order_by("id")

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return KanjiMeaningWriteSerializer
        return KanjiMeaningSerializer

    def perform_create(self, serializer):
        kanji = Kanji.objects.get(pk=self.kwargs['kanji_pk'])
        serializer.save(kanji=kanji)

@kanji_example_schema()
class KanjiExampleViewSet(viewsets.ModelViewSet):
    """
    GET    /kanjis/{kanji_pk}/examples/
    POST   /kanjis/{kanji_pk}/examples/
    PATCH  /kanjis/{kanji_pk}/examples/{id}/
    DELETE /kanjis/{kanji_pk}/examples/{id}/
    """
    lookup_value_regex = r'\d+'
    http_method_names  = ['get', 'post', 'patch', 'delete', 'head', 'options']
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomPagination

    def get_queryset(self):
        return Example.objects.filter(
            kanji_id=self.kwargs['kanji_pk']
        ).select_related('language', 'language_of_translation').order_by("id")

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return ExampleWriteSerializer
        return ExampleSerializer

    def perform_create(self, serializer):
        kanji = Kanji.objects.get(pk=self.kwargs['kanji_pk'])
        serializer.save(kanji=kanji)
        
@saved_word_list_schema()
class SavedWordListViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination
    
    def get_queryset(self):
        user = self.request.user
        
        if self.action in ['list', 'retrieve']:
            return SavedWordList.objects.filter(
                Q(user=user) | Q(is_public=True)
            ).prefetch_related('items__pinned_word__word__language').order_by('-created_at')
        return SavedWordList.objects.filter(user=user)
    
    def get_serializer(self, *args, **kwargs):
        if self.action in ['POST', 'PATCH']:
            return SavedWordListWriteSerializer
        return SavedWordListSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    @saved_word_list_schema()
    @action(detail=True, methods=['patch'], url_path='reorder')
    def reorder(self, request, *args, **kwargs):
        """
        PATCH /saved-word-lists/{id}/reorder/
        Body: [{"id": 1, "position": 1}, {"id": 2, "position": 2}, ...]
        """
        saved_list = self.get_object
        
        if saved_list.user != request.user:
            return Response(
                {'detail': 'You dont have permission to reorder this list'},
                status=status.HTTP_403_FORBIDDEN,
            )
            
        serializer = ReorderItemSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        items_data = serializer.validated_data
        
        items_ids = [i['id'] for i in items_data]
        existing_ids = set(SavedWordListItem.objects.filter(
            list = saved_list, pk__in=items_ids
        ).values_list('id', flat=True))
        
        invalid_ids = set(items_ids) - existing_ids
        if invalid_ids:
            return Response(
                {'detail': f'Items not found in this list: {list(invalid_ids)}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        for item_data in items_data:
            SavedWordListItem.objects.filter(
                pk=item_data['id'], list=saved_list
            ).update(position=item_data['position'])

        saved_list.refresh_from_db()
        return Response(
            SavedWordListSerializer(saved_list, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )
        
    @saved_word_list_remove_item_schema()
    @action(detail=True, methods=['delete'], url_path='items/(?P<item_pk>[^/.]+)')
    def remove_item(self, request, item_pk=None, *args, **kwargs):
        """
        DELETE /saved-word-lists/{id}/items/{item_pk}/
        Xóa từ khỏi list, không xóa pinned word.
        """
        saved_list = self.get_object()

        if saved_list.user != request.user:
            return Response(
                {'detail': 'You do not have permission to modify this list.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            item = SavedWordListItem.objects.get(pk=item_pk, list=saved_list)
        except SavedWordListItem.DoesNotExist:
            return Response({'detail': 'Item not found.'}, status=status.HTTP_404_NOT_FOUND)

        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
        
