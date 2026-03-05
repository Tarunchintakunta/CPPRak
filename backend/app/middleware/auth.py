"""JWT authentication decorators for Flask route protection."""

from functools import wraps

from flask import request, jsonify, current_app, g


def token_required(f):
    """Decorator that enforces a valid JWT in the Authorization header.

    Expects the header format ``Authorization: Bearer <token>``.  On success
    the decoded user payload is stored on ``g.current_user`` so that route
    handlers can access the authenticated user's ``user_id``, ``email``, and
    ``role`` without repeating verification logic.

    Returns a 401 JSON response if the token is missing, malformed, or invalid.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"error": "Authorization header is missing"}), 401

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"error": "Invalid authorization format. Use: Bearer <token>"}), 401

        token = parts[1]

        try:
            payload = current_app.auth_service.verify_token(token)
            if payload is None:
                return jsonify({"error": "Token is invalid or expired"}), 401

            g.current_user = payload
        except Exception:
            return jsonify({"error": "Token verification failed"}), 401

        return f(*args, **kwargs)

    return decorated


def admin_required(f):
    """Decorator that enforces admin-level access.

    Must be used *instead of* (not in addition to) ``token_required`` because
    it already performs token verification internally.  Returns 403 if the
    authenticated user's role is not ``"admin"``.
    """

    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        user = g.current_user
        if user.get("role") != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)

    return decorated
