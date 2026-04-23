#!/bin/sh
set -e

cd /app
python manage.py collectstatic --noinput || true
python manage.py migrate --noinput || true

# t2.micro: 1 vCPU, 1GB RAM
# Công thức chuẩn: 2×CPU+1 = 3 workers, nhưng với 1GB RAM
# mỗi Gunicorn worker ~100-150MB → 2 workers an toàn hơn
exec python -m gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --worker-class sync \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    hexalearn.wsgi:application