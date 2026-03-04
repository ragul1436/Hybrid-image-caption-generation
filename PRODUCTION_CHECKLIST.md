# Production Deployment Checklist

Complete this checklist before deploying to production.

## Security Requirements

- [ ] Generate strong `SECRET_KEY` using: `python -c \"import secrets; print(secrets.token_urlsafe(32))\"`
- [ ] Generate strong `DB_PASSWORD` using: `python -c \"import secrets; print(secrets.token_urlsafe(16))\"`
- [ ] Update `backend/app.env` with generated secrets
- [ ] Remove all localhost addresses from `BACKEND_CORS_ORIGINS`
- [ ] Add production domain(s) to `BACKEND_CORS_ORIGINS`
- [ ] .env file is in .gitignore (NEVER commit secrets to git)
- [ ] SMTP credentials configured (if email is needed)
- [ ] Verify no hardcoded passwords in code (grep -r \"password\" backend/)

## Infrastructure

- [ ] Docker and Docker Compose installed on server
- [ ] Server has sufficient disk space for uploads and database
- [ ] PostgreSQL is properly configured for production
- [ ] Backup strategy in place for database
- [ ] Backup strategy in place for uploaded files
- [ ] SSL/TLS certificate obtained (Let's Encrypt recommended)
- [ ] Reverse proxy configured (Nginx/Apache)
- [ ] Firewall rules properly configured
- [ ] Port 8000 only accessible internally, not from internet

## Application Configuration

- [ ] Health check endpoint verified: `GET /api/v1/health`
- [ ] Database migrations run: `docker-compose exec backend alembic upgrade head`
- [ ] Static files properly configured
- [ ] Upload directories have proper permissions
- [ ] Logging configured for production
- [ ] Rate limiting enabled on API endpoints
- [ ] CORS properly configured

## Testing

- [ ] Test database connectivity with production settings
- [ ] Test file uploads work correctly
- [ ] Test authentication flow (login/register)
- [ ] Load test to identify performance bottlenecks
- [ ] Security scan (e.g., using OWASP tools)
- [ ] Test backup and restore procedures
- [ ] Verify health endpoint is accessible
- [ ] Test API endpoints with production URLs

## Monitoring & Alerts

- [ ] Monitoring software installed (Prometheus, Datadog, New Relic, etc.)
- [ ] Log aggregation configured (ELK Stack, Splunk, etc.)
- [ ] Disk space alerts configured
- [ ] Database performance alerts configured
- [ ] API error rate alerts configured
- [ ] CPU/Memory alerts configured
- [ ] Uptime monitoring configured
- [ ] Automated backups verified

## Documentation

- [ ] DEPLOYMENT.md reviewed
- [ ] Team has access to documentation
- [ ] Emergency procedures documented
- [ ] Rollback procedures documented
- [ ] Database schema documented
- [ ] API endpoints documented

## Pre-Launch

- [ ] Database backed up before launch
- [ ] Code reviewed and tested
- [ ] No console errors in health check
- [ ] All routes responding correctly
- [ ] Email notifications configured (if applicable)
- [ ] Admin account created and tested
- [ ] Scheduled maintenance window documented

## Post-Launch (First 48 hours)

- [ ] Monitor logs for errors
- [ ] Monitor system resources (CPU, memory, disk)
- [ ] Check database performance
- [ ] Verify backups are working
- [ ] Monitor API response times
- [ ] Check file upload functionality
- [ ] Monitor for security issues
- [ ] Gather user feedback on performance

## Performance Optimization

- [ ] Database query optimization completed
- [ ] Caching strategy implemented
- [ ] Image optimization for uploads
- [ ] CDN configured for static assets (optional)
- [ ] Database connection pooling configured
- [ ] API response times monitored

## Security Hardening

- [ ] Fail2ban or similar rate limiting configured
- [ ] Web Application Firewall (WAF) configured
- [ ] DDoS protection enabled
- [ ] SQL injection prevention verified
- [ ] XSS protection enabled
- [ ] CSRF tokens configured
- [ ] Secure headers configured
- [ ] Security headers tested

## Database

- [ ] PostgreSQL version compatible verified
- [ ] Database backup tested and working
- [ ] Database user permissions properly restricted
- [ ] Connection pooling configured
- [ ] Slow query log enabled
- [ ] Query optimization completed

## Maintenance Plan

- [ ] Update schedule defined (security, dependencies)
- [ ] Rollback plan documented
- [ ] Disaster recovery plan documented
- [ ] Team trained on deployment procedures
- [ ] On-call schedule established
- [ ] Incident response plan documented

---

## Quick Deployment Commands

Once all items are checked:

```bash
# 1. Clone and setup
git clone <your-repo>
cd Hybrid-Image-Caption-Generator
cp .env.example .env
# Edit .env with production values
nano .env

# 2. Verify setup
docker-compose config

# 3. Build and launch
docker-compose up -d

# 4. Run migrations
docker-compose exec backend alembic upgrade head

# 5. Verify health
curl http://localhost:8000/api/v1/health

# 6. Check logs
docker-compose logs -f
```

---

**Last Updated:** March 4, 2026
**Status:** Ready for Production ✅
