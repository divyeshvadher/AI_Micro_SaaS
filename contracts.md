# GhostLink Backend Integration Contracts

## Overview
Transform GhostLink from mock frontend to full-stack application with AI-powered expiry rule parsing using Gemini API.

## A. API Contracts

### 1. POST /api/links/create
**Purpose**: Create a new smart link with AI-parsed expiry rules

**Request Body**:
```json
{
  "originalUrl": "https://example.com/long-url",
  "expiryText": "expire after 3 clicks or by tomorrow night"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "507f1f77bcf86cd799439011",
    "shortLink": "https://ghost.link/abc123",
    "shortCode": "abc123",
    "originalUrl": "https://example.com/long-url",
    "expiryInfo": {
      "summary": "Expires after 3 clicks or on 26 Nov, 11:59 PM",
      "type": "hybrid",
      "clickLimit": 3,
      "timeLimit": "2024-11-26T23:59:59Z",
      "currentClicks": 0
    },
    "status": "active",
    "createdAt": "2024-11-25T19:30:00Z"
  }
}
```

### 2. GET /api/links/:shortCode
**Purpose**: Get link details for redirection

**Response**:
```json
{
  "success": true,
  "data": {
    "originalUrl": "https://example.com/long-url",
    "status": "active",
    "expiryInfo": {...}
  }
}
```

### 3. POST /api/links/:shortCode/click
**Purpose**: Track a click and check expiry

**Response**:
```json
{
  "success": true,
  "shouldRedirect": true,
  "originalUrl": "https://example.com/long-url",
  "currentClicks": 1,
  "status": "active"
}
```

### 4. GET /api/links/:id/stats
**Purpose**: Get link statistics

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "507f1f77bcf86cd799439011",
    "shortCode": "abc123",
    "originalUrl": "https://example.com/long-url",
    "clicks": 2,
    "status": "active",
    "expiryInfo": {...},
    "createdAt": "2024-11-25T19:30:00Z"
  }
}
```

## B. Data Mocked in mock.js (To Be Replaced)

### Functions to Replace:
1. `generateMockShortLink()` → Backend generates real short codes
2. `parseMockExpiry()` → Gemini AI parses expiry rules
3. `mockCreateLink()` → Real API call to create links

### Mock Data Structure (Current):
```javascript
{
  shortLink: "https://ghost.link/abc123",
  originalUrl: "...",
  expiryInfo: {
    summary: "...",
    type: "clicks" | "time" | "hybrid",
    limit: 3,
    current: 1
  },
  status: "active",
  createdAt: "..."
}
```

## C. Backend Implementation Plan

### 1. MongoDB Models

**Collection: `links`**
```python
{
  "_id": ObjectId,
  "shortCode": str,              # Unique 6-char code
  "originalUrl": str,
  "expiryRules": {
    "summary": str,               # Human-readable
    "type": str,                  # "clicks", "time", "hybrid"
    "clickLimit": int | None,
    "timeLimit": datetime | None,
    "rawInput": str               # Original user input
  },
  "clicks": int,
  "status": str,                  # "active", "expired"
  "createdAt": datetime,
  "expiresAt": datetime | None
}
```

### 2. Gemini AI Integration

**Purpose**: Parse natural language expiry rules

**System Prompt**:
```
You are an expiry rule parser for a link shortener. Parse user input and return structured JSON.

Rules:
- Identify click-based expiry (e.g., "3 clicks", "after 5 clicks")
- Identify time-based expiry (e.g., "24 hours", "tomorrow", "2 days")
- Handle hybrid rules (e.g., "3 clicks or 24 hours")
- Return type: "clicks", "time", or "hybrid"

Output format:
{
  "type": "clicks" | "time" | "hybrid",
  "clickLimit": int | null,
  "timeLimit": "ISO 8601 datetime" | null,
  "summary": "Human-readable expiry description"
}
```

**Example Gemini Call**:
```python
from emergentintegrations.llm.chat import LlmChat, UserMessage

chat = LlmChat(
    api_key=GEMINI_KEY,
    session_id="expiry-parser",
    system_message=SYSTEM_PROMPT
).with_model("gemini", "gemini-2.0-flash")

response = await chat.send_message(
    UserMessage(text=f"Parse: {expiry_text}")
)
```

### 3. Short Code Generation

**Algorithm**: Generate unique 6-character alphanumeric codes
- Use random selection from [a-zA-Z0-9]
- Check MongoDB for uniqueness
- Retry if collision (rare)

### 4. Expiry Logic

**Check expiry on**:
- Every click (POST /api/links/:shortCode/click)
- Before returning link data

**Expiry conditions**:
- Click-based: clicks >= clickLimit
- Time-based: current_time >= timeLimit
- Hybrid: Either condition met

### 5. Backend Files to Create/Update

1. `/app/backend/models.py` - MongoDB models
2. `/app/backend/services/link_service.py` - Business logic
3. `/app/backend/services/ai_parser.py` - Gemini integration
4. `/app/backend/utils/short_code.py` - Code generation
5. `/app/backend/server.py` - Add new routes

## D. Frontend Integration

### Files to Update:
1. `/app/frontend/src/components/FormCard.jsx`
   - Replace `mockCreateLink()` with real API call
   - Use axios to POST to `/api/links/create`

2. `/app/frontend/src/mock.js`
   - Can be deleted or kept for future reference

### API Call Example:
```javascript
const response = await axios.post(`${API}/links/create`, {
  originalUrl: url,
  expiryText: expiryText
});
```

## E. Testing Checklist

- [ ] Gemini API key properly loaded from .env
- [ ] emergentintegrations installed
- [ ] Short codes are unique
- [ ] AI parser handles various expiry formats
- [ ] Click tracking increments correctly
- [ ] Expiry logic works (clicks, time, hybrid)
- [ ] Frontend successfully creates links
- [ ] Result card displays real data
- [ ] Copy to clipboard works with real short links
- [ ] MongoDB stores and retrieves data correctly

## F. Environment Variables

**Backend .env additions**:
```
GEMINI_API_KEY=AIzaSyB6KfWYp9qMigTLmyNQTp7UWC6JiNwAxac
```

## G. Implementation Order

1. ✅ Install emergentintegrations
2. ✅ Add Gemini API key to .env
3. Create MongoDB models
4. Create AI parser service (Gemini)
5. Create short code generator
6. Create link service (business logic)
7. Add API routes to server.py
8. Test backend with curl
9. Update frontend to use real APIs
10. End-to-end testing
