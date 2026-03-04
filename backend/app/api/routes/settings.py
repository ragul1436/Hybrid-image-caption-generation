
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.api import deps
from backend.app.core.database import get_db
from backend.app.models.db_models import User
from backend.app.schemas.pydantic_schemas import UserResponse, UserUpdate

router = APIRouter()

@router.get("/profile", response_model=UserResponse)
async def read_user_profile(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    return current_user

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    if user_in.name is not None:
        current_user.name = user_in.name
    if user_in.email is not None:
        # Check if email is taken
        # ... logic here ...
        current_user.email = user_in.email
    if user_in.avatar_url is not None:
        current_user.avatar_url = user_in.avatar_url
        
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user
