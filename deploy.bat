@echo off
REM Production Startup Script for Windows
REM This script securely sets up and starts the application for production

setlocal enabledelayedexpansion

echo.
echo 🚀 Hybrid Image Caption Generator - Production Setup (Windows)
echo ===========================================================
echo.

REM Check if .env file exists
if not exist \".env\" (
    echo ❌ Error: .env file not found!
    echo    Please copy .env.example to .env and configure it
    echo    copy .env.example .env
    pause
    exit /b 1
)

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed or not in PATH
    pause
    exit /b 1
)
echo ✅ Docker is installed

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed or not in PATH
    pause
    exit /b 1
)
echo ✅ Docker Compose is installed
echo.

REM Validate docker-compose.yml
echo 🔍 Validating docker-compose.yml...
docker-compose config >nul 2>&1
if errorlevel 1 (
    echo ❌ Invalid docker-compose.yml
    pause
    exit /b 1
)
echo ✅ Configuration valid
echo.

REM Create necessary directories
echo 📁 Creating required directories...
if not exist \"uploads\" mkdir uploads
if not exist \"ml_models\" mkdir ml_models
if not exist \"backups\" mkdir backups
echo ✅ Directories created
echo.

REM Build images
echo 🔨 Building Docker images...
docker-compose build --no-cache
if errorlevel 1 (
    echo ❌ Build failed
    pause
    exit /b 1
)
echo ✅ Build complete
echo.

REM Start services
echo ▶️  Starting services...
docker-compose up -d
if errorlevel 1 (
    echo ❌ Failed to start services
    docker-compose logs
    pause
    exit /b 1
)
echo ✅ Services started
echo.

REM Wait for database
echo ⏳ Waiting for database to be ready...
timeout /t 10 /nobreak
echo.

REM Run database migrations
echo 🗄️  Running database migrations...
docker-compose exec -T backend alembic upgrade head
if errorlevel 1 (
    echo ❌ Database migrations failed
    docker-compose logs backend
    pause
    exit /b 1
)
echo ✅ Migrations complete
echo.

REM Health check
echo 🏥 Checking application health...
timeout /t 5 /nobreak
for /f %%i in ('curl -s http://localhost:8000/api/v1/health 2^>nul') do set response=%%i
if \"%response%\"==\\\"\\\" (
    echo ⚠️  Could not reach health endpoint
) else (
    echo ✅ Application is responding
)
echo.

REM Display service status
echo 📊 Service Status:
docker-compose ps
echo.

echo ✨ Setup complete!
echo.
echo 📝 Next steps:
echo    1. Verify all services are running: docker-compose ps
echo    2. Check logs: docker-compose logs -f
echo    3. View API docs: http://localhost:8000/docs
echo    4. Set up reverse proxy (IIS/Nginx) for HTTPS
echo    5. Monitor logs and performance
echo.
echo 📚 Documentation:
echo    - Deployment: DEPLOYMENT.md
echo    - Checklist: PRODUCTION_CHECKLIST.md
echo.

pause
