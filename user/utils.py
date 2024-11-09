from datetime import datetime, timedelta
from typing import Any, Union

from user.models import User
from chat.models import *
from core.dependencies import get_db
from fastapi import HTTPException, Request, status
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import SessionLocal

ACCESS_TOKEN_EXPIRE_MINUTES = 240  # 240 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = "c87201cd0ea515c359feb1baf8dd9099c2ea4083020ac5b9212c0de0e7551d1d"  # generated using openssl rand -hex 32

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login/")

security = HTTPBearer()

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)


def create_access_token(data: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "sub": str(data)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def get_user_from_token(token: str, session: Session = Depends(get_db)):
    from user.crud import user    
    try:
        payload = jwt.decode(token, key=JWT_SECRET_KEY,
                             options={"verify_signature": False, "verify_aud": False, "verify_iss": False})
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # TODO: need to check why simply not session object, but SessionLocal is working
    user_in_db = user.get_user_by_username(SessionLocal(), username)
    if user_in_db is None:
        raise credentials_exception
    return user_in_db    


def get_current_user(authorization: HTTPAuthorizationCredentials = Depends(security), session: Session = Depends(get_db)):
    token = authorization.credentials
    return get_user_from_token(token, session)


def get_users_with_room(user):
    session = SessionLocal()

    # first get all room ids 
    room_ids = [room.id for room in user.chats]

    # get all users with whom user has a chat room
    other_users = session.query(room_members_table.c.member_id).filter(
        room_members_table.c.chat_room_id.in_(room_ids), 
        room_members_table.c.member_id != user.id).all()

    other_user_ids = [user_id[0] for user_id in other_users]
    users = session.query(User).filter(User.id.in_(other_user_ids)).all()
    return users