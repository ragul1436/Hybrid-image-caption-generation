
import uuid
import logging
import traceback
import os
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from backend.app.api import deps
from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.models.db_models import Caption, Image, User
from backend.app.schemas.pydantic_schemas import CaptionResponse, CaptionGenerateRequest, CaptionRatingCreate

logger = logging.getLogger(__name__)

def _get_pipeline():
    """Lazy-load the ML pipeline so the server can start without torch."""
    from backend.app.ml.hybrid_pipeline import pipeline
    return pipeline

router = APIRouter()

@router.post("/generate", response_model=CaptionResponse)
async def generate_caption(
    request: CaptionGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    logger.info(f"[CAPTION_GEN] Request: image_id={request.image_id}, model={request.model}, user={current_user.id}")
    
    # 1. Get Image
    try:
        result = await db.execute(select(Image).where(Image.id == request.image_id))
        image = result.scalars().first()
        if not image:
            logger.error(f"[CAPTION_GEN] Image not found: {request.image_id}")
            raise HTTPException(status_code=404, detail="Image not found")
            
        if image.user_id != current_user.id:
            logger.error(f"[CAPTION_GEN] Authorization failed: image {request.image_id} belongs to user {image.user_id}, not {current_user.id}")
            raise HTTPException(status_code=403, detail="Not authorized")
        
        logger.info(f"[CAPTION_GEN] Image found: {image.filename}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[CAPTION_GEN] Database error while fetching image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # 2. Run Pipeline
    image_path = os.path.join(settings.UPLOAD_DIR, image.filename)
    logger.info(f"[CAPTION_GEN] Generating caption for image_path={image_path}, model={request.model}")
    
    try:
        pipeline = _get_pipeline()
        logger.info(f"[CAPTION_GEN] Pipeline loaded, calling generate_caption()")
        res = await pipeline.generate_caption(
            image_path=image_path,
            model_name=request.model,
            language=request.language
        )
        logger.info(f"[CAPTION_GEN] Caption result: {res}")
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        logger.error(f"[CAPTION_GEN] Caption generation failed: {error_msg}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {error_msg}")
        
    # 3. Save to DB
    try:
        caption = Caption(
            image_id=image.id,
            user_id=current_user.id,
            caption_text=res["caption"],
            confidence_score=res["confidence"],
            model_used=request.model,
            language=request.language,
            generation_time=res["time_ms"],
            decode_method=request.decode_method
        )
        db.add(caption)
        await db.commit()
        await db.refresh(caption)
        logger.info(f"[CAPTION_GEN] Caption saved to DB: {caption.id}")
    except Exception as e:
        logger.error(f"[CAPTION_GEN] Failed to save caption to DB: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to save caption: {str(e)}")
    
    return caption

@router.get("/{image_id}", response_model=List[CaptionResponse])
async def get_captions_for_image(
    image_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    # Verify access
    result = await db.execute(select(Image).where(Image.id == image_id))
    image = result.scalars().first()
    if not image or (image.user_id != current_user.id and current_user.role != "admin"):
        raise HTTPException(status_code=404, detail="Image not found or unauthorized")

    result = await db.execute(select(Caption).where(Caption.image_id == image_id).order_by(desc(Caption.created_at)))
    return result.scalars().all()

@router.post("/{id}/rate")
async def rate_caption(
    id: uuid.UUID,
    rating: CaptionRatingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    # Placeholder for rating logic
    pass
