from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List
import uuid
from datetime import datetime, timezone

# Import our custom modules
from models import CreateLinkRequest, CreateLinkResponse, ClickResponse
from services.link_service import create_link, get_link_by_short_code, track_click, get_link_stats


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "GhostLink API - Self-Destructing Smart Links"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks


# GhostLink Routes
@api_router.post("/links/create", response_model=CreateLinkResponse)
async def create_smart_link(request: CreateLinkRequest):
    """
    Create a new smart link with AI-powered expiry rule parsing.
    """
    try:
        link_data = await create_link(db, request)
        return CreateLinkResponse(
            success=True,
            data=link_data
        )
    except Exception as e:
        logger.error(f"Error creating link: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/links/{short_code}")
async def get_link(short_code: str):
    """
    Get link details by short code.
    """
    try:
        link = await get_link_by_short_code(db, short_code)
        if not link:
            raise HTTPException(status_code=404, detail="Link not found")
        
        return {
            "success": True,
            "data": {
                "originalUrl": link['originalUrl'],
                "status": link['status'],
                "expiryInfo": link['expiryRules']
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting link: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/links/{short_code}/click", response_model=ClickResponse)
async def track_link_click(short_code: str):
    """
    Track a click on a link and check expiry.
    """
    try:
        result = await track_click(db, short_code)
        return ClickResponse(**result)
    except Exception as e:
        logger.error(f"Error tracking click: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/links/stats/{link_id}")
async def get_link_statistics(link_id: str):
    """
    Get statistics for a specific link.
    """
    try:
        stats = await get_link_stats(db, link_id)
        if not stats:
            raise HTTPException(status_code=404, detail="Link not found")
        
        return {
            "success": True,
            "data": stats
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()