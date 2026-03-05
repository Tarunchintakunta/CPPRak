"""Amazon Cognito service for email verification.

Handles user sign-up in Cognito User Pool and email OTP verification.
When USE_COGNITO is disabled (local dev), all operations are no-ops.
"""

import logging

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class CognitoService:
    """Manages Cognito user sign-up and email verification."""

    def __init__(self, app_config):
        self.enabled = getattr(app_config, "USE_COGNITO", False)
        self.user_pool_id = getattr(app_config, "COGNITO_USER_POOL_ID", "")
        self.client_id = getattr(app_config, "COGNITO_CLIENT_ID", "")

        if self.enabled:
            region = getattr(app_config, "AWS_REGION", "ap-southeast-2")
            self.client = boto3.client("cognito-idp", region_name=region)
        else:
            self.client = None

    def sign_up(self, email, password, name):
        """Register a user in Cognito to trigger email verification.

        Args:
            email: User's email address (used as username).
            password: User's password.
            name: User's display name.

        Returns:
            True if sign-up succeeded, False if Cognito is disabled.

        Raises:
            ClientError: On Cognito API failure.
        """
        if not self.enabled:
            return False

        try:
            self.client.sign_up(
                ClientId=self.client_id,
                Username=email,
                Password=password,
                UserAttributes=[
                    {"Name": "email", "Value": email},
                    {"Name": "name", "Value": name},
                ],
            )
            logger.info("Cognito sign-up successful for %s", email)
            return True
        except self.client.exceptions.UsernameExistsException:
            logger.info("User %s already exists in Cognito, skipping sign-up.", email)
            return True
        except ClientError as exc:
            logger.error("Cognito sign-up failed for %s: %s", email, exc)
            raise

    def verify_email(self, email, code):
        """Confirm a user's email with the verification code.

        Args:
            email: The email address (Cognito username).
            code: The 6-digit verification code from email.

        Returns:
            True if verification succeeded.

        Raises:
            ClientError: On invalid code or Cognito API failure.
        """
        if not self.enabled:
            return True

        try:
            self.client.confirm_sign_up(
                ClientId=self.client_id,
                Username=email,
                ConfirmationCode=code,
            )
            logger.info("Email verified for %s", email)
            return True
        except ClientError as exc:
            logger.error("Email verification failed for %s: %s", email, exc)
            raise

    def resend_code(self, email):
        """Resend the verification code to the user's email.

        Args:
            email: The email address (Cognito username).

        Returns:
            True if code was resent.
        """
        if not self.enabled:
            return True

        try:
            self.client.resend_confirmation_code(
                ClientId=self.client_id,
                Username=email,
            )
            logger.info("Verification code resent to %s", email)
            return True
        except ClientError as exc:
            logger.error("Failed to resend code to %s: %s", email, exc)
            raise

    def is_verified(self, email):
        """Check if a user's email is verified in Cognito.

        Args:
            email: The email address to check.

        Returns:
            True if verified or Cognito is disabled, False otherwise.
        """
        if not self.enabled:
            return True

        try:
            response = self.client.admin_get_user(
                UserPoolId=self.user_pool_id,
                Username=email,
            )
            status = response.get("UserStatus", "")
            return status == "CONFIRMED"
        except self.client.exceptions.UserNotFoundException:
            return False
        except ClientError as exc:
            logger.error("Failed to check verification for %s: %s", email, exc)
            return False
