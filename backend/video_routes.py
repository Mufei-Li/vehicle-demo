from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from typing import Optional
import os, shutil, tempfile, datetime
from ultralytics import YOLO
import tempfile
import os
import models
import models
from models import Project, Video
from database import get_db
from auth import get_current_user
import cv2
import json
import datetime


router = APIRouter(tags=["Video Management"])

# 创建视频文件保存目录（演示用）
# 在系统临时目录中创建上传目录
UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "uploaded_videos")
os.makedirs(UPLOAD_DIR, exist_ok=True)
# 加载YOLO模型
model = YOLO(os.getenv("MODEL_WEIGHTS", "best.pt"))


# =============================
# 创建新项目接口
# =============================
@router.post("/create_project")
def create_project(
    name: str = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """为当前用户创建新项目"""
    project = models.Project(name=name, user_id=current_user.id)
    db.add(project)
    db.commit()
    db.refresh(project)

    return {"message": "项目创建成功", "project_id": project.id, "name": project.name}


# =============================
# 上传视频接口
# =============================
@router.post("/upload_video")
def upload_video(
    project_id: int = Form(...),
    video: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """上传视频并保存到指定项目下"""
    # 检查项目归属
    project = db.query(models.Project).filter_by(id=project_id, user_id=current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在或无权限访问")

    # 保存视频到磁盘
    file_path = os.path.join(UPLOAD_DIR, f"{datetime.datetime.utcnow().timestamp()}_{video.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(video.file, buffer)

    # 写入数据库
    video_record = models.Video(
        project_id=project.id,
        filename=video.filename,
        file_path=file_path
    )
    db.add(video_record)
    db.commit()
    db.refresh(video_record)

    return {
        "message": "视频上传成功",
        "video_id": video_record.id,
        "filename": video.filename,
        "file_path": file_path
    }


# =============================
# 视频分析接口
# =============================
@router.post("/analyze_video")
def analyze_video(
    video_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """分析用户上传的视频"""
    video = (
        db.query(models.Video)
        .join(models.Project)
        .filter(models.Video.id == video_id, models.Project.user_id == current_user.id)
        .first()
    )
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在或无权限访问")

    # 打开视频
    cap = cv2.VideoCapture(video.file_path)
    if not cap.isOpened():
        raise HTTPException(status_code=400, detail="无法打开视频文件")

    frame_count = 0
    unique_ids = set()

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 1
        results = model.track(frame, persist=True, verbose=False)
        if results and results[0].boxes.id is not None:
            ids = results[0].boxes.id.cpu().numpy().astype(int)
            classes = results[0].boxes.cls.cpu().numpy().astype(int)
            for track_id, cls in zip(ids, classes):
                name = model.names[int(cls)].lower()
                if "car" in name or "vehicle" in name or "truck" in name or "bus" in name:
                    unique_ids.add(track_id)

    cap.release()

    # 保存分析结果
    analysis = models.AnalysisResult(
        video_id=video.id,
        result_json=json.dumps({
            "vehicle_count": len(unique_ids),
            "frames_checked": frame_count,
            "timestamp": str(datetime.datetime.utcnow())
        })
    )
    db.add(analysis)
    db.commit()

    return {
        "message": "分析完成",
        "video_id": video.id,
        "vehicle_count": len(unique_ids),
        "frames_checked": frame_count
    }
    
@router.get("/projects")
def get_user_projects(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """获取当前用户的所有项目"""
    projects = db.query(models.Project).filter(models.Project.user_id == current_user.id).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "created_at": getattr(p, "created_at", None),
            "updated_at": getattr(p, "updated_at", None),
        }
        for p in projects
    ]


@router.get("/list_videos")
def list_videos(project_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """获取当前用户指定项目下的视频"""
    project = db.query(models.Project).filter(models.Project.id == project_id, models.Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在或无权访问")

    videos = db.query(models.Video).filter(models.Video.project_id == project_id).all()
    BASE_URL = "https://ragpp-vehicle-detection-backend.hf.space"

    return [
        {
            "id": v.id,
            "filename": v.filename,
            # 改成可直接访问的完整 URL
            "path": f"{BASE_URL}/video/file/{v.id}",
            "created_at": getattr(v, "uploaded_at", None),
            "status": "uploaded",
        }
        for v in videos
    ]

    
@router.delete("/delete_project/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    删除当前用户的指定项目（自动级联删除视频和分析结果，并清理文件）
    """
    project = (
        db.query(models.Project)
        .filter(models.Project.id == project_id, models.Project.user_id == current_user.id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在或无权限访问")

    # 删除对应视频文件（数据库记录会通过 cascade 自动删除）
    for video in project.videos:
        if video.file_path and os.path.exists(video.file_path):
            try:
                os.remove(video.file_path)
            except Exception as e:
                print(f"删除文件失败: {video.file_path}, 错误: {e}")

    db.delete(project)
    db.commit()

    return {"message": f"项目《{project.name}》及其视频已删除"}

@router.delete("/delete_video/{video_id}")
def delete_video(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    删除当前用户的视频（自动删除对应分析结果）
    """
    video = (
        db.query(models.Video)
        .join(models.Project)
        .filter(models.Video.id == video_id, models.Project.user_id == current_user.id)
        .first()
    )
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在或无权限访问")

    # 删除物理视频文件
    if video.file_path and os.path.exists(video.file_path):
        try:
            os.remove(video.file_path)
        except Exception as e:
            print(f"删除文件失败: {video.file_path}, 错误: {e}")

    db.delete(video)
    db.commit()

    return {"message": f"视频《{video.filename}》及其分析结果已删除"}

@router.get("/file/{video_id}")
def get_video_file(video_id: int, db: Session = Depends(get_db)):
    """
    返回视频文件（允许匿名访问，供前端视频播放器使用）
    """
    video = db.query(models.Video).filter(models.Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    try:
        return FileResponse(video.file_path, media_type="video/mp4")
    except Exception as e:
        print(f"无法读取视频文件: {e}")
        raise HTTPException(status_code=500, detail="无法读取视频文件")

# @router.get("/debug/db_snapshot")
# def debug_db_snapshot(db: Session = Depends(get_db)):
#     return {
#         "users": [u.__dict__ for u in db.query(models.User).all()],
#         "projects": [p.__dict__ for p in db.query(models.Project).all()],
#         "videos": [v.__dict__ for v in db.query(models.Video).all()],
#         "analysis_results": [r.__dict__ for r in db.query(models.AnalysisResult).all()],
#     }
