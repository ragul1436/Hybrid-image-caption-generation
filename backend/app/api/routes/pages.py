"""
Server‑side page routes – serves Jinja2 templates for every page.
All API endpoints remain under /api/v1/… untouched.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

router = APIRouter()

# Resolve template directory relative to this file
_TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates")
templates = Jinja2Templates(directory=_TEMPLATE_DIR)


# ─── Public pages ───────────────────────────────

@router.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    return templates.TemplateResponse("pages/landing.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("pages/login.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("pages/register.html", {"request": request})


# ─── Protected pages (auth checked client‑side via JS) ──

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("pages/dashboard.html", {"request": request})


@router.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("pages/upload.html", {"request": request})


@router.get("/gallery", response_class=HTMLResponse)
async def gallery_page(request: Request):
    return templates.TemplateResponse("pages/gallery.html", {"request": request})


@router.get("/image/{image_id}", response_class=HTMLResponse)
async def image_detail_page(request: Request, image_id: str):
    return templates.TemplateResponse("pages/image_detail.html", {"request": request, "image_id": image_id})


@router.get("/albums", response_class=HTMLResponse)
async def albums_page(request: Request):
    return templates.TemplateResponse("pages/albums.html", {"request": request})


@router.get("/albums/{album_id}", response_class=HTMLResponse)
async def album_detail_page(request: Request, album_id: str):
    return templates.TemplateResponse("pages/album_detail.html", {"request": request, "album_id": album_id})


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    return templates.TemplateResponse("pages/settings.html", {"request": request})


@router.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    return templates.TemplateResponse("pages/admin.html", {"request": request})
