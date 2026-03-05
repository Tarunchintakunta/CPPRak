"""HMAC-SHA256 based ticket ID generation and payload signing."""

import hashlib
import hmac
import json
import uuid
from datetime import datetime, timezone

from .exceptions import TicketGenerationError
from .logger import TicketLogger


class TicketGenerator:
    """Generates cryptographically signed ticket IDs and payloads.

    Uses HMAC-SHA256 to create tamper-proof ticket identifiers that encode
    event and registration information.

    Attributes:
        secret_key: The secret key used for HMAC signing.
        logger: Structured logger instance.
    """

    def __init__(self, secret_key: str):
        if not secret_key:
            raise TicketGenerationError("Secret key must not be empty")
        self.secret_key = secret_key
        self.logger = TicketLogger("TicketGenerator")

    def generate_ticket_id(self) -> str:
        """Generate a unique ticket ID."""
        return str(uuid.uuid4())

    def create_signature(self, payload: dict) -> str:
        """Create HMAC-SHA256 signature for a payload.

        Args:
            payload: Dictionary of ticket data to sign.

        Returns:
            Hex-encoded HMAC-SHA256 signature string.
        """
        payload_str = json.dumps(payload, sort_keys=True, default=str)
        signature = hmac.new(
            self.secret_key.encode("utf-8"),
            payload_str.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return signature

    def generate_ticket(self, event_id: str, registration_id: str,
                        user_id: str, event_name: str) -> dict:
        """Generate a complete signed ticket.

        Args:
            event_id: The event identifier.
            registration_id: The registration identifier.
            user_id: The user identifier.
            event_name: Human-readable event name.

        Returns:
            Dictionary with ticket_id, payload, signature, and metadata.

        Raises:
            TicketGenerationError: If any required field is missing.
        """
        if not all([event_id, registration_id, user_id, event_name]):
            raise TicketGenerationError("All ticket fields are required")

        ticket_id = self.generate_ticket_id()
        created_at = datetime.now(timezone.utc).isoformat()

        payload = {
            "ticket_id": ticket_id,
            "event_id": event_id,
            "registration_id": registration_id,
            "user_id": user_id,
            "event_name": event_name,
            "created_at": created_at,
        }

        signature = self.create_signature(payload)

        ticket = {
            "ticket_id": ticket_id,
            "payload": payload,
            "signature": signature,
            "status": "valid",
            "created_at": created_at,
        }

        self.logger.info(
            "Ticket generated",
            ticket_id=ticket_id,
            event_id=event_id,
            registration_id=registration_id,
        )

        return ticket

    def create_qr_payload(self, ticket: dict) -> str:
        """Create the string payload to encode in a QR code.

        Args:
            ticket: The full ticket dictionary from generate_ticket().

        Returns:
            JSON string containing ticket_id, payload, and signature.
        """
        qr_data = {
            "ticket_id": ticket["ticket_id"],
            "payload": ticket["payload"],
            "signature": ticket["signature"],
        }
        return json.dumps(qr_data, default=str)
