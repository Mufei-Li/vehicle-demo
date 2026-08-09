# 开发日志

[English version](development-log.md)

## 车辆检测实验 — 2025-08-23

- 从项目视频中提取帧图像，并准备 YOLO 标注数据集。
- 使用车辆检测数据训练模型，共训练 100 个 epoch。
- 将参数、训练日志、指标、混淆矩阵、PR/F1 曲线、验证集预测结果和模型检查点保存至 `training/experiments/vehicle_detection_20250823_193130/`。
- 将最优检查点复制至 `training/deploy/best.pt`，供后端推理使用。

## 应用开发

- 构建了支持用户访问、项目管理、视频上传、分析和可视化的 React 仪表盘。
- 实现基于 FastAPI 的服务，提供认证、SQLite 数据持久化和视频分析接口。
- 配置前端通过 GitHub Pages 部署，并提供 Docker 化后端部署路径。
