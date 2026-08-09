# 车辆信息智能识别与数据分析平台

本仓库记录车辆识别与数据分析平台的完整开发过程，涵盖前端界面、后端接口、数据准备、模型训练和实验结果。

[English version](README.md) | [双语文档维护规则](docs/README.md)

## 目录结构

- `frontend/`：React + Vite 前端。
- `backend/`：FastAPI 接口、用户认证和视频分析接口。
- `training/scripts/`：视频抽帧、模型训练、测试和报告生成脚本。
- `training/dataset/`：已标注图像和 YOLO 格式标签。
- `training/experiments/`：训练参数、日志、指标、图表、报告和模型检查点。
- `training/weights/`：训练使用的基础 YOLO 权重。
- `training/deploy/`：后端推理使用的模型权重。
- `docs/`：开发过程和数据集说明。

数据集图像和模型权重通过 Git LFS 管理。克隆仓库后请运行 `git lfs pull` 下载这些文件。

## 本地运行

前端：

```powershell
cd frontend
npm install
npm run dev
```

后端：

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
$env:SECRET_KEY = "replace-with-a-long-random-secret"
$env:MODEL_WEIGHTS = "..\training\deploy\best.pt"
uvicorn app:app --reload --port 8000
```

在仓库根目录执行 `docker compose up --build` 可通过 Docker 启动后端。

## 训练记录

当前记录的实验为 `vehicle_detection_20250823_193130`。简要过程见[开发日志](docs/development-log.zh-CN.md)，数据构成见[数据集说明](docs/dataset.zh-CN.md)。

## Git 工作流

```powershell
git status
git add .
git commit -m "说明本次改动"
git push
```
