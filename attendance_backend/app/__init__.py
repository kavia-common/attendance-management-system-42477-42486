from flask import Flask
from flask_cors import CORS
from flask_smorest import Api
from .routes.health import blp as health_blp

# New imports for database and routes
from .db import init_db, db
from .routes.users import blp as users_blp
from .routes.attendance import blp as attendance_blp


def create_app():
    """
    Factory to create and configure the Flask app.
    - Enables CORS for http://localhost:3000
    - Configures OpenAPI docs at /docs
    - Initializes SQLite fallback if external DB is not configured
    - Registers blueprints for health, users, and attendance
    """
    app = Flask(__name__)
    app.url_map.strict_slashes = False

    # CORS setup for React dev server
    CORS(app, resources={r"/*": {"origins": ["http://localhost:3000"]}})

    # OpenAPI / Swagger configuration
    app.config["API_TITLE"] = "Attendance Management API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/docs"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    # Database configuration (SQLite fallback)
    # The following env vars can be provided to point to an external DB through SQLALCHEMY_DATABASE_URI
    # If not present, a local SQLite file will be used.
    app.config.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///attendance.db")
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)

    # Initialize DB and create tables
    init_db(app)

    # Register API blueprints
    api = Api(app)
    api.register_blueprint(health_blp)
    api.register_blueprint(users_blp)
    api.register_blueprint(attendance_blp)
    return app


# Create an app instance for WSGI and tools that import "app"
app = create_app()
