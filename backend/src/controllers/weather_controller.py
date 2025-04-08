from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.logic.weather_logic import get_weather_and_time

router = APIRouter()

class WeatherRequest(BaseModel):
    user_id: str

@router.post("/weather")
async def get_weather(request: WeatherRequest):
    try:
        data = get_weather_and_time(request.user_id)
        return data
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
