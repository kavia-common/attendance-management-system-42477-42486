from flask_smorest import Blueprint
from flask.views import MethodView

blp = Blueprint("Health", "health", url_prefix="/", description="Health check route")


@blp.route("/")
class HealthCheck(MethodView):
    # PUBLIC_INTERFACE
    def get(self):
        """Simple health check endpoint."""
        return {"message": "Healthy"}


@blp.route("/api/health")
class HealthCheckAlias(MethodView):
    # PUBLIC_INTERFACE
    def get(self):
        """Alias health check under /api/health for frontends expecting that path."""
        return {"message": "Healthy"}
