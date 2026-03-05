"""Local testing harness for QR ticket Lambda functions.

Simulates Lambda invocations without requiring a deployed AWS environment.
Uses a local DynamoDB endpoint (http://localhost:8000) and local file storage.

Usage:
    python -m lambda_functions.local_runner
    # or
    python lambda_functions/local_runner.py
"""

import json
import os
import sys

import boto3
from botocore.exceptions import ClientError

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

LOCAL_DYNAMODB_ENDPOINT = "http://localhost:8000"
LOCAL_STORAGE_PATH = os.path.join(os.path.dirname(__file__), "test_output", "qr_codes")
SECRET_KEY = "local-test-secret-key-for-development"
AWS_REGION = "us-east-1"

COMMON_CONFIG = {
    "secret_key": SECRET_KEY,
    "dynamodb_endpoint": LOCAL_DYNAMODB_ENDPOINT,
    "local_storage_path": LOCAL_STORAGE_PATH,
}


# ---------------------------------------------------------------------------
# DynamoDB table setup helpers
# ---------------------------------------------------------------------------

def _get_dynamodb_resource():
    """Return a boto3 DynamoDB resource pointing to the local endpoint."""
    return boto3.resource(
        "dynamodb",
        endpoint_url=LOCAL_DYNAMODB_ENDPOINT,
        region_name=AWS_REGION,
    )


def ensure_tickets_table():
    """Create the Tickets table in local DynamoDB if it does not exist."""
    dynamodb = _get_dynamodb_resource()
    existing = [t.name for t in dynamodb.tables.all()]
    if "Tickets" not in existing:
        print("[setup] Creating Tickets table in local DynamoDB...")
        dynamodb.create_table(
            TableName="Tickets",
            KeySchema=[
                {"AttributeName": "ticket_id", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "ticket_id", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        print("[setup] Tickets table created.")
    else:
        print("[setup] Tickets table already exists.")


def ensure_registrations_table():
    """Create the Registrations table in local DynamoDB if it does not exist."""
    dynamodb = _get_dynamodb_resource()
    existing = [t.name for t in dynamodb.tables.all()]
    if "Registrations" not in existing:
        print("[setup] Creating Registrations table in local DynamoDB...")
        dynamodb.create_table(
            TableName="Registrations",
            KeySchema=[
                {"AttributeName": "registration_id", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "registration_id", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        print("[setup] Registrations table created.")
    else:
        print("[setup] Registrations table already exists.")


def seed_registration(registration_id):
    """Insert a stub registration record so the validator can update it."""
    dynamodb = _get_dynamodb_resource()
    table = dynamodb.Table("Registrations")
    table.put_item(Item={
        "registration_id": registration_id,
        "checked_in": False,
    })
    print(f"[setup] Seeded registration: {registration_id}")


# ---------------------------------------------------------------------------
# Test functions
# ---------------------------------------------------------------------------

def test_generate_ticket():
    """Generate a QR ticket via the generator Lambda handler.

    Returns:
        The parsed response body dict (includes ticket_id, qr_payload, etc.)
        or None on failure.
    """
    from lambda_functions.qr_generator.handler import handler as generate_handler

    print("\n" + "=" * 60)
    print("TEST: Generate QR Ticket")
    print("=" * 60)

    event = {
        "event_id": "EVT-001",
        "registration_id": "REG-1001",
        "user_id": "USR-501",
        "event_name": "Tech Conference 2026",
        "config": COMMON_CONFIG,
    }

    # Seed the registration so validation can mark it as checked-in later
    seed_registration(event["registration_id"])

    response = generate_handler(event, None)
    status = response.get("statusCode")
    body = json.loads(response.get("body", "{}"))

    print(f"\nStatus Code : {status}")
    print(f"Ticket ID   : {body.get('ticket_id', 'N/A')}")
    print(f"QR URL      : {body.get('qr_url', 'N/A')}")
    print(f"Status      : {body.get('status', 'N/A')}")
    print(f"Event       : {body.get('event_name', 'N/A')}")
    print(f"Created At  : {body.get('created_at', 'N/A')}")

    if status == 200:
        print("\n[PASS] Ticket generated successfully.")
        return body
    else:
        print(f"\n[FAIL] Error: {body.get('error', 'unknown')}")
        return None


def test_validate_ticket(qr_payload=None):
    """Validate a QR ticket via the validator Lambda handler.

    Args:
        qr_payload: The JSON string from generate's response.  If None,
                     an invalid payload is used to test error handling.

    Returns:
        The parsed response body dict.
    """
    from lambda_functions.qr_validator.handler import handler as validate_handler

    print("\n" + "=" * 60)
    print("TEST: Validate QR Ticket")
    print("=" * 60)

    if qr_payload is None:
        # Use a deliberately invalid payload
        qr_payload = json.dumps({
            "ticket_id": "fake-id",
            "payload": {"ticket_id": "fake-id", "event_id": "x"},
            "signature": "invalid",
        })
        print("[info] Using intentionally invalid QR payload for error test.")

    event = {
        "qr_data": qr_payload,
        "config": COMMON_CONFIG,
    }

    response = validate_handler(event, None)
    status = response.get("statusCode")
    body = json.loads(response.get("body", "{}"))

    print(f"\nStatus Code : {status}")
    print(f"Valid       : {body.get('valid', 'N/A')}")
    print(f"Ticket ID   : {body.get('ticket_id', 'N/A')}")
    print(f"Message     : {body.get('message', 'N/A')}")

    if body.get("valid"):
        print("\n[PASS] Ticket validated successfully.")
    else:
        code = body.get("code", "")
        print(f"Error Code  : {code}")
        print(f"\n[{'PASS' if 'invalid' in (qr_payload or '') else 'FAIL'}] Validation returned invalid.")

    return body


def test_double_validation(qr_payload):
    """Attempt to validate the same ticket twice to confirm it gets rejected.

    Args:
        qr_payload: The QR payload string from a previously generated ticket.
    """
    from lambda_functions.qr_validator.handler import handler as validate_handler

    print("\n" + "=" * 60)
    print("TEST: Double Validation (should be rejected)")
    print("=" * 60)

    event = {
        "qr_data": qr_payload,
        "config": COMMON_CONFIG,
    }

    response = validate_handler(event, None)
    status = response.get("statusCode")
    body = json.loads(response.get("body", "{}"))

    print(f"\nStatus Code : {status}")
    print(f"Valid       : {body.get('valid', 'N/A')}")
    print(f"Message     : {body.get('message', 'N/A')}")
    print(f"Code        : {body.get('code', 'N/A')}")

    if not body.get("valid") and body.get("code") == "TICKET_ALREADY_USED":
        print("\n[PASS] Double-use correctly rejected.")
    else:
        print("\n[FAIL] Double-use was NOT rejected as expected.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    """Run the full local test suite."""
    print("QR Ticket System -- Local Lambda Test Runner")
    print("Local DynamoDB endpoint:", LOCAL_DYNAMODB_ENDPOINT)
    print("Local storage path:     ", LOCAL_STORAGE_PATH)

    # Set up tables
    try:
        ensure_tickets_table()
        ensure_registrations_table()
    except Exception as e:
        print(f"\n[ERROR] Could not connect to local DynamoDB at {LOCAL_DYNAMODB_ENDPOINT}")
        print(f"        Make sure DynamoDB Local is running. Error: {e}")
        sys.exit(1)

    # Test 1: Generate a ticket
    gen_result = test_generate_ticket()
    if gen_result is None:
        print("\nAborting remaining tests -- generation failed.")
        sys.exit(1)

    qr_payload = gen_result.get("qr_payload")

    # Test 2: Validate the generated ticket (first scan -- should pass)
    test_validate_ticket(qr_payload)

    # Test 3: Validate the same ticket again (should be rejected as already used)
    test_double_validation(qr_payload)

    # Test 4: Validate an invalid/tampered ticket
    test_validate_ticket(None)

    print("\n" + "=" * 60)
    print("All tests completed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
