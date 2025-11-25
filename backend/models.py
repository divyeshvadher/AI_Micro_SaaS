from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class ExpiryRules(BaseModel):
    """Expiry rules for a link"""
    summary: str
    type: str  # "clicks", "time", or "hybrid"
    clickLimit: Optional[int] = None
    timeLimit: Optional[datetime] = None
    rawInput: str


class Link(BaseModel):
    """Link model for MongoDB"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    shortCode: str
    originalUrl: str
    expiryRules: ExpiryRules
    clicks: int = 0
    status: str = "active"  # "active" or "expired"
    createdAt: datetime = Field(default_factory=datetime.utcnow)


class CreateLinkRequest(BaseModel):
    """Request model for creating a link"""
    originalUrl: str
    expiryText: str


class CreateLinkResponse(BaseModel):
    """Response model for link creation"""
    success: bool
    data: dict


class ClickResponse(BaseModel):
    """Response model for click tracking"""
    success: bool
    shouldRedirect: bool
    originalUrl: Optional[str] = None
    currentClicks: int
    status: str
