from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models_db import User, Tokens
from jwt_utils import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Авторизация"])

# Настройка схемы авторизации (указывает Swagger и фронтенду, куда слать логин/пароль)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# --- МОДЕЛИ ОТВЕТА ---
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str

# --- ЗАВИСИМОСТЬ ДЛЯ ЗАЩИТЫ РОУТОВ ---
def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    payload = decode_token(token, expected_type="access")
    if payload is None:
        raise HTTPException(status_code=401, detail="Недействительный токен")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Токен не содержит ID")
    return str(user_id)  # ✅ Гарантированно строка

# --- ЭНДПОИНТЫ АВТОРИЗАЦИИ ---
@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Вход в систему. Принимает username/password из формы.
    Сравнивает логин с ADMIN_USERNAME из .env, ищет юзера в БД, проверяет пароль.
    """
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_ozon_id = os.getenv("ADMIN_OZON_ID", "admin_internal_user")

    # 1. Проверяем логин
    if form_data.username != admin_username:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    # 2. Ищем пользователя в БД
    user = db.query(User).filter(User.ozon_seller_id == admin_ozon_id).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    # 3. Генерируем токены
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # 4. Сохраняем refresh_token в БД (для контроля сессий и выхода)
    expires_at = datetime.utcnow() + timedelta(minutes=30)  # Время жизни access token
    
    token_record = db.query(Tokens).filter(Tokens.user_id == user.id).first()
    if token_record:
        token_record.access_token = access_token
        token_record.refresh_token = refresh_token
        token_record.expires_at = expires_at
    else:
        db.add(Tokens(
            user_id=user.id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at  # ✅ Добавлено время истечения
        ))
    db.commit()

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

@router.post("/refresh", response_model=TokenResponse)
def refresh_token_endpoint(req: RefreshRequest, db: Session = Depends(get_db)):
    """Обновление пары токенов по refresh_token"""
    payload = decode_token(req.refresh_token, expected_type="refresh")
    if not payload:
        raise HTTPException(status_code=401, detail="Неверный refresh token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Токен повреждён")

    # Проверяем, что refresh_token действительно хранится в БД
    token_rec = db.query(Tokens).filter(Tokens.user_id == user_id, Tokens.refresh_token == req.refresh_token).first()
    if not token_rec:
        raise HTTPException(status_code=401, detail="Сессия отозвана или не найдена")

    new_access = create_access_token(data={"sub": user_id})
    new_refresh = create_refresh_token(data={"sub": user_id})
    
    from datetime import datetime, timedelta
    expires_at = datetime.utcnow() + timedelta(minutes=30)

    token_rec.access_token = new_access
    token_rec.refresh_token = new_refresh
    token_rec.expires_at = expires_at  # ✅ Обновляем время истечения
    db.commit()

    return TokenResponse(access_token=new_access, refresh_token=new_refresh)

@router.post("/logout")
def logout(user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """Отзыв токенов (выход из системы)"""
    db.query(Tokens).filter(Tokens.user_id == user_id).delete()
    db.commit()
    return {"message": "Выход выполнен"}