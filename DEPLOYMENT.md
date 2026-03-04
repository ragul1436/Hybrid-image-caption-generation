# Production Deployment Guide

This document outlines the steps to deploy the Hybrid Image Caption Generator to production.

## Pre-Deployment Checklist

### 1. Security Configuration

#### Generate Strong Secrets
```bash
# Generate secure SECRET_KEY
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# Generate secure DB password
python -c "import secrets; print('DB_PASSWORD=' + secrets.token_urlsafe(16))"
```

#### Set Environment Variables
1. Copy `.env.example` to `.env`
2. Update all placeholder values:
   - `DB_PASSWORD` - Strong database password
   - `SECRET_KEY` - Generated using command above
   - `BACKEND_CORS_ORIGINS` - Your production domain(s)
   - `SMTP_*` settings if email is needed

### 2. Database Configuration
- Ensure PostgreSQL is configured for:
  - Strong password (changed from `qwertyuiop`)
  - Proper backup strategy (daily backups recommended)
  - SSL/TLS connections in production

### 3. CORS Settings
Update `BACKEND_CORS_ORIGINS` in `backend/app.env` with your:
- Production domain(s)
- Frontend URL(s)
- Remove localhost addresses

### 4. File Uploads
- Configure persistent storage for `uploads/` directory
- Set up backup strategy for uploaded images
- Configure disk space monitoring

### 5. SSL/TLS
- Use HTTPS for all connections
- Install valid SSL certificate
- Consider using Let's Encrypt for free certificates

## Deployment Steps

### Using Docker Compose (Recommended)

#### 1. Prepare Server
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. Clone & Configure
```bash
git clone <your-repo-url>
cd Hybrid-Image-Caption-Generator
cp .env.example .env

# Edit .env with production values
nano .env
```

#### 3. Launch Services
```bash
# Build and start containers
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f db
```

#### 4. Verify Deployment
```bash
# Check health endpoint
curl http://localhost:8000/api/v1/health

# Check database connection
curl http://localhost:8000/api/v1/admin/  # If available
```

## Post-Deployment Configuration

### 1. Reverse Proxy (Nginx Example)
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

### 2. Monitoring & Logging
- Configure log aggregation (ELK Stack, Datadog, etc.)
- Set up uptime monitoring
- Configure alerts for system failures
- Monitor disk space for uploads directory

### 3. Backups
```bash
# Daily database backup
0 2 * * * docker-compose -f /path/to/docker-compose.yml exec -T db pg_dump -U postgres caption_db > /backups/db_$(date +\%Y\%m\%d).sql

# Backup uploads directory
0 3 * * * tar -czf /backups/uploads_$(date +\%Y\%m\%d).tar.gz /path/to/uploads/
```

### 4. Database Migrations
Run database migrations on deployment:
```bash
docker-compose exec backend alembic upgrade head
```

## Troubleshooting

### Container Won't Start
```bash
docker-compose logs backend
docker-compose logs db
```

### Database Connection Issues
- Verify DB_PASSWORD in .env
- Check PostgreSQL is running: `docker-compose ps db`
- Test connection: `docker-compose exec db psql -U postgres -d caption_db`

### Health Check Failing
- Verify backend service is running
- Check logs: `docker-compose logs backend`
- Ensure health endpoint is accessible: `curl http://localhost:8000/api/v1/health`

### Performance Issues
- Monitor container resource usage: `docker stats`
- Check database query performance
- Consider horizontal scaling with load balancer

## Security Best Practices

✅ **Implemented:**
- Environment variables for secrets
- Database password configuration
- Health check endpoint
- CORS origin validation
- Production-mode Docker image (no --reload)

✅ **Recommended Additional Steps:**
- Enable rate limiting on API endpoints
- Implement API key authentication
- Use secrets management (Vault, AWS Secrets Manager)
- Enable database SSL/TLS
- Set up WAF (Web Application Firewall)
- Regular security audits
- Enable logging and monitoring
- Implement backup and disaster recovery

## Scaling for Production

### Horizontal Scaling
```yaml
# Add multiple backend instances behind a load balancer
backend-1:
  # ... config ...

backend-2:
  # ... config ...

load-balancer:
  image: nginx:latest
  ports:
    - "80:80"
    - "443:443"
```

### Database Optimization
- Configure connection pooling
- Enable query caching
- Monitor slow queries
- Plan for database replication

## Maintenance

### Regular Tasks
- Monitor disk usage
- Check backup integrity
- Review logs for errors
- Update dependencies
- Security patches
- Performance optimization

### Update Procedure
```bash
# 1. Pull latest code
git pull origin main

# 2. Rebuild containers
docker-compose build --no-cache

# 3. Restart services
docker-compose up -d

# 4. Verify health
curl http://localhost:8000/api/v1/health
```
