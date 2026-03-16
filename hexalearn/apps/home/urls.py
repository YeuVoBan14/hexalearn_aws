from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.home.views import LevelViewSet, SourceViewSet, UserProfileView, RegisterView, delete_account

router = DefaultRouter()
app_name = 'home'

router.register('levels', LevelViewSet, basename='level')
router.register('sources', SourceViewSet, basename='source')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('register/',RegisterView.as_view(),name='register'),
    path('profile/',UserProfileView.as_view(),name='profile'),
    path('delete-account/', delete_account,name='delete-account'),
]