# SkyBook — Build Plan

**Project:** SkyBook — Airline Reservation & Management System
**Stack:** Python 3.11+ / Flask / MySQL (MariaDB 10.4 via XAMPP) / Flask-SQLAlchemy / PyMySQL / Bootstrap 5 / Jinja2 / Flask-Login / Flask-WTF / ReportLab / Pytest
**Design reference:** navy + white + sky-blue aviation UI, rounded cards, hero with aircraft, flight-result rows with fare badges (see project brief image).

---

## 0. Environment verification

- [x] Inspect working directory (empty)
- [x] Confirm Python available (3.13)
- [x] Start MySQL/MariaDB on `localhost:3306`
- [x] Verify DB connection as `root` (no password)

## 1. Plan & scaffolding

- [x] Write this plan file
- [x] Create folder structure (`app/`, `database/`, `tests/`, `docs/`, `generated_tickets/`)
- [x] `requirements.txt`, `run.py`, `.env`, `.env.example`, `.gitignore`
- [x] Create `skybook_db` + `skybook_test_db` databases

## 2. Core application (Phase 1)

- [x] `app/config.py` — env-driven config (dev + testing), hold window, cancellation policy
- [x] `app/extensions.py` — db, login_manager, csrf, migrate-free wiring
- [x] `app/__init__.py` — application factory, blueprint registration, error handlers, CLI commands (`init-db`, `seed-db`, `create-admin`)
- [x] Models: `user`, `airport`, `flight`, `schedule`, `seat`, `booking`, `passenger`, `payment`, `ticket`, `cancellation`
- [x] `database/schema.sql` — normalized DDL with PK/FK/unique indexes
- [x] `database/seed.sql` — Indian airports, flights, schedules, seats, demo accounts
- [x] `app/seed.py` — idempotent Python seeder (used by CLI + tests)

## 3. Data access & business logic

- [x] Repositories: `user_repository`, `flight_repository`, `booking_repository`
- [x] `flight_service` — search, filters, durations, availability
- [x] `booking_service` — transactional seat hold with `SELECT ... FOR UPDATE`, hold expiry sweeper, passenger validation, cancellation
- [x] `payment_service` — Strategy pattern (success/fail gateways), idempotency, retry
- [x] `cancellation_service` — eligibility, refund policy, seat release
- [x] `ticket_service` — ReportLab PDF, only for CONFIRMED bookings
- [x] Utils: `decorators.py` (admin_required), `validators.py`, `helpers.py`

## 4. Authentication & passenger routes (Phase 2–3)

- [x] `auth.py` — register, login, logout, role-based redirect
- [x] `main.py` — landing page, health
- [x] `flights.py` — search, results, details, seat map (JSON availability + hold)
- [x] `bookings.py` — passenger details, summary, my bookings, details, cancel
- [x] `payments.py` — payment page, process, retry, idempotent callback
- [x] `tickets.py` — PDF download with ownership check

## 5. Admin routes (Phase 4)

- [x] `admin.py` — dashboard stats, flight CRUD, schedule CRUD, airports, bookings, payments, cancellations
- [x] Admin templates: dashboard, flights, schedules, bookings, passengers, payments, cancellations
- [x] Every admin route protected by `@admin_required`

## 6. Frontend (Phase 5, image-driven)

- [x] `style.css` — design tokens (navy `#0B2A4A`, sky `#2E86DE`), hero, cards, seat map, badges, responsive
- [x] `main.js` — seat map interaction, price calc, passenger rows, hold countdown, payment mock toggle
- [x] Templates: base (nav + footer + flash), index, login, register, flights, flight_details, seats, passenger_details, booking_summary, payment, confirmation, my_bookings, booking_details, cancellation, errors
- [x] Seat map legend: available / selected / occupied / held
- [x] Brand mark (inline SVG plane + SkyBook wordmark)

## 7. Tests (Pytest)

- [x] `conftest.py` — app fixture on `skybook_test_db`, seeded, client & auth helpers
- [x] `test_auth.py` — register, login ok/fail, admin protection
- [x] `test_flights.py` — search, no flights, same-city rejection
- [x] `test_bookings.py` — seat selection, invalid passenger, duplicate seat, unauthorized access
- [x] `test_payments.py` — success, failure, retry, confirmation, ticket generation
- [x] `test_cancellations.py` — cancel eligibility, seat release, refund
- [x] Run suite and record real results

## 8. Verification (acceptance criteria)

- [x] App boots, MySQL connects
- [x] Register/login works
- [x] Search returns DB records
- [x] Seat hold + double-booking prevention verified
- [x] Payment success confirms, failure keeps pending
- [x] PDF ticket downloads
- [x] Cancellation releases seats
- [x] Admin can manage flights
- [x] README with setup, credentials, results

## 9. Documentation

- [x] `README.md` — overview, features, stack, architecture, schema, setup, run, tests, accounts, screenshots
- [x] `docs/` — design notes (ERD, patterns, workflow)
- [x] Final report of test results and limitations

---

## Status: complete (verified 2026-11-10)

All phases above are implemented and verified against MySQL/MariaDB 10.4.

**Defects fixed during final verification**

- `app/templates/index.html` — Python f-string inside a Jinja `{% set %}` block
  (`TemplateSyntaxError`); replaced with Jinja string concatenation.
- `app/repositories/booking_repository.py` — `FOR UPDATE SKIP LOCKED` is not
  supported by MariaDB 10.4 and broke every seat hold; switched to `FOR UPDATE`.
- `app/templates/admin/flights.html` — `flight.schedules|length` on a dynamic
  relationship (`AppenderQuery` has no `len()`); switched to `.count()`.
- Added the three missing admin templates (`passengers`, `payments`,
  `cancellations`) whose routes existed but raised `TemplateNotFound`.

**Verification performed**

- Application boots; all 38 routes register; every page renders.
- End-to-end passenger flow: search → seat hold → passengers → failed payment →
  retry → confirmation → PDF ticket → cancellation with seat release.
- Admin CRUD: flight create/edit/toggle, schedule create, seat-map regeneration.
- `database/schema.sql` + `database/seed.sql` restore into a scratch database
  with the expected row counts (6 airports, 12 flights, 120 schedules, 15,840
  seats, 3 users, 1 demo booking).
- Test suite: **32 passed in 121.00s** (`python -m pytest tests -q`).

**Not included:** UI screenshots.
