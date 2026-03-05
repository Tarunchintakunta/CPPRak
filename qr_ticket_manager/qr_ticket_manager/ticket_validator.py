"""Ticket validation with HMAC signature verification and status checking."""

import json
from .exceptions import (
    InvalidSignatureError,
    TicketAlreadyUsedError,
    TicketRevokedError,
    TicketValidationError,
)
from .ticket_generator import TicketGenerator
from .logger import TicketLogger


class TicketValidator:
    """Validates ticket authenticity and status.

    Performs two-layer validation:
    1. Cryptographic: HMAC-SHA256 signature verification
    2. Status: Check ticket hasn't been used, revoked, or expired

    Attributes:
        generator: TicketGenerator instance for signature operations.
        logger: Structured logger instance.
    """

    VALID_STATUSES = {"valid", "used", "revoked", "expired"}

    def __init__(self, secret_key: str):
        self.generator = TicketGenerator(secret_key)
        self.logger = TicketLogger("TicketValidator")

    def verify_signature(self, payload: dict, signature: str) -> bool:
        """Verify the HMAC-SHA256 signature of a ticket payload.

        Args:
            payload: The ticket payload dictionary.
            signature: The hex-encoded HMAC signature to verify.

        Returns:
            True if signature is valid.

        Raises:
            InvalidSignatureError: If the signature doesn't match.
        """
        expected_signature = self.generator.create_signature(payload)
        if expected_signature != signature:
            self.logger.warning("Invalid signature detected",
                                ticket_id=payload.get("ticket_id"))
            raise InvalidSignatureError()
        return True

    def check_status(self, status: str) -> bool:
        """Check if a ticket status allows entry.

        Args:
            status: Current ticket status string.

        Returns:
            True if ticket status is "valid".

        Raises:
            TicketAlreadyUsedError: If ticket was already used.
            TicketRevokedError: If ticket was revoked.
            TicketValidationError: For other invalid statuses.
        """
        if status == "valid":
            return True
        elif status == "used":
            raise TicketAlreadyUsedError()
        elif status == "revoked":
            raise TicketRevokedError()
        else:
            raise TicketValidationError(f"Invalid ticket status: {status}")

    def validate_ticket(self, qr_data: str, get_ticket_status=None) -> dict:
        """Full ticket validation from QR code data.

        Args:
            qr_data: JSON string from QR code scan.
            get_ticket_status: Optional callable that takes ticket_id and
                returns the current status from the database.

        Returns:
            Dictionary with validation result including ticket_id and status.

        Raises:
            TicketValidationError: If validation fails at any step.
        """
        try:
            data = json.loads(qr_data)
        except json.JSONDecodeError:
            raise TicketValidationError("Invalid QR code data format")

        ticket_id = data.get("ticket_id")
        payload = data.get("payload")
        signature = data.get("signature")

        if not all([ticket_id, payload, signature]):
            raise TicketValidationError("Missing required ticket fields")

        # Layer 1: Cryptographic verification
        self.verify_signature(payload, signature)
        self.logger.info("Signature verified", ticket_id=ticket_id)

        # Layer 2: Status check (from database if callback provided)
        if get_ticket_status:
            status = get_ticket_status(ticket_id)
        else:
            status = "valid"

        self.check_status(status)
        self.logger.info("Ticket validated successfully", ticket_id=ticket_id)

        return {
            "valid": True,
            "ticket_id": ticket_id,
            "event_id": payload.get("event_id"),
            "user_id": payload.get("user_id"),
            "message": "Ticket is valid for entry",
        }
