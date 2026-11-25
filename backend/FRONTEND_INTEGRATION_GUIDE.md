# ClauseLens – React Frontend Integration Guide

**Author:** Member 2 (Backend Lead)  
**Target:** Member 1 (Frontend Lead – React.js + Tailwind CSS)  
**Base URL:** `http://localhost:8000/api/`  
**Swagger UI:** `http://localhost:8000/api/docs/`  
**Standard Response Envelope:**
```typescript
interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
  errors?: Record<string, string[] | string>;
}
```

---

## 1. Authentication & Axios Setup

### Token Storage
Store the `access` and `refresh` tokens in `localStorage` or secure cookies. Include the `access` token in all authorized HTTP requests:
```http
Authorization: Bearer <access_token>
```

### Axios Interceptor Example (`src/api/client.js`)
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT access token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Automatic token refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refresh = localStorage.getItem('refresh_token');
        const res = await axios.post('http://localhost:8000/api/auth/token/refresh/', { refresh });
        const newAccess = res.data.data.access;
        localStorage.setItem('access_token', newAccess);
        originalRequest.headers.Authorization = `Bearer ${newAccess}`;
        return api(originalRequest);
      } catch (refreshErr) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
```

---

## 2. API Endpoints by Frontend Page

### Page 1: Login & Registration

#### Registration: `POST /api/auth/register/`
```json
// Request
{
  "username": "alex",
  "full_name": "Alex Smith",
  "email": "alex@example.com",
  "password": "Password123!",
  "password_confirm": "Password123!"
}
// Response 201
{
  "success": true,
  "message": "Account created successfully.",
  "data": {
    "user": { "id": 1, "username": "alex", "email": "alex@example.com", "full_name": "Alex Smith" },
    "access": "eyJhbG...",
    "refresh": "eyJhbG..."
  }
}
```

#### Login: `POST /api/auth/login/`
```json
// Request
{
  "email": "alex@example.com",
  "password": "Password123!"
}
// Response 200
{
  "success": true,
  "message": "Login successful.",
  "data": {
    "access": "eyJhbG...",
    "refresh": "eyJhbG..."
  }
}
```

---

### Page 2: Dashboard

#### `GET /api/dashboard/`
Returns all metrics, risk distribution chart data, and recent activity calculated live from the database.
```json
{
  "success": true,
  "message": "Dashboard data retrieved.",
  "data": {
    "documents_analyzed": 14,
    "high_risk_clauses": 9,
    "policies_monitored": 4,
    "changes_detected": 6,
    "risk_distribution": {
      "high": 9,
      "medium": 12,
      "low": 18
    },
    "recent_documents": [
      {
        "id": 5,
        "document_name": "Spotify Terms of Service",
        "document_type": "url",
        "status": "completed",
        "uploaded_at": "2026-11-25T10:00:00Z"
      }
    ],
    "recent_changes": [
      {
        "id": 2,
        "document": 5,
        "change_type": "modified",
        "change_direction": "less_favorable",
        "magnitude": 0.85,
        "alert_score": 0.72,
        "detected_at": "2026-11-25T12:00:00Z"
      }
    ],
    "recent_notifications": [
      {
        "id": 1,
        "title": "Policy Update: Third-Party Data Sharing",
        "message": "Spotify's terms are now less favourable regarding ad tracking.",
        "severity": "high",
        "is_read": false,
        "created_at": "2026-11-25T12:05:00Z"
      }
    ]
  }
}
```

---

### Page 3: User Profile

#### `GET /api/profile/` | `POST /api/profile/` | `PUT /api/profile/` | `PATCH /api/profile/`
```json
// Request (POST / PUT / PATCH)
{
  "age_group": "18_64", // Options: "under_13" | "13_17" | "18_64" | "65_plus"
  "intended_use": ["student", "freelancer"], // Array of: "personal", "student", "freelancer", "business", "parent_of_minor"
  "jurisdiction": "india" // Options: "india" | "eu" | "usa" | "other"
}

// Response 200/201
{
  "success": true,
  "data": {
    "age_group": "18_64",
    "intended_use": ["student", "freelancer"],
    "jurisdiction": "india",
    "created_at": "2026-11-25T09:00:00Z",
    "updated_at": "2026-11-25T10:30:00Z"
  }
}
```

---

### Page 4: Document Upload

#### PDF Upload: `POST /api/documents/upload/`
Must use `multipart/form-data`:
```javascript
const formData = new FormData();
formData.append('file', fileObject);
formData.append('document_name', 'OpenAI Terms');
const res = await api.post('/documents/upload/', formData, {
  headers: { 'Content-Type': 'multipart/form-data' },
  onUploadProgress: (progressEvent) => {
    const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
    console.log(percentCompleted);
  }
});
```

#### Policy URL Submission: `POST /api/documents/url/`
```json
// Request
{
  "policy_url": "https://openai.com/policies/terms-of-use",
  "document_name": "OpenAI Terms of Use"
}
```

---

### Page 5: My Documents

#### `GET /api/documents/?page=1&page_size=20`
```json
{
  "success": true,
  "data": {
    "count": 12,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "document_name": "OpenAI Terms of Use",
        "document_type": "url",
        "file_url": null,
        "policy_url": "https://openai.com/policies/terms-of-use",
        "status": "completed", // "uploaded" | "processing" | "completed" | "failed"
        "uploaded_at": "2026-11-25T08:00:00Z",
        "updated_at": "2026-11-25T08:02:15Z"
      }
    ]
  }
}
```

#### Polling Status for Pending Uploads:
`GET /api/documents/{id}/status/` returns `{ "status": "processing" }`. Poll every 3 seconds until status is `"completed"` or `"failed"`.

---

### Page 6: Analysis Results

#### 1. Summary: `GET /api/analysis/documents/{id}/result/`
```json
{
  "success": true,
  "data": {
    "id": 1,
    "document": 1,
    "total_clauses": 24,
    "high_risk_count": 5,
    "medium_risk_count": 11,
    "low_risk_count": 8,
    "overall_risk_score": 0.68,
    "analysis_status": "completed"
  }
}
```

#### 2. Clause List: `GET /api/analysis/documents/{id}/clauses/?page=1`
```json
{
  "success": true,
  "data": {
    "count": 24,
    "results": [
      {
        "id": 101,
        "clause_title": "Arbitration and Class Action Waiver",
        "original_text": "You agree that all disputes will be resolved by binding arbitration...",
        "category": "arbitration",
        "severity": 0.92,
        "simple_explanation": "You waive your right to sue in court or join class actions.",
        "created_at": "2026-11-25T08:02:00Z"
      }
    ]
  }
}
```

---

### Page 7: Personalized Risk Analysis

#### `GET /api/personalization/documents/{id}/risks/`
Calculated dynamically based on user's active profile:
```json
{
  "success": true,
  "data": {
    "count": 24,
    "results": [
      {
        "id": 501,
        "clause": 101,
        "clause_title": "Arbitration and Class Action Waiver",
        "clause_category": "arbitration",
        "clause_severity": 0.92,
        "relevance_score": 0.88,
        "risk_level": "High",
        "why_it_matters": "High impact for individual users in India where arbitration costs exceed typical dispute amounts."
      }
    ]
  }
}
```

---

### Page 8: Policy Monitoring

#### Add to Monitoring: `POST /api/monitoring/`
```json
{
  "policy_url": "https://discord.com/terms",
  "policy_name": "Discord Terms of Service",
  "check_interval_hours": 24
}
```

#### List: `GET /api/monitoring/`
#### Pause / Resume: `PATCH /api/monitoring/{id}/` with `{ "monitoring_status": "paused" | "active" }`
#### Delete: `DELETE /api/monitoring/{id}/`

---

### Page 9: Version History & Diff Comparison

#### Version List: `GET /api/versions/{document_id}/`
#### Version Compare: `GET /api/versions/{document_id}/compare/`
Returns the previous and latest version details, plus all clause-level changes detected:
```json
{
  "success": true,
  "data": {
    "old_version": { "version_number": 1, "content_hash": "a1b2...", "fetched_at": "..." },
    "new_version": { "version_number": 2, "content_hash": "c3d4...", "fetched_at": "..." },
    "changes": [
      {
        "id": 8,
        "change_type": "modified", // "added" | "removed" | "modified" | "unchanged"
        "change_direction": "less_favorable", // "more_favorable" | "neutral" | "less_favorable" | "unclear"
        "magnitude": 0.75,
        "alert_score": 0.62
      }
    ]
  }
}
```

---

### Page 10: Notifications

#### List: `GET /api/notifications/?unread=true`
#### Mark Single Read: `PATCH /api/notifications/{id}/read/`
#### Mark All Read: `PATCH /api/notifications/read-all/`
#### Delete: `DELETE /api/notifications/{id}/`

---

### Page 11: Settings

#### Change Password: `POST /api/auth/change-password/`
```json
{
  "old_password": "OldPassword123!",
  "new_password": "NewPassword456!",
  "new_password_confirm": "NewPassword456!"
}
```

---

## 3. Tailwind Styling Tips for Risk Levels

| Risk Level | Badge Color | Hex / Class |
|------------|-------------|-------------|
| **High** ($\ge 0.67$) | Red | `bg-red-100 text-red-800 border-red-300` |
| **Medium** ($0.34 - 0.66$) | Amber / Yellow | `bg-amber-100 text-amber-800 border-amber-300` |
| **Low** ($< 0.34$) | Emerald / Green | `bg-emerald-100 text-emerald-800 border-emerald-300` |

| Change Direction | Badge Color | Label |
|------------------|-------------|-------|
| `less_favorable` | Red | 🔴 More Restrictive / Less Favorable |
| `unclear` | Yellow | 🟡 Ambiguous / Unclear |
| `neutral` | Blue | 🔵 Neutral Update |
| `more_favorable` | Green | 🟢 User Friendly / More Favorable |
