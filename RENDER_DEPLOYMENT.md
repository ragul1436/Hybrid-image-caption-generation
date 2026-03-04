# Deploying to Render

Render is a modern cloud platform that simplifies deployment. This guide shows how to deploy the Hybrid Image Caption Generator to Render.

## Prerequisites

1. **Render Account** - Sign up at https://render.com (free tier available)
2. **GitHub Repository** - Push your code to GitHub (Render integrates with GitHub)
3. **Environment Variables** - Documented below

## Step 1: Prepare Your Repository

### 1.1 Create .renderignore (Optional)
Create `.renderignore` in your project root to exclude unnecessary files:

```
venv/
__pycache__/
*.pyc
.pytest_cache/
.git/
node_modules/
uploads/
ml_models/
*.log
```

### 1.2 Create render.yaml
Create `render.yaml` in your project root for Infrastructure as Code deployment:

```yaml
services:
  - type: web
    name: hybrid-caption-backend
    env: python
    plan: standard
    buildCommand: pip install -r backend/requirements.txt
    startCommand: uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /api/v1/health
    healthCheckInterval: 10
    autoDeploy: true
    envVars:
      - key: PYTHON_VERSION
        value: 3.9
      - key: DATABASE_URL
        fromDatabase:
          name: caption-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: BACKEND_CORS_ORIGINS
        value: '["https://yourdomain.com"]'

  - type: pserv
    name: caption-db
    plan: standard
    ipAllowList: []
    postgresSQLVersion: 15
    envVars:
      - key: POSTGRES_USER
        value: postgres
      - key: POSTGRES_PASSWORD
        generateValue: true
      - key: POSTGRES_DB
        value: caption_db
```

### 1.3 Update render.yaml with Your Details

Replace `yourdomain.com` with your actual domain (or remove if using Render's default domain).

## Step 2: Push to GitHub

```bash
git init
git add .
git commit -m "Prepare for Render deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

## Step 3: Deploy via Render Dashboard

### Option A: Deploy via Dashboard (Recommended for Beginners)

1. **Go to Render** - https://dashboard.render.com
2. **Sign in with GitHub** - Click "New +" and select "Web Service"
3. **Connect Repository**
   - Select "Build and deploy from a Git repository"
   - Connect your GitHub account
   - Select your repository

4. **Configure Web Service**
   - **Name:** `hybrid-caption-backend`
   - **Environment:** `Docker`
   - **Region:** Choose closest to users (e.g., Oregon, Frankfurt)
   - **Plan:** Standard (or higher for production)

5. **Add Environment Variables**
   - Click "Advanced" → "Add Environment Variable"
   - Add each variable (see Environment Variables section below)

6. **Deploy Database**
   - From dashboard, click "New +" → "PostgreSQL Database"
   - **Name:** `caption-db`
   - **Database:** `caption_db`
   - **User:** `postgres`
   - Render will auto-generate password
   - Copy the **Internal Database URL** (starts with `postgresql://`)

7. **Update Backend Environment Variables**
   - Add `DATABASE_URL` = Internal Database URL from PostgreSQL
   - Add `SECRET_KEY` = Generate a strong key

8. **Connect Database to Backend**
   - In backend service settings
   - Click "Environment" → Link the PostgreSQL database
   - Render auto-populates `DATABASE_URL`

9. **Deploy**
   - Click "Create Web Service"
   - Render starts building and deploying

### Option B: Deploy via render.yaml (Infrastructure as Code)

```bash
# Just push your render.yaml file to GitHub
git add render.yaml
git commit -m "Add render.yaml for IaC deployment"
git push origin main

# Render will automatically use render.yaml to deploy both services
```

## Step 4: Environment Variables Required

Set these in Render dashboard under "Environment":

| Variable | Value | Notes |
|----------|-------|-------|
| `DATABASE_URL` | Auto-linked from PostgreSQL | Render handles this |
| `SECRET_KEY` | Generate using: `python -c "import secrets; print(secrets.token_urlsafe(32))"` | ⚠️ Keep secret |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Optional |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Optional |
| `BACKEND_CORS_ORIGINS` | `["https://yourdomain.com"]` | Update with your domain |
| `UPLOAD_DIR` | `./uploads` | Default |
| `MAX_FILE_SIZE_MB` | `10` | Adjust as needed |
| `DEFAULT_MODEL` | `blip` | Model to use |
| `SMTP_HOST` | `smtp.gmail.com` | If using email |
| `SMTP_PORT` | `587` | If using email |
| `SMTP_USER` | Your email | If using email |
| `SMTP_PASS` | App password | If using email (not real password) |

## Step 5: Database Migrations

After first deployment, run migrations:

```bash
# In Render Dashboard:
# 1. Go to your backend service
# 2. Click "Shell" tab
# 3. Run:
alembic upgrade head
```

Or use Render's deployment hooks in `render.yaml`:

```yaml
services:
  - type: web
    # ... other config ...
    buildCommand: |
      pip install -r backend/requirements.txt
      alembic upgrade head
```

## Step 6: Configure Custom Domain (Optional)

1. **In Render Dashboard**
   - Go to your web service
   - Click "Settings" → "Custom Domain"
   - Add your domain (e.g., `api.yourdomain.com`)

2. **Update DNS Records**
   - Go to your domain registrar
   - Add CNAME record pointing to Render
   - Example: `api.yourdomain.com CNAME xxx.onrender.com`
   - Wait 24-48 hours for DNS propagation

3. **Enable HTTPS**
   - Render automatically provides SSL/TLS via Let's Encrypt

## Step 7: Monitor & Test

### Check Deployment Status

```bash
# View logs in Render Dashboard
# Service → Logs tab
# Look for: "Server running on http://0.0.0.0:10000"
```

### Test Your API

```bash
# Check health endpoint
curl https://yourdomain-backend.onrender.com/api/v1/health

# View API documentation
https://yourdomain-backend.onrender.com/docs
```

### Monitor Performance

- **Render Dashboard:** View resource usage, deployment history
- **Logs:** Check for errors and performance issues
- **Metrics:** Monitor CPU, memory, and request rates

## Step 8: Handle File Uploads

⚠️ **Important:** Render uses ephemeral file storage. Files are deleted when the service restarts!

### Option 1: Use External Storage (Recommended)

**AWS S3:**
```python
# Install boto3
pip install boto3

# Add to config.py
import boto3

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)
```

Add environment variables in Render:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_S3_BUCKET`

**Cloudinary (Image Storage):**
```python
# Install cloudinary
pip install cloudinary

import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)
```

### Option 2: Use Persistent Disk (Render Disk)

```yaml
# Add to render.yaml
services:
  - type: web
    name: hybrid-caption-backend
    # ... other config ...
    disk:
      name: uploads-disk
      path: /app/uploads
      sizeGB: 10  # Adjust size as needed
```

Learn more: https://render.com/docs/disks

## Pricing

### Render Free Tier
- ✅ Web Service: 0.5 CPU, 512MB RAM (auto-sleep after 15 min inactivity)
- ✅ PostgreSQL: Up to 1GB
- ⚠️ **Limitations:** Services auto-sleep, slower startup

### Paid Plans
| Resource | Standard | Pro |
|----------|----------|-----|
| Web Service | $7/month | $12/month |
| PostgreSQL | $15/month | $51/month |
| Disk | $0.25/GB/month | $0.25/GB/month |

## Troubleshooting

### Deployment Failed
```bash
# Check logs in Render Dashboard
# Common issues:
# 1. Missing DATABASE_URL environment variable
# 2. Python version mismatch
# 3. Import errors in code
```

### Database Connection Error
```
error: could not connect to database
```
**Solution:**
1. Verify `DATABASE_URL` is set correctly
2. Check PostgreSQL service is running
3. Verify firewall rules (Render databases are secured)

### Service Won't Start
```
Error: Module not found
```
**Solution:**
1. Ensure `requirements.txt` is in project root
2. Check Python version matches (3.9+)
3. Verify build command is correct

### Uploads Not Persisting
```python
# If using ephemeral storage, uploads disappear on restart
# Use S3/Cloudinary instead
```

### Health Check Failing
```
FAILED: /api/v1/health returned 502
```
**Solution:**
1. Ensure health endpoint is accessible
2. Check all dependencies are installed
3. Verify database is connected

## Security Checklist

- ✅ `SECRET_KEY` is strong and unique
- ✅ `DATABASE_URL` uses environment variable
- ✅ `BACKEND_CORS_ORIGINS` set to your domain only
- ✅ Environment variables marked as secret in Render
- ✅ HTTPS enforced with custom domain
- ✅ Database backups enabled (Render default)

## Auto-Deploy Setup

Render automatically deploys on push to main branch. To disable:

1. Go to service settings
2. Click "Auto-Deploy" → Off

## Scale Your Application

As traffic grows:

1. **Upgrade Web Service Plan**
   - Render Dashboard → Service Settings → Plan
   - Choose higher CPU/RAM

2. **Scale PostgreSQL**
   - Database Settings → Plan
   - Upgrade to dedicated instance

3. **Enable Caching** (Optional)
   - Add Redis: Create new Render service
   - Configure FastAPI caching middleware

4. **Use CDN**
   - Cloudflare integration for static files
   - Faster global content delivery

## Useful Links

- **Render Docs:** https://render.com/docs
- **FastAPI on Render:** https://render.com/docs/deploy-fastapi
- **PostgreSQL on Render:** https://render.com/docs/databases
- **Environment Variables:** https://render.com/docs/configure-environment-variables
- **Custom Domains:** https://render.com/docs/custom-domains

## Next Steps

1. ✅ Push code to GitHub
2. ✅ Create Render account
3. ✅ Deploy PostgreSQL database
4. ✅ Deploy web service
5. ✅ Set environment variables
6. ✅ Run database migrations
7. ✅ Configure custom domain
8. ✅ Test API endpoints
9. ✅ Set up monitoring
10. ✅ Configure backups

---

**Happy deploying! 🚀**

Questions? Visit Render Support: https://support.render.com
