"""QR Ticket Manager - A library for generating and validating QR-coded event tickets."""

from .ticket_generator import TicketGenerator
from .qr_code_creator import QRCodeCreator
from .ticket_validator import TicketValidator
from .logger import TicketLogger
from .exceptions import (
    QRTicketError,
    TicketGenerationError,
    TicketValidationError,
    InvalidSignatureError,
    TicketAlreadyUsedError,
    TicketRevokedError,
    TicketExpiredError,
    QRCodeGenerationError,
    StorageError,
)

__version__ = "1.0.0"
__all__ = [
    "TicketGenerator",
    "QRCodeCreator",
    "TicketValidator",
    "TicketLogger",
    "QRTicketError",
    "TicketGenerationError",
    "TicketValidationError",
    "InvalidSignatureError",
    "TicketAlreadyUsedError",
    "TicketRevokedError",
    "TicketExpiredError",
    "QRCodeGenerationError",
    "StorageError",
]
