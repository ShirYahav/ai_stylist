# user_controller.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from src.logic.auth_logic import register_user, login_user
from src.utils.auth_utils import create_access_token
from src.models.user_model import User
from typing import Optional
from src.utils.auth_utils import get_current_user_optional  

router = APIRouter()

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    country: str
    city: str
    full_name: str = None
    gender: str = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
async def register(auth: RegisterRequest):
    try:
        user = register_user(
            email=auth.email,
            password=auth.password,
            country=auth.country,
            city=auth.city,
            full_name=auth.full_name,
            gender=auth.gender
        )
        return {"message": "User registered successfully", "user_id": str(user.id)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
async def login(auth: LoginRequest):
    try:
        user = login_user(email=auth.email, password=auth.password)
        token = create_access_token({"user-id": str(user.id)})
        
        return {"access_token": token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    