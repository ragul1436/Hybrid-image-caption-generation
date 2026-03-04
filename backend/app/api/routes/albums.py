
import uuid
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, delete
from sqlalchemy.orm import selectinload
from backend.app.api import deps
from backend.app.core.database import get_db
from backend.app.models.db_models import Album, Image, User, album_images_table
from backend.app.schemas.pydantic_schemas import AlbumCreate, AlbumUpdate, AlbumResponse, AlbumAddImages

router = APIRouter()

@router.post("/", response_model=AlbumResponse)
async def create_album(
    album_in: AlbumCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    album = Album(
        name=album_in.name,
        description=album_in.description,
        user_id=current_user.id
    )
    db.add(album)
    await db.commit()
    await db.refresh(album, attribute_names=['images'])
    return album

@router.get("/", response_model=List[AlbumResponse])
async def read_albums(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    result = await db.execute(
        select(Album)
        .options(selectinload(Album.images))
        .where(Album.user_id == current_user.id)
        .order_by(desc(Album.created_at))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

@router.get("/{id}", response_model=AlbumResponse)
async def read_album(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    result = await db.execute(
        select(Album).options(selectinload(Album.images)).where(Album.id == id)
    )
    album = result.scalars().first()
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    if album.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return album

@router.put("/{id}", response_model=AlbumResponse)
async def update_album(
    id: uuid.UUID,
    album_in: AlbumUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    result = await db.execute(
        select(Album)
        .options(selectinload(Album.images))
        .where(Album.id == id)
    )
    album = result.scalars().first()
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    if album.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    if album_in.name is not None:
        album.name = album_in.name
    if album_in.description is not None:
        album.description = album_in.description
        
    await db.commit()
    await db.refresh(album)
    return album

@router.delete("/{id}")
async def delete_album(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    result = await db.execute(select(Album).where(Album.id == id))
    album = result.scalars().first()
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    if album.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    await db.delete(album)
    await db.commit()
    return {"msg": "Album deleted"}

@router.post("/{id}/images")
async def add_images_to_album(
    id: uuid.UUID,
    payload: AlbumAddImages,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    # Verify album ownership
    result = await db.execute(select(Album).where(Album.id == id))
    album = result.scalars().first()
    if not album or album.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Album not found")

    # Verify images ownership and existence
    # This is a simplified check; ideally check all IDs
    # Insert mappings
    for image_id in payload.image_ids:
        # Check if image exists and belongs to user
        img_res = await db.execute(select(Image).where(Image.id == image_id, Image.user_id == current_user.id))
        img = img_res.scalars().first()
        if img:
            # Add to association table
            # In SQLAlchemy Core/async:
            stmt = album_images_table.insert().values(album_id=id, image_id=image_id)
            try:
                await db.execute(stmt)
            except Exception:
                pass # Already exists or constraint error
    
    await db.commit()
    return {"msg": "Images added to album"}
