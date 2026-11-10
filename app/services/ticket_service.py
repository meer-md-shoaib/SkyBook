"""Electronic ticket generation (ReportLab PDF)."""
import os
from datetime import datetime

from flask import current_app
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from app.extensions import db
from app.models import Ticket

NAVY = HexColor("#0B2A4A")
SKY = HexColor("#2E86DE")
LIGHT = HexColor("#EAF3FB")
GREY = HexColor("#6B7C93")
GREEN = HexColor("#1E9E6A")


class TicketService:
    def output_dir(self) -> str:
        folder = current_app.config.get("TICKET_OUTPUT_DIR", "generated_tickets")
        if not os.path.isabs(folder):
            folder = os.path.join(current_app.root_path, "..", folder)
        folder = os.path.abspath(folder)
        os.makedirs(folder, exist_ok=True)
        return folder

    # ------------------------------------------------------------------
    def generate_for_booking(self, booking) -> Ticket | None:
        """Create (or refresh) the e-ticket for a CONFIRMED booking."""
        if booking.booking_status != "CONFIRMED":
            return None

        ticket = booking.ticket
        if ticket is None:
            ticket = Ticket(booking_id=booking.booking_id)
            db.session.add(ticket)
            db.session.flush()

        filename = f"{booking.booking_reference}.pdf"
        path = os.path.join(self.output_dir(), filename)
        self._render(booking, ticket, path)
        ticket.file_path = filename
        ticket.generated_at = datetime.utcnow()
        db.session.add(ticket)
        return ticket

    def file_for(self, booking) -> str | None:
        ticket = booking.ticket
        if not ticket:
            return None
        filename = ticket.file_path or f"{booking.booking_reference}.pdf"
        path = os.path.join(self.output_dir(), filename)
        return path if os.path.exists(path) else None

    # ------------------------------------------------------------------
    def _render(self, booking, ticket, path: str) -> None:
        schedule = booking.schedule
        flight = schedule.flight
        width, height = A4
        c = canvas.Canvas(path, pagesize=A4)
        c.setTitle(f"SkyBook e-ticket {booking.booking_reference}")

        # ---- header band ------------------------------------------------
        c.setFillColor(NAVY)
        c.rect(0, height - 42 * mm, width, 42 * mm, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 28)
        c.drawString(20 * mm, height - 24 * mm, "SkyBook")
        c.setFont("Helvetica", 9)
        c.setFillColor(HexColor("#9CC3E8"))
        c.drawString(20 * mm, height - 30 * mm, "BOOK FLIGHTS SEAMLESSLY ACROSS THE GLOBE")
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 18)
        c.drawRightString(width - 20 * mm, height - 22 * mm, "E-TICKET")
        c.setFont("Helvetica", 9)
        c.setFillColor(HexColor("#9CC3E8"))
        c.drawRightString(width - 20 * mm, height - 29 * mm, "BOARDING CONFIRMATION")

        # ---- booking reference strip -----------------------------------
        c.setFillColor(LIGHT)
        c.rect(20 * mm, height - 58 * mm, width - 40 * mm, 12 * mm, fill=1, stroke=0)
        c.setFillColor(GREY)
        c.setFont("Helvetica", 8)
        c.drawString(24 * mm, height - 49 * mm, "BOOKING REFERENCE")
        c.drawString(84 * mm, height - 49 * mm, "TICKET NUMBER")
        c.drawString(134 * mm, height - 49 * mm, "ISSUED ON")
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(24 * mm, height - 55 * mm, booking.booking_reference)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(84 * mm, height - 55 * mm, ticket.ticket_number)
        c.setFont("Helvetica", 10)
        c.drawString(134 * mm, height - 55 * mm, ticket.generated_at.strftime("%d %b %Y"))

        # ---- route block ------------------------------------------------
        top = height - 74 * mm
        c.setFillColor(SKY)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(20 * mm, top, f"{flight.airline_name.upper()}  ·  {flight.flight_number}")

        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 26)
        c.drawString(20 * mm, top - 14 * mm, flight.source_airport.airport_code)
        c.setFont("Helvetica", 10)
        c.setFillColor(GREY)
        c.drawString(20 * mm, top - 20 * mm, flight.source_airport.city)
        c.drawString(20 * mm, top - 26 * mm, schedule.departure_time.strftime("%I:%M %p · %d %b %Y"))

        c.setFillColor(GREY)
        c.setFont("Helvetica", 9)
        c.drawCentredString(105 * mm, top - 9 * mm, schedule.duration_label)
        c.setStrokeColor(HexColor("#C9DCEF"))
        c.setLineWidth(1)
        c.line(62 * mm, top - 11 * mm, 148 * mm, top - 11 * mm)
        c.setFillColor(SKY)
        c.circle(105 * mm, top - 11 * mm, 1.6 * mm, fill=1, stroke=0)

        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 26)
        c.drawRightString(width - 20 * mm, top - 14 * mm, flight.destination_airport.airport_code)
        c.setFillColor(GREY)
        c.setFont("Helvetica", 10)
        c.drawRightString(width - 20 * mm, top - 20 * mm, flight.destination_airport.city)
        c.drawRightString(
            width - 20 * mm, top - 26 * mm, schedule.arrival_time.strftime("%I:%M %p · %d %b %Y")
        )

        # ---- flight meta -------------------------------------------------
        meta_top = top - 40 * mm
        c.setFillColor(LIGHT)
        c.rect(20 * mm, meta_top, width - 40 * mm, 18 * mm, fill=1, stroke=0)
        labels = [
            ("AIRCRAFT", flight.aircraft_type),
            ("SEAT(S)", booking.seat_numbers or "—"),
            ("PASSENGERS", str(booking.passenger_count)),
        ]
        for i, (label, value) in enumerate(labels):
            x = 26 * mm + i * 55 * mm
            c.setFillColor(GREY)
            c.setFont("Helvetica", 7.5)
            c.drawString(x, meta_top + 12 * mm, label)
            c.setFillColor(NAVY)
            c.setFont("Helvetica-Bold", 10.5)
            c.drawString(x, meta_top + 6 * mm, value)

        # ---- passenger table --------------------------------------------
        table_top = meta_top - 16 * mm
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(20 * mm, table_top, "PASSENGER DETAILS")

        row_y = table_top - 8 * mm
        c.setFillColor(HexColor("#F5F9FD"))
        c.rect(20 * mm, row_y - 4 * mm, width - 40 * mm, 8 * mm, fill=1, stroke=0)
        c.setFillColor(GREY)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(23 * mm, row_y - 1.5 * mm, "NAME")
        c.drawString(68 * mm, row_y - 1.5 * mm, "DATE OF BIRTH")
        c.drawString(103 * mm, row_y - 1.5 * mm, "ID TYPE")
        c.drawString(135 * mm, row_y - 1.5 * mm, "ID NUMBER")
        c.drawString(168 * mm, row_y - 1.5 * mm, "SEAT")

        row_y -= 10 * mm
        for passenger in booking.passengers:
            c.setStrokeColor(HexColor("#E3EDF7"))
            c.line(20 * mm, row_y + 4 * mm, width - 20 * mm, row_y + 4 * mm)
            c.setFillColor(NAVY)
            c.setFont("Helvetica-Bold", 9)
            c.drawString(23 * mm, row_y, passenger.full_name[:26])
            c.setFont("Helvetica", 9)
            c.setFillColor(GREY)
            c.drawString(68 * mm, row_y, passenger.date_of_birth.strftime("%d %b %Y"))
            c.drawString(103 * mm, row_y, passenger.identification_type.replace("_", " ").title())
            c.drawString(135 * mm, row_y, passenger.masked_id)
            c.setFillColor(NAVY)
            c.setFont("Helvetica-Bold", 9)
            c.drawString(168 * mm, row_y, passenger.seat.seat_number if passenger.seat else "—")
            row_y -= 9 * mm

        # ---- payment / status box ---------------------------------------
        box_y = row_y - 14 * mm
        c.setFillColor(HexColor("#F5F9FD"))
        c.rect(20 * mm, box_y, width - 40 * mm, 24 * mm, fill=1, stroke=0)
        payment = booking.payment
        c.setFillColor(GREY)
        c.setFont("Helvetica", 7.5)
        c.drawString(24 * mm, box_y + 17 * mm, "TOTAL PAID")
        c.drawString(80 * mm, box_y + 17 * mm, "PAYMENT STATUS")
        c.drawString(136 * mm, box_y + 17 * mm, "BOOKING STATUS")

        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(24 * mm, box_y + 9 * mm, "INR {:,.0f}".format(float(booking.total_amount)))
        c.setFillColor(GREEN)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(80 * mm, box_y + 9 * mm, payment.payment_status if payment else "—")
        c.drawString(136 * mm, box_y + 9 * mm, booking.booking_status)

        # ---- footer ------------------------------------------------------
        c.setStrokeColor(HexColor("#C9DCEF"))
        c.line(20 * mm, 30 * mm, width - 20 * mm, 30 * mm)
        c.setFillColor(GREY)
        c.setFont("Helvetica", 7.5)
        c.drawString(
            20 * mm, 24 * mm,
            "Please carry a valid government-issued photo ID matching the details above.",
        )
        c.drawString(
            20 * mm, 20 * mm,
            "Report to the airport at least 2 hours before departure. This is a computer-generated ticket.",
        )
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 8)
        c.drawRightString(width - 20 * mm, 24 * mm, "SkyBook · support@skybook.example")
        c.setFillColor(SKY)
        c.setFont("Helvetica", 7)
        c.drawCentredString(width / 2, 12 * mm, f"Ticket {ticket.ticket_number} · Transaction generated for booking {booking.booking_reference}")
        c.showPage()
        c.save()
