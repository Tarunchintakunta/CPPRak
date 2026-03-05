# QR Ticket Manager

A Python library for generating and validating QR-coded event tickets with HMAC-SHA256 cryptographic signing.

## Features

- **Ticket Generation**: HMAC-SHA256 signed ticket IDs with tamper-proof payloads
- **QR Code Creation**: High error-correction QR code images (PNG, base64)
- **Ticket Validation**: Two-layer validation — cryptographic signature check + status verification
- **Structured Logging**: CloudWatch-compatible JSON logging
- **Custom Exceptions**: Detailed error hierarchy for precise error handling

## Installation

```bash
pip install qr_ticket_manager
```

## Quick Start

```python
from qr_ticket_manager import TicketGenerator, QRCodeCreator, TicketValidator

# Generate a ticket
generator = TicketGenerator(secret_key="your-secret-key")
ticket = generator.generate_ticket(
    event_id="evt-001",
    registration_id="reg-001",
    user_id="usr-001",
    event_name="Tech Conference 2026"
)

# Create QR code
qr_creator = QRCodeCreator()
qr_payload = generator.create_qr_payload(ticket)
qr_bytes = qr_creator.generate_qr_image(qr_payload)

# Validate ticket
validator = TicketValidator(secret_key="your-secret-key")
result = validator.validate_ticket(qr_payload)
print(result)  # {'valid': True, 'ticket_id': '...', ...}
```

## Classes

### TicketGenerator
Generates HMAC-SHA256 signed tickets with unique IDs.

### QRCodeCreator
Creates QR code images in PNG bytes, base64, or saves to file.

### TicketValidator
Two-layer validation: signature verification + status checking.

### TicketLogger
CloudWatch-compatible structured JSON logger.

## License

MIT
