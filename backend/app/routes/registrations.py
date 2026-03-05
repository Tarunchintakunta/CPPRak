"""Registration routes -- create, list, view, and cancel event registrations."""

import uuid
from datetime import datetime, timezone

from flask import Blueprint, request, jsonify, current_app, g

from app.middleware.auth import token_required

registrations_bp = Blueprint("registrations", __name__, url_prefix="/api/registrations")


@registrations_bp.route("/", methods=["POST"])
@token_required
def create_registration():
    """Register the current user for an event.

    Expects JSON body with ``event_id``.  Validates that the event exists,
    is active, has remaining capacity, and that the user has not already
    registered.  On success, invokes the QR generator Lambda to create a
    ticket and QR code.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        event_id = data.get("event_id", "").strip()
        if not event_id:
            return jsonify({"error": "event_id is required"}), 400

        user_id = g.current_user["user_id"]

        # Verify event exists and is active
        event = current_app.dynamo_service.get_event(event_id)
        if not event:
            return jsonify({"error": "Event not found"}), 404
        if event.get("status") != "active":
            return jsonify({"error": "Event is not active"}), 400

        # Check capacity
        existing_regs = current_app.dynamo_service.get_event_registrations(event_id)
        active_regs = [r for r in existing_regs if r.get("status") != "cancelled"]
        capacity = int(event.get("capacity", 0))
        if capacity > 0 and len(active_regs) >= capacity:
            return jsonify({"error": "Event is at full capacity"}), 409

        # Check duplicate registration
        is_duplicate = current_app.dynamo_service.check_duplicate_registration(user_id, event_id)
        if is_duplicate:
            return jsonify({"error": "You are already registered for this event"}), 409

        # Create registration record
        registration_id = str(uuid.uuid4())
        reg_item = {
            "registration_id": registration_id,
            "user_id": user_id,
            "event_id": event_id,
            "status": "confirmed",
            "checked_in": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        current_app.dynamo_service.create_registration(reg_item)

        # Invoke Lambda QR generator
        user = current_app.dynamo_service.get_user(user_id)
        lambda_payload = {
            "event_id": event_id,
            "registration_id": registration_id,
            "user_id": user_id,
            "event_name": event.get("name", ""),
        }

        lambda_result = current_app.lambda_service.invoke_qr_generator(lambda_payload)

        ticket_data = {}
        if lambda_result.get("statusCode") == 200:
            body = lambda_result.get("body", {})
            ticket_data = {
                "ticket_id": body.get("ticket_id"),
                "qr_url": body.get("qr_url"),
                "status": body.get("status"),
            }

        return jsonify({
            "message": "Registration successful",
            "registration": reg_item,
            "ticket": ticket_data,
        }), 201

    except Exception as exc:
        return jsonify({"error": f"Registration failed: {str(exc)}"}), 500


@registrations_bp.route("/", methods=["GET"])
@token_required
def list_registrations():
    """List all registrations for the current user."""
    try:
        user_id = g.current_user["user_id"]
        registrations = current_app.dynamo_service.get_user_registrations(user_id)

        # Enrich with event and ticket details
        for reg in registrations:
            event = current_app.dynamo_service.get_event(reg.get("event_id", ""))
            if event:
                reg["event_name"] = event.get("name", "")
                reg["event_date"] = event.get("date", "")
                reg["event_location"] = event.get("location", "")

            ticket = current_app.dynamo_service.get_ticket_by_registration(reg.get("registration_id", ""))
            if ticket:
                reg["ticket"] = {
                    "ticket_id": ticket.get("ticket_id"),
                    "status": ticket.get("status"),
                }

        return jsonify({"registrations": registrations}), 200

    except Exception as exc:
        return jsonify({"error": f"Failed to fetch registrations: {str(exc)}"}), 500


@registrations_bp.route("/<registration_id>", methods=["GET"])
@token_required
def get_registration(registration_id):
    """Get a single registration (must be owned by the current user)."""
    try:
        reg = current_app.dynamo_service.get_registration(registration_id)
        if not reg:
            return jsonify({"error": "Registration not found"}), 404

        # Verify ownership
        if reg["user_id"] != g.current_user["user_id"]:
            return jsonify({"error": "Access denied"}), 403

        # Attach event details
        event = current_app.dynamo_service.get_event(reg.get("event_id", ""))
        if event:
            reg["event_name"] = event.get("name", "")
            reg["event_date"] = event.get("date", "")
            reg["event_location"] = event.get("location", "")

        # Attach ticket details
        ticket = current_app.dynamo_service.get_ticket_by_registration(registration_id)
        if ticket:
            reg["ticket"] = {
                "ticket_id": ticket.get("ticket_id"),
                "status": ticket.get("status"),
            }

        return jsonify({"registration": reg}), 200

    except Exception as exc:
        return jsonify({"error": f"Failed to fetch registration: {str(exc)}"}), 500


@registrations_bp.route("/<registration_id>", methods=["DELETE"])
@token_required
def cancel_registration(registration_id):
    """Cancel a registration and revoke its associated ticket."""
    try:
        reg = current_app.dynamo_service.get_registration(registration_id)
        if not reg:
            return jsonify({"error": "Registration not found"}), 404

        # Verify ownership
        if reg["user_id"] != g.current_user["user_id"]:
            return jsonify({"error": "Access denied"}), 403

        if reg.get("status") == "cancelled":
            return jsonify({"error": "Registration is already cancelled"}), 400

        # Cancel registration
        current_app.dynamo_service.update_registration(registration_id, {
            "status": "cancelled",
            "cancelled_at": datetime.now(timezone.utc).isoformat(),
        })

        # Revoke associated ticket
        ticket = current_app.dynamo_service.get_ticket_by_registration(registration_id)
        if ticket:
            current_app.dynamo_service.update_ticket_status(
                ticket["ticket_id"], "revoked",
            )

        return jsonify({"message": "Registration cancelled successfully"}), 200

    except Exception as exc:
        return jsonify({"error": f"Failed to cancel registration: {str(exc)}"}), 500
