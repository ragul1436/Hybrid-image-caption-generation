
import os
import shutil
import uuid
from typing import List, Any
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query, BackgroundTasks
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from backend.app.api import deps
from backend.app.core.database import get_db, AsyncSessionLocal
from backend.app.core.config import settings
from backend.app.models.db_models import User, Image, Caption

def _get_pipeline():
    """Lazy-load the ML pipeline so the server can start without torch."""
    from backend.app.ml.hybrid_pipeline import pipeline
    return pipeline

# Simple in-memory job status store: {str(image_id): {status: 'pending'|'processing'|'done'|'failed', 'caption_id': UUID|null, 'error': str|null}}
JOB_STATUS = {}
from backend.app.schemas.pydantic_schemas import ImageResponse, ImageCreate

router = APIRouter()

@router.post("/upload", response_model=List[ImageResponse])
async def upload_images(
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    uploaded_images = []
    
    # Ensure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    for file in files:
        # Validate file type
        if file.content_type not in ["image/jpeg", "image/png", "image/webp", "image/gif"]:
            continue # Skip invalid
            
        file_ext = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create DB record
        db_image = Image(
            filename=unique_filename,
            original_url=f"/uploads/{unique_filename}", # Relative URL to be served by static files
            file_size=file_size,
            format=file.content_type,
            user_id=current_user.id
        )
        db.add(db_image)
        uploaded_images.append(db_image)
        # Mark job as pending
        JOB_STATUS[str(db_image.id)] = {"status": "pending", "caption_id": None, "error": None}
    
    await db.commit()
    for img in uploaded_images:
        await db.refresh(img)
        # enqueue background generation task
        if background_tasks is not None:
            background_tasks.add_task(_process_image_generate, str(img.id), str(current_user.id))
        
    return uploaded_images


async def _process_image_generate(image_id: str, user_id: str):
    """Background task to run caption generation and save result to DB."""
    JOB_STATUS[image_id]["status"] = "processing"
    try:
        # Open a new async DB session for background task
        async with AsyncSessionLocal() as session:
            # fetch image
            res = await session.execute(select(Image).where(Image.id == image_id))
            image = res.scalars().first()
            if not image:
                JOB_STATUS[image_id]["status"] = "failed"
                JOB_STATUS[image_id]["error"] = "Image not found"
                return

            image_path = os.path.join(settings.UPLOAD_DIR, image.filename)
            # Call pipeline
            try:
                result = await _get_pipeline().generate_caption(image_path=image_path, model_name=settings.DEFAULT_MODEL, language="en")
            except Exception as e:
                JOB_STATUS[image_id]["status"] = "failed"
                JOB_STATUS[image_id]["error"] = str(e)
                return

            # Save caption
            caption = Caption(
                image_id=image.id,
                user_id=image.user_id,
                caption_text=result.get("caption", ""),
                confidence_score=result.get("confidence", 0.0),
                model_used=settings.DEFAULT_MODEL,
                language="en",
                generation_time=result.get("time_ms", 0.0),
                decode_method="auto"
            )
            session.add(caption)
            await session.commit()
            await session.refresh(caption)
            JOB_STATUS[image_id]["status"] = "done"
            JOB_STATUS[image_id]["caption_id"] = str(caption.id)
    except Exception as e:
        JOB_STATUS[image_id]["status"] = "failed"
        JOB_STATUS[image_id]["error"] = str(e)


@router.get('/status/{image_id}')
async def image_status(image_id: uuid.UUID):
    key = str(image_id)
    info = JOB_STATUS.get(key)
    if not info:
        raise HTTPException(status_code=404, detail="No processing job found for image")
    return info

@router.get("/", response_model=List[ImageResponse])
async def read_images(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    result = await db.execute(
        select(Image).where(Image.user_id == current_user.id).order_by(desc(Image.uploaded_at)).offset(skip).limit(limit)
    )
    return result.scalars().all()

@router.get("/{image_id}", response_model=ImageResponse)
async def read_image(
    image_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    result = await db.execute(select(Image).where(Image.id == image_id))
    image = result.scalars().first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
        
    # Check permission? Ideally, yes.
    if image.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    return image

@router.delete("/{image_id}")
async def delete_image(
    image_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    result = await db.execute(select(Image).where(Image.id == image_id))
    image = result.scalars().first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
        
    if image.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Remove file from disk
    file_path = os.path.join(settings.UPLOAD_DIR, image.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        
    await db.delete(image)
    await db.commit()
    return {"msg": "Image deleted"}
