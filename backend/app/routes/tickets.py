"""Ticket routes -- view ticket details, serve QR images, and validate tickets."""

import os

from flask import Blueprint, request, jsonify, current_app, g, send_file, redirect

from app.middleware.auth import token_required

tickets_bp = Blueprint("tickets", __name__, url_prefix="/api/tickets")


@tickets_bp.route("/<ticket_id>", methods=["GET"])
@token_required
def get_ticket(ticket_id):
    """Get ticket details for a given ticket ID.

    The ticket must belong to the currently authenticated user (verified
    via the user_id stored on the ticket record).
    """
    try:
        ticket = current_app.dynamo_service.get_ticket(ticket_id)
        if not ticket:
            return jsonify({"error": "Ticket not found"}), 404

        # Verify ownership
        if ticket.get("user_id") != g.current_user["user_id"]:
            return jsonify({"error": "Access denied"}), 403

        # Attach a QR image URL
        qr_url = current_app.s3_service.get_qr_image_url(ticket_id)
        ticket["qr_url"] = qr_url

        return jsonify({"ticket": ticket}), 200

    except Exception as exc:
        return jsonify({"error": f"Failed to fetch ticket: {str(exc)}"}), 500


@tickets_bp.route("/<ticket_id>/qr", methods=["GET"])
def get_qr_image(ticket_id):
    """Serve the QR code image for a ticket.

    In local development mode the PNG file is served directly from the
    filesystem.  In production mode the client is redirected to an S3
    presigned URL.
    """
    try:
        # Try local file first
        local_path = current_app.s3_service.get_local_image_path(ticket_id)
        if local_path and os.path.isfile(local_path):
            return send_file(local_path, mimetype="image/png")

        # Fall back to S3 presigned URL redirect
        presigned_url = current_app.s3_service.get_qr_image_url(ticket_id)
        if presigned_url:
            return redirect(presigned_url)

        return jsonify({"error": "QR code image not found"}), 404

    except Exception as exc:
        return jsonify({"error": f"Failed to serve QR image: {str(exc)}"}), 500


@tickets_bp.route("/validate", methods=["POST"])
def validate_ticket():
    """Validate QR code data via the QR validator Lambda.

    Expects JSON body with ``qr_data`` -- the raw string scanned from the
    QR code.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        qr_data = data.get("qr_data", "")
        if not qr_data:
            return jsonify({"error": "qr_data is required"}), 400

        result = current_app.lambda_service.invoke_qr_validator({"qr_data": qr_data})

        status_code = result.get("statusCode", 500)
        body = result.get("body", {})

        return jsonify(body), status_code

    except Exception as exc:
        return jsonify({"error": f"Validation failed: {str(exc)}"}), 500
