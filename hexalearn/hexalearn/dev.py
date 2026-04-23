from .base import *
import cloudinary
DEBUG = True
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': env.db('DATABASE_URL')  #avien
}

CORS_ALLOW_ALL_ORIGINS = True

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

cloudinary.config(
    cloud_name=env('CLOUDINARY_CLOUD_NAME'),
    api_key=env('CLOUDINARY_API_KEY'),
    api_secret=env('CLOUDINARY_API_SECRET'),
)

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    'http://localhost:8001',
    'http://127.0.0.1:8001',
]