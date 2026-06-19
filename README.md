# AI Personal CFO

A production-grade AI-powered financial platform that combines the intelligence of a personal CFO with premium fintech UX.

## What’s New in v2.0

- **JWT Authentication**: Full auth system with registration, login, password reset, email verification, and onboarding flow
- **Multi-User Platform**: Every user has isolated data, separate chat history, and personalized AI memory
- **AI Agent with Function Calling**: The AI can actually create, update, and delete expenses, goals, investments, loans, and budgets
- **Notification System**: Smart alerts for overspending, goal milestones, EMI reminders, and budget exceeded
- **World-Class Landing Page**: Premium hero section with 3D CSS transforms, animated feature cards, and CTA
- **Onboarding Flow**: Collects country, currency, income, occupation, risk profile, and financial goals
- **Dark/Light Mode**: Toggle with localStorage persistence
- **Responsive Design**: Mobile drawer, collapsible sidebar, card-based mobile tables
- **Premium UI**: Glassmorphism, KPI cards, progress rings, animated charts, loading skeletons, empty states
- **Edit / Delete**: Every table supports inline editing and soft deletes with confirmation
- **Search / Filter**: Search and filter on all tables
- **Budget Module**: Full budget vs actual tracking with utilization bars
- **AI ChatGPT-Style Chat**: Markdown rendering, typing indicators, conversation persistence, auto-scroll, tool execution

## Tech Stack

**Backend**
- FastAPI + Uvicorn
- SQLAlchemy 2.0 + SQLite (production-ready for PostgreSQL migration)
- Groq API (Llama 3.3 70B) for AI CFO
- Pydantic v2 for validation & response models
- JWT Authentication (python-jose + passlib bcrypt)
- OAuth2 Password Bearer flow

**Frontend**
- React 19 + Vite
- React Router v7
- Chart.js + react-chartjs-2
- Lucide React (icons)
- React Markdown (AI chat formatting)
- Custom CSS Design System (27KB, 200+ utilities)

## Project Structure

```
AI-Money-Manager/
├── backend/
│   ├── main.py              # App entry point + exception handlers + all routers
│   ├── database.py          # Engine, session, DI, FK pragma
│   ├── models.py            # SQLAlchemy models with auth + relationships + notifications
│   ├── schemas.py           # Pydantic request/response models (including auth)
│   ├── auth.py              # JWT tokens, password hashing, OAuth2, get_current_user
│   ├── migrate.py           # Schema migration script (run once before startup)
│   ├── requirements.txt
│   ├── routers/
│   │   ├── auth.py          # Register, login, forgot/reset password, onboarding, me
│   │   ├── dashboard.py     # Dashboard, insights, forecasts, health score (auth-gated)
│   │   ├── expenses.py      # CRUD + search/filter (auth-gated)
│   │   ├── investments.py   # CRUD + search/filter (auth-gated)
│   │   ├── loans.py         # CRUD + debt health (auth-gated)
│   │   ├── goals.py         # CRUD + smart progress (auth-gated)
│   │   ├── budgets.py       # Budget vs actual (auth-gated)
│   │   ├── ai.py            # Chat + advisor endpoints with tool execution
│   │   ├── ai_tools.py      # Direct tool execution endpoint
│   │   ├── notifications.py # Unread count, mark read, delete
│   │   └── users.py         # Admin user management
│   └── services/
│       ├── ai_service.py    # Groq client + system prompt with tool instructions
│       ├── analytics_service.py  # All aggregation logic (DRY)
│       └── agent_tools.py   # AI agent CRUD functions
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Routes: Landing, Login, Register, Onboarding, App (protected)
│   │   ├── index.css        # Complete design system (27KB)
│   │   ├── services/api.js  # Axios with JWT interceptor + 401 redirect
│   │   ├── contexts/
│   │   │   └── AuthContext.jsx  # Auth state, login, register, logout
│   │   ├── hooks/
│   │   │   ├── useTheme.js  # Dark/light mode toggle
│   │   │   └── useFetch.js  # Data fetching hooks
│   │   ├── utils/
│   │   │   └── formatters.js  # Currency, number, date, chart colors
│   │   ├── components/
│   │   │   ├── Layout.jsx       # Sidebar + NotificationBell + Outlet
│   │   │   ├── Sidebar.jsx      # Responsive, collapsible, mobile drawer, user info
│   │   │   ├── NotificationBell.jsx  # Real-time notification bell with dropdown
│   │   │   ├── KpiCard.jsx      # Animated KPI cards
│   │   │   ├── ProgressRing.jsx # SVG circular progress
│   │   │   ├── DataTable.jsx    # Sortable, editable, responsive
│   │   │   ├── EmptyState.jsx   # Empty states with illustrations
│   │   │   ├── Skeleton.jsx     # Loading skeletons
│   │   │   └── GlassCard.jsx
│   │   └── pages/
│   │       ├── Landing.jsx      # World-class landing page with 3D hero
│   │       ├── Login.jsx        # JWT login page
│   │       ├── Register.jsx     # JWT registration page
│   │       ├── Onboarding.jsx   # 3-step onboarding flow
│   │       ├── Dashboard.jsx    # Executive command center
│   │       ├── Expenses.jsx     # + pie charts, category bars, search
│   │       ├── Investments.jsx  # + allocation, ROI colors, search
│   │       ├── Loans.jsx        # + debt health, payoff, search
│   │       ├── Goals.jsx        # + progress rings, visualizer, search
│   │       ├── Budget.jsx       # Budget vs actual with month selector
│   │       └── AIChat.jsx       # ChatGPT-like with markdown, tools, persistence
│   └── package.json
```

## Quick Start

### 1. Backend

```bash
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set your environment variables
# Create a .env file in backend/ with:
# GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# SECRET_KEY=your_super_secret_key_here

# Migrate existing database (if you have one)
python migrate.py

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API docs will be available at `http://localhost:8000/docs`

### 2. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

The app will be at `http://localhost:5173`

### 3. Environment Variables

Create `backend/.env`:

```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SECRET_KEY=your_super_secret_key_change_in_production
```

## API Endpoints

| Resource | Endpoint | Description |
|---|---|---|
| **Auth** | `POST /api/auth/register` | Register new user |
| | `POST /api/auth/login` | Login + JWT tokens |
| | `POST /api/auth/refresh` | Refresh access token |
| | `POST /api/auth/forgot-password` | Request reset token |
| | `POST /api/auth/reset-password` | Reset with token |
| | `GET /api/auth/me` | Current user profile |
| | `PUT /api/auth/me` | Update profile |
| | `POST /api/auth/onboarding` | Complete onboarding |
| | `POST /api/auth/logout` | Logout |
| **Dashboard** | `GET /api/dashboard` | Consolidated KPIs |
| | `GET /api/health-score` | Financial health + rating |
| | `GET /api/net-worth` | Assets / liabilities breakdown |
| | `GET /api/cash-flow` | Monthly cash flow analysis |
| | `GET /api/forecast?months=12` | Financial projections |
| | `GET /api/ai-insights` | Rule-based insights |
| **Expenses** | `POST /api/expenses` | Add expense |
| | `GET /api/expenses` | List (search, filter, date range) |
| | `GET /api/expenses/summary` | Category breakdown |
| | `PUT /api/expenses/{id}` | Update |
| | `DELETE /api/expenses/{id}` | Soft delete |
| **Investments** | `POST /api/investments` | Add investment |
| | `GET /api/investments` | List (type, status filters) |
| | `GET /api/investments/summary` | Portfolio summary + ROI |
| | `PUT /api/investments/{id}` | Update |
| | `DELETE /api/investments/{id}` | Soft delete |
| **Loans** | `POST /api/loans` | Add loan |
| | `GET /api/loans` | List |
| | `GET /api/loan-summary` | Debt burden + payoff projection |
| | `PUT /api/loans/{id}` | Update |
| | `DELETE /api/loans/{id}` | Soft delete |
| **Goals** | `POST /api/goals` | Add goal |
| | `GET /api/goals` | List |
| | `GET /api/goals/summary` | Goal progress summary |
| | `PUT /api/goals/{id}` | Update |
| | `DELETE /api/goals/{id}` | Soft delete |
| **Budgets** | `POST /api/budgets` | Set budget |
| | `GET /api/budgets` | List for month/year |
| | `GET /api/budgets/status` | Budget vs actual |
| | `DELETE /api/budgets/{id}` | Delete |
| **AI** | `POST /api/ai/ask-cfo` | Chat with AI CFO (with tool execution) |
| | `POST /api/ai/ask-cfo/stream` | Streaming response |
| | `GET /api/ai/advisor` | Full financial report |
| | `GET /api/ai/expense-advisor` | Spending analysis |
| | `GET /api/ai/investment-advisor` | Portfolio review |
| | `GET /api/ai/loan-advisor` | Debt strategy |
| | `GET /api/ai/goal-advisor` | Goal planning |
| **AI Tools** | `POST /api/ai/tools/execute` | Direct tool execution |
| **Notifications** | `GET /api/notifications` | List notifications |
| | `POST /api/notifications/mark-read` | Mark all read |
| | `POST /api/notifications/{id}/read` | Mark one read |
| | `DELETE /api/notifications/{id}` | Delete notification |

## Design System

- **Glassmorphism**: `backdrop-filter: blur(20px)` with translucent borders
- **Dark/Light Mode**: Toggle in sidebar, persisted to `localStorage`
- **Animations**: `fadeInUp`, `slideInRight`, staggered delays, 3D CSS transforms
- **Responsive**: Mobile-first, collapsible sidebar, card-based mobile tables
- **Colors**: Indigo + Teal primary palette, semantic green/amber/red states

## Key Improvements Over v1

| Area | v1 | v2 |
|---|---|---|
| **Backend Architecture** | 1,158-line monolithic `main.py` | Modular routers, services, DI |
| **Error Handling** | Plain dicts, 200 OK for errors | `HTTPException`, proper status codes |
| **Validation** | No bounds checking | Pydantic v2 with `Field(..., ge=0)` |
| **Database** | Integer amounts, string dates, no FKs | `Numeric(12,2)`, `DateTime`, relationships |
| **Soft Deletes** | Hard deletes only | `is_deleted` + `deleted_at` on all tables |
| **Authentication** | None | JWT with bcrypt, refresh tokens, OAuth2 |
| **Multi-User** | Hardcoded `user_id=1` | `get_current_user` on every endpoint |
| **AI Agent** | Basic chat only | Function calling, tool execution, memory |
| **Frontend Styling** | Inline styles everywhere | 27KB CSS design system |
| **Responsive** | Fixed 250px sidebar, breaks on mobile | Collapsible sidebar, mobile drawer |
| **Dark Mode** | CSS-only `prefers-color-scheme` | Toggle with localStorage persistence |
| **Edit/Delete** | Not possible | Modal forms + soft delete with confirmation |
| **Search/Filter** | None | Search + filter on all tables |
| **Budget Module** | Missing | Full budget vs actual tracking |
| **Notifications** | Missing | Smart alerts with severity levels |
| **AI Chat** | Plain text, no markdown | ReactMarkdown, typing dots, auto-scroll, tool execution |
| **Landing Page** | None | World-class 3D hero, animations, feature cards |
| **Onboarding** | None | 3-step flow with goals, risk profile, income |
| **Loading States** | Plain text | Skeletons, animated placeholders |
| **Empty States** | Blank tables | Illustrated empty states with CTAs |
| **Currency Formatting** | Raw `₹1234567` | `₹12,34,567` with locale |

## License

MIT
