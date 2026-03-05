"""Custom exception hierarchy for the QR Ticket Manager library."""


class QRTicketError(Exception):
    """Base exception for all QR Ticket Manager errors."""

    def __init__(self, message: str, code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class TicketGenerationError(QRTicketError):
    """Raised when ticket generation fails."""

    def __init__(self, message: str = "Failed to generate ticket"):
        super().__init__(message, code="TICKET_GENERATION_ERROR")


class TicketValidationError(QRTicketError):
    """Raised when ticket validation fails."""

    def __init__(self, message: str = "Ticket validation failed"):
        super().__init__(message, code="TICKET_VALIDATION_ERROR")


class InvalidSignatureError(TicketValidationError):
    """Raised when HMAC signature verification fails."""

    def __init__(self, message: str = "Invalid ticket signature"):
        super().__init__(message)
        self.code = "INVALID_SIGNATURE"


class TicketExpiredError(TicketValidationError):
    """Raised when a ticket has expired."""

    def __init__(self, message: str = "Ticket has expired"):
        super().__init__(message)
        self.code = "TICKET_EXPIRED"


class TicketAlreadyUsedError(TicketValidationError):
    """Raised when a ticket has already been used."""

    def __init__(self, message: str = "Ticket has already been used"):
        super().__init__(message)
        self.code = "TICKET_ALREADY_USED"


class TicketRevokedError(TicketValidationError):
    """Raised when a ticket has been revoked."""

    def __init__(self, message: str = "Ticket has been revoked"):
        super().__init__(message)
        self.code = "TICKET_REVOKED"


class QRCodeGenerationError(QRTicketError):
    """Raised when QR code image generation fails."""

    def __init__(self, message: str = "Failed to generate QR code"):
        super().__init__(message, code="QR_CODE_GENERATION_ERROR")


class StorageError(QRTicketError):
    """Raised when storage operations fail (S3 or local)."""

    def __init__(self, message: str = "Storage operation failed"):
        super().__init__(message, code="STORAGE_ERROR")
