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
