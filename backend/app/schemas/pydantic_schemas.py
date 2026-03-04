
from pydantic import BaseModel, EmailStr, Field, ConfigDict, computed_field
from typing import Optional, List, Literal
from uuid import UUID
from datetime import datetime

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None

class TokenData(BaseModel):
    id: Optional[UUID] = None
    role: Optional[str] = None

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)

class UserCreate(UserBase):
    password: str = Field(min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: UUID
    role: str
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Image Schemas ---
class ImageBase(BaseModel):
    filename: str
    original_url: str
    file_size: Optional[int] = None
    format: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None

class ImageCreate(ImageBase):
    pass

class ImageResponse(ImageBase):
    id: UUID
    user_id: UUID
    uploaded_at: datetime
    # Optionally include brief caption info?
    
    model_config = ConfigDict(from_attributes=True)

# --- Caption Schemas ---
class CaptionBase(BaseModel):
    caption_text: str
    confidence_score: Optional[float] = None
    model_used: Optional[str] = None
    language: str = "en"
    generation_time: Optional[float] = None
    decode_method: Optional[str] = None
    # Allow fields starting with "model_" without triggering protected namespace warnings
    model_config = ConfigDict(protected_namespaces=())

class CaptionCreate(CaptionBase):
    image_id: UUID

class CaptionUpdate(BaseModel):
    caption_text: Optional[str] = None

class CaptionResponse(CaptionBase):
    id: UUID
    image_id: UUID
    user_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CaptionGenerateRequest(BaseModel):
    image_id: UUID
    model: str = "blip"
    language: str = "en"
    decode_method: str = "beam_search"
    caption_length: str = "medium" # short, medium, detailed

class CaptionRatingCreate(BaseModel):
    rating: int = Field(description="1 for like, -1 for dislike")

# --- Album Schemas ---
class AlbumBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: Optional[str] = None

class AlbumCreate(AlbumBase):
    pass

class AlbumUpdate(AlbumBase):
    name: Optional[str] = None
    description: Optional[str] = None

class AlbumResponse(AlbumBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    images: List[ImageResponse] = []

    @computed_field
    @property
    def image_count(self) -> int:
        return len(self.images)

    model_config = ConfigDict(from_attributes=True)

class AlbumAddImages(BaseModel):
    image_ids: List[UUID]

# --- ML Model Schemas ---
class MLModelBase(BaseModel):
    name: str
    version: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    is_default: bool = False

class MLModelCreate(MLModelBase):
    file_path: str

class MLModelResponse(MLModelBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Dashboard/Stats Schemas ---
class StatsResponse(BaseModel):
    total_images: int
    total_captions: int
    total_models: int
    storage_usage_mb: float

class ActivityData(BaseModel):
    date: str
    uploads: int
    captions: int

class KeywordData(BaseModel):
    keyword: str
    count: int

class ModelUsageData(BaseModel):
    model_name: str
    usage_count: int
    # Allow fields starting with "model_" without triggering protected namespace warnings
    model_config = ConfigDict(protected_namespaces=())

# --- Notification Schemas ---
class NotificationResponse(BaseModel):
    id: UUID
    message: str
    type: Optional[str]
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

