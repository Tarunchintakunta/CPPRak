"""AWS Lambda handler for QR ticket validation.

Validates a scanned QR code by verifying its HMAC signature and checking
the ticket status in DynamoDB. On success, marks the ticket as used.
"""

import json
import os
import traceback
from datetime import datetime, timezone

import boto3

from qr_ticket_manager import (
    TicketValidator,
    InvalidSignatureError,
    TicketAlreadyUsedError,
    TicketRevokedError,
    TicketExpiredError,
    TicketValidationError,
    QRTicketError,
)


def _get_config(event):
    """Extract configuration from the event or environment variables."""
    config = event.get("config", {})
    return {
        "secret_key": config.get("secret_key", os.environ.get("TICKET_SECRET_KEY", "")),
        "dynamodb_endpoint": config.get("dynamodb_endpoint", os.environ.get("DYNAMODB_ENDPOINT", "")),
    }


def _get_dynamodb_table(config, table_name="Tickets"):
    """Return a DynamoDB Table resource, pointing to local or AWS endpoint."""
    kwargs = {"region_name": os.environ.get("AWS_REGION", "us-east-1")}
    if config["dynamodb_endpoint"]:
        kwargs["endpoint_url"] = config["dynamodb_endpoint"]
    dynamodb = boto3.resource("dynamodb", **kwargs)
    return dynamodb.Table(table_name)


def _get_dynamodb_resource(config):
    """Return a DynamoDB resource for table-level operations."""
    kwargs = {"region_name": os.environ.get("AWS_REGION", "us-east-1")}
    if config["dynamodb_endpoint"]:
        kwargs["endpoint_url"] = config["dynamodb_endpoint"]
    return boto3.resource("dynamodb", **kwargs)


def _make_ticket_status_callback(config):
    """Create a callback that queries DynamoDB for the ticket's current status.

    The callback conforms to the signature expected by TicketValidator.validate_ticket:
        get_ticket_status(ticket_id) -> str

    Returns:
        A callable that takes ticket_id and returns the status string.
    """
    def get_ticket_status(ticket_id):
        table = _get_dynamodb_table(config)
        response = table.get_item(Key={"ticket_id": ticket_id})
        item = response.get("Item")
        if not item:
            raise TicketValidationError(f"Ticket {ticket_id} not found in database")
        return item.get("status", "valid")

    return get_ticket_status


def _mark_ticket_used(config, ticket_id):
    """Update the ticket status to 'used' in the Tickets DynamoDB table."""
    table = _get_dynamodb_table(config)
    table.update_item(
        Key={"ticket_id": ticket_id},
        UpdateExpression="SET #s = :status, used_at = :used_at",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={
            ":status": "used",
            ":used_at": datetime.now(timezone.utc).isoformat(),
        },
    )


def _mark_registration_checked_in(config, registration_id):
    """Update checked_in flag on the Registrations table.

    This is a best-effort operation; if the Registrations table does not
    exist or the item is missing the handler will not fail.
    """
    try:
        dynamodb = _get_dynamodb_resource(config)
        table = dynamodb.Table("Registrations")
        table.update_item(
            Key={"registration_id": registration_id},
            UpdateExpression="SET checked_in = :val, checked_in_at = :ts",
            ExpressionAttributeValues={
                ":val": True,
                ":ts": datetime.now(timezone.utc).isoformat(),
            },
        )
    except Exception:
        # Best-effort: Registrations table may not exist in all environments
        pass


def handler(event, context):
    """Lambda handler for QR ticket validation.

    Args:
        event: Dict containing:
            - qr_data (str): JSON string from scanning the QR code.
            - config (dict, optional): Override configuration with keys
              secret_key, dynamodb_endpoint.
        context: AWS Lambda context object (unused).

    Returns:
        Dict with statusCode and JSON body containing validation result:
        valid (bool), ticket_id, message, and error details if applicable.
    """
    try:
        config = _get_config(event)

        if not config["secret_key"]:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "Missing secret_key. Provide via event config or TICKET_SECRET_KEY env var.",
                }),
            }

        qr_data = event.get("qr_data", "")
        if not qr_data:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "Missing required field: qr_data",
                }),
            }

        # Build validator and status callback
        validator = TicketValidator(config["secret_key"])
        status_callback = _make_ticket_status_callback(config)

        # Validate the ticket (signature + status)
        result = validator.validate_ticket(qr_data, get_ticket_status=status_callback)

        # Validation passed -- mark ticket as used
        ticket_id = result["ticket_id"]
        _mark_ticket_used(config, ticket_id)

        # Also mark registration as checked-in
        try:
            qr_parsed = json.loads(qr_data)
            registration_id = qr_parsed.get("payload", {}).get("registration_id", "")
            if registration_id:
                _mark_registration_checked_in(config, registration_id)
        except (json.JSONDecodeError, KeyError):
            pass

        return {
            "statusCode": 200,
            "body": json.dumps({
                "valid": True,
                "ticket_id": ticket_id,
                "event_id": result.get("event_id", ""),
                "user_id": result.get("user_id", ""),
                "message": "Ticket is valid for entry",
            }),
        }

    except InvalidSignatureError as e:
        return {
            "statusCode": 403,
            "body": json.dumps({
                "valid": False,
                "ticket_id": _safe_extract_ticket_id(event),
                "message": e.message,
                "code": e.code,
            }),
        }

    except TicketAlreadyUsedError as e:
        return {
            "statusCode": 409,
            "body": json.dumps({
                "valid": False,
                "ticket_id": _safe_extract_ticket_id(event),
                "message": e.message,
                "code": e.code,
            }),
        }

    except TicketRevokedError as e:
        return {
            "statusCode": 403,
            "body": json.dumps({
                "valid": False,
                "ticket_id": _safe_extract_ticket_id(event),
                "message": e.message,
                "code": e.code,
            }),
        }

    except TicketExpiredError as e:
        return {
            "statusCode": 410,
            "body": json.dumps({
                "valid": False,
                "ticket_id": _safe_extract_ticket_id(event),
                "message": e.message,
                "code": e.code,
            }),
        }

    except TicketValidationError as e:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "valid": False,
                "ticket_id": _safe_extract_ticket_id(event),
                "message": e.message,
                "code": e.code,
            }),
        }

    except QRTicketError as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "valid": False,
                "ticket_id": _safe_extract_ticket_id(event),
                "message": e.message,
                "code": e.code,
            }),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "valid": False,
                "ticket_id": _safe_extract_ticket_id(event),
                "message": f"Internal error: {str(e)}",
                "code": "INTERNAL_ERROR",
                "trace": traceback.format_exc(),
            }),
        }


def _safe_extract_ticket_id(event):
    """Best-effort extraction of ticket_id from the event's qr_data."""
    try:
        qr_data = event.get("qr_data", "")
        parsed = json.loads(qr_data)
        return parsed.get("ticket_id", "unknown")
    except Exception:
        return "unknown"
