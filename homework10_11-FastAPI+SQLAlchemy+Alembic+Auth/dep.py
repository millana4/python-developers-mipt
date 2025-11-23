from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from auth import AuthService
from db_service import DBManager
from models import User

security = HTTPBearer()

def get_db():
    db = DBManager()
    try:
        yield db.session
    finally:
        db.close()

def get_current_user(
    token: str = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    auth_service = AuthService(db)
    username = auth_service.verify_token(token.credentials)
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user