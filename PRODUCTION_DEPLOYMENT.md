# MintelliFunds - Production Deployment Guide

## 🚀 Production Deployment Overview

This guide covers deploying the MintelliFunds Financial AI Assistant to production environments with security, scalability, and reliability best practices.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Ubuntu 20.04+ / CentOS 8+ / Windows Server 2019+
- **Memory**: Minimum 4GB RAM (8GB+ recommended)
- **CPU**: 2+ cores (4+ cores recommended)
- **Storage**: 20GB+ SSD storage
- **Network**: Stable internet connection

### Required Software
- Docker 20.10+
- Docker Compose 2.0+
- Git
- SSL certificates (for HTTPS)
- Domain name (for production)

## 🔧 Environment Setup

### 1. Clone and Prepare Repository
```bash
# Clone the repository
git clone <repository-url>
cd MintelliFunds

# Create production directories
mkdir -p data logs backups docker/ssl
chmod 755 data logs backups
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit production settings
nano .env
```

#### Required Environment Variables
```bash
# Application Settings
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<generate-secure-32-char-key>
JWT_SECRET_KEY=<generate-secure-32-char-key>

# Database Settings
DATABASE_URL=postgresql://username:password@postgres:5432/financial_ai

# AI Service Keys (Optional but recommended)
GOOGLE_AI_API_KEY=<your-google-ai-api-key>
OPENAI_API_KEY=<your-openai-api-key>

# Redis Settings
REDIS_PASSWORD=<secure-redis-password>

# Monitoring (Optional)
GRAFANA_PASSWORD=<secure-grafana-password>

# CORS Settings (Update with your domain)
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

### 3. SSL Certificate Setup
```bash
# For Let's Encrypt (recommended)
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates to docker directory
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem docker/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem docker/ssl/
sudo chmod 644 docker/ssl/*.pem
```

### 4. Create Nginx Configuration
Create `docker/nginx.conf`:
```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    server {
        listen 80;
        server_name your-domain.com www.your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com www.your-domain.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
        ssl_prefer_server_ciphers off;
        
        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

## 🐳 Docker Deployment

### 1. Build and Deploy
```bash
# Build the application
docker-compose build

# Deploy with production configuration
docker-compose -f docker-compose.yml up -d

# Verify deployment
docker-compose ps
docker-compose logs backend
```

### 2. Database Migration (First Time)
```bash
# Run database migrations
docker-compose exec backend python -c "
from app.database import create_tables
create_tables()
print('Database tables created successfully')
"
```

### 3. Create Admin User
```bash
# Create admin user
docker-compose exec backend python -c "
from app.security.auth import security_manager, MOCK_USERS
print('Admin credentials:')
print('Username: admin_user')
print('Password: admin_password')
print('API will be available at: https://your-domain.com')
"
```

## 🔒 Security Hardening

### 1. Firewall Configuration
```bash
# Allow only necessary ports
sudo ufw enable
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP (redirects to HTTPS)
sudo ufw allow 443/tcp   # HTTPS
sudo ufw deny 8000/tcp   # Block direct backend access
```

### 2. System Security Updates
```bash
# Set up automatic security updates
sudo apt update && sudo apt upgrade -y
sudo apt install unattended-upgrades
sudo dpkg-reconfigure unattended-upgrades
```

### 3. Docker Security
```bash
# Secure Docker daemon
sudo nano /etc/docker/daemon.json
```

Add the following configuration:
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "userland-proxy": false,
  "experimental": false
}
```

### 4. Backup Configuration
```bash
# Create backup script
cat > /opt/backup-financial-ai.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups/financial-ai"
mkdir -p $BACKUP_DIR

# Backup database
docker-compose exec postgres pg_dump -U postgres financial_ai > $BACKUP_DIR/database_$DATE.sql

# Backup application data
tar -czf $BACKUP_DIR/app_data_$DATE.tar.gz data/ logs/

# Cleanup old backups (keep last 7 days)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /opt/backup-financial-ai.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/backup-financial-ai.sh >> /var/log/financial-ai-backup.log 2>&1") | crontab -
```

## 📊 Monitoring Setup

### 1. Prometheus Configuration
Create `docker/prometheus.yml`:
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'financial-ai-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
```

### 2. Log Monitoring
```bash
# Install log rotation
sudo apt install logrotate

# Create logrotate configuration
sudo tee /etc/logrotate.d/financial-ai << 'EOF'
/opt/MintelliFunds/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
    postrotate
        docker-compose restart backend
    endscript
}
EOF
```

### 3. Health Check Monitoring
```bash
# Create health check script
cat > /opt/health-check.sh << 'EOF'
#!/bin/bash
HEALTH_URL="https://your-domain.com/api/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $RESPONSE -eq 200 ]; then
    echo "$(date): Health check passed"
else
    echo "$(date): Health check failed - Response: $RESPONSE"
    # Send alert (email, Slack, etc.)
    # /opt/send-alert.sh "Financial AI health check failed"
fi
EOF

chmod +x /opt/health-check.sh

# Add to crontab (every 5 minutes)
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/health-check.sh >> /var/log/health-check.log 2>&1") | crontab -
```

## 📈 Performance Optimization

### 1. Database Optimization
```bash
# Optimize PostgreSQL settings
docker-compose exec postgres psql -U postgres -d financial_ai -c "
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
SELECT pg_reload_conf();
"
```

### 2. Redis Configuration
```bash
# Optimize Redis for caching
docker-compose exec redis redis-cli CONFIG SET maxmemory 512mb
docker-compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

### 3. Nginx Performance
Update `docker/nginx.conf` with performance optimizations:
```nginx
http {
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
    
    client_max_body_size 10M;
    client_body_timeout 60;
    client_header_timeout 60;
    
    keepalive_timeout 65;
    keepalive_requests 100;
}
```

## 🔄 Deployment Updates

### 1. Zero-Downtime Deployment
```bash
# Create deployment script
cat > /opt/deploy-update.sh << 'EOF'
#!/bin/bash
set -e

echo "Starting deployment update..."

# Pull latest code
cd /opt/MintelliFunds
git pull origin main

# Build new image
docker-compose build backend

# Perform rolling update
docker-compose up -d --no-deps backend

# Health check
sleep 30
if curl -f https://your-domain.com/api/health; then
    echo "Deployment successful"
    # Cleanup old images
    docker image prune -f
else
    echo "Deployment failed, rolling back..."
    docker-compose restart backend
    exit 1
fi
EOF

chmod +x /opt/deploy-update.sh
```

### 2. Database Migrations
```bash
# Create migration script
cat > /opt/migrate-database.sh << 'EOF'
#!/bin/bash
echo "Running database migrations..."

# Backup before migration
/opt/backup-financial-ai.sh

# Run migrations
docker-compose exec backend python -c "
from app.database import run_migrations
run_migrations()
print('Database migrations completed')
"
EOF

chmod +x /opt/migrate-database.sh
```

## 🚨 Incident Response

### 1. Common Issues and Solutions

#### Service Won't Start
```bash
# Check logs
docker-compose logs backend
docker-compose logs postgres
docker-compose logs redis

# Restart services
docker-compose restart
```

#### High Memory Usage
```bash
# Check resource usage
docker stats

# Scale backend if needed
docker-compose up -d --scale backend=2
```

#### Database Connection Issues
```bash
# Check database status
docker-compose exec postgres pg_isready -U postgres

# Reset database connection pool
docker-compose restart backend
```

### 2. Emergency Procedures

#### Complete System Restore
```bash
# Stop services
docker-compose down

# Restore from backup
tar -xzf /opt/backups/financial-ai/app_data_latest.tar.gz
docker-compose exec postgres psql -U postgres -d financial_ai < /opt/backups/financial-ai/database_latest.sql

# Restart services
docker-compose up -d
```

## 📋 Maintenance Checklist

### Daily
- [ ] Check application health status
- [ ] Review error logs
- [ ] Monitor system resources

### Weekly
- [ ] Review security logs
- [ ] Check backup integrity
- [ ] Update dependencies (test environment first)

### Monthly
- [ ] Security updates
- [ ] Performance review
- [ ] Capacity planning
- [ ] SSL certificate renewal check

## 🎯 Production Readiness Checklist

### Security ✅
- [ ] SSL/TLS encryption enabled
- [ ] Authentication implemented
- [ ] Rate limiting configured
- [ ] Security headers set
- [ ] Input validation active
- [ ] Audit logging enabled

### Reliability ✅
- [ ] Health checks configured
- [ ] Auto-restart policies set
- [ ] Database backups automated
- [ ] Error handling implemented
- [ ] Graceful shutdown configured

### Performance ✅
- [ ] Connection pooling configured
- [ ] Caching implemented
- [ ] Resource limits set
- [ ] Monitoring enabled
- [ ] Load balancing ready

### Observability ✅
- [ ] Logging configured
- [ ] Metrics collection enabled
- [ ] Health monitoring active
- [ ] Alert system configured
- [ ] Dashboard setup complete

## 📞 Support and Troubleshooting

### Getting Help
1. Check the logs: `docker-compose logs backend`
2. Review health endpoints: `curl https://your-domain.com/api/health`
3. Monitor system resources: `docker stats`
4. Check database connectivity: `docker-compose exec postgres pg_isready -U postgres`

### Common Commands
```bash
# View all services status
docker-compose ps

# Restart a specific service
docker-compose restart backend

# View real-time logs
docker-compose logs -f backend

# Execute command in container
docker-compose exec backend python -c "print('Hello from backend')"

# Update and restart
git pull && docker-compose build && docker-compose up -d
```

---

## 🎊 Production Ready!

Your MintelliFunds Financial AI Assistant is now deployed to production with:

✅ **Security**: SSL encryption, authentication, input validation  
✅ **Reliability**: Health checks, auto-restart, backups  
✅ **Performance**: Optimized database, caching, load balancing  
✅ **Monitoring**: Logs, metrics, alerts, dashboards  
✅ **Maintenance**: Automated updates, backups, monitoring  

The application is ready to serve users securely and reliably in production!

---

**Last Updated**: 2024-01-XX  
**Version**: 1.0.0  
**Support**: Check logs and health endpoints for troubleshooting