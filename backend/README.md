# Backend Service

[中文版本](README.zh-CN.md)

The backend is a FastAPI service for user authentication, project and video management, and YOLO-based vehicle analysis.

## Main files

- `app.py`: creates the FastAPI application and registers routes.
- `auth.py`: registration, login, JWT issuance, and current-user validation.
- `database.py` and `models.py`: SQLite connection and SQLAlchemy models.
- `video_routes.py`: project, video upload, and analysis endpoints.
- `requirements.txt`: Python dependencies.

## Local run

From the repository root, create a virtual environment, install `backend/requirements.txt`, set `SECRET_KEY` and `MODEL_WEIGHTS`, then run `uvicorn app:app --reload --port 8000` from `backend/`.
