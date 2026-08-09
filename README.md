# Vehicle Detection Platform

This repository records the end-to-end development of a vehicle recognition and analysis platform: interface development, API implementation, data preparation, model training, and experimental results.

## Structure

- `frontend/`: React + Vite client.
- `backend/`: FastAPI API, authentication, and video-analysis endpoints.
- `training/scripts/`: frame extraction, training, testing, and report-generation scripts.
- `training/dataset/`: labelled images and YOLO labels.
- `training/experiments/`: training configuration, logs, metrics, charts, report, and model checkpoints.
- `training/weights/`: base YOLO weights used during training.
- `training/deploy/`: the model weight used by the backend.
- `docs/`: development and dataset documentation.

Dataset images and model weights are tracked with Git LFS. Clone the project with `git lfs pull` to retrieve them.

## Run locally

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

Backend:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
$env:SECRET_KEY = "replace-with-a-long-random-secret"
$env:MODEL_WEIGHTS = "..\training\deploy\best.pt"
uvicorn app:app --reload --port 8000
```

To run the backend in Docker, use `docker compose up --build` from the repository root.

## Training records

The current experiment is `vehicle_detection_20250823_193130`. See [development log](docs/development-log.md) for a concise record and [dataset notes](docs/dataset.md) for dataset composition.

## Git workflow

```powershell
git status
git add .
git commit -m "Describe the change"
git push
```
