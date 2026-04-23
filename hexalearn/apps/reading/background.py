"""
background.py — Thay thế Celery bằng Django threading cho AWS Free Tier.

Dùng cho các fire-and-forget tasks nhẹ như detect vocabulary.
Không cần retry/scheduling → threading.Thread là đủ.
"""

import threading
import logging

logger = logging.getLogger(__name__)


def run_in_background(func, *args, **kwargs):
    """
    Chạy func trong background thread — non-blocking.

    Usage:
        run_in_background(detect_vocabulary_for_passage, passage, replace=True)

    Notes:
        - daemon=True: thread tự kết thúc khi main process exit
        - Không có retry — nếu cần retry, dùng Huey hoặc Django-Q
    """
    def _wrapper():
        try:
            func(*args, **kwargs)
        except Exception as e:
            logger.exception(
                "Background task %s failed: %s", func.__name__, e
            )

    thread = threading.Thread(target=_wrapper, daemon=True)
    thread.start()
    logger.info("Background task started: %s", func.__name__)