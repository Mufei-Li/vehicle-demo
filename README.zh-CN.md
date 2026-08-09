# 车辆信息智能识别与数据分析平台

[English version](README.md) | [双语文档维护规则](docs/README.zh-CN.md)

## 项目概述

车辆信息智能识别与数据分析平台是一套面向车辆视频分析项目的端到端 Web 应用。平台将 React 仪表盘、FastAPI 服务和基于 YOLO 的检测与跟踪流程结合起来。本仓库按照开发作品集组织：除应用代码外，还保留标注数据集、实验配置、可视化结果、日志和模型检查点，便于读者了解平台的完整开发过程。

## 平台功能

- **账户与项目管理：** 支持注册、登录、创建分析项目，并按用户维度管理项目。
- **视频工作流：** 支持在项目内上传、查看、获取和删除视频。
- **车辆分析：** 使用 YOLO 模型逐帧处理上传视频，保留跟踪 ID，并统计检测帧数和去重后的车辆数量。
- **结果可视化：** 在仪表盘中以摘要和图表形式展示分析结果。
- **位置交互：** 前端提供基于地图的位置选择与搜索能力。

## 开发过程

1. **数据准备：** 从项目视频中提取帧图像，完成检查和 YOLO 格式标注，并划分训练集与验证集。
2. **模型训练：** 训练车辆检测模型共 100 个 epoch；仓库保留训练参数、日志、指标、混淆矩阵、PR/F1 曲线、验证集预测结果和模型检查点。
3. **应用集成：** 将训练得到的最优检查点用于后端推理，并接入 FastAPI 视频分析接口。
4. **产品界面与部署：** 构建 React 仪表盘以支持项目和视频工作流，同时配置 Docker、GitHub Actions 和 GitHub Pages 部署路径。

更多细节见[开发日志](docs/development-log.zh-CN.md)和[数据集说明](docs/dataset.zh-CN.md)。

## 技术栈

- **前端：** React、Vite、Ant Design、Recharts 和高德地图 JavaScript API。
- **后端：** FastAPI、SQLAlchemy、SQLite、JWT 认证和 Uvicorn。
- **计算机视觉：** Ultralytics YOLO、OpenCV 和 PyTorch。
- **可复现与交付：** Git、Git LFS、Docker，以及 GitHub Actions/GitHub Pages 配置。

## 目录结构

- `frontend/`：React + Vite 前端。
- `backend/`：FastAPI 接口、用户认证和视频分析接口。
- `training/scripts/`：视频抽帧、模型训练、测试和报告生成脚本。
- `training/dataset/`：本次记录实验所使用的已标注图像和 YOLO 格式标签。
- `training/experiments/`：训练参数、日志、指标、图表、报告和模型检查点。
- `training/weights/`：训练使用的基础 YOLO 权重。
- `training/deploy/`：后端推理使用的模型权重。
- `docs/`：中英文开发过程和数据集说明。

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

当前记录的实验为 `vehicle_detection_20250823_193130`。其数据集、实验产物和部署权重均已纳入仓库版本管理，方便评审者查看完整流程。

## Git 工作流

```powershell
git status
git add .
git commit -m "说明本次改动"
git push
```
