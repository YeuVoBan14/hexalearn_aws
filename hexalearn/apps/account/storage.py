"""
storage.py — Helper xóa file trên Cloudinary hoặc S3.

Tự động detect backend dựa vào settings.STORAGES['default']['BACKEND'].
Dùng chung cho WordViewSet, WordImageViewSet, và bất kỳ app nào khác sau này.

Usage:
    from .storage import delete_media_file

    delete_media_file(media_file)          # xóa trên cloud + xóa DB
    delete_media_file(media_file, db=False) # chỉ xóa trên cloud, không xóa DB
"""

import logging
import cloudinary.uploader

from django.conf import settings

logger = logging.getLogger(__name__)


def delete_from_cloud(file_path: str) -> None:
    try:
        result = cloudinary.uploader.destroy(file_path)
        if result.get('result') != 'ok':
            logger.warning("Cloudinary delete non-ok for '%s': %s", file_path, result)
    except Exception as e:
        logger.warning("Failed to delete '%s' from Cloudinary: %s", file_path, e)


def delete_media_file(media_file, db: bool = True) -> None:
    """
    Xóa file trên cloud và (tùy chọn) xóa MediaFile khỏi DB.

    Args:
        media_file: instance MediaFile cần xóa.
        db:         nếu True (mặc định), xóa luôn record trong DB sau khi xóa cloud.
    """
    delete_from_cloud(media_file.file_path)
    if db:
        media_file.delete()


def delete_media_files_bulk(media_files, db: bool = True) -> None:
    """
    Xóa nhiều MediaFile cùng lúc.
    Dùng khi xóa Word (cần xóa hết ảnh liên quan).

    Args:
        media_files: queryset hoặc list của MediaFile.
        db:          nếu True, xóa hết record trong DB sau khi xóa cloud.
    """
    # Ép về list để tránh queryset bị evaluate lại sau khi DB xóa
    files = list(media_files)
    for media_file in files:
        delete_from_cloud(media_file.file_path)
    if db:
        ids = [f.pk for f in files]
        from apps.home.models import MediaFile as MediaFileModel
        MediaFileModel.objects.filter(pk__in=ids).delete()