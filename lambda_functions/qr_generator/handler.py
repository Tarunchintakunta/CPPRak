"""AWS Lambda handler for QR ticket generation.

Generates a signed ticket, creates a QR code image, and stores both
the image (S3 or local filesystem) and the ticket record (DynamoDB).
"""

import json
import os
import traceback
from datetime import datetime, timezone

import boto3
from botocore.config import Config

from qr_ticket_manager import (
    TicketGenerator,
    QRCodeCreator,
    TicketGenerationError,
    QRCodeGenerationError,
    StorageError,
)


def _get_config(event):
    """Extract configuration from the event or environment variables.

    Priority: event['config'] values > environment variables > defaults.
    """
    config = event.get("config", {})
    return {
        "secret_key": config.get("secret_key", os.environ.get("TICKET_SECRET_KEY", "")),
        "s3_bucket": config.get("s3_bucket", os.environ.get("S3_BUCKET", "qr-tickets")),
        "dynamodb_endpoint": config.get("dynamodb_endpoint", os.environ.get("DYNAMODB_ENDPOINT", "")),
        "s3_endpoint": config.get("s3_endpoint", os.environ.get("S3_ENDPOINT", "")),
        "local_storage_path": config.get("local_storage_path", os.environ.get("LOCAL_STORAGE_PATH", "/tmp/qr_codes")),
    }


def _get_dynamodb_table(config, table_name="Tickets"):
    """Return a DynamoDB Table resource, pointing to local or AWS endpoint."""
    kwargs = {"region_name": os.environ.get("AWS_REGION", "us-east-1")}
    if config["dynamodb_endpoint"]:
        kwargs["endpoint_url"] = config["dynamodb_endpoint"]
    dynamodb = boto3.resource("dynamodb", **kwargs)
    return dynamodb.Table(table_name)


def _get_s3_client(config):
    """Return an S3 client, pointing to local or AWS endpoint."""
    kwargs = {"region_name": os.environ.get("AWS_REGION", "us-east-1")}
    if config.get("s3_endpoint"):
        kwargs["endpoint_url"] = config["s3_endpoint"]
    return boto3.client("s3", **kwargs)


def _store_qr_image(config, ticket_id, image_bytes):
    """Store the QR image to S3 or local filesystem.

    When a dynamodb_endpoint is set (local development), the image is saved
    to the local filesystem instead of S3.

    Returns:
        The URL or file path where the QR image was stored.
    """
    if config["dynamodb_endpoint"]:
        # Local mode: save to filesystem
        storage_dir = config["local_storage_path"]
        os.makedirs(storage_dir, exist_ok=True)
        file_path = os.path.join(storage_dir, f"{ticket_id}.png")
        with open(file_path, "wb") as f:
            f.write(image_bytes)
        return file_path
    else:
        # AWS mode: upload to S3
        s3_client = _get_s3_client(config)
        s3_key = f"qr_codes/{ticket_id}.png"
        s3_client.put_object(
            Bucket=config["s3_bucket"],
            Key=s3_key,
            Body=image_bytes,
            ContentType="image/png",
        )
        return f"s3://{config['s3_bucket']}/{s3_key}"


def _store_ticket_record(config, ticket):
    """Write the ticket record to DynamoDB."""
    table = _get_dynamodb_table(config)
    item = {
        "ticket_id": ticket["ticket_id"],
        "event_id": ticket["payload"]["event_id"],
        "registration_id": ticket["payload"]["registration_id"],
        "user_id": ticket["payload"]["user_id"],
        "event_name": ticket["payload"]["event_name"],
        "status": ticket["status"],
        "signature": ticket["signature"],
        "created_at": ticket["created_at"],
    }
    table.put_item(Item=item)
    return item


def handler(event, context):
    """Lambda handler for QR ticket generation.

    Args:
        event: Dict containing:
            - event_id (str): The event identifier.
            - registration_id (str): The registration identifier.
            - user_id (str): The user identifier.
            - event_name (str): Human-readable event name.
            - config (dict, optional): Override configuration with keys
              secret_key, s3_bucket, dynamodb_endpoint, s3_endpoint,
              local_storage_path.
        context: AWS Lambda context object (unused).

    Returns:
        Dict with statusCode and JSON body containing ticket_id,
        qr_url, status, and full ticket data.
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

        # Extract required fields
        event_id = event.get("event_id", "")
        registration_id = event.get("registration_id", "")
        user_id = event.get("user_id", "")
        event_name = event.get("event_name", "")

        if not all([event_id, registration_id, user_id, event_name]):
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "Missing required fields: event_id, registration_id, user_id, event_name",
                }),
            }

        # Step 1: Generate signed ticket
        generator = TicketGenerator(config["secret_key"])
        ticket = generator.generate_ticket(event_id, registration_id, user_id, event_name)

        # Step 2: Create QR payload and image
        qr_payload = generator.create_qr_payload(ticket)
        qr_creator = QRCodeCreator()
        image_bytes = qr_creator.generate_qr_image(qr_payload)

        # Step 3: Store QR image (S3 or local)
        qr_url = _store_qr_image(config, ticket["ticket_id"], image_bytes)

        # Step 4: Store ticket record in DynamoDB
        _store_ticket_record(config, ticket)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "ticket_id": ticket["ticket_id"],
                "qr_url": qr_url,
                "status": ticket["status"],
                "event_id": event_id,
                "registration_id": registration_id,
                "user_id": user_id,
                "event_name": event_name,
                "created_at": ticket["created_at"],
                "qr_payload": qr_payload,
            }),
        }

    except TicketGenerationError as e:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": e.message,
                "code": e.code,
            }),
        }
    except QRCodeGenerationError as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": e.message,
                "code": e.code,
            }),
        }
    except StorageError as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": e.message,
                "code": e.code,
            }),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": f"Internal error: {str(e)}",
                "code": "INTERNAL_ERROR",
                "trace": traceback.format_exc(),
            }),
        }
