from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import Header, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from src.models.user_model import User
from bson import ObjectId
from dotenv import load_dotenv
from typing import Optional
import os
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False) 



load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user_optional(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[User]:
    if token is None:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user-id")
        if user_id is None:
            return None
        user = User.objects(id=ObjectId(user_id)).first()  # 👈 המרה!
        return user
    except JWTError:
        return None
