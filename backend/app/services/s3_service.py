"""S3 service for QR code image storage.

Supports two modes controlled by the config object:
  - **Production**: uploads to and reads from a real S3 bucket.
  - **Development**: saves to and reads from the local filesystem under
    ``config.LOCAL_STORAGE_PATH/qr_codes/``.
"""

import logging
import os

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class S3Service:
    """Manages QR code image storage in S3 or the local filesystem."""

    def __init__(self, app_config):
        """Initialise the service from the application config.

        Args:
            app_config: A config object with the following attributes:
                - USE_LOCAL_STORAGE (bool)
                - LOCAL_STORAGE_PATH (str)  -- used when local
                - S3_BUCKET (str)
                - AWS_REGION (str)
                - Optionally AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY
        """
        self.config = app_config
        self.use_local = getattr(app_config, "USE_LOCAL_STORAGE", False)
        self.bucket = getattr(app_config, "S3_BUCKET", "")

        if self.use_local:
            self.storage_dir = os.path.join(
                getattr(app_config, "LOCAL_STORAGE_PATH", "local_data"),
                "qr_codes",
            )
            os.makedirs(self.storage_dir, exist_ok=True)
            self.client = None
        else:
            kwargs = {"region_name": getattr(app_config, "AWS_REGION", "us-east-1")}
            access_key = getattr(app_config, "AWS_ACCESS_KEY_ID", None)
            secret_key = getattr(app_config, "AWS_SECRET_ACCESS_KEY", None)
            if access_key and secret_key:
                kwargs["aws_access_key_id"] = access_key
                kwargs["aws_secret_access_key"] = secret_key
            self.client = boto3.client("s3", **kwargs)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def upload_qr_image(self, ticket_id, image_bytes):
        """Upload a QR code PNG image for the given ticket.

        Args:
            ticket_id: Unique ticket identifier used as the filename.
            image_bytes: Raw PNG bytes of the QR code image.

        Returns:
            The storage location string (local path or S3 URI).
        """
        if self.use_local:
            return self._save_local(ticket_id, image_bytes)
        return self._upload_s3(ticket_id, image_bytes)

    def get_qr_image_url(self, ticket_id):
        """Return a URL or path where the QR image can be retrieved.

        - **Local mode**: returns an API path ``/api/tickets/{ticket_id}/qr``
          that a Flask route can serve.
        - **Production mode**: returns an S3 presigned URL valid for one hour.

        Args:
            ticket_id: The ticket whose QR image is requested.

        Returns:
            A URL string, or ``None`` if the image cannot be found.
        """
        if self.use_local:
            return self._get_local_url(ticket_id)
        return self._get_presigned_url(ticket_id)

    def get_local_image_path(self, ticket_id):
        """Return the absolute filesystem path for a locally stored QR image.

        This is intended for the Flask route that serves local QR images.

        Returns:
            The file path string, or ``None`` if the file does not exist.
        """
        if not self.use_local:
            return None
        file_path = os.path.join(self.storage_dir, f"{ticket_id}.png")
        if os.path.isfile(file_path):
            return file_path
        return None

    # ------------------------------------------------------------------
    # Internal helpers -- local filesystem
    # ------------------------------------------------------------------

    def _save_local(self, ticket_id, image_bytes):
        """Write the image bytes to the local QR codes directory."""
        try:
            file_path = os.path.join(self.storage_dir, f"{ticket_id}.png")
            with open(file_path, "wb") as fh:
                fh.write(image_bytes)
            logger.info("Saved QR image locally: %s", file_path)
            return file_path
        except OSError as exc:
            logger.error("Failed to save QR image locally for %s: %s", ticket_id, exc)
            raise

    def _get_local_url(self, ticket_id):
        """Return the API path for serving a locally stored QR image."""
        file_path = os.path.join(self.storage_dir, f"{ticket_id}.png")
        if os.path.isfile(file_path):
            return f"/api/tickets/{ticket_id}/qr"
        logger.warning("Local QR image not found for ticket %s.", ticket_id)
        return None

    # ------------------------------------------------------------------
    # Internal helpers -- AWS S3
    # ------------------------------------------------------------------

    def _upload_s3(self, ticket_id, image_bytes):
        """Upload the image bytes to the configured S3 bucket."""
        s3_key = f"qr_codes/{ticket_id}.png"
        try:
            self.client.put_object(
                Bucket=self.bucket,
                Key=s3_key,
                Body=image_bytes,
                ContentType="image/png",
            )
            location = f"s3://{self.bucket}/{s3_key}"
            logger.info("Uploaded QR image to S3: %s", location)
            return location
        except ClientError as exc:
            logger.error(
                "Failed to upload QR image to S3 for %s: %s", ticket_id, exc
            )
            raise

    def _get_presigned_url(self, ticket_id):
        """Generate a presigned GET URL for the QR image in S3."""
        s3_key = f"qr_codes/{ticket_id}.png"
        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": s3_key},
                ExpiresIn=3600,
            )
            return url
        except ClientError as exc:
            logger.error(
                "Failed to generate presigned URL for %s: %s", ticket_id, exc
            )
            return None
