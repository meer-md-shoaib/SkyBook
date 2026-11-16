<div align="center">

# ✈️ SkyBook — Modern Airline Reservation & Operations Platform
### *Seamless Journeys. Bulletproof Concurrency. Effortless Flight Management.*

**A full-stack, enterprise-grade airline booking and flight operations system engineered with Flask, SQLAlchemy, MySQL / TiDB Cloud, and Bootstrap 5 — featuring ACID-compliant seat holds, dynamic schedule advancement, simulated payment gateways, and automated PDF e-ticketing.**

---

[![Render Deployment](https://img.shields.io/badge/Render-Live%20Deployment-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://github.com/meer-md-shoaib/SkyBook)
[![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask Version](https://img.shields.io/badge/Flask-3.1.x-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.x-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Database](https://img.shields.io/badge/MySQL%20%7C%20TiDB-Serverless%20Cloud-00758F?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Bootstrap 5](https://img.shields.io/badge/Bootstrap-5.3.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![ReportLab](https://img.shields.io/badge/ReportLab-PDF%20Generation-E25A1C?style=for-the-badge)](https://www.reportlab.com/)
[![Tests](https://img.shields.io/badge/Pytest-42%2F42%20Passed-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

<br/>

<!-- Interactive Quick Action Buttons -->
<p align="center">
  <a href="https://github.com/meer-md-shoaib/SkyBook">
    <img src="https://img.shields.io/badge/🚀_Live_App-Visit_SkyBook-0B2A4A?style=for-the-badge&labelColor=17324D" alt="Live App" />
  </a>
  &nbsp;&nbsp;
  <a href="SkyBook_SDD_Presentation_Fixed.pptx">
    <img src="https://img.shields.io/badge/📊_Presentation-SDD_Slide_Deck-2E86DE?style=for-the-badge&labelColor=0F172A" alt="Presentation Deck" />
  </a>
  &nbsp;&nbsp;
  <a href="#-automated-testing--quality-assurance">
    <img src="https://img.shields.io/badge/🧪_Test_Suite-42%20Passing%20Tests-1E9E6A?style=for-the-badge&labelColor=064E3B" alt="Test Suite" />
  </a>
  &nbsp;&nbsp;
  <a href="https://github.com/meer-md-shoaib/SkyBook/stargazers">
    <img src="https://img.shields.io/badge/⭐_Star_Repository-GitHub-orange?style=for-the-badge&labelColor=334155" alt="Star Repository" />
  </a>
</p>

</div>

---

## 📌 Table of Contents

- [💡 Overview & The Engineering Challenge](#-overview--the-engineering-challenge)
- [✨ Key System Capabilities](#-key-system-capabilities)
  - [Passenger Experience](#-passenger-experience)
  - [Administrator Operations](#-administrator-operations)
- [🛡️ High-Concurrency & ACID Guarantees](#️-high-concurrency--acid-guarantees)
- [🔄 Dynamic Flight Schedule Engine](#-dynamic-flight-schedule-engine)
- [🏗️ System Architecture & Workflow](#️-system-architecture--workflow)
- [🛠️ Technology Stack](#️-technology-stack)
- [📂 Project Directory Tree](#-project-directory-tree)
- [🚀 Quickstart & Local Setup](#-quickstart--local-setup)
- [⚙️ Environment Configuration](#️-environment-configuration)
- [🧪 Automated Testing & Quality Assurance](#-automated-testing--quality-assurance)
- [📡 Application Routes & API Reference](#-application-routes--api-reference)
- [👥 Authors & Acknowledgments](#-authors--acknowledgments)
- [📄 License & Ethics](#-license--ethics)

---

## 💡 Overview & The Engineering Challenge

Modern commercial airline reservation platforms process millions of concurrent queries and seat reservations across global flight networks. The primary engineering challenge lies in **preventing double-bookings**, guaranteeing **data consistency under high contention**, and providing **instant booking confirmation** with valid electronic boarding documentation.

Traditional naive implementations suffer from critical failure modes:
- **Race Conditions:** Two passengers simultaneously selecting seat `14B` on a high-demand route both receive confirmation because status updates occur after isolated query reads.
- **Abandoned Cart Seat Locking:** Incomplete booking flows hold seats indefinitely, causing flights to artificially appear fully booked and inflicting severe airline revenue loss.
- **Stale Schedule Breakages:** Pre-seeded flights pass departure thresholds, causing reservation exceptions when passengers search for domestic journeys.
- **Inconsistent Financial Reconciliations:** Payment failures leave orphaned records, while un-audited cancellations fail to properly compute airline refund tiers.

### 🎯 Our Mission: SkyBook

**SkyBook** solves these core airline domain challenges by combining **pessimistic row-level locking (`SELECT ... FOR UPDATE`)**, a **dual-state seat reservation model** with a **unique constraint on active holds**, a **self-healing dynamic schedule engine**, and a **Strategy-pattern simulated payment gateway**.

Whether running locally on XAMPP MySQL or globally on TiDB Cloud Serverless MySQL behind Render, SkyBook delivers a high-performance passenger booking experience and an administrative operations suite.

---

## ✨ Key System Capabilities

### 🧳 Passenger Experience

- **⚡ Real-Time Flight Discovery:** Search flights by origin, destination, departure date, airline preference, fare ceilings, and departure windows (Morning, Afternoon, Evening, Night).
- **💺 Interactive Seat Selection:** Visual seat map displaying realistic airliner layouts with distinct Business and Economy configurations, color-coded seat states (`Available`, `Selected`, `Held`, `Booked`).
- **⏱️ 10-Minute Hold Window:** Atomic reservation timer holding selected seats for 10 minutes with client-side countdown and background automatic expiration.
- **📋 Server-Side Passenger Validation:** Detailed identity verification supporting Aadhaar, Passport, PAN, Voter ID, and Driving License, with duplicate identity prevention.
- **💳 Multi-Method Simulated Payment:** Strategy-pattern payment module supporting Cards and UPI with one-click outcome simulation (*Success* or *Declined Retry*).
- **📄 Instant PDF E-Ticket Generation:** Automated ReportLab vector PDF generation with custom airline header, flight metadata, seat badges, and boarding instructions.
- **🔄 Transparent Cancellation & Refunds:** Real-time cancellation quote calculation deducting configurable airline fee tiers (default 10%), with instantaneous seat inventory release.
- **🌓 Adaptive Dark / Light Mode:** Fully responsive theme switcher persisting passenger preference in `localStorage` with system OS color scheme fallback.
- **✨ Fluid UI Page Transitions:** Smooth CSS sliding transitions across routes (`/`, `/services`, `/contact`, `/flights/results`).

### 🛠️ Administrator Operations

- **📊 Comprehensive Command Center:** Live metrics tracking total confirmed bookings, gross revenue generated, active flights in air, and average load factor.
- **🛫 Route & Flight Management (CRUD):** Create, inspect, update, and toggle active status for domestic and international aircraft routes.
- **🗓️ Schedule Operations & Seat Regeneration:** Publish flight schedules with customized base fares, departure windows, and automatic 132-seat aircraft layout generator.
- **👥 Passenger & Booking Audit Trail:** Real-time visibility into all bookings, passenger manifest records, transaction references, and processed cancellations.
- **🔐 Role-Based Access Control:** Strict authorization boundaries enforced via custom decorators (`@admin_required`), isolating administrative routes from passenger access.

---

## 🛡️ High-Concurrency & ACID Guarantees

In airline reservation systems, seat booking conflicts represent the highest risk to business operations. SkyBook implements a multi-tier defense architecture to ensure that **no two passengers can ever hold or book the same seat simultaneously**.

```
   Passenger 1                              Database (InnoDB)                          Passenger 2
        |                                           |                                       |
        |--- 1. POST /flights/12/seats/hold ------->|                                       |
        |    seat_ids: [14A, 14B]                   |                                       |
        |                                           |--- 2. POST /flights/12/seats/hold --->|
        |                                           |    seat_ids: [14B, 14C]               |
        |                                           |                                       |
        |    [Acquires SELECT ... FOR UPDATE]       |    [BLOCKED: Waiting for Lock]        |
        |    Status: AVAILABLE -> HELD              |                                       |
        |    Inserts active_seat_id (UNIQUE)        |                                       |
        |    Creates PENDING Booking (10 min hold)  |                                       |
        |    COMMIT Transaction                     |                                       |
        |<-- Returns 302 /passengers ---------------|                                       |
        |                                           |    [Lock Acquired by Passenger 2]     |
        |                                           |    Detects seat 14B status != AVAIL   |
        |                                           |    ROLLBACK Transaction               |
        |                                           |<-- Returns 400 Seat Just Taken -------|
```

### 1. Pessimistic Row-Level Locking (`SELECT ... FOR UPDATE`)
When seats are requested, `BookingRepository.lock_seats_for_update()` requests exclusive row locks on the requested `seats` rows inside an active database transaction. Any concurrent request for those exact seat IDs blocks until the first transaction completes.

### 2. Dual-Layer Unique Constraint (`uq_active_seat`)
The `booking_seats` table maintains an `active_seat_id` column alongside `seat_id`:
- When a booking holds or confirms a seat, `active_seat_id` stores the `seat_id`.
- The database enforces a `UNIQUE(active_seat_id)` constraint.
- If two processes ever bypassed application locks, the database engine itself rejects the collision with an `IntegrityError`.
- Upon cancellation or expiration, `active_seat_id` is set to `NULL` (which MySQL allows multiple times), preserving historical audit logs while instantly unlocking the physical seat.

### 3. Background Sweeper & Opportunistic Expiration
Pending holds automatically expire after `SEAT_HOLD_MINUTES = 10`. To avoid costly daemon threads, SkyBook utilizes **opportunistic sweeping**: before every search, seat map render, and payment attempt, stale holds are detected (`hold_expires_at < utcnow()`) and their seats atomically set back to `AVAILABLE`.

---

## 🔄 Dynamic Flight Schedule Engine

In real-world testing and academic presentations, static demo databases frequently decay as dates advance into the past. SkyBook includes an autonomous **Schedule Health Engine**:

1. **Auto-Advancement on Booking:** When any flight is selected whose departure timestamp is in the past, SkyBook shifts its departure time to an active upcoming window (today if hours remain, or tomorrow) while strictly preserving flight duration, aircraft model, and route metadata.
2. **Catalog Health Sweeper (`ensure_upcoming_schedules()`):** On flight searches and landing page requests, expired schedules are cycled forward across a 7-day rolling window, resetting held seats and ensuring flight discovery never returns empty routes.

---

## 🏗️ System Architecture & Workflow

SkyBook follows a clean, decoupled **Layered Architecture (N-Tier)** enforcing strict separation of concerns across presentation, domain business logic, data persistence, and database layers:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Presentation Layer (UI)                         │
│   Bootstrap 5.3 + Jinja2 Templates + Vanilla JS + CSS3 Theme Engine    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP Requests / Form Data
┌───────────────────────────────────▼────────────────────────────────────┐
│                       Controller / Route Layer                         │
│   auth_bp | main_bp | flights_bp | bookings_bp | payments_bp | admin_bp│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Validated Payloads
┌───────────────────────────────────▼────────────────────────────────────┐
│                        Domain & Service Layer                          │
│   BookingService │ FlightService │ PaymentService │ TicketService      │
│   - Hold Sweeper │ - Fares Quote │ - Strategy GW  │ - ReportLab PDF    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ ORM Queries & Locking
┌───────────────────────────────────▼────────────────────────────────────┐
│                       Repository & Data Access                         │
│   BookingRepository │ FlightRepository │ UserRepository                │
│   - SELECT ... FOR UPDATE              │ - Atomic Transactions         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ SQL Execution
┌───────────────────────────────────▼────────────────────────────────────┐
│                        Database & Storage Layer                        │
│         MySQL 8.0+ / MariaDB 10.4 / TiDB Cloud Serverless              │
└────────────────────────────────────────────────────────────────────────┘
```

### 🧩 Software Design Patterns

| Pattern | Component | Description & Purpose |
|---|---|---|
| **Application Factory** | `app.create_app()` | Isolates configurations across `development`, `testing`, and `production`. Enables clean pytest fixture creation. |
| **Repository Pattern** | `app.repositories.*` | Decouples business services from direct SQLAlchemy queries, centralizing complex SQL logic and row-level locks. |
| **Strategy Pattern** | `app.services.payment_service` | Implements `PaymentStrategy` with interchangeable concrete classes (`MockSuccessStrategy`, `MockFailureStrategy`) for extensible payment gateways. |
| **Decorator Pattern** | `app.utils.decorators` | Implements `@admin_required` and custom authentication guards cleanly wrapping route endpoints. |
| **State Pattern** | `Booking.booking_status` | Enforces explicit, valid transitions across `PENDING ➔ CONFIRMED ➔ CANCELLED` and `PENDING ➔ EXPIRED`. |

---

## 🛠️ Technology Stack

| Layer | Component | Version | Purpose |
|---|---|---|---|
| **Backend Framework** | Flask | 3.1.x | Lightweight WSGI web application framework and routing engine |
| **Language** | Python | 3.11 – 3.13 | Core programming language with typed signatures and clean exception handling |
| **ORM & Data Mapping** | SQLAlchemy | 2.0.x | Object-Relational Mapper providing transactional Unit of Work and connection pooling |
| **Database Driver** | PyMySQL | 1.1.x | Pure-Python MySQL client driver supporting SSL/TLS connections for TiDB Cloud |
| **Primary Database** | MySQL / TiDB | 8.0 / v8.5 | Relational ACID database with row-level locking (Local MySQL / Cloud Serverless) |
| **Authentication** | Flask-Login | 0.6.x | Session-based user authentication, remember-me cookies, and credential verification |
| **Forms & Security** | Flask-WTF / CSRF | 1.2.x | Form validation, password policy enforcement, and synchronized CSRF token protection |
| **Document Engine** | ReportLab | 4.3.x | Enterprise PDF rendering engine generating vector airline e-tickets and boarding passes |
| **Frontend Styling** | Bootstrap | 5.3.3 | Modern responsive grid system, modals, badges, and accessible forms |
| **Icons & Visuals** | Bootstrap Icons | 1.11.x | Consistent iconography across navigation, admin metrics, and seat maps |
| **Testing Suite** | Pytest | 9.1.x | Automated unit, service, integration, and security test runner (42 tests) |
| **Cloud Deployment** | Render | Native | Production cloud web service with automatic deployment pipeline from GitHub `main` |

---

## 📂 Project Directory Tree

```
SkyBook/
├── app/
│   ├── __init__.py                # Flask application factory, CLI registration, context processors
│   ├── config.py                  # Environment-driven configuration (Dev, Testing, Prod)
│   ├── extensions.py              # Initialized extensions: db (SQLAlchemy), login_manager, csrf
│   ├── forms.py                   # Passenger and Admin forms with WTForms validators
│   ├── seed.py                    # Multi-route domestic seeder (36 flights, 360 schedules, 47k seats)
│   ├── models/                    # 10 Normalized SQLAlchemy Database Models
│   │   ├── airport.py             # IATA codes, international airport names, cities
│   │   ├── flight.py              # Aircraft types, airlines, active route status
│   │   ├── schedule.py            # Timetables, duration, status (SCHEDULED, DEPARTED)
│   │   ├── seat.py                # Seat classes (BUSINESS, ECONOMY), row-column coordinates
│   │   ├── user.py                # User credentials, roles (ADMIN, PASSENGER), hashed passwords
│   │   ├── booking.py             # PNR references, hold timers, total amounts, booking statuses
│   │   ├── passenger.py           # Government ID validations, dates of birth, assigned seats
│   │   ├── payment.py             # Transaction references, payment methods, gateway messages
│   │   ├── ticket.py              # E-ticket references, generation timestamps, PDF file paths
│   │   └── cancellation.py        # Refund amounts, cancellation fees, cancellation reasons
│   ├── repositories/              # Database Query & Locking Layer
│   │   ├── booking_repository.py  # Row-level seat locking (SELECT FOR UPDATE), hold sweepers
│   │   ├── flight_repository.py   # Route search, catalog queries, auto-advancement health sweeper
│   │   └── user_repository.py     # User lookup and role querying
│   ├── services/                  # Core Business Logic Layer
│   │   ├── booking_service.py     # Atomicity manager: holds, passenger mapping, confirmation
│   │   ├── flight_service.py      # Route search validation, seat-map projection
│   │   ├── payment_service.py     # Strategy pattern simulated payment processing
│   │   ├── ticket_service.py      # Vector ReportLab PDF electronic ticket generator
│   │   └── cancellation_service.py# Refund quote calculation and seat inventory release
│   ├── routes/                    # Modular Blueprint Controllers
│   │   ├── auth.py                # User registration, login, logout, session persistence
│   │   ├── main.py                # Landing page, `/services` showcase, `/contact` support
│   │   ├── flights.py             # Search results, flight details, interactive seat maps
│   │   ├── bookings.py            # Hold creation, passenger details, booking summary, cancellation
│   │   ├── payments.py            # Checkout screen, payment execution, gateway retry
│   │   ├── tickets.py             # PDF download endpoint with owner/admin authorization
│   │   └── admin.py               # Administrative command console (CRUD flights, schedules, audits)
│   ├── static/                    # Frontend Assets
│   │   ├── css/style.css          # SkyBook custom styling & responsive CSS variables
│   │   ├── js/main.js             # Theme switcher, seat selection engine, hold countdown timer
│   │   └── images/                # Airplane vectors, brand badges, hero graphics
│   ├── templates/                 # Jinja2 Frontend Templates
│   │   ├── base.html              # Core layout, navigation bar, dark mode toggle, alerts
│   │   ├── index.html             # Hero search bar, featured domestic routes, services highlights
│   │   ├── flights.html           # Filterable search results list with live fare comparisons
│   │   ├── seats.html             # Interactive aircraft cabin seat map
│   │   ├── passenger_details.html # Dynamic passenger identification capture form
│   │   ├── booking_summary.html   # Final fare review and flight summary before payment
│   │   ├── payment.html           # Simulated Card & UPI checkout interface
│   │   ├── confirmation.html      # Success screen with instant PDF ticket download link
│   │   ├── my_bookings.html       # Passenger booking history and status tracker
│   │   ├── booking_details.html   # Detailed booking review with cancellation quote modal
│   │   ├── cancellation.html      # Cancellation confirmation and refund receipt
│   │   ├── services.html          # Cabin class amenities showcase (Business, Premium, Economy)
│   │   ├── contact.html           # 24/7 Customer assistance and feedback form
│   │   └── admin/                 # Dedicated admin layout, dashboard, schedules, manifest views
│   └── utils/                     # Formatting, decorators, and validators
├── database/                      # Raw SQL Backups & Seeding Scripts
│   ├── schema.sql                 # Complete MySQL schema DDL
│   └── seed.sql                   # Raw SQL dataset backup
├── docs/                          # System Architecture Documentation
│   └── design.md                  # Detailed Software Design Document (SDD)
├── tests/                         # Comprehensive Pytest Suite (42 tests)
│   ├── conftest.py                # Seeded testing fixtures & test clients
│   ├── test_auth.py               # Authentication & session security tests
│   ├── test_flights.py            # Search engine & date clamping tests
│   ├── test_bookings.py           # Concurrency, seat hold, & passenger validation tests
│   ├── test_payments.py           # Payment strategy, retry, & idempotency tests
│   └── test_cancellations.py      # Cancellation eligibility & refund formula tests
├── SkyBook_SDD_Presentation.pptx  # Academic presentation slide deck
├── SkyBook_SDD_Presentation_Fixed.pptx # Enhanced presentation deck with screenshots & test logs
├── requirements.txt               # Locked production dependencies
├── run.py                         # WSGI entry point
└── README.md                      # Comprehensive project documentation
```

---

## 🚀 Quickstart & Local Setup

### 1. Prerequisites

- **Python:** `3.11` to `3.13`
- **Database:** Local MySQL / MariaDB (e.g. XAMPP) or a free [TiDB Cloud Serverless](https://tidbcloud.com) cluster.
- **Git** installed on your system.

### 2. Clone the Repository

```bash
git clone https://github.com/meer-md-shoaib/SkyBook.git
cd SkyBook
```

### 3. Set Up Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Database Configuration

Create a `.env` file in the root directory by copying `.env.example`:

```bash
cp .env.example .env
```

#### Option A: Local MySQL / XAMPP
```env
FLASK_ENV=development
SECRET_KEY=skybook-local-dev-secret-key-2026
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=skybook_db
SEAT_HOLD_MINUTES=10
CANCELLATION_FEE_PERCENT=10
```

#### Option B: TiDB Cloud Serverless MySQL
```env
FLASK_ENV=production
SECRET_KEY=skybook-prod-secret-key-live-2026
DATABASE_URL=mysql+pymysql://<user>:<password>@gateway01.us-east-1.prod.aws.tidbcloud.com:4000/skybook_db?ssl_verify_cert=true
SEAT_HOLD_MINUTES=10
CANCELLATION_FEE_PERCENT=10
```

### 6. Initialize & Seed Database

SkyBook comes with custom Flask CLI commands to create all schemas and seed realistic domestic Indian flight networks (IndiGo, Air India, Vistara, Akasa Air, SpiceJet across Delhi, Mumbai, Bengaluru, Hyderabad, Chennai, Kochi):

```bash
# Initialize schema and seed 36 flights with full seat layouts
flask --app run.py init-db
flask --app run.py seed-db
```

> **Pro-Tip:** Run `flask --app run.py reset-db` at any time to drop all tables, recreate schemas, and re-seed clean data in one step!

### 7. Run the Application

```bash
python run.py
```

Access the application in your browser at: **`http://127.0.0.1:5000`**

---

### 🔑 Demo User Credentials

| Role | Email | Password | Privileges |
|---|---|---|---|
| **Administrator** | `admin@skybook.com` | `Admin@123` | Full access to `/admin` dashboard, flight CRUD, schedule management, manifest audits |
| **Demo Passenger 1** | `demo@skybook.com` | `Passenger@123` | Search, hold seats, simulated checkout, PDF e-ticket download, cancellation quotes |
| **Demo Passenger 2** | `riya@example.com` | `Passenger@123` | Multi-passenger and concurrent booking simulation account |

---

## 🧪 Automated Testing & Quality Assurance

SkyBook maintains a comprehensive, production-grade test suite covering domain services, transactional concurrency, security boundaries, and HTTP route handlers.

```bash
# Run the entire test suite with verbose output
python -m pytest -v
```

```
============================= test session starts =============================
platform win32 -- Python 3.13.15, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\meerm\Freebuff\SkyBook
collected 42 items

tests\test_auth.py ...........                                           [ 26%]
tests\test_bookings.py ..........                                        [ 50%]
tests\test_cancellations.py .....                                        [ 61%]
tests\test_flights.py .........                                          [ 83%]
tests\test_payments.py .......                                           [100%]

============================= 42 passed in 55.94s =============================
```

### 📋 Test Coverage Matrix

| Test Module | Tests | Primary Verification Focus |
|---|:---:|---|
| **`test_auth.py`** | 11 | Registration validation, secure password hashing, session lifecycle, role-based access control, CSRF protections, unauthorized redirects. |
| **`test_flights.py`** | 9 | Route search queries, same-city validation, date clamping, price filtering, departure window matching, standalone `/services` & `/contact` views. |
| **`test_bookings.py`** | 10 | Atomic seat holds, duplicate seat rejection, max seat limits (6 per booking), passenger manifest data validation, expired hold sweepers, ownership protection. |
| **`test_payments.py`** | 7 | Strategy-pattern payment charge, simulated gateway failure and retry, booking confirmation, ReportLab PDF ticket generation, payment callback idempotency. |
| **`test_cancellations.py`** | 5 | Cancellation eligibility checks, 10% fee calculation, seat inventory release, double-cancellation prevention, confirmation prompts. |

---

## 📡 Application Routes & API Reference

### 🌐 Passenger & Public Endpoints

| Method | Endpoint | Description | Auth Required |
|---|---|---|:---:|
| `GET` | `/` | SkyBook home landing page with search bar and featured routes | No |
| `GET` | `/services` | Cabin class showcase and onboard amenities guide | No |
| `GET`, `POST` | `/contact` | Customer support ticketing and inquiry submission | No |
| `GET`, `POST` | `/auth/login` | Passenger and administrator sign-in | No |
| `GET`, `POST` | `/auth/register` | New passenger account registration | No |
| `GET` | `/auth/logout` | Session termination and cookie invalidation | Yes |
| `GET` | `/flights/results` | Multi-filter flight schedule search results | No |
| `GET` | `/flights/<id>` | Comprehensive flight timetable and aircraft details | No |
| `GET` | `/flights/<id>/seats` | Interactive cabin layout and seat selection interface | Yes |
| `POST` | `/flights/<id>/seats/hold` | Atomic seat hold reservation with 10-minute timer | Yes |
| `GET` | `/flights/<id>/availability`| Live JSON endpoint for seat availability polling | No |
| `GET` | `/bookings/` | Passenger booking history dashboard | Yes |
| `GET` | `/bookings/<id>` | Detailed booking overview and cancellation quote modal | Yes |
| `GET`, `POST` | `/bookings/<id>/passengers` | Passenger identity information capture form | Yes |
| `GET` | `/bookings/<id>/summary` | Final fare breakdown and flight itinerary review | Yes |
| `GET` | `/bookings/<id>/confirmation`| Booking confirmation screen with e-ticket link | Yes |
| `GET`, `POST` | `/bookings/<id>/cancel` | Cancellation review, fee calculation, and seat release | Yes |
| `GET` | `/payments/<id>` | Simulated checkout screen with Card and UPI selectors | Yes |
| `POST` | `/payments/<id>/pay` | Process simulated payment (Strategy pattern) | Yes |
| `POST` | `/payments/<id>/retry` | Retry failed transaction while seat hold remains active | Yes |
| `POST` | `/payments/callback` | Idempotent webhook receiver for gateway updates | No (CSRF exempt) |
| `GET` | `/tickets/<id>/download` | Secure PDF electronic ticket streaming endpoint | Yes (Owner/Admin) |

### 🛡️ Administrator Endpoints (`/admin/*`)

| Method | Endpoint | Description | Access Level |
|---|---|---|:---:|
| `GET` | `/admin/` | Operations dashboard: revenue, active flights, load factor | Administrator |
| `GET`, `POST` | `/admin/flights` | Flight inventory listing and new aircraft route creation | Administrator |
| `POST` | `/admin/flights/<id>/toggle` | Toggle route status between Active and Inactive | Administrator |
| `GET`, `POST` | `/admin/schedules` | Schedule timetables and automatic seat layout generator | Administrator |
| `GET` | `/admin/bookings` | System-wide booking records and passenger counts | Administrator |
| `GET` | `/admin/passengers` | Passenger manifest records and government ID references | Administrator |
| `GET` | `/admin/payments` | Financial audit ledger of all transaction attempts | Administrator |
| `GET` | `/admin/cancellations`| Cancellation and refund processing history | Administrator |

---

## 👥 Authors & Acknowledgments

<div align="center">

<table>
  <tr>
    <td align="center" width="100%">
      <a href="https://github.com/meer-md-shoaib">
        <img src="https://github.com/meer-md-shoaib.png" width="125px;" style="border-radius: 50%;" alt="Meer Mohammed Shoaib"/><br />
        <sub><b>Meer Mohammed Shoaib</b></sub>
      </a><br />
      <span style="color: #0ea5e9; font-weight: bold;">Lead Software Architect & Full-Stack Engineer</span>
      <p style="font-size: 0.85em; color: #64748b; max-width: 500px; margin-top: 6px;">
        Core system architecture, concurrency & pessimistic seat-locking model, dynamic schedule auto-advancement engine, ReportLab PDF e-ticketing pipeline, TiDB Cloud Serverless deployment, and full test suite design.
      </p>
      <a href="https://github.com/meer-md-shoaib">
        <img src="https://img.shields.io/badge/GitHub-Profile-181717?style=flat-square&logo=github" alt="GitHub" />
      </a>
      &nbsp;
      <a href="mailto:shoaibmeermd@gmail.com">
        <img src="https://img.shields.io/badge/Email-Contact%20Author-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email" />
      </a>
    </td>
  </tr>
</table>

</div>

---

## 📄 License & Academic Attribution

This project is open-source software licensed under the **[MIT License](LICENSE)**.

> **Academic Presentation Artifacts:** For university reviews, software design defenses, and system demonstrations, refer to **[`SkyBook_SDD_Presentation_Fixed.pptx`](SkyBook_SDD_Presentation_Fixed.pptx)** for the complete slide deck containing architectural diagrams, test logs, and live application screenshots.

<br/>

<div align="center">
  <b>Built with ❤️ by Meer Mohammed Shoaib</b><br/>
  <sub>© 2026 SkyBook Airline Reservation System. All rights reserved.</sub>
</div>
