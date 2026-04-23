from .base import *

import cloudinary

DEBUG = False
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=[])
ALLOWED_HOSTS += ['127.0.0.1', 'localhost']

DATABASES = {
    'default': env.db('DATABASE_URL')  # AWS RDS
}

CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS')

DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

cloudinary.config(
    cloud_name=env('CLOUDINARY_CLOUD_NAME'),
    api_key=env('CLOUDINARY_API_KEY'),
    api_secret=env('CLOUDINARY_API_SECRET'),
)

# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])
