from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
import logging
from models import Link, ExpiryRules, CreateLinkRequest
from utils.short_code import generate_unique_short_code
from services.ai_parser import parse_expiry_with_gemini

logger = logging.getLogger(__name__)


async def create_link(db: AsyncIOMotorDatabase, request: CreateLinkRequest) -> dict:
    """
    Create a new smart link with AI-parsed expiry rules.
    
    Args:
        db: MongoDB database instance
        request: Create link request with originalUrl and expiryText
    
    Returns:
        Dictionary with created link data
    """
    try:
        # Generate unique short code
        short_code = await generate_unique_short_code(db)
        logger.info(f"Generated short code: {short_code}")
        
        # Parse expiry rules using Gemini AI
        parsed_expiry = await parse_expiry_with_gemini(request.expiryText)
        logger.info(f"Parsed expiry rules: {parsed_expiry}")
        
        # Create expiry rules object
        expiry_rules = ExpiryRules(
            summary=parsed_expiry['summary'],
            type=parsed_expiry['type'],
            clickLimit=parsed_expiry['clickLimit'],
            timeLimit=datetime.fromisoformat(parsed_expiry['timeLimit'].replace('Z', '+00:00')) if parsed_expiry['timeLimit'] else None,
            rawInput=request.expiryText
        )
        
        # Create link object
        link = Link(
            shortCode=short_code,
            originalUrl=request.originalUrl,
            expiryRules=expiry_rules,
            clicks=0,
            status="active"
        )
        
        # Save to MongoDB
        link_dict = link.dict()
        await db.links.insert_one(link_dict)
        logger.info(f"Link created: {short_code}")
        
        # Return response
        return {
            "id": link.id,
            "shortLink": f"https://ghost.link/{short_code}",
            "shortCode": short_code,
            "originalUrl": link.originalUrl,
            "expiryInfo": {
                "summary": expiry_rules.summary,
                "type": expiry_rules.type,
                "clickLimit": expiry_rules.clickLimit,
                "timeLimit": expiry_rules.timeLimit.isoformat() + 'Z' if expiry_rules.timeLimit else None,
                "currentClicks": link.clicks
            },
            "status": link.status,
            "createdAt": link.createdAt.isoformat() + 'Z'
        }
        
    except Exception as e:
        logger.error(f"Error creating link: {e}")
        raise


async def get_link_by_short_code(db: AsyncIOMotorDatabase, short_code: str) -> dict:
    """
    Get link details by short code.
    
    Args:
        db: MongoDB database instance
        short_code: The short code to look up
    
    Returns:
        Dictionary with link data or None if not found
    """
    link = await db.links.find_one({"shortCode": short_code})
    return link


async def track_click(db: AsyncIOMotorDatabase, short_code: str) -> dict:
    """
    Track a click on a link and check if it should expire.
    
    Args:
        db: MongoDB database instance
        short_code: The short code that was clicked
    
    Returns:
        Dictionary with click tracking result
    """
    try:
        # Get link
        link = await db.links.find_one({"shortCode": short_code})
        if not link:
            return {
                "success": False,
                "shouldRedirect": False,
                "currentClicks": 0,
                "status": "not_found"
            }
        
        # Check if already expired
        if link['status'] == 'expired':
            return {
                "success": True,
                "shouldRedirect": False,
                "originalUrl": None,
                "currentClicks": link['clicks'],
                "status": "expired"
            }
        
        # Increment click count
        new_click_count = link['clicks'] + 1
        
        # Check expiry conditions
        should_expire = False
        expiry_rules = link['expiryRules']
        
        # Check click limit
        if expiry_rules['clickLimit'] and new_click_count >= expiry_rules['clickLimit']:
            should_expire = True
            logger.info(f"Link {short_code} reached click limit")
        
        # Check time limit
        if expiry_rules['timeLimit']:
            time_limit = datetime.fromisoformat(expiry_rules['timeLimit'].replace('Z', '+00:00'))
            if datetime.utcnow() >= time_limit:
                should_expire = True
                logger.info(f"Link {short_code} reached time limit")
        
        # Update link
        update_data = {
            "clicks": new_click_count
        }
        if should_expire:
            update_data["status"] = "expired"
        
        await db.links.update_one(
            {"shortCode": short_code},
            {"$set": update_data}
        )
        
        return {
            "success": True,
            "shouldRedirect": not should_expire,
            "originalUrl": link['originalUrl'] if not should_expire else None,
            "currentClicks": new_click_count,
            "status": "expired" if should_expire else "active"
        }
        
    except Exception as e:
        logger.error(f"Error tracking click: {e}")
        raise


async def get_link_stats(db: AsyncIOMotorDatabase, link_id: str) -> dict:
    """
    Get statistics for a link.
    
    Args:
        db: MongoDB database instance
        link_id: The link ID
    
    Returns:
        Dictionary with link statistics
    """
    link = await db.links.find_one({"id": link_id})
    if not link:
        return None
    
    return {
        "id": link['id'],
        "shortCode": link['shortCode'],
        "originalUrl": link['originalUrl'],
        "clicks": link['clicks'],
        "status": link['status'],
        "expiryInfo": {
            "summary": link['expiryRules']['summary'],
            "type": link['expiryRules']['type'],
            "clickLimit": link['expiryRules']['clickLimit'],
            "timeLimit": link['expiryRules']['timeLimit'],
            "currentClicks": link['clicks']
        },
        "createdAt": link['createdAt'].isoformat() + 'Z' if isinstance(link['createdAt'], datetime) else link['createdAt']
    }
