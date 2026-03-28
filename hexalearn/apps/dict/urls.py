from django.urls import include, path
from rest_framework_nested import routers
from .views import (
    PartOfSpeechViewSet, WordViewSet, KanjiViewSet,
    WordMeaningViewSet, WordPronunciationViewSet,
    WordImageViewSet, WordExampleViewSet, WordKanjiWordViewSet,
    KanjiMeaningViewSet, KanjiExampleViewSet, SavedWordListViewSet
)

app_name = 'dict'
router = routers.DefaultRouter()
router.register(r'part-of-speech', PartOfSpeechViewSet, basename='part-of-speech')
router.register(r'words', WordViewSet, basename='word')
router.register(r'kanjis', KanjiViewSet, basename='kanji')
router.register(r'saved-word-lists', SavedWordListViewSet, basename='saved-word-list')

words_router = routers.NestedDefaultRouter(router, r'words', lookup='word')
words_router.register(r'meanings',       WordMeaningViewSet,       basename='word-meanings')
words_router.register(r'pronunciations', WordPronunciationViewSet,  basename='word-pronunciations')
words_router.register(r'images',         WordImageViewSet,          basename='word-images')
words_router.register(r'examples',       WordExampleViewSet,        basename='word-examples')
words_router.register(r'kanjis',         WordKanjiWordViewSet,      basename='word-kanjis')

kanjis_router = routers.NestedDefaultRouter(router, r'kanjis', lookup='kanji')
kanjis_router.register(r'meanings', KanjiMeaningViewSet, basename='kanji-meanings')
kanjis_router.register(r'examples', KanjiExampleViewSet, basename='kanji-examples')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/', include(words_router.urls)),
    path('v1/', include(kanjis_router.urls)),
]