from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Level, Source
from .serializers import LevelSerializer, SourceSerializer
from .docs import *
from .pagination import CustomPagination

# Create your views here.
@level_schema()
class LevelViewSet(viewsets.ModelViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomPagination

@source_schema()
class SourceViewSet(viewsets.ModelViewSet):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomPagination
    