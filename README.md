# Ofiuco Medical — Service Order Management System

Biomedical equipment service order management system. Track clients, equipment, service orders, attachments, and generate PDF reports — all from a single interface.

## Architecture

```
┌──────────────┐     ┌──────────────────┐     ┌────────────┐
│   Frontend   │────▶│     Backend      │────▶│ PostgreSQL │
│ React + Vite │     │ FastAPI + Alembic│     │    16      │
│  nginx:80    │     │   uvicorn:8000   │     │  :5432     │
└──────────────┘     └──────────────────┘     └────────────┘
```

**Hexagonal Architecture** (Ports & Adapters):
- **Domain**: entities, enums, and port interfaces (no framework dependencies)
- **Application**: DTOs and service orchestration
- **Infrastructure**: database repos, auth (JWT), PDF generation (WeasyPrint), OneDrive integration, QR codes
- **API**: FastAPI routes with dependency injection

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) ≥ 24
- [Docker Compose](https://docs.docker.com/compose/install/) ≥ 2.20

For local development without Docker:
- Python 3.12+
- Node.js 20+
- PostgreSQL 16+

## Quick Start

```bash
# 1. Clone the repository
git clone <repo-url> && cd ofiuco-medical

# 2. Copy environment variables
cp .env.example .env

# 3. Edit .env — at minimum, set a strong JWT_SECRET
#    (other variables have sensible defaults)

# 4. Start everything
docker compose up --build

# 5. Access the application
#    Frontend:  http://localhost
#    API Docs:  http://localhost/docs (Swagger)
#               http://localhost/redoc (ReDoc)
#    Health:    http://localhost/health
```

On first run the backend will:
1. Wait for PostgreSQL to be healthy
2. Run all Alembic migrations automatically
3. Start the API server

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@db:5432/ofiuco_medical` | Async PostgreSQL connection string |
| `POSTGRES_DB` | `ofiuco_medical` | PostgreSQL database name |
| `POSTGRES_USER` | `postgres` | PostgreSQL user |
| `POSTGRES_PASSWORD` | `postgres` | PostgreSQL password |
| `JWT_SECRET` | *(required)* | Secret key for JWT signing — **change in production** |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token lifetime |
| `AZURE_TENANT_ID` | *(optional)* | Azure AD tenant for OneDrive integration |
| `AZURE_CLIENT_ID` | *(optional)* | Azure AD client ID |
| `AZURE_CLIENT_SECRET` | *(optional)* | Azure AD client secret |
| `PUBLIC_URL` | `http://localhost:8000` | Public-facing API URL (used in PDFs) |
| `DEBUG` | `true` | Enable debug mode |
| `DB_PORT` | `5432` | Host port for PostgreSQL |
| `BACKEND_PORT` | `8000` | Host port for backend API |
| `FRONTEND_PORT` | `80` | Host port for frontend |

## Development Setup

### Backend (without Docker)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Start PostgreSQL (or use docker for just the DB)
docker compose up db -d

# Run migrations
DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/ofiuco_medical" \
  PYTHONPATH=. alembic upgrade head

# Start the server (with hot reload)
PYTHONPATH=. uvicorn backend.app.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (without Docker)

```bash
cd frontend
npm install
npm run dev    # Starts Vite dev server on :5173 with API proxy to :8000
```

### Database Migrations

```bash
# Generate a new migration after model changes
cd backend
alembic revision --autogenerate -m "description"

# Apply pending migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1
```

## API Endpoints

All endpoints are prefixed with `/api/v1` unless noted.

### Authentication
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/auth/register` | Admin | Create a new user |
| POST | `/api/v1/auth/login` | No | Login, returns JWT tokens |
| POST | `/api/v1/auth/refresh` | No | Refresh access token |
| POST | `/api/v1/auth/logout` | Yes | Logout |
| GET | `/api/v1/auth/me` | Yes | Current user info |

### Clients
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/clients` | Yes | List clients (paginated) |
| POST | `/api/v1/clients` | Yes | Create client |
| GET | `/api/v1/clients/:id` | Yes | Get client |
| PUT | `/api/v1/clients/:id` | Yes | Update client |
| DELETE | `/api/v1/clients/:id` | Yes | Delete client |

### Equipment
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/equipment` | Yes | List equipment (paginated) |
| POST | `/api/v1/equipment` | Yes | Create equipment |
| GET | `/api/v1/equipment/:id` | Yes | Get equipment |
| PUT | `/api/v1/equipment/:id` | Yes | Update equipment |
| DELETE | `/api/v1/equipment/:id` | Yes | Delete equipment |
| GET | `/api/v1/equipment/qr/:qrCode` | No | Get equipment by QR code |
| GET | `/api/v1/equipment/:id/qr-image` | Yes | Download QR image |

### Service Orders
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/orders` | Yes | List orders (paginated, filterable) |
| POST | `/api/v1/orders` | Yes | Create order |
| GET | `/api/v1/orders/:id` | Yes | Get order |
| PUT | `/api/v1/orders/:id` | Yes | Update order |
| DELETE | `/api/v1/orders/:id` | Yes | Delete order |
| PATCH | `/api/v1/orders/:id/status` | Yes | Update order status |
| POST | `/api/v1/orders/:id/parts` | Yes | Add part to order |
| DELETE | `/api/v1/orders/:id/parts/:partId` | Yes | Remove part |

### Attachments
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/attachments/upload` | Yes | Upload attachment |
| GET | `/api/v1/attachments/:id/download` | Yes | Download attachment |
| GET | `/api/v1/attachments/equipment/:id` | Yes | List equipment attachments |
| GET | `/api/v1/attachments/orders/:id` | Yes | List order attachments |
| DELETE | `/api/v1/attachments/:id` | Yes | Delete attachment |

### PDF & OneDrive
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/orders/:id/pdf` | Yes | Download order PDF |
| POST | `/api/v1/orders/:id/regenerate` | Yes | Regenerate order PDF |
| POST | `/api/v1/onedrive/sync/:id` | Yes | Sync equipment to OneDrive |
| GET | `/api/v1/onedrive/status` | Yes | OneDrive connection status |

### Public (no auth)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/public/equipment/attachments/:id` | No | Download public attachment |

### Health
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Service health check |

## Project Structure

```
ofiuco-medical/
├── docker-compose.yml          # Multi-service orchestration
├── .env.example                # Environment template
│
├── backend/
│   ├── Dockerfile              # Python 3.12-slim + WeasyPrint deps
│   ├── entrypoint.sh           # Migrations + uvicorn startup
│   ├── requirements.txt        # Python dependencies
│   ├── alembic.ini             # Alembic configuration
│   ├── alembic/                # Database migrations
│   ├── templates/              # Jinja2 PDF templates
│   └── app/
│       ├── domain/             # Entities, enums, port interfaces
│       ├── application/        # DTOs and service layer
│       ├── infrastructure/     # DB repos, auth, PDF, QR, OneDrive
│       └── api/                # FastAPI routes and app factory
│
├── frontend/
│   ├── Dockerfile              # Multi-stage: node build → nginx serve
│   ├── nginx.conf              # SPA routing + API proxy
│   ├── package.json            # React + Vite + TailwindCSS v4
│   └── src/
│       ├── api/                # Axios client and endpoint definitions
│       ├── components/         # Reusable UI components
│       ├── contexts/           # React context (auth)
│       ├── hooks/              # Custom hooks
│       ├── pages/              # Page components
│       └── types/              # TypeScript type definitions
```

## Features

- **Client Management**: Register and manage biomedical clients with contact info
- **Equipment Tracking**: Register equipment by category/subcategory with QR code generation
- **Service Orders**: Create, track, and close service orders with parts and cost tracking
- **File Attachments**: Upload and manage documents linked to equipment or orders
- **PDF Generation**: Auto-generate service order reports using WeasyPrint
- **OneDrive Integration**: Sync equipment documents to Microsoft OneDrive
- **QR Code Scanning**: Public equipment lookup via QR code (no login required)
- **JWT Authentication**: Secure API with role-based access control (Admin / Technician)

## Production Deployment

For production:

1. Set a strong `JWT_SECRET` in `.env`
2. Configure real Azure credentials for OneDrive integration
3. Set `DEBUG=false`
4. Use a reverse proxy (nginx, Caddy) for TLS termination
5. Consider managed PostgreSQL (e.g., AWS RDS, Azure Database)

```bash
# Production startup
docker compose -f docker-compose.yml up -d --build
```

## License

Private — Ofiuco Medical
