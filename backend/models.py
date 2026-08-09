from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
import datetime
from database import Base


# =====================
# 用户表
# =====================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=True)
    phone = Column(String, unique=True, nullable=True)
    hashed_password = Column(String, nullable=False)

    # 与 Project 的一对多关系
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User id={self.id} email={self.email or self.phone}>"


# =====================
# 项目表
# =====================
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="projects")
    videos = relationship("Video", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project id={self.id} name={self.name} user_id={self.user_id}>"


# =====================
# 视频表
# =====================
class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    filename = Column(String(1024), nullable=False)
    file_path = Column(String(2048), nullable=False)  # 实际保存路径
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

    # 关系
    project = relationship("Project", back_populates="videos")
    analysis = relationship("AnalysisResult", back_populates="video", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Video id={self.id} filename={self.filename} project_id={self.project_id}>"


# =====================
# 分析结果表
# =====================
class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), index=True)
    result_json = Column(JSON().with_variant(Text, "sqlite"), nullable=False)  # 在SQLite中用Text存储
    analyzed_at = Column(DateTime, default=datetime.datetime.utcnow)

    # 关系
    video = relationship("Video", back_populates="analysis")

    def __repr__(self):
        return f"<AnalysisResult id={self.id} video_id={self.video_id}>"

