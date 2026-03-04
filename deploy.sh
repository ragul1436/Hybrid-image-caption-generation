#!/bin/bash

# Production Startup Script
# This script securely sets up and starts the application for production

set -e

echo \"🚀 Hybrid Image Caption Generator - Production Setup\"
echo \"=================================================\"
echo

# Check if .env file exists
if [ ! -f \".env\" ]; then
    echo \"❌ Error: .env file not found!\"
    echo \"   Please copy .env.example to .env and configure it\"
    echo \"   cp .env.example .env\"
    exit 1
fi

# Verify .env is not in git
if git ls-files | grep -q '^\\.env$'; then
    echo \"❌ Warning: .env file is tracked by git!\"
    echo \"   Run: git rm --cached .env\"
    echo \"   This could expose secrets!\"
    exit 1
fi

# Check Docker and Docker Compose
if ! command -v docker &> /dev/null; then
    echo \"❌ Docker is not installed\"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo \"❌ Docker Compose is not installed\"
    exit 1
fi

echo \"✅ Docker is installed\"
echo

# Validate docker-compose.yml
echo \"🔍 Validating docker-compose.yml...\"
docker-compose config > /dev/null || {
    echo \"❌ Invalid docker-compose.yml\"
    exit 1
}
echo \"✅ Configuration valid\"
echo

# Create necessary directories
echo \"📁 Creating required directories...\"
mkdir -p uploads
mkdir -p ml_models
mkdir -p backups
chmod 755 uploads ml_models backups
echo \"✅ Directories created\"
echo

# Build images
echo \"🔨 Building Docker images...\"
docker-compose build --no-cache || {
    echo \"❌ Build failed\"
    exit 1
}
echo \"✅ Build complete\"
echo

# Start services
echo \"▶️  Starting services...\"
docker-compose up -d || {
    echo \"❌ Failed to start services\"
    exit 1
}
echo \"✅ Services started\"
echo

# Wait for database to be ready
echo \"⏳ Waiting for database to be ready...\"
sleep 10
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if docker-compose exec -T db psql -U postgres -d caption_db -c \"\\q\" 2>/dev/null; then
        echo \"✅ Database is ready\"
        break
    fi
    attempt=$((attempt + 1))
    if [ $attempt -lt $max_attempts ]; then
        echo \"   Attempt $attempt/$max_attempts... retrying in 3 seconds\"
        sleep 3
    fi
done

if [ $attempt -eq $max_attempts ]; then
    echo \"❌ Database failed to start after 90 seconds\"
    docker-compose logs db
    exit 1
fi
echo

# Run database migrations
echo \"🗄️  Running database migrations...\"
docker-compose exec -T backend alembic upgrade head || {
    echo \"❌ Database migrations failed\"
    docker-compose logs backend
    exit 1
}
echo \"✅ Migrations complete\"
echo

# Health check
echo \"🏥 Checking application health...\"
sleep 5
response=$(curl -s http://localhost:8000/api/v1/health 2>/dev/null || echo \"{}\")
if echo $response | grep -q \"healthy\"; then
    echo \"✅ Application is healthy\"
else
    echo \"⚠️  Health check response: $response\"
fi
echo

# Display service status
echo \"📊 Service Status:\"
docker-compose ps
echo

echo \"✨ Setup complete!\"
echo
echo \"📝 Next steps:\"
echo \"   1. Verify all services are running: docker-compose ps\"
echo \"   2. Check logs: docker-compose logs -f\"
echo \"   3. View API docs: http://localhost:8000/docs\"
echo \"   4. Set up reverse proxy (Nginx/Apache) for HTTPS\"
echo \"   5. Monitor logs and performance\"
echo
echo \"📚 Documentation:\"
echo \"   - Deployment: DEPLOYMENT.md\"
echo \"   - Checklist: PRODUCTION_CHECKLIST.md\"
echo
