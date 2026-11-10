# SkyBook — Design Notes

## 1. Data model (ERD)

```
users ──1:N── bookings ──1:N── passengers
                  │                │
                  │                └──N:1── seats
                  ├──1:1── payments
                  ├──1:1── tickets
                  ├──1:1── cancellations
                  └──1:N── booking_seats ──N:1── seats
                              (active_seat_id UNIQUE)

airports ──1:N── flights (source_airport_id, destination_airport_id)
flights  ──1:N── flight_schedules ──1:N── seats
```

| Table | Purpose |
| --- | --- |
| `users` | Accounts; `role` is `PASSENGER` or `ADMIN`, `is_active` gates login |
| `airports` | IATA code, name, city, country |
| `flights` | Airline, flight number, route, aircraft, active flag |
| `flight_schedules` | A flight on a date with departure/arrival, base fare, status |
| `seats` | Per-schedule seat inventory: class, row/column, `AVAILABLE`/`HELD`/`BOOKED` |
| `bookings` | One reservation, `PENDING`/`CONFIRMED`/`CANCELLED`/`EXPIRED`, hold expiry |
| `booking_seats` | Join table; `is_active` + unique `active_seat_id` enforces one live hold per seat |
| `passengers` | Traveller details, one per held seat |
| `payments` | One per booking, transaction reference, status, attempts |
| `tickets` | One per confirmed booking, ticket number and PDF filename |
| `cancellations` | Refund record with reason, amount and refund status |

## 2. Layering

- **Routes** parse requests, call services, render templates. No SQL.
- **Services** hold business rules and transactions.
- **Repositories** encapsulate queries, including seat locking.
- **Models** are persistence + small derived properties (e.g. `seat_numbers`,
  `is_hold_expired`, `available_seats`).

This keeps the booking transaction and refund policy testable without HTTP.

## 3. Booking workflow

1. `GET /flights/results` — `FlightService.search()` validates input and filters
   schedules by route, date, airline, price and time window, keeping only those
   with enough free seats for the party.
2. `GET /flights/<schedule>/seats` — seat map grouped by row, with counts.
3. `POST …/seats/hold` — `BookingService.create_pending_booking()`:
   opens a transaction, inserts the booking, `SELECT … FOR UPDATE`s the requested
   seats, re-checks each is `AVAILABLE`, flips them to `HELD`, writes
   `booking_seats` rows and the total, then commits. Any conflict rolls back.
4. `POST /bookings/<id>/passengers` — validation and one passenger per seat.
5. `GET /bookings/<id>/summary` — review page.
6. `POST /payments/<id>/pay` — payment strategy charges the mock gateway; on
   success the booking is confirmed, seats become `BOOKED`, and the PDF ticket is
   generated.
7. `GET /tickets/<id>/download` — owner/admin only.

Holds that lapse are expired by `BookingService.expire_stale_holds()`, which
releases seats, marks the booking `EXPIRED` and fails any pending payment. It is
called on search results, seat maps, booking pages and payments.

## 4. Concurrency and integrity

- Row-level locks on seat rows serialise competing bookings.
- The status re-check happens *after* acquiring the lock, so a seat taken between
  page render and submit is rejected with a friendly message.
- `uq_active_seat` guarantees at most one active booking-seat row per seat, even
  if application logic were bypassed.
- `uq_booking_seat` prevents the same seat appearing twice in one booking.
- Payment charges lock the booking row, so duplicate submissions return the
  existing result instead of charging twice.

## 5. Design patterns

| Pattern | Where |
| --- | --- |
| Application factory | `create_app()` in `app/__init__.py` |
| Blueprints | auth, main, flights, bookings, payments, tickets, admin |
| Repository | `app/repositories/*` |
| Service layer | `app/services/*` |
| Strategy + Factory | `PaymentStrategy`, `MockSuccessStrategy`, `MockFailureStrategy`, `PaymentStrategyFactory` |
| Decorator | `@admin_required` in `app/utils/decorators.py` |

Swapping in a real gateway means implementing `PaymentStrategy` and returning it
from `PaymentStrategyFactory`; no route or service changes are required.

## 6. Refund policy

`CancellationService.refund_quote()` computes:

```
fee    = total_amount * CANCELLATION_FEE_PERCENT / 100
refund = max(total_amount - fee, 0)
```

`cancel()` releases seats, marks the booking `CANCELLED`, records a `PROCESSED`
cancellation and flips a successful payment to `REFUNDED`. Eligibility rejects
pending, expired, already-cancelled and departed bookings.

## 7. Known constraints

- MariaDB 10.4 has no `SKIP LOCKED`; the sweeper uses plain `FOR UPDATE`.
- Timestamps are naive UTC to match column defaults.
- No migration tooling; schema changes require `reset-db` or a manual migration.
