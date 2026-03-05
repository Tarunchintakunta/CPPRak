"""DynamoDB service for all table operations.

Provides CRUD methods for Users, Events, Registrations, and Tickets tables.
Uses the config object passed at init time (no Flask current_app dependency).
"""

import logging
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

from app.models.schemas import TABLES

logger = logging.getLogger(__name__)


class DynamoService:
    """Manages all DynamoDB interactions for the application."""

    def __init__(self, app_config):
        """Initialise the DynamoDB resource from the application config.

        Args:
            app_config: A config object with attributes DYNAMODB_ENDPOINT,
                        AWS_REGION, and optionally AWS_ACCESS_KEY_ID /
                        AWS_SECRET_ACCESS_KEY (for local development).
        """
        self.config = app_config

        kwargs = {"region_name": getattr(app_config, "AWS_REGION", "us-east-1")}

        # Local DynamoDB endpoint (DynamoDB Local / LocalStack)
        endpoint = getattr(app_config, "DYNAMODB_ENDPOINT", None)
        if endpoint:
            kwargs["endpoint_url"] = endpoint

        # Explicit credentials for local development
        access_key = getattr(app_config, "AWS_ACCESS_KEY_ID", None)
        secret_key = getattr(app_config, "AWS_SECRET_ACCESS_KEY", None)
        if access_key and secret_key:
            kwargs["aws_access_key_id"] = access_key
            kwargs["aws_secret_access_key"] = secret_key

        self.resource = boto3.resource("dynamodb", **kwargs)

    # ------------------------------------------------------------------
    # Table management
    # ------------------------------------------------------------------

    def create_tables(self):
        """Create all application tables if they do not already exist.

        Reads table definitions from ``app.models.schemas.TABLES`` and
        silently skips any table that has already been created.
        """
        existing = self._list_existing_tables()
        for table_name, schema in TABLES.items():
            if table_name in existing:
                logger.info("Table %s already exists, skipping.", table_name)
                continue
            try:
                self.resource.create_table(**schema)
                logger.info("Created table %s.", table_name)
            except ClientError as exc:
                # Race condition guard: table may have been created concurrently
                if exc.response["Error"]["Code"] == "ResourceInUseException":
                    logger.info("Table %s already exists (race).", table_name)
                else:
                    logger.error("Failed to create table %s: %s", table_name, exc)
                    raise

    def _list_existing_tables(self):
        """Return a set of table names that already exist."""
        try:
            client = self.resource.meta.client
            paginator = client.get_paginator("list_tables")
            names = set()
            for page in paginator.paginate():
                names.update(page.get("TableNames", []))
            return names
        except ClientError as exc:
            logger.error("Failed to list tables: %s", exc)
            return set()

    # ------------------------------------------------------------------
    # User operations
    # ------------------------------------------------------------------

    def create_user(self, user_data):
        """Put a new user item into the Users table.

        Args:
            user_data: Dict with at least ``user_id`` and ``email``.

        Returns:
            The user_data dict on success.

        Raises:
            ClientError: On DynamoDB failure.
        """
        try:
            table = self.resource.Table("Users")
            user_data.setdefault("created_at", datetime.now(timezone.utc).isoformat())
            table.put_item(Item=user_data)
            logger.info("Created user %s.", user_data.get("user_id"))
            return user_data
        except ClientError as exc:
            logger.error("Failed to create user: %s", exc)
            raise

    def get_user(self, user_id):
        """Fetch a single user by primary key.

        Returns:
            The user dict, or ``None`` if not found.
        """
        try:
            table = self.resource.Table("Users")
            response = table.get_item(Key={"user_id": user_id})
            return response.get("Item")
        except ClientError as exc:
            logger.error("Failed to get user %s: %s", user_id, exc)
            raise

    def get_user_by_email(self, email):
        """Look up a user via the ``email-index`` GSI.

        Returns:
            The first matching user dict, or ``None``.
        """
        try:
            table = self.resource.Table("Users")
            from boto3.dynamodb.conditions import Key as DKey
            response = table.query(
                IndexName="email-index",
                KeyConditionExpression=DKey("email").eq(email),
            )
            items = response.get("Items", [])
            return items[0] if items else None
        except ClientError as exc:
            logger.error("Failed to query user by email %s: %s", email, exc)
            raise

    # ------------------------------------------------------------------
    # Event operations
    # ------------------------------------------------------------------

    def create_event(self, event_data):
        """Put a new event item into the Events table.

        Args:
            event_data: Dict with at least ``event_id``.

        Returns:
            The event_data dict on success.
        """
        try:
            table = self.resource.Table("Events")
            event_data.setdefault("created_at", datetime.now(timezone.utc).isoformat())
            event_data.setdefault("status", "active")
            table.put_item(Item=event_data)
            logger.info("Created event %s.", event_data.get("event_id"))
            return event_data
        except ClientError as exc:
            logger.error("Failed to create event: %s", exc)
            raise

    def get_event(self, event_id):
        """Fetch a single event by primary key.

        Returns:
            The event dict, or ``None`` if not found.
        """
        try:
            table = self.resource.Table("Events")
            response = table.get_item(Key={"event_id": event_id})
            return response.get("Item")
        except ClientError as exc:
            logger.error("Failed to get event %s: %s", event_id, exc)
            raise

    def list_events(self, status="active"):
        """Query events by status via the ``status-date-index`` GSI.

        Args:
            status: The status partition key value (default ``"active"``).

        Returns:
            A list of event dicts sorted by date (ascending).
        """
        try:
            table = self.resource.Table("Events")
            from boto3.dynamodb.conditions import Key as DKey
            response = table.query(
                IndexName="status-date-index",
                KeyConditionExpression=DKey("status").eq(status),
            )
            return response.get("Items", [])
        except ClientError as exc:
            logger.error("Failed to list events with status %s: %s", status, exc)
            raise

    def update_event(self, event_id, updates):
        """Update specific attributes of an event.

        Args:
            event_id: The event primary key.
            updates: Dict of attribute_name -> new_value.

        Returns:
            The full updated item (Attributes from RETURN_VALUES).
        """
        try:
            table = self.resource.Table("Events")

            # Automatically track when the item was last updated
            updates["updated_at"] = datetime.now(timezone.utc).isoformat()

            expression_parts = []
            attr_names = {}
            attr_values = {}
            for idx, (key, value) in enumerate(updates.items()):
                placeholder_name = f"#attr{idx}"
                placeholder_value = f":val{idx}"
                expression_parts.append(f"{placeholder_name} = {placeholder_value}")
                attr_names[placeholder_name] = key
                attr_values[placeholder_value] = value

            update_expr = "SET " + ", ".join(expression_parts)

            response = table.update_item(
                Key={"event_id": event_id},
                UpdateExpression=update_expr,
                ExpressionAttributeNames=attr_names,
                ExpressionAttributeValues=attr_values,
                ReturnValues="ALL_NEW",
            )
            logger.info("Updated event %s.", event_id)
            return response.get("Attributes")
        except ClientError as exc:
            logger.error("Failed to update event %s: %s", event_id, exc)
            raise

    def delete_event(self, event_id):
        """Delete an event by primary key.

        Returns:
            True on success.
        """
        try:
            table = self.resource.Table("Events")
            table.delete_item(Key={"event_id": event_id})
            logger.info("Deleted event %s.", event_id)
            return True
        except ClientError as exc:
            logger.error("Failed to delete event %s: %s", event_id, exc)
            raise

    # ------------------------------------------------------------------
    # Registration operations
    # ------------------------------------------------------------------

    def create_registration(self, reg_data):
        """Put a new registration item into the Registrations table.

        Args:
            reg_data: Dict with at least ``registration_id``, ``user_id``,
                      and ``event_id``.

        Returns:
            The reg_data dict on success.
        """
        try:
            table = self.resource.Table("Registrations")
            reg_data.setdefault("created_at", datetime.now(timezone.utc).isoformat())
            reg_data.setdefault("status", "confirmed")
            reg_data.setdefault("checked_in", False)
            table.put_item(Item=reg_data)
            logger.info("Created registration %s.", reg_data.get("registration_id"))
            return reg_data
        except ClientError as exc:
            logger.error("Failed to create registration: %s", exc)
            raise

    def get_registration(self, reg_id):
        """Fetch a single registration by primary key.

        Returns:
            The registration dict, or ``None`` if not found.
        """
        try:
            table = self.resource.Table("Registrations")
            response = table.get_item(Key={"registration_id": reg_id})
            return response.get("Item")
        except ClientError as exc:
            logger.error("Failed to get registration %s: %s", reg_id, exc)
            raise

    def get_user_registrations(self, user_id):
        """Query all registrations for a user via ``user-event-index`` GSI.

        Returns:
            A list of registration dicts.
        """
        try:
            table = self.resource.Table("Registrations")
            from boto3.dynamodb.conditions import Key as DKey
            response = table.query(
                IndexName="user-event-index",
                KeyConditionExpression=DKey("user_id").eq(user_id),
            )
            return response.get("Items", [])
        except ClientError as exc:
            logger.error(
                "Failed to get registrations for user %s: %s", user_id, exc
            )
            raise

    def check_duplicate_registration(self, user_id, event_id):
        """Check whether a user is already registered for an event.

        Uses the ``user-event-index`` GSI with both hash and range keys.

        Returns:
            True if a registration already exists, False otherwise.
        """
        try:
            table = self.resource.Table("Registrations")
            from boto3.dynamodb.conditions import Key as DKey
            response = table.query(
                IndexName="user-event-index",
                KeyConditionExpression=(
                    DKey("user_id").eq(user_id) & DKey("event_id").eq(event_id)
                ),
            )
            return len(response.get("Items", [])) > 0
        except ClientError as exc:
            logger.error(
                "Failed to check duplicate registration (user=%s, event=%s): %s",
                user_id,
                event_id,
                exc,
            )
            raise

    def get_event_registrations(self, event_id):
        """Query all registrations for an event via ``event-index`` GSI.

        Returns:
            A list of registration dicts.
        """
        try:
            table = self.resource.Table("Registrations")
            from boto3.dynamodb.conditions import Key as DKey
            response = table.query(
                IndexName="event-index",
                KeyConditionExpression=DKey("event_id").eq(event_id),
            )
            return response.get("Items", [])
        except ClientError as exc:
            logger.error(
                "Failed to get registrations for event %s: %s", event_id, exc
            )
            raise

    def update_registration(self, registration_id, updates):
        """Update specific attributes of a registration.

        Args:
            registration_id: The registration primary key.
            updates: Dict of attribute_name -> new_value.

        Returns:
            The full updated item attributes.
        """
        try:
            table = self.resource.Table("Registrations")

            updates["updated_at"] = datetime.now(timezone.utc).isoformat()

            expression_parts = []
            attr_names = {}
            attr_values = {}
            for idx, (key, value) in enumerate(updates.items()):
                placeholder_name = f"#attr{idx}"
                placeholder_value = f":val{idx}"
                expression_parts.append(f"{placeholder_name} = {placeholder_value}")
                attr_names[placeholder_name] = key
                attr_values[placeholder_value] = value

            update_expr = "SET " + ", ".join(expression_parts)

            response = table.update_item(
                Key={"registration_id": registration_id},
                UpdateExpression=update_expr,
                ExpressionAttributeNames=attr_names,
                ExpressionAttributeValues=attr_values,
                ReturnValues="ALL_NEW",
            )
            logger.info("Updated registration %s.", registration_id)
            return response.get("Attributes")
        except ClientError as exc:
            logger.error("Failed to update registration %s: %s", registration_id, exc)
            raise

    # ------------------------------------------------------------------
    # Table scanning (admin)
    # ------------------------------------------------------------------

    def scan_table(self, table_name):
        """Scan an entire DynamoDB table and return all items.

        Handles pagination automatically.  Use sparingly -- scans are
        expensive on large tables.

        Args:
            table_name: Name of the table to scan.

        Returns:
            A list of all item dicts in the table.
        """
        try:
            table = self.resource.Table(table_name)
            items = []
            response = table.scan()
            items.extend(response.get("Items", []))
            while response.get("LastEvaluatedKey"):
                response = table.scan(
                    ExclusiveStartKey=response["LastEvaluatedKey"],
                )
                items.extend(response.get("Items", []))
            return items
        except ClientError as exc:
            logger.error("Failed to scan table %s: %s", table_name, exc)
            raise

    # ------------------------------------------------------------------
    # Ticket operations
    # ------------------------------------------------------------------

    def create_ticket(self, ticket_data):
        """Put a new ticket item into the Tickets table.

        Args:
            ticket_data: Dict with at least ``ticket_id`` and
                         ``registration_id``.

        Returns:
            The ticket_data dict on success.
        """
        try:
            table = self.resource.Table("Tickets")
            ticket_data.setdefault("created_at", datetime.now(timezone.utc).isoformat())
            ticket_data.setdefault("status", "valid")
            table.put_item(Item=ticket_data)
            logger.info("Created ticket %s.", ticket_data.get("ticket_id"))
            return ticket_data
        except ClientError as exc:
            logger.error("Failed to create ticket: %s", exc)
            raise

    def get_ticket(self, ticket_id):
        """Fetch a single ticket by primary key.

        Returns:
            The ticket dict, or ``None`` if not found.
        """
        try:
            table = self.resource.Table("Tickets")
            response = table.get_item(Key={"ticket_id": ticket_id})
            return response.get("Item")
        except ClientError as exc:
            logger.error("Failed to get ticket %s: %s", ticket_id, exc)
            raise

    def update_ticket_status(self, ticket_id, status):
        """Update the status field of a ticket.

        Args:
            ticket_id: The ticket primary key.
            status: New status string (e.g. ``"valid"``, ``"used"``,
                    ``"revoked"``).

        Returns:
            The full updated item attributes.
        """
        try:
            table = self.resource.Table("Tickets")
            response = table.update_item(
                Key={"ticket_id": ticket_id},
                UpdateExpression="SET #s = :status, updated_at = :ts",
                ExpressionAttributeNames={"#s": "status"},
                ExpressionAttributeValues={
                    ":status": status,
                    ":ts": datetime.now(timezone.utc).isoformat(),
                },
                ReturnValues="ALL_NEW",
            )
            logger.info("Updated ticket %s status to %s.", ticket_id, status)
            return response.get("Attributes")
        except ClientError as exc:
            logger.error(
                "Failed to update ticket %s status: %s", ticket_id, exc
            )
            raise

    def get_ticket_by_registration(self, registration_id):
        """Look up a ticket via the ``registration-index`` GSI.

        Returns:
            The first matching ticket dict, or ``None``.
        """
        try:
            table = self.resource.Table("Tickets")
            from boto3.dynamodb.conditions import Key as DKey
            response = table.query(
                IndexName="registration-index",
                KeyConditionExpression=DKey("registration_id").eq(registration_id),
            )
            items = response.get("Items", [])
            return items[0] if items else None
        except ClientError as exc:
            logger.error(
                "Failed to get ticket for registration %s: %s",
                registration_id,
                exc,
            )
            raise
