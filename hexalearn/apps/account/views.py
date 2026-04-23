from rest_framework import generics, permissions

from .docs import upload_credential_schema
from .serializers import UserSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

import hashlib
import time
import uuid
import cloudinary

from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
    
UPLOAD_FOLDER_MAP = {
    'flashcard': 'flashcard',
    'dict'     : 'dict/words',
    'reading'  : 'reading',
    'avatar'   : 'avatars', 
}

@upload_credential_schema()
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_upload_credential(request):
    file_name = request.query_params.get('file_name', 'image')
    app       = request.query_params.get('app', 'flashcard')

    folder = UPLOAD_FOLDER_MAP.get(app)
    if not folder:
        return Response(
            {"error": f"app '{app}' not available. Choose: {list(UPLOAD_FOLDER_MAP.keys())}"},
            status=400
        )

    timestamp = int(time.time())
    params    = f"folder={folder}&timestamp={timestamp}{cloudinary.config().api_secret}"
    signature = hashlib.sha1(params.encode()).hexdigest()

    return Response({
        "provider"  : "cloudinary",
        "signature" : signature,
        "timestamp" : timestamp,
        "folder"    : folder,
        "cloud_name": cloudinary.config().cloud_name,
        "api_key"   : cloudinary.config().api_key,
    })