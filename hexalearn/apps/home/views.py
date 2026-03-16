from django.shortcuts import render
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

from .models import Level, Source
from .serializers import LevelSerializer, RegisterSerializer, SourceSerializer, UserProfileSerializer
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
    
@user_profile_schema()
class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user.profile

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True,           # only update fields provided in the request
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@delete_account_schema()
def delete_account(request):
    profile = request.user.profile
    profile.is_deleted = True
    profile.save()
    return Response(
        {"detail": "Account has been deleted."},
        status=status.HTTP_200_OK
    )