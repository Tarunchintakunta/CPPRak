"""Event management routes -- CRUD operations for events."""

import uuid
from datetime import datetime, timezone

from flask import Blueprint, request, jsonify, current_app

from app.middleware.auth import admin_required

events_bp = Blueprint("events", __name__, url_prefix="/api/events")


@events_bp.route("/", methods=["GET"])
def list_events():
    """List all active events (public endpoint)."""
    try:
        status = request.args.get("status", "active")
        events = current_app.dynamo_service.list_events(status=status)
        return jsonify({"events": events}), 200
    except Exception as exc:
        return jsonify({"error": f"Failed to list events: {str(exc)}"}), 500


@events_bp.route("/<event_id>", methods=["GET"])
def get_event(event_id):
    """Get a single event by ID (public endpoint)."""
    try:
        event = current_app.dynamo_service.get_event(event_id)
        if not event:
            return jsonify({"error": "Event not found"}), 404
        return jsonify({"event": event}), 200
    except Exception as exc:
        return jsonify({"error": f"Failed to fetch event: {str(exc)}"}), 500


@events_bp.route("/", methods=["POST"])
@admin_required
def create_event():
    """Create a new event (admin only).

    Expects JSON body with ``name``, ``description``, ``date``, ``time``,
    ``location``, and ``capacity``.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        required = ["name", "date", "time", "location", "capacity"]
        missing = [f for f in required if not data.get(f)]
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        event_id = str(uuid.uuid4())
        event_item = {
            "event_id": event_id,
            "name": data["name"],
            "description": data.get("description", ""),
            "date": data["date"],
            "time": data["time"],
            "location": data["location"],
            "capacity": int(data["capacity"]),
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        current_app.dynamo_service.create_event(event_item)

        return jsonify({
            "message": "Event created successfully",
            "event": event_item,
        }), 201

    except Exception as exc:
        return jsonify({"error": f"Failed to create event: {str(exc)}"}), 500


@events_bp.route("/<event_id>", methods=["PUT"])
@admin_required
def update_event(event_id):
    """Update an existing event (admin only).

    Accepts any subset of event fields in the JSON body.
    """
    try:
        # Verify event exists
        event = current_app.dynamo_service.get_event(event_id)
        if not event:
            return jsonify({"error": "Event not found"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        # Only allow known fields to be updated
        allowed_fields = {"name", "description", "date", "time", "location", "capacity", "status"}
        updates = {}
        for field in allowed_fields:
            if field in data:
                value = data[field]
                if field == "capacity":
                    value = int(value)
                updates[field] = value

        if not updates:
            return jsonify({"error": "No valid fields to update"}), 400

        updated = current_app.dynamo_service.update_event(event_id, updates)

        return jsonify({
            "message": "Event updated successfully",
            "event": updated,
        }), 200

    except Exception as exc:
        return jsonify({"error": f"Failed to update event: {str(exc)}"}), 500


@events_bp.route("/<event_id>", methods=["DELETE"])
@admin_required
def delete_event(event_id):
    """Delete an event (admin only)."""
    try:
        event = current_app.dynamo_service.get_event(event_id)
        if not event:
            return jsonify({"error": "Event not found"}), 404

        current_app.dynamo_service.delete_event(event_id)

        return jsonify({"message": "Event deleted successfully"}), 200

    except Exception as exc:
        return jsonify({"error": f"Failed to delete event: {str(exc)}"}), 500
