import os

from fastapi import APIRouter, Form, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
import models, database

# ==========================================================
# 路由实例
# ==========================================================
router = APIRouter()

# 密码哈希配置（使用 sha256_crypt 以避免 Hugging Face 环境问题）
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "development-only-secret-change-me")
ALGORITHM = "HS256"

# ==========================================================
# 辅助函数
# ==========================================================

def get_password_hash(password: str):
    """生成密码哈希"""
    return pwd_context.hash(password[:72])

def verify_password(plain_password: str, hashed_password: str):
    """验证密码"""
    try:
        return pwd_context.verify(plain_password[:72], hashed_password)
    except Exception:
        return False

def create_access_token(data: dict):
    """生成 JWT token"""
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

# ==========================================================
# 注册接口
# ==========================================================

@router.post("/register")
def register_user(
    email: str = Form(None),
    phone: str = Form(None),
    password: str = Form(...),
    db: Session = Depends(database.get_db)
):
    """
    注册新用户（支持邮箱或手机号）
    """
    if not (email or phone):
        raise HTTPException(status_code=400, detail="请填写邮箱或手机号。")

    try:
        # 检查重复
        if email:
            existing = db.query(models.User).filter(models.User.email == email).first()
            if existing:
                raise HTTPException(status_code=400, detail="该邮箱已注册，请直接登录。")

        if phone:
            existing = db.query(models.User).filter(models.User.phone == phone).first()
            if existing:
                raise HTTPException(status_code=400, detail="该手机号已注册，请直接登录。")

        # 加密密码并保存
        hashed = get_password_hash(password)
        new_user = models.User(email=email, phone=phone, hashed_password=hashed)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        print(f"新用户注册成功: id={new_user.id}, email={email}, phone={phone}")
        return {"status": "success", "message": "注册成功，请登录。"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print("❌ 注册错误:", e)
        raise HTTPException(status_code=500, detail=f"服务器内部错误：{str(e)}")

# ==========================================================
# 登录接口
# ==========================================================

@router.post("/login")
def login_user(
    identifier: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(database.get_db)
):
    """
    登录接口（支持邮箱或手机号 + 密码）
    """
    try:
        print(f"登录尝试: identifier={identifier}")

        # 查询用户
        user = db.query(models.User).filter(models.User.email == identifier).first()
        if not user:
            user = db.query(models.User).filter(models.User.phone == identifier).first()

        if not user:
            print("❌ 用户不存在")
            raise HTTPException(status_code=400, detail="用户不存在，请检查邮箱或手机号。")

        # 验证密码
        if not verify_password(password, user.hashed_password):
            print("❌ 密码错误")
            raise HTTPException(status_code=400, detail="密码错误，请重新输入。")

        # 成功登录
        token = create_access_token({"sub": str(user.id)})
        print(f"登录成功: user_id={user.id}")

        return {
            "status": "success",
            "access_token": token,
            "token_type": "bearer",
            "user_id": user.id
        }

    except HTTPException:
        raise
    except Exception as e:
        print("登录错误:", e)
        raise HTTPException(status_code=500, detail=f"服务器内部错误：{str(e)}")


# ==========================================================
# 获取当前用户依赖函数
# ==========================================================

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(database.get_db)
):
    """
    验证并返回当前登录用户。
    所有需要登录才能访问的接口，都可以通过 Depends(auth.get_current_user) 使用。
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="无效或过期的Token")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")

    return user
