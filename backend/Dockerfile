FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for WeasyPrint (PDF generation), psycopg2, and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    libcairo2 \
    libglib2.0-0 \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (cached layer)
COPY requirements.txt /app/backend/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy application code into /app/backend/ to match "backend.app.*" import paths
COPY . /app/backend

# Copy entrypoint script
COPY entrypoint.sh /app/backend/entrypoint.sh
RUN chmod +x /app/backend/entrypoint.sh

# Alembic reads alembic.ini from the working directory
WORKDIR /app/backend

EXPOSE 8000

# Entrypoint: run migrations then start uvicorn
ENTRYPOINT ["/app/backend/entrypoint.sh"]
