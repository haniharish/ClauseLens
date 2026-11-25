# ClauseLens — Frontend

**Context-Aware Terms & Conditions Risk Summarization with Version-Diff Personalized Alerts**

ClauseLens is a modern dark-themed React + Tailwind CSS SaaS frontend designed for an AI-powered legal document intelligence platform. It enables users to analyze Terms & Conditions and Privacy Policies, inspect plain-language AI clause explanations tailored to their user profile, monitor policy URLs, and review semantic version diffs.

---

## Tech Stack

- **React 18** + **Vite 6**
- **Tailwind CSS 3** (dark SaaS palette: `#080A12` background, `#0D0F19` sidebar, `#141725` cards, `#9B7AFF` purple accent)
- **React Router DOM** (client-side routing)
- **Lucide React** (icons)
- **Recharts** (Risk Distribution donut chart & 6-month Risk Trend area chart)
- **React Dropzone** (drag-and-drop PDF upload)
- **Axios** (API client configured for Django REST Framework + JWT)
- **React Hot Toast** (notifications)

---

## Project Structure

```text
clauselens-frontend/
├── public/
│   └── favicon.svg
├── src/
│   ├── components/
│   │   ├── analysis/        # ClauseCard
│   │   ├── charts/          # RiskDonutChart, RiskTrendChart
│   │   ├── common/          # Badge, Modal, EmptyState, DemoBanner
│   │   ├── dashboard/       # StatCard, RiskOverviewCard, RecentDocumentsTable, etc.
│   │   ├── layout/          # Sidebar, TopNavbar, DashboardLayout
│   │   └── notifications/   # NotificationItem
│   ├── context/             # AppContext (theme, auth, documents, policies, notifications, profile)
│   ├── data/                # mockData.js (demonstration datasets)
│   ├── hooks/               # useDebounce.js
│   ├── pages/               # Dashboard, AnalyzeDocument, AnalysisResults, MyDocuments,
│   │                        # RiskAnalysis, PolicyMonitoring, VersionHistory, Notifications,
│   │                        # Profile, Settings, Login, Register
│   ├── services/            # api.js, authService.js, documentService.js, analysisService.js, notificationService.js
│   ├── utils/               # helpers.js
│   ├── App.jsx
│   ├── index.css
│   └── main.jsx
├── .env.example
├── package.json
└── README.md
```

---

## Installation & Running Locally

1. **Install dependencies**

```bash
cd clauselens-frontend
npm install
```

2. **Configure environment variables (optional)**

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Default values:
- `VITE_API_BASE_URL=http://localhost:8000/api/v1`
- `VITE_USE_MOCK_API=true` (uses local demonstration mock data when the Django backend is offline)

3. **Start the development server**

```bash
npm run dev
```

4. **Build for production**

```bash
npm run build
npm run preview
```

---

## Backend Integration Notes

- Set `VITE_USE_MOCK_API=false` and point `VITE_API_BASE_URL` to your Django REST Framework server.
- `src/services/api.js` automatically attaches JWT `Bearer` tokens from `localStorage` (`clauselens_access_token`) and handles `401` token refresh via `/auth/token/refresh/`.
- Demonstration mock data is clearly labeled throughout the UI and separated into `src/data/mockData.js`.
