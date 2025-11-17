# attendance-management-system-42477-42486

## Backend (attendance_backend)

- Run: python run.py (listens on http://localhost:3001)
- Docs: http://localhost:3001/docs
- CORS: enabled for http://localhost:3000
- DB: Uses SQLALCHEMY_DATABASE_URI if provided; falls back to SQLite file attendance.db

### Health
- GET /            -> { "message": "Healthy" }
- GET /api/health  -> { "message": "Healthy" } (alias for convenience)

### Key Endpoints
- POST /api/users
- GET /api/users
- GET /api/users/{id}
- POST /api/attendance
- GET /api/attendance?userId=&date=&startDate=&endDate=
- GET /api/attendance/stats?userId=&date=&startDate=&endDate=

See attendance_backend/api_docs.md for examples.