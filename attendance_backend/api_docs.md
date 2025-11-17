# Attendance Management API

Base URL: http://localhost:3001

OpenAPI/Swagger UI: http://localhost:3001/docs

CORS: Enabled for http://localhost:3000

## Users

- POST /api/users
  - Body:
    {
      "name": "Jane Doe",
      "email": "jane@example.com"
    }
  - 201 Created:
    {
      "id": 1,
      "name": "Jane Doe",
      "email": "jane@example.com",
      "createdAt": "2025-01-01T12:00:00.000000"
    }

- GET /api/users
  - 200 OK:
    { "users": [ { "id": 1, "name": "Jane Doe", "email": "jane@example.com", "createdAt": "..." } ] }

- GET /api/users/{id}
  - 200 OK:
    { "id": 1, "name": "Jane Doe", "email": "jane@example.com", "createdAt": "..." }
  - 404 if not found.

## Attendance

- POST /api/attendance
  - Body:
    {
      "userId": 1,
      "date": "2025-01-02",
      "status": "present",
      "notes": "On time"
    }
  - 201 Created:
    {
      "id": 1,
      "userId": 1,
      "date": "2025-01-02",
      "status": "present",
      "notes": "On time",
      "createdAt": "..."
    }
  - 404 if user not found, 409 if already exists for user/date.

- GET /api/attendance?userId=1&date=2025-01-02
  - Filters by userId and/or date or by startDate/endDate range.
  - 200 OK:
    { "attendance": [ { "id": 1, "userId": 1, "date": "2025-01-02", "status": "present", "notes": "On time", "createdAt": "..." } ] }

- GET /api/attendance/stats?startDate=2025-01-01&endDate=2025-01-31
  - Global stats:
    {
      "total": 12,
      "byStatus": { "present": 10, "absent": 1, "late": 1 }
    }
  - With userId query param: returns user-specific totals and byStatus.

## Notes

- SQLite fallback: If no external SQLALCHEMY_DATABASE_URI is provided via environment, a local `attendance.db` SQLite database will be used automatically.
- Errors follow JSON format:
  { "message": "Error details..." }
