from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from mock_data import db

security = HTTPBearer()

def mock_auth():
    # Для MVP — всегда возвращаем фиксированного пользователя
    # В реальном приложении тут проверка токена
    user_id = "mock_user_123"
    db.get_or_create_user(user_id)
    return user_id

# mock_auth = lambda: "mock_user_123"