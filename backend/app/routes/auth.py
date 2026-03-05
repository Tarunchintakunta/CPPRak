"""Authentication routes -- register, login, and profile retrieval."""

import uuid
from datetime import datetime, timezone

from flask import Blueprint, request, jsonify, current_app, g

from app.middleware.auth import token_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user account.

    Expects JSON body with ``name``, ``email``, and ``password``.
    Returns a JWT token on success.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        name = data.get("name", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not all([name, email, password]):
            return jsonify({"error": "Name, email, and password are required"}), 400

        # Check for duplicate email
        existing = current_app.dynamo_service.get_user_by_email(email)
        if existing:
            return jsonify({"error": "Email is already registered"}), 409

        # Hash password and build user record
        password_hash = current_app.auth_service.hash_password(password)
        user_id = str(uuid.uuid4())

        user_item = {
            "user_id": user_id,
            "name": name,
            "email": email,
            "password_hash": password_hash,
            "role": "user",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        current_app.dynamo_service.create_user(user_item)

        # Generate JWT
        token = current_app.auth_service.generate_token(user_id, email, "user")

        return jsonify({
            "message": "User registered successfully",
            "token": token,
            "user": {
                "user_id": user_id,
                "name": name,
                "email": email,
                "role": "user",
            },
        }), 201

    except Exception as exc:
        return jsonify({"error": f"Registration failed: {str(exc)}"}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate an existing user.

    Expects JSON body with ``email`` and ``password``.
    Returns a JWT token on success.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not all([email, password]):
            return jsonify({"error": "Email and password are required"}), 400

        # Look up user
        user = current_app.dynamo_service.get_user_by_email(email)
        if not user:
            return jsonify({"error": "Invalid email or password"}), 401

        # Verify password
        if not current_app.auth_service.verify_password(password, user["password_hash"]):
            return jsonify({"error": "Invalid email or password"}), 401

        # Generate JWT
        token = current_app.auth_service.generate_token(
            user["user_id"], user["email"], user.get("role", "user"),
        )

        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": {
                "user_id": user["user_id"],
                "name": user.get("name", ""),
                "email": user["email"],
                "role": user.get("role", "user"),
            },
        }), 200

    except Exception as exc:
        return jsonify({"error": f"Login failed: {str(exc)}"}), 500


@auth_bp.route("/me", methods=["GET"])
@token_required
def me():
    """Return the profile of the currently authenticated user."""
    try:
        user_id = g.current_user["user_id"]
        user = current_app.dynamo_service.get_user(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Strip the password hash before returning
        user.pop("password_hash", None)

        return jsonify({"user": user}), 200

    except Exception as exc:
        return jsonify({"error": f"Failed to fetch profile: {str(exc)}"}), 500
