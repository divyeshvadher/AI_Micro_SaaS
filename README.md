# XpireLink — AI-Powered Self-Destructing Links

Create smart links that automatically expire based on custom rules described in natural language.

## 🎯 Features

- **Natural Language Expiry Rules** - Describe expiry conditions in plain English (e.g., "expire after 3 clicks or by tomorrow night")
- **Smart Link Generation** - Convert any URL into a short, trackable link
- **Click Tracking** - Monitor usage with progress indicators
- **Flexible Expiry Options** - Support for click-based, time-based, and hybrid expiry rules
- **Modern UI** - Clean, responsive design with micro-animations
- **Real-time Validation** - Client-side form validation with helpful error messages

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and Yarn
- Python 3.10+
- MongoDB (optional; in-memory fallback is used if unavailable)
- Google Gemini API key (for AI expiry parsing)

### Setup

1. **Environment**
```powershell
# Backend (.env in backend/)
setx MONGO_URL "mongodb://localhost:27017"
setx DB_NAME "xpirelink"
setx GEMINI_API_KEY "<your_api_key>"

# Frontend (.env in frontend/)
setx REACT_APP_BACKEND_URL "http://localhost:8001"
```

2. **Install Dependencies**
```powershell
# Backend
cd .\backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd ..\frontend
yarn install
```

3. **Start Services**
```powershell
# Backend
cd .\backend
.\.venv\Scripts\activate
python -m uvicorn server:app --host 0.0.0.0 --port 8001

# Frontend (in a separate shell)
cd .\frontend
yarn start
```

2. **Start Services**

Use the commands above to run backend (Uvicorn) and frontend (CRACO). Supervisor is not required for local development.

3. **Access the Application**

- Frontend: http://localhost:3000
- Backend API: http://localhost:8001/api

## 🔗 API Endpoints

- `POST /api/links/create` — Create a smart link with parsed expiry rules
- `GET /api/links/{short_code}` — Fetch live metadata: status, clickLimit, timeLimit, currentClicks
- `GET /api/link/{short_code}` — Alias for the above
- `POST /api/links/{short_code}/click` — Increment click count and evaluate expiry
- `GET /{short_code}` — Redirect to the original URL when active; returns an expired HTML page once expired
- `GET /l/{short_code}` — Alias redirect route

Expiry conditions:
- Expired when `clicks >= clickLimit` or current time is past `timeLimit`
- Status flips to `expired` and further accesses show the expired page (no redirects)

## 🔧 Tech Stack

- **Frontend**: React (CRACO dev), Tailwind CSS, shadcn/ui components, Lucide React
- **Backend**: FastAPI, Uvicorn, Pydantic, Starlette CORS
- **Data**: MongoDB via Motor (async); in-memory fallback when MongoDB is unavailable
- **AI/NLP**: Gemini via `emergentintegrations.llm.chat` with `GEMINI_API_KEY`
- **Config**: `python-dotenv` for environment variables

## 📝 Usage Examples

### Example Expiry Rules

The mock parser currently recognizes:

- `"expire after 3 clicks"` → Click-based expiry
- `"expire in 24 hours"` → Time-based expiry
- `"expire in 2 days"` → Multi-day expiry
- `"expire by tomorrow night"` → Specific time expiry
- `"expire after 5 clicks or by tomorrow"` → Hybrid rules

## 🎨 Design Principles

- Modern cyan/teal color scheme (avoiding typical purple/blue)
- Generous spacing and clean layouts
- Micro-animations for better UX
- Proper color contrast for accessibility
- No hero background images (clean, focused design)
- Inter font for modern typography

## 🔮 Next Steps (Backend Integration)

To transform this into a full-featured application:

1. **Backend API Development**
   - Short URL generation and storage
   - Real expiry rule parsing (potentially with AI/NLP)
   - Click tracking and analytics
   - Link expiration logic

2. **Database Schema**
   - Links collection (originalUrl, shortCode, expiryRules, clicks, status)
   - Analytics collection (click history, timestamps, referrers)

3. **Advanced Features**
   - Custom domains
   - Link analytics dashboard
   - User authentication
   - Link management (edit, delete, archive)
   - QR code generation
   - Password protection

## 📂 Project Structure

```
AI_Micro_SaaS/
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── FormCard.jsx       # Form for creating links
│       │   ├── ResultCard.jsx     # Display created link details
│       │   └── ui/                # UI primitives
│       ├── pages/
│       │   └── Home.jsx           # Main landing page
│       ├── App.js                 # Root component
│       └── index.css              # Global styles
└── backend/
    ├── server.py                  # FastAPI app & routes
    └── services/
        ├── link_service.py        # Create/fetch/redirect/expiry logic
        └── ai_parser.py           # Gemini + fallback expiry parsing
```

## 🐛 Known Limitations

- MongoDB is optional; when unavailable, in-memory storage is used (data resets on restart)
- Gemini parsing requires `GEMINI_API_KEY`; fallback parser covers common phrases
- No authentication or analytics dashboard yet

## 💡 Tips

- Use realistic URLs (must start with http:// or https://)
- Try different expiry descriptions to see the mock parser in action
- Check the browser console for any errors

---

**Built with React + FastAPI • Live backend with AI parsing • MongoDB optional (in-memory fallback)**