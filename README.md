
# Hybrid Image Caption Generator using Deep Learning

A full-stack web application that generates captions for images using a hybrid Deep Learning pipeline (CNN + Transformer / BLIP).

## Tech Stack

- **Frontend:** React + Vite + Tailwind CSS
- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL
- **Deep Learning:** PyTorch, Transformers (HuggingFace)
- **Infrastructure:** Docker, Docker Compose

## Features

- **User Authentication:** JWT-based login/register system.
- **Image Upload:** Drag-and-drop interface for uploading images.
- **Auto-Captioning:** Generates captions automatically using BLIP model.
- **Dashboard:** Interactive charts showing upload statistics.
- **Gallery:** Browse and search uploaded images.
- **Responsive Design:** Premium dark mode UI.

## Setup Instructions

### Prerequisites
- Docker & Docker Compose
- Node.js & npm (for local frontend dev)
- Python 3.9+ (for local backend dev)

### Quick Start (Docker)

1. **Clone the repository** (if applicable)

2. **Run with Docker Compose**
   ```bash
   docker-compose up --build
   ```
   This will start:
   - Backend API at `http://localhost:8000`
   - Frontend App at `http://localhost:5173`
   - PostgreSQL Database at `localhost:5432`

### Local Development Setup

#### 1. Backend

```bash
cd backend
python -m venv venv
# Activate venv (Windows: venv\Scripts\activate, Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
uvicorn backend.app.main:app --reload
```

**Note:** You need a running PostgreSQL instance. Update `.env` or `config.py` with your DB credentials.

#### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Documentation

Once the backend is running, access the Swagger UI at:
`http://localhost:8000/docs`

## Project Structure

- `backend/app`: FastAPI application source code.
  - `models`: Database models (SQLAlchemy).
  - `schemas`: Pydantic schemas.
  - `api`: API route handlers.
  - `ml`: Deep learning pipeline logic.
- `frontend/src`: React application source code.
  - `components`: Reusable UI components.
  - `pages`: Application pages.
  - `store`: Zustand state management.

## Default Credentials

- **Register a new user** on the signup page to get started.

---

## 🚀 Production Deployment

This application is **production-ready** and can be deployed to multiple platforms.

### ☁️ Deploy to Render (Easiest)

Render is a modern cloud platform perfect for FastAPI + PostgreSQL apps with free tier available.

**Quick Setup:**
1. Push code to GitHub
2. Go to https://dashboard.render.com
3. Click "New +" → "Infrastructure as Code"
4. Select your repository and deploy from `render.yaml`
5. Render auto-configures database, backend, and environment variables

For detailed instructions, see **[RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)**

### 🐳 Deploy with Docker (Self-Hosted)

For VPS, Ubuntu Server, or your own infrastructure:

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Windows:**
```bash
deploy.bat
```

### 📚 Documentation

Choose your deployment method:

| Platform | Guide | Setup Time | Cost |
|----------|-------|-----------|------|
| **Render** (Recommended) | [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) | 5 min | Free tier + $7/mo |
| **Docker (Self-Hosted)** | [DEPLOYMENT.md](DEPLOYMENT.md) | 10 min | Your server cost |
| **Production Checklist** | [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md) | - | All platforms |

### ⚠️ Important Security Notes

- ✅ **Secrets Management:** Environment variables properly configured
- ✅ **Database:** PostgreSQL with password protection
- ✅ **Health Checks:** Built-in container health monitoring
- ✅ **Production Mode:** Auto-reload disabled
- ✅ **CORS:** Configurable for production domains

**Before deploying:**
1. Copy `.env.example` to `.env` (for Docker deployment)
2. Generate strong secrets (see PRODUCTION_CHECKLIST.md or RENDER_DEPLOYMENT.md)
3. Update production domain settings
4. Review appropriate guide for your chosen platform

---

Built with ❤️ by AI Agent
