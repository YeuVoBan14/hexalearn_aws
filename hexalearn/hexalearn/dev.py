from .base import *
import cloudinary
DEBUG = True
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': env.db('DATABASE_URL')  #avien
}

CORS_ALLOW_ALL_ORIGINS = True

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
cloudinary.config(
    cloud_name=env('CLOUDINARY_CLOUD_NAME'),
    api_key=env('CLOUDINARY_API_KEY'),
    api_secret=env('CLOUDINARY_API_SECRET'),
)