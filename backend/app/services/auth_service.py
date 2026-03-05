"""JWT authentication service.

Provides password hashing (bcrypt) and JWT token generation / verification.
All configuration is passed at init time -- no Flask dependency required.
"""

import logging
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

logger = logging.getLogger(__name__)


class AuthService:
    """Handles password hashing, JWT creation, and JWT verification."""

    def __init__(self, secret_key, expiration_hours=24):
        """Initialise the auth service.

        Args:
            secret_key: The secret used to sign and verify JWT tokens.
            expiration_hours: Number of hours before a token expires
                              (default 24).
        """
        self.secret_key = secret_key
        self.expiration_hours = expiration_hours

    # ------------------------------------------------------------------
    # Password helpers
    # ------------------------------------------------------------------

    def hash_password(self, password):
        """Hash a plaintext password using bcrypt.

        Args:
            password: The plaintext password string.

        Returns:
            The bcrypt hash as a UTF-8 string.
        """
        try:
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
            return hashed.decode("utf-8")
        except Exception as exc:
            logger.error("Failed to hash password: %s", exc)
            raise

    def verify_password(self, password, hashed):
        """Verify a plaintext password against a bcrypt hash.

        Args:
            password: The plaintext password to check.
            hashed: The stored bcrypt hash string.

        Returns:
            True if the password matches, False otherwise.
        """
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"),
                hashed.encode("utf-8") if isinstance(hashed, str) else hashed,
            )
        except Exception as exc:
            logger.error("Failed to verify password: %s", exc)
            return False

    # ------------------------------------------------------------------
    # JWT helpers
    # ------------------------------------------------------------------

    def generate_token(self, user_id, email, role="user"):
        """Generate a signed JWT for the given user.

        The token payload includes:
          - ``user_id``
          - ``email``
          - ``role``
          - ``iat`` (issued-at timestamp)
          - ``exp`` (expiration timestamp)

        Args:
            user_id: Unique user identifier.
            email: User's email address.
            role: User role string (default ``"user"``).

        Returns:
            The encoded JWT string.
        """
        try:
            now = datetime.now(timezone.utc)
            payload = {
                "user_id": user_id,
                "email": email,
                "role": role,
                "iat": now,
                "exp": now + timedelta(hours=self.expiration_hours),
            }
            token = jwt.encode(payload, self.secret_key, algorithm="HS256")
            return token
        except Exception as exc:
            logger.error("Failed to generate token: %s", exc)
            raise

    def verify_token(self, token):
        """Decode and validate a JWT.

        Args:
            token: The encoded JWT string.

        Returns:
            The decoded payload dict on success, or ``None`` if the token
            is invalid or expired.
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired.")
            return None
        except jwt.InvalidTokenError as exc:
            logger.warning("Invalid token: %s", exc)
            return None
