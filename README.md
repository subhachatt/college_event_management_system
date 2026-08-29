# 🎓 CampusHub — College Event Management System

A full-stack, modular, and self-contained **College Event Management System** built with **Python FastAPI, SQLAlchemy, SQLite** on the backend and **Vanilla HTML5, CSS3, JavaScript & Chart.js** on the frontend.

---

## 📌 Table of Contents
1. [Project Overview](#-project-overview)
2. [Key Features](#-key-features)
3. [Technology Stack](#-technology-stack)
4. [System Architecture](#-system-architecture)
5. [Project Structure](#-project-structure)
6. [Database Schema](#-database-schema)
7. [Getting Started (Windows Setup)](#-getting-started-windows-setup)
8. [Demo Credentials](#-demo-credentials)
9. [REST API Endpoints & Documentation](#-rest-api-endpoints--documentation)
10. [How to Reset the Database](#-how-to-reset-the-database)
11. [Important Files for Beginners](#-important-files-for-beginners)
12. [Future Improvements](#-future-improvements)

---

## 🚀 Project Overview

CampusHub is designed for universities and colleges to streamline event discovery, capacity management, and student participation. Students can explore upcoming technical workshops, hackathons, sports championships, and cultural galas, registering with a single click while preventing double-bookings. Administrators get real-time analytics, attendee rosters with CSV export, and complete event lifecycle management.

**Key Design Highlights:**
- **100% Local**: Uses embedded SQLite (`backend/college_events.db`). No external servers (MySQL, PostgreSQL, MongoDB, XAMPP, or Docker) are needed.
- **Zero Frontend Framework Overhead**: Clean Vanilla JavaScript (ES6+), modern CSS custom properties, and native Fetch API.
- **Strict Role-Based Access Control**: Backend validates JWT tokens and prevents unauthorized access to admin endpoints.
- **Automatic Initialization**: Tables and realistic demo data (1 Admin, 5 Students, 9 Events, sample registrations) are populated automatically on first run.

---

## ✨ Key Features

### 👨‍🎓 For Students
- **Account Registration & Login**: Fast registration with Student ID & Academic Department.
- **1-Click Demo Login**: Quick login buttons on the login page for testing.
- **Event Discovery**: Filter by 8 categories (*Technical, Cultural, Sports, Workshop, Seminar, Hackathon, Competition, Other*), search by keywords, and sort by date.
- **Live Seat Availability**: Real-time progress bars showing registered seats vs maximum capacity.
- **One-Click Pass Registration**: Instant registration with duplicate prevention and capacity enforcement.
- **Pass Cancellation**: Students can cancel registration to instantly free up their seat.
- **My Registrations Portal**: Filter registrations by tabs (*Upcoming, Completed, Cancelled, All*) with digital Pass IDs.
- **Student Profile**: Virtual College ID Card displaying student details and profile edit functionality.

### 👑 For Administrators
- **Admin Control Center**: KPI summary cards for *Total Students, Total Events, Upcoming Events*, and *Active Registrations*.
- **Interactive Analytics**: Chart.js visualizations for *Registrations by Event* (Bar Chart) and *Events by Category* (Doughnut Chart).
- **Event CRUD Operations**: Create new events with image preview & time validation, edit existing events, or delete with confirmation modals.
- **Attendee Roster Management**: Search participants by name/email/ID and filter by department.
- **Export to CSV**: One-click download of verified participant lists.

---

## 🛠 Technology Stack

### Frontend
- **HTML5**: Semantic markup, accessible forms, meta tags.
- **CSS3**: Vanilla design system, CSS variables, glassmorphism, responsive grid & flexbox layouts.
- **Vanilla JavaScript (ES6+)**: Modular scripts, Fetch API, DOM manipulation.
- **Chart.js (CDN)**: Interactive charts on Admin Dashboard.

### Backend
- **Python 3.10+ / 3.13**: Modern async Python runtime.
- **FastAPI**: High-performance RESTful API framework with automatic Swagger & ReDoc.
- **Uvicorn**: Lightning-fast ASGI web server.
- **SQLAlchemy 2.0 ORM**: Python SQL toolkit and Object Relational Mapper.
- **Pydantic v2**: Strict request/response schema validation.
- **PyJWT & Bcrypt**: Secure token authentication and salted password hashing.
- **SQLite 3**: Embedded database (`backend/college_events.db`).

---

## 🏛 System Architecture

```
[ Browser / Frontend Client ]
  HTML5 Pages + Modern CSS3 + Vanilla JS (api.js, auth.js, events.js, admin.js)
            |
            | HTTP / REST (JSON with JWT Bearer Token)
            v
[ FastAPI Backend (Port 8000) ]
  ├── CORS Middleware (Allows frontend origin communication)
  ├── Dependency Injection (get_current_user, get_current_admin, get_db)
  ├── Routers (auth, users, events, registrations, admin)
  └── Services (auth_service, event_service, registration_service, seed_service)
            |
            | SQLAlchemy 2.0 ORM
            v
[ Local SQLite Database (backend/college_events.db) ]
  ├── Users Table (Admin & Student roles)
  ├── Events Table (Capacity, Dates, Categories)
  └── Registrations Table (Unique user_id + event_id constraint)
```

---

## 📁 Project Structure

```
c:/College Event Management System/
│
├── backend/
│   ├── main.py                     # FastAPI entry point, CORS, lifespan startup & seeder
│   ├── database.py                 # SQLite database engine, session factory, Base model
│   ├── dependencies.py             # Auth & Role dependencies (get_current_user, get_current_admin)
│   ├── requirements.txt            # Python dependencies list
│   ├── .env.example                # Configuration template (JWT secrets, token expiration)
│   ├── college_events.db           # Local SQLite database (auto-generated)
│   ├── test_api.py                 # Automated backend test suite
│   │
│   ├── models/                     # SQLAlchemy ORM Models
│   │   ├── __init__.py
│   │   ├── user.py                 # User table (id, name, email, hashed_password, role, etc.)
│   │   ├── event.py                # Event table (id, title, category, venue, capacity, etc.)
│   │   └── registration.py         # Registration table (id, user_id, event_id, status)
│   │
│   ├── schemas/                    # Pydantic Schemas for Validation
│   │   ├── __init__.py
│   │   ├── user.py                 # UserCreate, UserLogin, UserResponse, UserUpdate, Token
│   │   ├── event.py                # EventCreate, EventUpdate, EventResponse, EventDetail
│   │   ├── registration.py         # RegistrationCreate, RegistrationResponse
│   │   └── admin.py                # AdminDashboardStats, ParticipantResponse
│   │
│   ├── routers/                    # FastAPI REST API Endpoints
│   │   ├── __init__.py
│   │   ├── auth.py                 # /api/auth/register, /api/auth/login, /api/auth/me
│   │   ├── users.py                # /api/users/me (profile view and update)
│   │   ├── events.py               # /api/events (CRUD for events)
│   │   ├── registrations.py        # /api/events/{id}/register, /api/my-registrations
│   │   └── admin.py                # /api/admin/dashboard, /api/admin/events/{id}/participants
│   │
│   └── services/                   # Business Logic & Helpers
│       ├── __init__.py
│       ├── auth_service.py         # Password hashing & JWT generation/verification
│       ├── event_service.py        # Event queries, filtering, sorting, seat calculation
│       ├── registration_service.py # Registration workflow, duplicate & capacity checks
│       └── seed_service.py         # Demo data generation on startup
│
├── frontend/
│   ├── index.html                  # Landing page (Hero, Categories, Featured Events, Stats)
│   ├── login.html                  # Sign in page with 1-Click Demo accounts
│   ├── register.html               # Student registration page
│   ├── events.html                 # Events Catalog with category chips, search & date filters
│   ├── event-details.html          # Event details, capacity meter & Register/Cancel actions
│   ├── dashboard.html              # Student dashboard & upcoming passes
│   ├── my-registrations.html       # Student registered passes (Upcoming/Completed/Cancelled)
│   ├── profile.html                # Student ID card & profile edit
│   ├── admin-dashboard.html        # Admin Dashboard with Chart.js & event management
│   ├── create-event.html           # Admin event creation form with image preview
│   ├── edit-event.html             # Admin event editor
│   ├── participants.html           # Admin attendee list with search & CSV export
│   │
│   ├── css/
│   │   ├── style.css               # Global theme tokens, typography, buttons, modals, toasts
│   │   ├── auth.css                # Authentication forms and demo login chips
│   │   ├── dashboard.css           # Student dashboard and ticket card styling
│   │   ├── events.css              # Event cards, category badges, search toolbar
│   │   ├── admin.css               # Admin layout, sidebar, stats widgets, charts
│   │   └── responsive.css          # Mobile, tablet, and desktop responsive breakpoints
│   │
│   └── js/
│       ├── api.js                  # Centralized Fetch API client, JWT handler, Toast notifications
│       ├── auth.js                 # Authentication logic, demo fill, route guards
│       ├── events.js               # Event listing, search, filtering, registration triggers
│       ├── dashboard.js            # Student dashboard loader & next event spotlight
│       ├── registrations.js        # Student registration tabs and cancel workflow
│       ├── admin.js                # Admin analytics loader, Chart.js, event CRUD, CSV export
│       └── profile.js              # User profile loader and updater
│
└── README.md                       # Complete documentation
```

---

## 🗄 Database Schema

### `users`
| Column | Type | Description |
|---|---|---|
| `id` | Integer | Primary key, Auto-increment |
| `name` | String(100) | Full Name |
| `email` | String(150) | Unique Email (Indexed) |
| `hashed_password` | String(255) | Bcrypt hashed password |
| `student_id` | String(50) | Optional for Admin, required for Students |
| `department` | String(100) | Academic Department |
| `role` | String(20) | `'STUDENT'` or `'ADMIN'` |
| `created_at` | DateTime | Timestamp of creation |

### `events`
| Column | Type | Description |
|---|---|---|
| `id` | Integer | Primary key, Auto-increment |
| `title` | String(200) | Event title |
| `description` | Text | Event description |
| `category` | String(50) | Technical, Cultural, Sports, Workshop, etc. |
| `venue` | String(150) | Room or campus location |
| `event_date` | String(20) | Format: `YYYY-MM-DD` |
| `start_time` | String(10) | Format: `HH:MM` |
| `end_time` | String(10) | Format: `HH:MM` |
| `capacity` | Integer | Maximum attendee capacity |
| `image_url` | String(500) | Cover image URL |
| `organizer` | String(150) | Organizing club or department |
| `created_at` | DateTime | Timestamp of creation |
| `updated_at` | DateTime | Timestamp of last update |

### `registrations`
| Column | Type | Description |
|---|---|---|
| `id` | Integer | Primary key, Auto-increment |
| `user_id` | Integer | Foreign Key (`users.id`) |
| `event_id` | Integer | Foreign Key (`events.id`) |
| `registration_date` | DateTime | Timestamp of registration |
| `status` | String(20) | `'CONFIRMED'` or `'CANCELLED'` |

> **Constraint:** Unique index on `(user_id, event_id)` prevents double bookings.

---

## 💻 Getting Started (Windows Setup)

### Step 1: Open PowerShell / Command Prompt in the project folder
```powershell
cd "C:\College Event Management System"
```

### Step 2: Create and Activate Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### Step 3: Install Python Dependencies
```powershell
pip install -r backend\requirements.txt
```

### Step 4: Run the Backend Server
```powershell
python -m uvicorn backend.main:app --reload --port 8000
```
- The backend will start on: **`http://localhost:8000`**
- The database `backend/college_events.db` will be created and seeded automatically.
- Interactive Swagger API docs available at: **`http://localhost:8000/docs`**

### Step 5: Run the Frontend (In a separate terminal)
Open another terminal window, navigate to the project directory, and serve the `frontend/` folder:
```powershell
cd "C:\College Event Management System"
python -m http.server 3000 --directory frontend
```
- Open your browser and navigate to: **`http://localhost:3000`**

---

## 🔑 Demo Credentials

For quick evaluation, you can use the **1-Click Demo Login** buttons on `http://localhost:3000/login.html` or type the credentials below:

### 👑 Administrator Account
- **Email:** `admin@college.edu`
- **Password:** `adminpassword123`
- **Role:** `ADMIN`

### 👨‍🎓 Student Accounts
| Name | Email | Password | Student ID | Department |
|---|---|---|---|---|
| **Rahul Sharma** | `rahul@student.edu` | `student123` | `CS-2024-001` | Computer Science |
| **Priya Patel** | `priya@student.edu` | `student123` | `IT-2024-042` | Information Technology |
| **Aman Verma** | `aman@student.edu` | `student123` | `EC-2024-018` | Electronics & Comm. |
| **Sneha Reddy** | `sneha@student.edu` | `student123` | `ME-2024-029` | Mechanical Eng. |
| **Vikram Singh** | `vikram@student.edu` | `student123` | `CV-2024-015` | Civil Eng. |

*(You can also click "Register as Student" to create your own brand new account).*

---

## 📡 REST API Endpoints & Documentation

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/` | Public | API Health Check |
| `POST` | `/api/auth/register` | Public | Register student (role forced to `STUDENT`) |
| `POST` | `/api/auth/login` | Public | Login and receive JWT access token |
| `GET` | `/api/auth/me` | Authenticated | Retrieve authenticated user profile |
| `GET` | `/api/users/me` | Authenticated | Get current user details |
| `PUT` | `/api/users/me` | Authenticated | Update user name, department, or password |
| `GET` | `/api/events` | Public | List events with category, search & date filters |
| `GET` | `/api/events/{id}` | Public/Auth | Get event details with seat availability & registration status |
| `POST` | `/api/events` | **Admin Only** | Create a new event |
| `PUT` | `/api/events/{id}` | **Admin Only** | Update an existing event |
| `DELETE` | `/api/events/{id}` | **Admin Only** | Delete an event |
| `POST` | `/api/events/{id}/register` | **Student Only** | Register for event (enforces capacity & duplicate check) |
| `DELETE` | `/api/events/{id}/register` | **Student Only** | Cancel event registration |
| `GET` | `/api/my-registrations` | **Student Only** | Get all event passes registered by the student |
| `GET` | `/api/admin/dashboard` | **Admin Only** | Aggregated stats and chart data |
| `GET` | `/api/admin/users` | **Admin Only** | List of all users |
| `GET` | `/api/admin/events/{id}/participants` | **Admin Only** | Attendee roster for a specific event |

Explore and test all endpoints live at **`http://localhost:8000/docs`** (Swagger UI) or **`http://localhost:8000/redoc`** (ReDoc).

---

## 🔄 How to Reset the Database

To reset the database to a clean default state with fresh demo data:
1. Stop the backend server (`Ctrl + C`).
2. Delete the database file:
   ```powershell
   Remove-Item "backend\college_events.db"
   ```
3. Restart the backend:
   ```powershell
   python -m uvicorn backend.main:app --reload --port 8000
   ```
The backend will automatically recreate `college_events.db` and repopulate all demo accounts and events.

---

## 📚 Important Files for Beginners

1. **[`backend/main.py`](file:///c:/College%20Event%20Management%20System/backend/main.py)**: Entry point where FastAPI is instantiated, CORS middleware is configured, lifespan startup creates SQLite tables and triggers demo seeding.
2. **[`backend/dependencies.py`](file:///c:/College%20Event%20Management%20System/backend/dependencies.py)**: Shows how FastAPI dependency injection works to extract JWT tokens, verify signatures, and restrict admin routes (`get_current_admin`).
3. **[`backend/models/`](file:///c:/College%20Event%20Management%20System/backend/models/)**: Declarative SQLAlchemy models mapping Python classes to SQLite tables with relational foreign keys.
4. **[`backend/services/registration_service.py`](file:///c:/College%20Event%20Management%20System/backend/services/registration_service.py)**: Contains core business logic for seat capacity verification and duplicate prevention.
5. **[`frontend/js/api.js`](file:///c:/College%20Event%20Management%20System/frontend/js/api.js)**: Centralizes all HTTP communication between Vanilla JS and FastAPI, handling Authorization headers and toast notifications.
6. **[`frontend/js/admin.js`](file:///c:/College%20Event%20Management%20System/frontend/js/admin.js)**: Demonstrates how to render dynamic Chart.js charts from REST API data and generate downloadable CSV files client-side.

---

## 🔮 Future Improvements
- QR Code generation on event passes for on-site check-in scanning.
- Automated email reminders 24 hours before registered events.
- Student certificate generation after event completion.
- Feedback and rating system for past events.

---
**CampusHub** • Built with Python FastAPI, SQLAlchemy, SQLite, Vanilla JavaScript & CSS3.
