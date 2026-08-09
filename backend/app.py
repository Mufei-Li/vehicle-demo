from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

import models
import database
import auth
from video_routes import router as video_router

# ==========================================================
# 创建 FastAPI 应用
# ==========================================================
app = FastAPI(title="Vehicle Detection Backend")

# ==========================================================
# 数据库初始化（自动创建表）
# ==========================================================
models.Base.metadata.create_all(bind=database.engine)

# ==========================================================
# 跨域配置（允许前端访问）
# ==========================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================
# 注册路由模块
# ==========================================================
app.include_router(auth.router, prefix="", tags=["Authentication"])
app.include_router(video_router, prefix="/video", tags=["Video & Projects"])

# ==========================================================
# 根路径（主页）
# ==========================================================
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>Vehicle Detection Backend</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #fafafa; }
                .container { max-width: 800px; margin: 0 auto; }
                .upload-form { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; background: #fff; }
                h1 { color: #333; }
                a { color: #007bff; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚗 Vehicle Detection Backend</h1>
                <p>This API provides vehicle detection, tracking, and analysis features with user login support.</p>

                <div class="upload-form">
                    <h3>Quick Test:</h3>
                    <form action="/video/analyze_video" method="post" enctype="multipart/form-data">
                        <input type="file" name="video" accept="video/*">
                        <input type="submit" value="Analyze Video">
                    </form>
                </div>

                <p><strong>API Documentation:</strong></p>
                <ul>
                    <li><a href="/docs">Swagger UI</a> - Interactive API documentation</li>
                    <li><a href="/redoc">ReDoc</a> - Alternative documentation</li>
                </ul>

                <p><strong>Endpoints:</strong></p>
                <ul>
                    <li>POST /register — User registration</li>
                    <li>POST /login — User login</li>
                    <li>POST /video/upload_video — Upload a video</li>
                    <li>POST /video/analyze_video — Analyze a video</li>
                    <li>GET /video/user_projects — Get all projects for current user</li>
                </ul>
            </div>
        </body>
    </html>
    """
