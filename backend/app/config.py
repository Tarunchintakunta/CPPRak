"""Application configuration for dev (local) and prod (AWS) environments."""

import os


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    TICKET_SECRET_KEY = os.environ.get("TICKET_SECRET_KEY", "ticket-hmac-secret-key-2026")
    JWT_EXPIRATION_HOURS = int(os.environ.get("JWT_EXPIRATION_HOURS", "24"))
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")


class DevelopmentConfig(Config):
    """Local development with DynamoDB Local."""
    DEBUG = True
    ENV = "development"
    DYNAMODB_ENDPOINT = os.environ.get("DYNAMODB_ENDPOINT", "http://localhost:8000")
    AWS_REGION = "us-east-1"
    AWS_ACCESS_KEY_ID = "fakeMyKeyId"
    AWS_SECRET_ACCESS_KEY = "fakeSecretAccessKey"
    S3_BUCKET = "local-tickets"
    LOCAL_STORAGE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "local_data")
    USE_LOCAL_STORAGE = True
    USE_LOCAL_LAMBDA = True


class ProductionConfig(Config):
    """AWS production environment."""
    DEBUG = False
    ENV = "production"
    DYNAMODB_ENDPOINT = None  # Use default AWS endpoint
    AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
    S3_BUCKET = os.environ.get("S3_BUCKET", "rakshan-qr-tickets")
    USE_LOCAL_STORAGE = False
    USE_LOCAL_LAMBDA = False
    LAMBDA_QR_GENERATOR = os.environ.get("LAMBDA_QR_GENERATOR", "qr-ticket-generator")
    LAMBDA_QR_VALIDATOR = os.environ.get("LAMBDA_QR_VALIDATOR", "qr-ticket-validator")


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
