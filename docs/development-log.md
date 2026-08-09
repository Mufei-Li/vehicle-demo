# Development Log

[中文版本](development-log.zh-CN.md)

## Vehicle detection experiment — 2025-08-23

- Extracted video frames and prepared a labelled YOLO dataset.
- Trained a vehicle detector for 100 epochs.
- Saved parameters, training logs, metrics, confusion matrices, PR/F1 curves, validation predictions, and model checkpoints under `training/experiments/vehicle_detection_20250823_193130/`.
- Promoted the best checkpoint to `training/deploy/best.pt` for backend inference.

## Application development

- Built a React dashboard for user access, project management, video uploads, analysis, and visualisation.
- Implemented a FastAPI service with authentication, SQLite persistence, and video analysis routes.
- Configured the frontend for GitHub Pages and packaged a Docker-based backend deployment path.
