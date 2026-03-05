"""Flask application factory.

Creates and configures the Flask app, initialises services, and registers
all route blueprints.
"""

import logging
import os

from flask import Flask
from flask_cors import CORS

from app.config import config
from app.services.dynamo_service import DynamoService
from app.services.s3_service import S3Service
from app.services.lambda_service import LambdaService
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)


def create_app(config_name=None):
    """Application factory.

    Args:
        config_name: One of ``"development"``, ``"production"``, or
                     ``"default"``.  Falls back to the ``FLASK_ENV``
                     environment variable, then ``"development"``.

    Returns:
        A fully configured Flask application instance.
    """
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)

    # Load configuration
    app_config = config.get(config_name, config["default"])
    app.config.from_object(app_config)

    # CORS
    cors_origins = getattr(app_config, "CORS_ORIGINS", ["http://localhost:3000"])
    CORS(app, resources={r"/api/*": {"origins": cors_origins}})

    # ------------------------------------------------------------------
    # Initialise services and attach to the app instance
    # ------------------------------------------------------------------
    app.dynamo_service = DynamoService(app_config)
    app.s3_service = S3Service(app_config)
    app.lambda_service = LambdaService(app_config)
    app.auth_service = AuthService(
        secret_key=app_config.SECRET_KEY,
        expiration_hours=getattr(app_config, "JWT_EXPIRATION_HOURS", 24),
    )

    # ------------------------------------------------------------------
    # Register blueprints
    # ------------------------------------------------------------------
    from app.routes.auth import auth_bp
    from app.routes.events import events_bp
    from app.routes.registrations import registrations_bp
    from app.routes.tickets import tickets_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(registrations_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(admin_bp)

    # ------------------------------------------------------------------
    # Create DynamoDB tables on startup
    # ------------------------------------------------------------------
    with app.app_context():
        try:
            app.dynamo_service.create_tables()
            logger.info("DynamoDB tables verified / created.")
        except Exception as exc:
            logger.warning("Could not create DynamoDB tables on startup: %s", exc)

    # ------------------------------------------------------------------
    # Health-check endpoint
    # ------------------------------------------------------------------
    @app.route("/api/health", methods=["GET"])
    def health():
        return {"status": "healthy", "environment": config_name}, 200

    return app
