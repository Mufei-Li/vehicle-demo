# Vehicle Detection Platform

[中文版本](README.zh-CN.md) | [Bilingual documentation policy](docs/README.md)

## Overview

Vehicle Detection Platform is an end-to-end web application for managing vehicle-video analysis projects. It combines a React dashboard, a FastAPI service, and a YOLO-based detection and tracking pipeline. This repository is intentionally organised as a development portfolio: it preserves the application code, labelled dataset, experiment configuration, visual outputs, logs, and checkpoints needed to understand how the platform was built.

## Platform capabilities

- **Account and project management:** register and sign in, create analysis projects, and keep projects scoped to their owners.
- **Video workflow:** upload, list, retrieve, and delete videos within a project.
- **Vehicle analysis:** process uploaded video frame by frame with a YOLO model, retain tracking IDs, and report the number of checked frames and unique vehicles.
- **Results visualisation:** present analysis results in the dashboard through summaries and charts.
- **Location interaction:** provide map-based location selection and search in the frontend interface.

## Development journey

1. **Data preparation:** frames were extracted from project video material, reviewed, annotated in YOLO format, and split into training and validation sets.
2. **Model training:** a vehicle detector was trained for 100 epochs. The repository includes the corresponding parameters, logs, metrics, confusion matrices, PR/F1 curves, validation predictions, and checkpoints.
3. **Application integration:** the trained best checkpoint was promoted for backend inference and connected to FastAPI video-analysis routes.
4. **Product interface and deployment:** a React dashboard was built for project and video workflows, while Docker and GitHub Pages deployment paths were configured.

See the [development log](docs/development-log.md) and [dataset notes](docs/dataset.md) for supporting details.

## Technology stack

- **Frontend:** React, Vite, Ant Design, Recharts, and AMap JavaScript API.
- **Backend:** FastAPI, SQLAlchemy, SQLite, JWT authentication, and Uvicorn.
- **Computer vision:** Ultralytics YOLO, OpenCV, and PyTorch.
- **Reproducibility and delivery:** Git, Git LFS, Docker, and GitHub Actions/GitHub Pages configuration.

## Repository structure

- `frontend/`: React + Vite client.
- `backend/`: FastAPI API, authentication, and video-analysis endpoints.
- `training/scripts/`: frame extraction, training, testing, and report-generation scripts.
- `training/dataset/`: labelled images and YOLO labels used by the recorded experiment.
- `training/experiments/`: training configuration, logs, metrics, charts, report, and model checkpoints.
- `training/weights/`: base YOLO weights used during training.
- `training/deploy/`: the model weight used by the backend.
- `docs/`: development and dataset documentation in English and Chinese.

Dataset images and model weights are tracked with Git LFS. After cloning, run `git lfs pull` to retrieve them.

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

The current recorded experiment is `vehicle_detection_20250823_193130`. Its dataset, experiment artefacts, and deployment weight are versioned in this repository so that reviewers can inspect the full workflow.

## Git workflow

```powershell
git status
git add .
git commit -m "Describe the change"
git push
```
