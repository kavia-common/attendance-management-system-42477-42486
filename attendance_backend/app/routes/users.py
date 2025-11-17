from flask_smorest import Blueprint, abort
from flask.views import MethodView
from webargs.flaskparser import use_kwargs
from marshmallow import Schema, fields, validate
from sqlalchemy.exc import IntegrityError

from ..db import db, User

blp = Blueprint(
    "Users",
    "users",
    url_prefix="/api/users",
    description="Endpoints to manage users"
)


class UserCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1), description="User full name")
    email = fields.Email(required=True, description="Unique email address")


class UserSchema(UserCreateSchema):
    id = fields.Int(required=True, dump_only=True)
    createdAt = fields.Str(required=True, dump_only=True)


@blp.route("/")
class UsersCollection(MethodView):
    # PUBLIC_INTERFACE
    def get(self):
        """List all users."""
        users = User.query.order_by(User.id.asc()).all()
        return {"users": [u.to_dict() for u in users]}

    # PUBLIC_INTERFACE
    @use_kwargs(UserCreateSchema, location="json")
    def post(self, name, email):
        """
        Create a new user with name and email.
        Returns 201 with the created user.
        """
        name = name.strip()
        email = email.strip().lower()
        if not name:
            abort(400, message="Name cannot be empty")
        if not email:
            abort(400, message="Email cannot be empty")

        user = User(name=name, email=email)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(409, message="Email already exists")
        return user.to_dict(), 201


@blp.route("/<int:user_id>")
class UserItem(MethodView):
    # PUBLIC_INTERFACE
    def get(self, user_id: int):
        """Get user by ID."""
        user = User.query.get(user_id)
        if not user:
            abort(404, message="User not found")
        return user.to_dict()
