# ClauseLens Backend

**ClauseLens: Context-Aware Terms & Conditions Risk Summarization with Version-Diff Personalized Alerts**

This is the **Django REST Framework backend** (Member 2) that acts as the central communication hub between all ClauseLens modules.

---

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL 15+
- Redis 7+ (for Celery)

### Installation

```bash
# 1. Clone and navigate to the backend
cd ClauseLens/backend

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/macOS

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your database credentials and secrets

# 5. Run database migrations
python manage.py makemigrations
python manage.py migrate

# 6. Create a superuser (for Django admin)
python manage.py createsuperuser

# 7. Run the development server
python manage.py runserver
```

### Running Celery (required for background NLP processing)

```bash
# In a separate terminal:
celery -A config worker --loglevel=info
```

### API Documentation

After starting the server, visit:

- Swagger UI: http://localhost:8000/api/docs/
- ReDoc:       http://localhost:8000/api/redoc/
- OpenAPI Schema: http://localhost:8000/api/schema/
- Django Admin: http://localhost:8000/admin/

---

## Project Structure

```
backend/
├── config/              # Django project settings, URLs, Celery
├── apps/
│   ├── accounts/        # User authentication (JWT)
│   ├── profiles/        # User profile management
│   ├── documents/       # Document upload and management
│   ├── analysis/        # Clause storage and NLP results
│   ├── personalization/ # Personalized risk scores
│   ├── monitoring/      # Policy monitoring, versions, changes
│   ├── alerts/          # Notifications, alerts, dashboard
│   └── common/          # Shared utilities, pagination, permissions
├── integrations/        # External service clients (NLP, personalization, etc.)
├── tests/               # Pytest test suite
├── requirements.txt
├── .env.example
├── manage.py
└── pytest.ini
```

---

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov-report=html

# Run specific test file
pytest tests/test_accounts.py -v
```

> Tests require a running PostgreSQL database (uses `clauselens_db` by default).
> Set `USE_MOCK_NLP=True`, `USE_MOCK_PERSONALIZATION=True`, `USE_MOCK_VERSION=True` in `.env` for testing without real services.

---

## Production Deployment

```bash
# Collect static files
python manage.py collectstatic

# Run with Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

---

## Module Integration

| Module | Member | Integration Point |
|--------|--------|-------------------|
| NLP Service | Member 4 | `integrations/nlp_client.py` + `POST /api/internal/nlp-callback/` |
| Personalization | Member 5 | `integrations/personalization_client.py` |
| Version Tracking | Member 6 | `integrations/version_client.py` + `POST /api/internal/version-update/` |
| Frontend (React) | Member 1 | All `/api/` endpoints |
| Database | Member 3 | Django ORM models (see `apps/*/models.py`) |

---

## Environment Variables

See [.env.example](.env.example) for all configuration options.

Key variables:
- `USE_MOCK_NLP` – Use mock NLP client (default: True)
- `USE_MOCK_PERSONALIZATION` – Use mock personalization (default: True)
- `USE_MOCK_VERSION` – Use mock version tracker (default: True)
- `INTERNAL_SERVICE_TOKEN` – Shared secret for internal microservice calls
- `ALERT_THRESHOLD` – Minimum alert score to create a notification (default: 0.5)

---

## Security Notes

- JWT tokens expire after 1 hour (access) / 24 hours (refresh) by default.
- All document endpoints enforce ownership – users can only access their own data.
- Internal endpoints (`/api/internal/`) require `X-Internal-Token` header.
- Never commit `.env` to version control.
- In production, set `DEBUG=False` and configure `ALLOWED_HOSTS`.
