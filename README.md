# 🟣 HexaLearn AWS — Lightweight Deployment Version

This is the **AWS Free Tier optimized** version of HexaLearn.  
The main difference from the full version: **Celery + Redis replaced by Python daemon threading** to reduce RAM usage by ~200MB.

**Live demo:** [hexalearn.ddns.net](http://hexalearn.ddns.net)  
**Full version:** [github.com/yourusername/hexalearn](https://github.com/YeuVoBan14/HexaLearn)

---

##  Differences from Full Version

| | Full Version | AWS Version (this repo) |
|---|---|---|
| Background tasks | Celery + Redis | Python `threading.Thread` |
| Docker services | 3 (app + celery + redis) | 2 (app + nginx) |
| RAM usage | ~500MB+ | ~300MB |
| Target | Development / VPS | AWS EC2 t2.micro (1GB RAM) |

---

## Quick Start

### 1. Clone & setup `.env`

```bash
git clone https://github.com/yourusername/hexalearn-aws.git
cd hexalearn-aws
cp .env.example .env
# Fill in your values in .env
```

### 2. `.env` required variables

```env
SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=postgres://user:password@host:5432/hexalearn
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
GEMINI_API_KEY=your-gemini-api-key
DJANGO_ALLOWED_HOSTS=your-domain.com,your-ec2-ip
CORS_ALLOWED_ORIGINS=http://your-domain.com
CSRF_TRUSTED_ORIGINS=http://your-domain.com
```

### 3. Build & run

```bash
docker compose build --no-cache
docker compose up -d
```

### 4. Access

| URL | Description |
|---|---|
| `http://your-domain.com/` | Swagger UI |
| `http://your-domain.com/admin/` | Django Admin |
| `http://your-domain.com/redoc/` | ReDoc |

---

## 🏗 Docker Services

```
hexalearn_aws        Django + Gunicorn (2 workers, port 8000 internal)
hexalearn_aws_nginx  Nginx Alpine reverse proxy (port 80 public)
```

> Gunicorn runs with `--max-requests 1000` to auto-restart workers and prevent memory leaks on long-running instances.

---

## Tech Stack

Python · Django 6 · PostgreSQL · Google Gemini AI · Fugashi NLP · Cloudinary · Docker · Nginx · AWS EC2
