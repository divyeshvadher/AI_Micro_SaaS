import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

SYSTEM_PROMPT = """You are an expiry rule parser for a link shortener called XpireLink. Your job is to parse user's natural language input describing when a link should expire and return structured JSON.

Rules:
- Identify click-based expiry (e.g., "3 clicks", "after 5 clicks", "5 times")
- Identify time-based expiry (e.g., "24 hours", "tomorrow", "2 days", "next week")
- Handle hybrid rules (e.g., "3 clicks or 24 hours", "5 clicks or by tomorrow")
- Current date and time: {current_time}

Output ONLY valid JSON in this exact format (no markdown, no code blocks, just JSON):
{{
  "type": "clicks" | "time" | "hybrid",
  "clickLimit": number or null,
  "timeLimit": "ISO 8601 datetime string" or null,
  "summary": "Human-readable expiry description"
}}

Examples:
Input: "expire after 3 clicks"
Output: {{"type": "clicks", "clickLimit": 3, "timeLimit": null, "summary": "Expires after 3 clicks"}}

Input: "expire in 24 hours"
Output: {{"type": "time", "clickLimit": null, "timeLimit": "2024-11-26T19:30:00Z", "summary": "Expires in 24 hours (Nov 26, 7:30 PM)"}}

Input: "expire after 5 clicks or by tomorrow"
Output: {{"type": "hybrid", "clickLimit": 5, "timeLimit": "2024-11-26T23:59:59Z", "summary": "Expires after 5 clicks or by tomorrow (Nov 26, 11:59 PM)"}}

Be precise with dates and times. Return ONLY the JSON, nothing else."""


async def parse_expiry_with_gemini(expiry_text: str) -> dict:
    """
    Parse natural language expiry text using Gemini AI.
    
    Args:
        expiry_text: Natural language description of expiry rules
    
    Returns:
        Dictionary with parsed expiry rules
    """
    try:
        current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        system_message = SYSTEM_PROMPT.format(current_time=current_time)

        if not GEMINI_API_KEY:
            raise ValueError("Missing GEMINI_API_KEY")

        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
        except Exception as e:
            raise e

        chat = LlmChat(
            api_key=GEMINI_API_KEY,
            session_id="expiry-parser",
            system_message=system_message
        ).with_model("gemini", "gemini-2.0-flash")

        user_message = UserMessage(
            text=f"Parse this expiry rule: {expiry_text}"
        )

        response = await chat.send_message(user_message)
        logger.info(f"Gemini raw response: {response}")
        
        cleaned_response = response.strip()
        if cleaned_response.startswith('```'):
            lines = cleaned_response.split('\n')
            cleaned_response = '\n'.join(lines[1:-1] if len(lines) > 2 else lines)
            cleaned_response = cleaned_response.replace('```json', '').replace('```', '').strip()
        
        parsed_data = json.loads(cleaned_response)
        required_fields = ['type', 'clickLimit', 'timeLimit', 'summary']
        if not all(field in parsed_data for field in required_fields):
            raise ValueError("Missing required fields in AI response")
        
        return parsed_data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response as JSON: {e}")
        logger.error(f"Raw response: {response}")
        return _fallback_parse(expiry_text)
    except Exception as e:
        logger.error(f"Error parsing expiry with Gemini: {e}")
        return _fallback_parse(expiry_text)


def _fallback_parse(expiry_text: str) -> dict:
    """
    Fallback parser if Gemini fails.
    Basic pattern matching for common cases.
    """
    text = expiry_text.lower()
    
    # Click-based expiry
    if 'click' in text:
        import re
        click_match = re.search(r'(\d+)\s*click', text)
        clicks = int(click_match.group(1)) if click_match else 3
        return {
            "type": "clicks",
            "clickLimit": clicks,
            "timeLimit": None,
            "summary": f"Expires after {clicks} clicks"
        }
    
    # Time-based expiry
    if 'min' in text or 'minute' in text or 'minutes' in text:
        import re
        minute_match = re.search(r'(\d+)\s*(min|mins|minute|minutes)', text)
        minutes = int(minute_match.group(1)) if minute_match else 1
        expiry_time = datetime.utcnow() + timedelta(minutes=minutes)
        return {
            "type": "time",
            "clickLimit": None,
            "timeLimit": expiry_time.isoformat() + 'Z',
            "summary": f"Expires in {minutes} minute{'s' if minutes != 1 else ''}"
        }
    if 'hour' in text:
        import re
        hour_match = re.search(r'(\d+)\s*hour', text)
        hours = int(hour_match.group(1)) if hour_match else 24
        expiry_time = datetime.utcnow() + timedelta(hours=hours)
        return {
            "type": "time",
            "clickLimit": None,
            "timeLimit": expiry_time.isoformat() + 'Z',
            "summary": f"Expires in {hours} hours"
        }
    
    if 'day' in text:
        import re
        day_match = re.search(r'(\d+)\s*day', text)
        days = int(day_match.group(1)) if day_match else 1
        expiry_time = datetime.utcnow() + timedelta(days=days)
        return {
            "type": "time",
            "clickLimit": None,
            "timeLimit": expiry_time.isoformat() + 'Z',
            "summary": f"Expires in {days} days"
        }
    
    if 'tomorrow' in text:
        expiry_time = datetime.utcnow() + timedelta(days=1)
        expiry_time = expiry_time.replace(hour=23, minute=59, second=59)
        return {
            "type": "time",
            "clickLimit": None,
            "timeLimit": expiry_time.isoformat() + 'Z',
            "summary": "Expires tomorrow at 11:59 PM"
        }
    
    # Default: 7 days
    expiry_time = datetime.utcnow() + timedelta(days=7)
    return {
        "type": "time",
        "clickLimit": None,
        "timeLimit": expiry_time.isoformat() + 'Z',
        "summary": "Expires in 7 days"
    }
