"""
Database initialization and models for the Attendance Management API.

This module sets up SQLAlchemy with a SQLite fallback and defines the core models:
- User
- Attendance

Environment configuration:
- SQLALCHEMY_DATABASE_URI (optional) can be provided externally.
"""
from __future__ import annotations

from datetime import date, datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, UniqueConstraint
from typing import Optional

db = SQLAlchemy()


def init_db(app):
    """Initialize SQLAlchemy with the Flask app and create tables if they don't exist."""
    db.init_app(app)
    with app.app_context():
        db.create_all()


class User(db.Model):
    """User model representing a person whose attendance is tracked."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email, "createdAt": self.created_at.isoformat()}


class Attendance(db.Model):
    """Attendance model representing a user's attendance record for a date."""
    __tablename__ = "attendance"
    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_attendance_user_date"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default="present")  # "present" | "absent" | "late"
    notes = db.Column(db.String(512), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("attendance", lazy=True, cascade="all, delete"))

    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "date": self.date.isoformat(),
            "status": self.status,
            "notes": self.notes,
            "createdAt": self.created_at.isoformat(),
        }


# Helper functions for stats
def attendance_stats_for_range(start: Optional[date], end: Optional[date]):
    """
    Compute attendance stats across all users for a date range.

    Returns counts per status and total records.
    """
    q = db.session.query(Attendance.status, func.count(Attendance.id)).group_by(Attendance.status)
    if start:
        q = q.filter(Attendance.date >= start)
    if end:
        q = q.filter(Attendance.date <= end)
    rows = q.all()
    by_status = {status: count for status, count in rows}
    total = sum(by_status.values())
    return {
        "total": total,
        "byStatus": by_status,
    }
