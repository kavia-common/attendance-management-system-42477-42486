from flask_smorest import Blueprint, abort
from flask.views import MethodView
from webargs.flaskparser import use_kwargs
from marshmallow import Schema, fields, validate
from sqlalchemy.exc import IntegrityError

from ..db import db, User, Attendance, attendance_stats_for_range

blp = Blueprint(
    "Attendance",
    "attendance",
    url_prefix="/api/attendance",
    description="Endpoints to record and view attendance"
)


class AttendanceCreateSchema(Schema):
    userId = fields.Int(required=True, data_key="userId", description="User ID")
    date = fields.Date(required=True, description="Attendance date (YYYY-MM-DD)")
    status = fields.Str(required=True, validate=validate.OneOf(["present", "absent", "late"]), description="Status")
    notes = fields.Str(required=False, allow_none=True, description="Optional notes")


class AttendanceQuerySchema(Schema):
    userId = fields.Int(required=False, description="Filter by user ID")
    date = fields.Date(required=False, description="Filter by specific date (YYYY-MM-DD)")
    startDate = fields.Date(required=False, description="Start date for range (YYYY-MM-DD)")
    endDate = fields.Date(required=False, description="End date for range (YYYY-MM-DD)")


class AttendanceSchema(AttendanceCreateSchema):
    id = fields.Int(required=True, dump_only=True)
    createdAt = fields.Str(required=True, dump_only=True)


@blp.route("/")
class AttendanceCollection(MethodView):
    # PUBLIC_INTERFACE
    @use_kwargs(AttendanceQuerySchema, location="query")
    def get(self, userId=None, date=None, startDate=None, endDate=None):
        """
        Get attendance records filtered by optional userId and date/range.
        Query params:
        - userId: int
        - date: YYYY-MM-DD
        - startDate: YYYY-MM-DD
        - endDate: YYYY-MM-DD
        """
        q = Attendance.query
        if userId is not None:
            q = q.filter(Attendance.user_id == userId)
        if date is not None:
            q = q.filter(Attendance.date == date)
        if startDate is not None:
            q = q.filter(Attendance.date >= startDate)
        if endDate is not None:
            q = q.filter(Attendance.date <= endDate)

        q = q.order_by(Attendance.date.desc(), Attendance.id.desc())
        rows = q.all()
        return {"attendance": [a.to_dict() for a in rows]}

    # PUBLIC_INTERFACE
    @use_kwargs(AttendanceCreateSchema, location="json")
    def post(self, userId, date, status, notes=None):
        """
        Record attendance for a user and date.
        Enforces uniqueness of (userId, date).
        """
        user = User.query.get(userId)
        if not user:
            abort(404, message="User not found")

        record = Attendance(user_id=userId, date=date, status=status, notes=notes)
        db.session.add(record)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(409, message="Attendance already recorded for this user and date")
        return record.to_dict(), 201


@blp.route("/stats")
class AttendanceStats(MethodView):
    # PUBLIC_INTERFACE
    @use_kwargs(AttendanceQuerySchema, location="query")
    def get(self, userId=None, date=None, startDate=None, endDate=None):
        """
        Get attendance statistics.
        - If userId is provided, returns stats for that user.
        - Otherwise, returns global stats across all users.
        Supports optional date, startDate, endDate filters.
        """
        if userId:
            # User-specific stats
            user = User.query.get(userId)
            if not user:
                abort(404, message="User not found")

        # date/Range parsing already handled by schema
        stats = attendance_stats_for_range(startDate, endDate)

        if userId:
            # Count for a specific user within range
            q = Attendance.query.filter(Attendance.user_id == userId)
            if date is not None:
                q = q.filter(Attendance.date == date)
            if startDate is not None:
                q = q.filter(Attendance.date >= startDate)
            if endDate is not None:
                q = q.filter(Attendance.date <= endDate)
            total = q.count()
            by_status = {}
            for status in ["present", "absent", "late"]:
                by_status[status] = q.filter(Attendance.status == status).count()
            return {"userId": userId, "total": total, "byStatus": by_status}

        return stats
