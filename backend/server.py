from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
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
    return {"message": "XpireLink API - Self-Destructing Smart Links"}

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
        
        expiry = link.get('expiryRules', {})
        time_limit = expiry.get('timeLimit')
        if isinstance(time_limit, str):
            formatted_time_limit = time_limit
        elif time_limit is not None:
            formatted_time_limit = time_limit.isoformat() + 'Z'
        else:
            formatted_time_limit = None

        return {
            "success": True,
            "data": {
                "originalUrl": link['originalUrl'],
                "status": link['status'],
                "expiryInfo": {
                    "summary": expiry.get('summary'),
                    "type": expiry.get('type'),
                    "clickLimit": expiry.get('clickLimit'),
                    "timeLimit": formatted_time_limit,
                    "currentClicks": link.get('clicks', 0)
                }
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting link: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/link/{short_code}")
async def get_link_alias(short_code: str):
    return await get_link(short_code)


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

# Minimal expired HTML page
def expired_html(link: dict) -> str:
    summary = (link.get('expiryRules') or {}).get('summary') or 'This link has expired.'
    return f"""
    <!doctype html>
    <html><head><meta charset='utf-8'><title>Link Expired</title>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <style>
    body{{font-family:system-ui,-apple-system,Segoe UI,Roboto;display:flex;align-items:center;justify-content:center;height:100vh;background:#fafafa;color:#111}}
    .card{{background:#fff;border:1px solid #e5e7eb;border-radius:16px;box-shadow:0 10px 25px rgba(0,0,0,0.08);max-width:560px;width:90%;padding:24px}}
    .badge{{display:inline-block;padding:4px 10px;border-radius:9999px;background:#fee2e2;color:#991b1b;font-weight:600;font-size:12px;margin-bottom:8px}}
    .title{{font-size:20px;font-weight:700;margin:0 0 8px}}
    .desc{{font-size:14px;color:#374151;margin:0 0 12px}}
    </style></head>
    <body>
      <div class='card'>
        <div class='badge'>Expired</div>
        <h1 class='title'>This XpireLink has expired</h1>
        <p class='desc'>{summary}</p>
      </div>
    </body></html>
    """

# Redirect short code at root
@app.get("/{short_code}")
async def redirect_short_code(short_code: str):
    try:
        result = await track_click(db, short_code)
        if result.get("shouldRedirect") and result.get("originalUrl"):
            return RedirectResponse(url=result["originalUrl"], status_code=307)
        link = await get_link_by_short_code(db, short_code)
        return HTMLResponse(content=expired_html(link or {}), status_code=410)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error redirecting: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/l/{short_code}")
async def redirect_alias(short_code: str):
    return await redirect_short_code(short_code)