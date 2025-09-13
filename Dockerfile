# Multi-stage Docker build for Financial AI Assistant

# Build stage for frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /frontend

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY src/ ./src/
COPY assets/ ./assets/

# Build the Electron app for production
RUN npm run build

# Python backend stage
FROM python:3.11-slim AS backend

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set work directory
WORKDIR /app

# Copy backend requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/ .

# Create necessary directories
RUN mkdir -p data logs backups temp uploads && \
    chown -R appuser:appuser /app

# Copy frontend build (if building integrated version)
# COPY --from=frontend-builder /frontend/dist ./frontend/

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run the application
CMD ["python", "run_server.py"]

# Production stage with additional optimizations
FROM backend AS production

# Install additional production dependencies
USER root
RUN pip install gunicorn uvicorn[standard] prometheus-client

# Copy production configuration
COPY docker/production.env .env

# Set production environment
ENV ENVIRONMENT=production \
    WORKERS=4 \
    LOG_LEVEL=info

# Switch back to app user
USER appuser

# Use Gunicorn for production
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]