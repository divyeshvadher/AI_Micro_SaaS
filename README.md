# GhostLink - Self-Destructing Smart Links

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
- Node.js 14+ and Yarn
- Python 3.8+
- MongoDB

### Installation

1. **Install Dependencies**

```bash
# Frontend
cd /app/frontend
yarn install

# Backend
cd /app/backend
pip install -r requirements.txt
```

2. **Start Services**

The application uses supervisor to manage services:

```bash
# Restart all services
sudo supervisorctl restart all

# Or individually
sudo supervisorctl restart frontend
sudo supervisorctl restart backend
```

3. **Access the Application**

- Frontend: http://localhost:3000
- Backend API: http://localhost:8001/api

## 📦 Current Version (v0.1 - Frontend Only)

**What's Working:**
- ✅ Complete UI with form and result display
- ✅ Client-side URL validation
- ✅ Natural language parsing for expiry rules (mocked)
- ✅ Loading states and animations
- ✅ Copy-to-clipboard functionality
- ✅ Progress tracking for click-based expiry
- ✅ Responsive design

**What's Mocked:**
- 🔶 Short link generation (uses random codes)
- 🔶 Expiry rule parsing (basic pattern matching)
- 🔶 Click tracking (random current values)
- 🔶 No data persistence

## 🔧 Tech Stack

- **Frontend**: React 19, Tailwind CSS, shadcn/ui components
- **Backend**: FastAPI (ready for integration)
- **Database**: MongoDB (ready for integration)
- **Icons**: Lucide React
- **Font**: Inter (Google Fonts)

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
/app/
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── FormCard.jsx       # Form for creating links
│       │   ├── ResultCard.jsx     # Display created link details
│       │   └── ui/                # shadcn components
│       ├── pages/
│       │   └── Home.jsx           # Main landing page
│       ├── mock.js                # Mock data and functions
│       ├── App.js                 # Root component
│       └── index.css              # Global styles
└── backend/
    └── server.py                  # FastAPI server (ready for routes)
```

## 🐛 Known Limitations

- Currently frontend-only with mocked data
- No actual link shortening or redirection
- No data persistence
- Expiry parsing is basic pattern matching
- No user accounts or link management

## 💡 Tips

- Use realistic URLs (must start with http:// or https://)
- Try different expiry descriptions to see the mock parser in action
- Check the browser console for any errors

---

**Built with React • Currently using mocked data • Ready for backend integration**
