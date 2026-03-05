"""Lambda invocation service with local fallback.

Supports two modes controlled by the config object:
  - **Production**: invokes AWS Lambda functions via the boto3 client.
  - **Development**: imports and directly calls the handler functions
    from the ``lambda_functions`` package, avoiding any network round-trip.
"""

import json
import logging

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class LambdaService:
    """Manages invocation of QR generator and validator Lambda functions."""

    def __init__(self, app_config):
        """Initialise the service from the application config.

        Args:
            app_config: A config object with:
                - USE_LOCAL_LAMBDA (bool)
                - AWS_REGION (str)
                - LAMBDA_QR_GENERATOR (str)  -- function name for prod
                - LAMBDA_QR_VALIDATOR (str)   -- function name for prod
                - TICKET_SECRET_KEY (str)     -- passed to local handlers
                - DYNAMODB_ENDPOINT (str)     -- passed to local handlers
                - LOCAL_STORAGE_PATH (str)    -- passed to local handlers
                - S3_BUCKET (str)             -- passed to local handlers
        """
        self.config = app_config
        self.use_local = getattr(app_config, "USE_LOCAL_LAMBDA", False)

        if self.use_local:
            self.client = None
        else:
            kwargs = {"region_name": getattr(app_config, "AWS_REGION", "us-east-1")}
            access_key = getattr(app_config, "AWS_ACCESS_KEY_ID", None)
            secret_key = getattr(app_config, "AWS_SECRET_ACCESS_KEY", None)
            if access_key and secret_key:
                kwargs["aws_access_key_id"] = access_key
                kwargs["aws_secret_access_key"] = secret_key
            self.client = boto3.client("lambda", **kwargs)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def invoke_qr_generator(self, payload):
        """Invoke the QR ticket generator function.

        Args:
            payload: Dict with keys expected by the generator handler
                     (event_id, registration_id, user_id, event_name, ...).

        Returns:
            Parsed response dict from the Lambda function (or local handler).
        """
        if self.use_local:
            return self._invoke_local_generator(payload)
        return self._invoke_remote(
            getattr(self.config, "LAMBDA_QR_GENERATOR", "qr-ticket-generator"),
            payload,
        )

    def invoke_qr_validator(self, payload):
        """Invoke the QR ticket validator function.

        Args:
            payload: Dict with keys expected by the validator handler
                     (qr_data, ...).

        Returns:
            Parsed response dict from the Lambda function (or local handler).
        """
        if self.use_local:
            return self._invoke_local_validator(payload)
        return self._invoke_remote(
            getattr(self.config, "LAMBDA_QR_VALIDATOR", "qr-ticket-validator"),
            payload,
        )

    # ------------------------------------------------------------------
    # Internal -- local direct invocation
    # ------------------------------------------------------------------

    def _build_local_config(self):
        """Build the ``config`` sub-dict expected by the Lambda handlers."""
        return {
            "secret_key": getattr(self.config, "TICKET_SECRET_KEY", ""),
            "dynamodb_endpoint": getattr(self.config, "DYNAMODB_ENDPOINT", ""),
            "s3_bucket": getattr(self.config, "S3_BUCKET", ""),
            "local_storage_path": getattr(self.config, "LOCAL_STORAGE_PATH", "/tmp/qr_codes"),
        }

    def _invoke_local_generator(self, payload):
        """Import and call the QR generator handler directly.

        Returns:
            The handler's response dict.
        """
        try:
            from lambda_functions.qr_generator.handler import handler

            # Merge caller payload with the local config overrides
            event = dict(payload)
            event["config"] = self._build_local_config()

            result = handler(event, None)
            logger.info("Local QR generator returned status %s.", result.get("statusCode"))

            # Parse the body if it is a JSON string
            if isinstance(result.get("body"), str):
                result["body"] = json.loads(result["body"])

            return result
        except Exception as exc:
            logger.error("Failed to invoke local QR generator: %s", exc)
            return {
                "statusCode": 500,
                "body": {"error": f"Local generator error: {str(exc)}"},
            }

    def _invoke_local_validator(self, payload):
        """Import and call the QR validator handler directly.

        Returns:
            The handler's response dict.
        """
        try:
            from lambda_functions.qr_validator.handler import handler

            event = dict(payload)
            event["config"] = self._build_local_config()

            result = handler(event, None)
            logger.info("Local QR validator returned status %s.", result.get("statusCode"))

            if isinstance(result.get("body"), str):
                result["body"] = json.loads(result["body"])

            return result
        except Exception as exc:
            logger.error("Failed to invoke local QR validator: %s", exc)
            return {
                "statusCode": 500,
                "body": {"error": f"Local validator error: {str(exc)}"},
            }

    # ------------------------------------------------------------------
    # Internal -- AWS Lambda invocation
    # ------------------------------------------------------------------

    def _invoke_remote(self, function_name, payload):
        """Invoke an AWS Lambda function synchronously.

        Args:
            function_name: The Lambda function name or ARN.
            payload: Dict to send as the event payload.

        Returns:
            Parsed response dict with ``statusCode`` and ``body``.
        """
        try:
            response = self.client.invoke(
                FunctionName=function_name,
                InvocationType="RequestResponse",
                Payload=json.dumps(payload).encode("utf-8"),
            )

            response_payload = json.loads(response["Payload"].read().decode("utf-8"))

            # If the Lambda returned a body string, parse it
            if isinstance(response_payload.get("body"), str):
                response_payload["body"] = json.loads(response_payload["body"])

            logger.info(
                "Lambda %s returned status %s.",
                function_name,
                response_payload.get("statusCode"),
            )
            return response_payload

        except ClientError as exc:
            logger.error("Failed to invoke Lambda %s: %s", function_name, exc)
            return {
                "statusCode": 502,
                "body": {"error": f"Lambda invocation failed: {str(exc)}"},
            }
        except (json.JSONDecodeError, KeyError) as exc:
            logger.error("Invalid response from Lambda %s: %s", function_name, exc)
            return {
                "statusCode": 502,
                "body": {"error": f"Invalid Lambda response: {str(exc)}"},
            }
