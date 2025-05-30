import requests
from datetime import datetime, timedelta
from urllib.parse import quote
from src.models.user_model import User
import os
import json

def get_weather_and_time(user_id: str) -> dict:
    try:
        user = User.objects.get(id=user_id)
    except Exception as e:
        raise ValueError("User not found")
    
    city = user.city.strip()
    country = user.country.strip()
    
    query = f"{city},{country}"
    query_encoded = quote(query) 
    
    API_KEY = os.getenv("WEATHER_API")
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={query_encoded}&appid={API_KEY}&units=metric"
    
    response = requests.get(url)

    if response.status_code != 200:
        raise ValueError("Failed to retrieve weather data")
    
    weather_json = response.json()
    try:
        forecast = weather_json["list"][0]
        description = forecast["weather"][0]["description"]
        temperature = forecast["main"]["temp"]
        tz_offset = weather_json["city"].get("timezone", 0)
    except (KeyError, IndexError) as e:
        raise ValueError("Weather data incomplete")
    
    local_time = datetime.utcnow() + timedelta(seconds=tz_offset)
    local_time_str = local_time.strftime("%Y-%m-%d %H:%M:%S")
    
    return {
        "Country" : country,
        "City" : city,
        "weather_description": description,
        "temperature": temperature,
        "local_time": local_time_str
    }
