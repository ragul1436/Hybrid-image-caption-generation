
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.api import deps
from backend.app.core.database import get_db
from backend.app.models.db_models import User
from backend.app.schemas.pydantic_schemas import UserResponse

router = APIRouter()

@router.get("/users", response_model=List[UserResponse])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()
