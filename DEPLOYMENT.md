# AI Money Manager - Production Deployment Guide

## Overview

This guide covers deploying the AI Money Manager application in production environments. The stack consists of:
- **Backend**: FastAPI + SQLAlchemy + SQLite/PostgreSQL
- **Frontend**: React + Vite (served via Nginx)
- **AI**: Groq API (llama-3.3-70b-versatile)
- **Auth**: JWT + bcrypt + OAuth2
- **Rate Limiting**: slowapi (memory-backed, Redis-ready)
- **Email**: SMTP (Gmail, SendGrid, etc.) — logs to console in dev
- **Error Tracking**: Sentry (production only)
- **HTTPS**: Caddy reverse proxy with auto SSL

---

## Prerequisites

- Docker & Docker Compose
- Git
- Groq API key (get from https://console.groq.com)
- Domain name (for production HTTPS)
- SMTP credentials (for production email)

---

## 1. Environment Setup

### Copy environment template

```bash
cp .env.example .env
```

### Edit `.env` with real values

```bash
# Environment: development | production
ENV=production

# Backend
SECRET_KEY=your-super-secret-32-char-key-here
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxx
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Database (PostgreSQL recommended for production)
DATABASE_URL=postgresql://aimoney:aimoney_pass@postgres:5432/aimoney

# Admin (change before first deploy!)
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=YourStrongAdminPassword123

# Frontend
VITE_API_URL=https://api.yourdomain.com
FRONTEND_URL=https://yourdomain.com

# SMTP Email (required in production)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@yourdomain.com

# Error Tracking (optional)
SENTRY_DSN=https://xxx@yyy.ingest.sentry.io/zzz
```

**Security checklist:**
- [ ] `ENV=production` set
- [ ] `SECRET_KEY` is 32+ random characters
- [ ] `ADMIN_PASSWORD` is strong and changed from default
- [ ] `GROQ_API_KEY` is not committed to Git
- [ ] `.env` is in `.gitignore`
- [ ] `CORS_ORIGINS` does NOT include `*` in production
- [ ] `DATABASE_URL` uses PostgreSQL for production
- [ ] `SMTP_*` credentials are configured for real email
- [ ] `SENTRY_DSN` configured for error tracking

---

## 2. Docker Deployment (Recommended)

### With SQLite (development / small deployments)

```bash
docker-compose up --build -d
```

### With PostgreSQL (production)

1. Uncomment the `postgres` service in `docker-compose.yml`
2. Uncomment the `postgres_data` volume
3. Set `DATABASE_URL=postgresql://aimoney:aimoney_pass@postgres:5432/aimoney` in `.env`
4. Deploy:

```bash
docker-compose up --build -d
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| Backend | 8000 | FastAPI API server |
| Frontend | 80 | Nginx static server |
| PostgreSQL | 5432 | (optional) PostgreSQL database |

### Verify deployment

```bash
# Backend health check
curl http://localhost:8000/health

# API docs (development only — hidden in production)
open http://localhost:8000/docs
```

### Database persistence

- **SQLite**: Stored in `./backend/data/` and mounted as a Docker volume
- **PostgreSQL**: Data stored in `postgres_data` Docker volume

---

## 3. HTTPS with Caddy (Production)

Caddy automatically handles SSL certificates via Let's Encrypt.

### Update Caddyfile

Replace `yourdomain.com` with your actual domain in `Caddyfile`.

### Run Caddy

```bash
# Install Caddy first: https://caddyserver.com/docs/install
caddy run
```

Or use Docker:

```bash
docker run -d -p 443:443 -p 80:80 \
  -v $(pwd)/Caddyfile:/etc/caddy/Caddyfile \
  -v caddy_data:/data \
  caddy:2-alpine
```

---

## 4. Local Development (Without Docker)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
# Use SQLite for local dev
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
# For local dev (points to localhost:8000)
npm run dev
# For production build test
VITE_API_URL=http://localhost:8000 npm run build
```

---

## 5. Production Checklist

### Security
- [ ] `ENV=production` set
- [ ] Change default admin credentials
- [ ] Use HTTPS for all traffic (Caddy/Nginx/Traefik)
- [ ] Set strong `SECRET_KEY`
- [ ] Restrict `CORS_ORIGINS` to your domain only
- [ ] Enable firewall (only expose 443, not 8000 directly)
- [ ] Use reverse proxy with SSL
- [ ] Set up log rotation
- [ ] API docs are hidden in production (`docs_url=None`)
- [ ] Password reset emails are sent (not returned in API response)
- [ ] Rate limiting enabled on auth and AI endpoints

### Performance
- [ ] Use PostgreSQL instead of SQLite for high traffic
- [ ] Add Redis for rate limiting storage (replace memory backend)
- [ ] Enable CDN for static assets
- [ ] Add database connection pooling (handled automatically for PostgreSQL)

### Monitoring
- [ ] Set up health check endpoint monitoring (`/health`)
- [ ] Configure Sentry error tracking (`SENTRY_DSN`)
- [ ] Configure log aggregation
- [ ] Monitor Groq API rate limits and costs

---

## 6. Database Migration

Migrations run automatically on startup via the lifespan event. For manual migration:

```bash
cd backend
python -c "from migrate import migrate; migrate()"
```

**Caution**: The migration script rebuilds tables if columns are missing. Back up your database before running on production data.

### PostgreSQL Migration

If switching from SQLite to PostgreSQL:

1. Export SQLite data: `sqlite3 ai_money_manager.db .dump > backup.sql`
2. Start PostgreSQL container
3. Run `Base.metadata.create_all()` to create tables
4. Import data (may need manual transformation)

---

## 7. Admin Access

The first startup creates an admin user from `.env` values:
- Default email: `admin@example.com` (change this!)
- Default password: `Admin@123` (change this!)

Admin endpoints:
- `GET /api/users` - List all users
- `DELETE /api/users/{id}` - Deactivate a user

---

## 8. API Rate Limits

| Endpoint | Limit |
|----------|-------|
| `POST /api/auth/register` | 5/minute |
| `POST /api/auth/login` | 10/minute |
| `POST /api/auth/forgot-password` | 3/minute |
| `POST /api/auth/reset-password` | 5/minute |
| `POST /api/ai/ask-cfo` | 15/minute |
| `POST /api/ai/ask-cfo/stream` | 15/minute |

---

## 9. Email Configuration

### Development
- Leave `SMTP_HOST` blank or set `ENV=development`
- Emails are logged to console instead of sent

### Production (Gmail)
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Use App Password, not your login password
SMTP_FROM=noreply@yourdomain.com
```

### Production (SendGrid)
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SMTP_FROM=noreply@yourdomain.com
```

---

## 10. Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Verify dependencies
pip install -r backend/requirements.txt
```

### CORS errors in frontend
- Ensure `CORS_ORIGINS` includes your frontend URL
- Check that `allow_credentials=True` is set

### Database locked (SQLite)
- SQLite doesn't support multiple concurrent writers well
- Switch to PostgreSQL for production multi-user scenarios

### AI responses are slow
- Groq API has rate limits; check your plan
- Consider caching frequent AI queries

### Email not sending in production
- Check `ENV=production` is set
- Verify SMTP credentials
- Check backend logs for SMTP errors

---

## 11. Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENV` | No | `development` | Environment mode |
| `SECRET_KEY` | Yes | - | JWT signing key (32+ chars) |
| `GROQ_API_KEY` | Yes | - | Groq API key |
| `DATABASE_URL` | No | SQLite | Database connection string |
| `CORS_ORIGINS` | No | localhost | Comma-separated allowed origins |
| `ADMIN_EMAIL` | No | admin@example.com | Default admin email |
| `ADMIN_PASSWORD` | No | Admin@123 | Default admin password |
| `VITE_API_URL` | Yes (frontend) | http://localhost:8000 | Backend URL for frontend |
| `FRONTEND_URL` | No | http://localhost | Frontend URL for email links |
| `SMTP_HOST` | No | - | SMTP server host |
| `SMTP_PORT` | No | 587 | SMTP server port |
| `SMTP_USER` | No | - | SMTP username |
| `SMTP_PASSWORD` | No | - | SMTP password |
| `SMTP_FROM` | No | noreply@... | From address for emails |
| `SENTRY_DSN` | No | - | Sentry error tracking DSN |

---

## 12. File Structure

```
AI-Money-Manager/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── auth.py              # JWT + bcrypt auth
│   ├── database.py          # SQLAlchemy setup (SQLite/PostgreSQL)
│   ├── models.py            # Database models
│   ├── schemas.py           # Pydantic schemas
│   ├── migrate.py           # Database migrations
│   ├── rate_limit.py        # Rate limiting config
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile           # Backend container
│   ├── routers/             # API route modules
│   └── services/            # Business logic + email + AI
├── frontend/
│   ├── src/                 # React source
│   ├── Dockerfile           # Frontend container
│   ├── nginx.conf           # Nginx config
│   └── package.json         # Node dependencies
├── docker-compose.yml       # Docker orchestration
├── Caddyfile                # HTTPS reverse proxy config
├── .env.example             # Environment template
├── .gitignore               # Git ignore rules
└── DEPLOYMENT.md            # This guide
```
