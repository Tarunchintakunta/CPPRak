"""Application configuration for dev (local) and prod (AWS) environments."""

import os


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    TICKET_SECRET_KEY = os.environ.get("TICKET_SECRET_KEY", "ticket-hmac-secret-key-2026")
    JWT_EXPIRATION_HOURS = int(os.environ.get("JWT_EXPIRATION_HOURS", "24"))
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:3000,http://rakshan-frontend.s3-website-ap-southeast-2.amazonaws.com").split(",")
    COGNITO_USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID", "ap-southeast-2_yK2wHJqUR")
    COGNITO_CLIENT_ID = os.environ.get("COGNITO_CLIENT_ID", "7n5fhjhl3ktldkokc6nen4p9co")


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
    USE_COGNITO = False


class ProductionConfig(Config):
    """AWS production environment."""
    DEBUG = False
    ENV = "production"
    DYNAMODB_ENDPOINT = None  # Use default AWS endpoint
    AWS_REGION = os.environ.get("AWS_REGION", "ap-southeast-2")
    S3_BUCKET = os.environ.get("S3_BUCKET", "rakshan-qr-tickets")
    USE_LOCAL_STORAGE = False
    USE_LOCAL_LAMBDA = False
    USE_COGNITO = True
    LAMBDA_QR_GENERATOR = os.environ.get("LAMBDA_QR_GENERATOR", "qr-ticket-generator")
    LAMBDA_QR_VALIDATOR = os.environ.get("LAMBDA_QR_VALIDATOR", "qr-ticket-validator")


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
