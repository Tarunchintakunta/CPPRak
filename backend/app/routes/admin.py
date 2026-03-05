"""Admin routes -- dashboard stats, attendee lists, and CSV export."""

import csv
import io
from datetime import datetime, timezone

from flask import Blueprint, jsonify, current_app, make_response

from app.middleware.auth import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.route("/dashboard", methods=["GET"])
@admin_required
def dashboard():
    """Return aggregate statistics for the admin dashboard.

    Counts are gathered by scanning the respective DynamoDB tables.
    """
    try:
        users = current_app.dynamo_service.scan_table("Users")
        events = current_app.dynamo_service.scan_table("Events")
        registrations = current_app.dynamo_service.scan_table("Registrations")
        tickets = current_app.dynamo_service.scan_table("Tickets")

        active_events = [e for e in events if e.get("status") == "active"]
        confirmed_regs = [r for r in registrations if r.get("status") != "cancelled"]

        stats = {
            "total_users": len(users),
            "total_events": len(events),
            "active_events": len(active_events),
            "total_registrations": len(registrations),
            "confirmed_registrations": len(confirmed_regs),
            "total_tickets": len(tickets),
        }

        return jsonify({"stats": stats}), 200

    except Exception as exc:
        return jsonify({"error": f"Failed to fetch dashboard stats: {str(exc)}"}), 500


@admin_bp.route("/events/<event_id>/attendees", methods=["GET"])
@admin_required
def event_attendees(event_id):
    """Get all registrations for an event, enriched with user details."""
    try:
        event = current_app.dynamo_service.get_event(event_id)
        if not event:
            return jsonify({"error": "Event not found"}), 404

        registrations = current_app.dynamo_service.get_event_registrations(event_id)

        attendees = []
        for reg in registrations:
            user = current_app.dynamo_service.get_user(reg.get("user_id", ""))
            attendee = {
                "registration_id": reg.get("registration_id"),
                "user_id": reg.get("user_id"),
                "name": user.get("name", "") if user else "",
                "email": user.get("email", "") if user else "",
                "status": reg.get("status"),
                "checked_in": reg.get("checked_in", False),
                "registered_at": reg.get("created_at", ""),
            }

            # Attach ticket info if available
            ticket = current_app.dynamo_service.get_ticket_by_registration(
                reg.get("registration_id", ""),
            )
            if ticket:
                attendee["ticket_id"] = ticket.get("ticket_id")
                attendee["ticket_status"] = ticket.get("status")

            attendees.append(attendee)

        return jsonify({
            "event": {
                "event_id": event.get("event_id"),
                "name": event.get("name"),
                "date": event.get("date"),
            },
            "attendees": attendees,
            "total": len(attendees),
        }), 200

    except Exception as exc:
        return jsonify({"error": f"Failed to fetch attendees: {str(exc)}"}), 500


@admin_bp.route("/events/<event_id>/export", methods=["GET"])
@admin_required
def export_attendees(event_id):
    """Export the attendee list for an event as a CSV file."""
    try:
        event = current_app.dynamo_service.get_event(event_id)
        if not event:
            return jsonify({"error": "Event not found"}), 404

        registrations = current_app.dynamo_service.get_event_registrations(event_id)

        # Build CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Registration ID",
            "User ID",
            "Name",
            "Email",
            "Status",
            "Checked In",
            "Registered At",
            "Ticket ID",
            "Ticket Status",
        ])

        for reg in registrations:
            user = current_app.dynamo_service.get_user(reg.get("user_id", ""))
            ticket = current_app.dynamo_service.get_ticket_by_registration(
                reg.get("registration_id", ""),
            )

            writer.writerow([
                reg.get("registration_id", ""),
                reg.get("user_id", ""),
                user.get("name", "") if user else "",
                user.get("email", "") if user else "",
                reg.get("status", ""),
                reg.get("checked_in", False),
                reg.get("created_at", ""),
                ticket.get("ticket_id", "") if ticket else "",
                ticket.get("status", "") if ticket else "",
            ])

        csv_content = output.getvalue()
        output.close()

        event_name = event.get("name", "event").replace(" ", "_")
        filename = f"attendees_{event_name}_{event_id[:8]}.csv"

        response = make_response(csv_content)
        response.headers["Content-Type"] = "text/csv"
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"

        return response

    except Exception as exc:
        return jsonify({"error": f"Failed to export attendees: {str(exc)}"}), 500
