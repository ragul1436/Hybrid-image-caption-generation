
from sqlalchemy import (
    Column, Integer, String, Boolean, ForeignKey, DateTime, Float, Enum, Text, CheckConstraint, Table
)
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import enum
import uuid
from datetime import datetime

class Base(DeclarativeBase):
    pass

class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER)
    avatar_url = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    images = relationship("Image", back_populates="owner", cascade="all, delete-orphan")
    captions = relationship("Caption", back_populates="owner", cascade="all, delete-orphan")
    albums = relationship("Album", back_populates="owner", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="owner", cascade="all, delete-orphan")
    export_logs = relationship("ExportLog", back_populates="owner", cascade="all, delete-orphan")
    caption_ratings = relationship("CaptionRating", back_populates="owner", cascade="all, delete-orphan")

# Many-to-Many association table for Album-Image
album_images_table = Table(
    "album_images",
    Base.metadata,
    Column("album_id", UUID(as_uuid=True), ForeignKey("albums.id", ondelete="CASCADE"), primary_key=True),
    Column("image_id", UUID(as_uuid=True), ForeignKey("images.id", ondelete="CASCADE"), primary_key=True),
)

# Many-to-Many association table for Image-Tag
image_tags_table = Table(
    "image_tags",
    Base.metadata,
    Column("image_id", UUID(as_uuid=True), ForeignKey("images.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

class Image(Base):
    __tablename__ = "images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    filename = Column(String(255), nullable=False)
    original_url = Column(Text, nullable=False)
    file_size = Column(Integer, nullable=True)
    format = Column(String(20), nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    owner = relationship("User", back_populates="images")
    captions = relationship("Caption", back_populates="original_image", cascade="all, delete-orphan")
    albums = relationship("Album", secondary=album_images_table, back_populates="images")
    tags = relationship("Tag", secondary=image_tags_table, back_populates="images")

class Caption(Base):
    __tablename__ = "captions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_id = Column(UUID(as_uuid=True), ForeignKey("images.id", ondelete="CASCADE"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    caption_text = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=True)
    model_used = Column(String(100), nullable=True)
    language = Column(String(50), default="en")
    generation_time = Column(Float, nullable=True)
    decode_method = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    owner = relationship("User", back_populates="captions")
    original_image = relationship("Image", back_populates="captions")
    ratings = relationship("CaptionRating", back_populates="caption", cascade="all, delete-orphan")

class CaptionRating(Base):
    __tablename__ = "caption_ratings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    caption_id = Column(UUID(as_uuid=True), ForeignKey("captions.id", ondelete="CASCADE"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    rating = Column(Integer, CheckConstraint("rating IN (1, -1)"))
    rated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    owner = relationship("User", back_populates="caption_ratings")
    caption = relationship("Caption", back_populates="ratings")

class Album(Base):
    __tablename__ = "albums"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    owner = relationship("User", back_populates="albums")
    images = relationship("Image", secondary=album_images_table, back_populates="albums")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)

    # Relationships
    images = relationship("Image", secondary=image_tags_table, back_populates="tags")

class MLModel(Base):
    __tablename__ = "ml_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    version = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    file_path = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    message = Column(Text, nullable=False)
    type = Column(String(50), nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    owner = relationship("User", back_populates="notifications")

class ExportLog(Base):
    __tablename__ = "export_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    export_type = Column(String(20), nullable=True)
    file_url = Column(Text, nullable=True)
    record_count = Column(Integer, nullable=True)
    exported_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    owner = relationship("User", back_populates="export_logs")
