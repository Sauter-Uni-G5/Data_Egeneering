from fastapi import APIRouter, Query
from typing import Optional
from app.services.weather_service import get_weather_data

router = APIRouter()

@router.get("/data/weather")
def get_weather(
    latitude: float = Query(..., description="Latitude do reservatório ou região"),
    longitude: float = Query(..., description="Longitude do reservatório ou região"),
    start_date: str = Query(..., description="Data inicial (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Data final (YYYY-MM-DD)")
):
    return get_weather_data(latitude, longitude, start_date, end_date)