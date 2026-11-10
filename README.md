# SkyBook — Airline Reservation & Management System

SkyBook is a Flask + MySQL airline booking application: passengers search flights,
hold seats, pay through a simulated gateway, download a PDF e-ticket, and cancel
under a configurable refund policy. Administrators get a separate console for
flights, schedules, seat maps, bookings, passengers, payments and cancellations.

![stack](https://img.shields.io/badge/Flask-3.1-0B2A4A) ![db](https://img.shields.io/badge/MariaDB-10.4-2E86DE)

## Features

**Passenger**
- Registration and login (Flask-Login, hashed passwords)
- Flight search by route, date, airline, fare ceiling and departure window
- Interactive seat map with live availability (available / selected / held / booked)
- Transactional seat hold (10 minutes by default) with countdown
- Passenger detail capture with server-side validation
- Simulated card/UPI payment, retry after decline, idempotent gateway callback
- PDF e-ticket download (owner/admin only, confirmed bookings only)
- Booking history, booking detail and cancellation with refund quote
- Dedicated standalone pages: `/services` (amenities & cabin classes) and `/contact` (support ticketing)
- Dark mode toggle switch with theme persistence (`localStorage`) and system preference sync
- Official support channel: `shoaibmeermd@gmail.com`

**Administrator**
- Dashboard: bookings, revenue, upcoming flights, seat occupancy, recent activity
- Flight CRUD (add, edit, activate/deactivate)
- Schedule CRUD plus seat-map regeneration
- Read-only views of bookings, passengers, payments and cancellations

## Stack

| Layer | Technology |
| --- | --- |
| Language | Python 3.11+ (tested on 3.13) |
| Web | Flask 3.1, Jinja2, Bootstrap 5 |
| Auth | Flask-Login, Flask-WTF |
| Data | Flask-SQLAlchemy, SQLAlchemy 2.x, PyMySQL, MySQL / MariaDB 10.4 |
| PDF | ReportLab |
| Tests | Pytest |

## Project structure

```
SkyBook/
├── app/
│   ├── __init__.py          # application factory, blueprints, CLI commands
│   ├── config.py            # environment-driven configuration
│   ├── extensions.py        # db, login_manager, csrf
│   ├── forms.py             # login / registration forms
│   ├── models/              # 10 SQLAlchemy models
│   ├── repositories/        # data access (incl. row-level seat locking)
│   ├── services/            # business logic (booking, payment, tickets…)
│   ├── routes/              # auth, main, flights, bookings, payments, tickets, admin
│   ├── utils/               # validators, decorators, formatting helpers
│   ├── templates/           # Jinja2 UI (passenger + admin)
│   └── static/              # CSS, JS, SVG assets
├── database/
│   ├── schema.sql           # DDL for all tables
│   └── seed.sql             # demo airports, flights, schedules, seats, accounts
├── tests/                   # pytest suite (32 tests)
├── docs/design.md           # ERD, workflows, design patterns
├── generated_tickets/       # PDF output (git-ignored)
├── run.py
└── requirements.txt
```

## Setup

1. **Start MySQL** (XAMPP): start the MySQL module, or
   `C:\xampp\mysql\bin\mysqld.exe --defaults-file=C:\xampp\mysql\bin\my.ini`.
2. **Install dependencies**

   ```bash
   python -m venv .venv
   .venv/Scripts/activate        # Windows
   pip install -r requirements.txt
   ```

3. **Configure environment** — copy `.env.example` to `.env` and set `DB_*`
   values (XAMPP defaults are `root` with no password).
4. **Create and seed the database** (either route works):

   ```bash
   # Option A — SQL scripts
   mysql -u root < database/schema.sql
   mysql -u root skybook_db < database/seed.sql

   # Option B — Flask CLI
   flask --app run.py init-db
   flask --app run.py seed-db
   ```

5. **Run**

   ```bash
   python run.py
   ```

   Open <http://127.0.0.1:5000>.

`flask --app run.py reset-db` drops everything, recreates the schema and reseeds
demo data in one step.

## Demo accounts

| Role | Email | Password |
| --- | --- | --- |
| Administrator | `admin@skybook.com` | `Admin@123` |
| Passenger | `demo@skybook.com` | `Passenger@123` |
| Passenger | `riya@example.com` | `Passenger@123` |

Payment is simulated: on the payment page choose *simulate success* for a
confirmed booking and e-ticket, or *simulate failure* to see the retry path.

## Business rules

- **Seat hold:** a pending booking locks its seats for `SEAT_HOLD_MINUTES`
  (default 10). Expired holds are swept on page loads and release their seats.
- **Double-booking prevention:** `SELECT … FOR UPDATE` on seat rows, a
  `BOOKED`/`HELD` status check inside the transaction, and a unique index on
  `booking_seats.active_seat_id`.
- **Cancellation:** only confirmed, not-yet-departed bookings. Refund is the
  total minus `CANCELLATION_FEE_PERCENT` (default 10%); seats are released and
  the payment marked `REFUNDED`.
- **Tickets:** generated only for `CONFIRMED` bookings; downloads are restricted
  to the booking owner or an administrator.

## Tests

The suite runs against `skybook_test_db` (create it first if it does not exist):

```bash
python -m pytest tests -q
```

Coverage by module:

| File | What it checks |
| --- | --- |
| `test_auth.py` | registration, login success/failure, role protection, logout, CSRF & password policy |
| `test_flights.py` | search results, no-route, same-city, past/invalid date, clamping, standalone services & contact views |
| `test_bookings.py` | seat hold, duplicate/already-held seats, passenger validation, hold expiry, ownership |
| `test_payments.py` | decline keeps pending, retry, confirmation, ticket file, idempotency, callback |
| `test_cancellations.py` | eligibility, refund math, seat release, double cancellation, confirmation prompt |

Each test gets a fresh schema seeded with 2 days of schedules, so the suite never
touches `skybook_db`.

## Notes and limitations

- Payments are simulated; no real gateway is contacted.
- No Alembic migrations — the schema is created from the SQLAlchemy metadata or
  `database/schema.sql`.
- `FOR UPDATE SKIP LOCKED` is not used because MariaDB 10.4 (XAMPP) lacks it;
  the hold sweeper uses a plain `FOR UPDATE` instead.
- Timestamps are naive UTC (`datetime.utcnow()`), matching the model defaults.
- Screenshots are not included.

See `docs/design.md` for the ERD, booking workflow and design-pattern notes.
