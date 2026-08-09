# 后端服务

[English version](README.md)

后端是基于 FastAPI 的服务，提供用户认证、项目和视频管理，以及基于 YOLO 的车辆分析能力。

## 主要文件

- `app.py`：创建 FastAPI 应用并注册路由。
- `auth.py`：实现注册、登录、JWT 签发和当前用户校验。
- `database.py` 与 `models.py`：SQLite 连接和 SQLAlchemy 数据模型。
- `video_routes.py`：项目、视频上传和分析接口。
- `requirements.txt`：Python 依赖。

## 本地运行

请在仓库根目录创建虚拟环境、安装 `backend/requirements.txt`、设置 `SECRET_KEY` 与 `MODEL_WEIGHTS`，随后切换到 `backend/` 并运行 `uvicorn app:app --reload --port 8000`。
