import random
import string
from motor.motor_asyncio import AsyncIOMotorDatabase


async def generate_unique_short_code(db: AsyncIOMotorDatabase, length: int = 6) -> str:
    """
    Generate a unique short code for link shortening.
    
    Args:
        db: MongoDB database instance
        length: Length of the short code (default 6)
    
    Returns:
        A unique alphanumeric short code
    """
    chars = string.ascii_letters + string.digits
    max_attempts = 10
    
    for _ in range(max_attempts):
        short_code = ''.join(random.choice(chars) for _ in range(length))
        
        # Check if code already exists
        existing = await db.links.find_one({"shortCode": short_code})
        if not existing:
            return short_code
    
    # If we couldn't generate unique code in max_attempts, try with longer code
    return await generate_unique_short_code(db, length + 1)
