from fastapi import APIRouter, HTTPException
import httpx

from services import weather_service

router = APIRouter(tags=["weather"])


@router.get("/weather")
async def get_weather(location: str):
    """Fetch current weather and forecast for a given city."""
    if not location.strip():
        raise HTTPException(status_code=422, detail="'location' query parameter is required.")
    try:
        result = weather_service.get_weather_response(location.strip())
        return result
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Location '{location}' not found.")
        raise HTTPException(status_code=502, detail="Weather service unavailable.")
    except Exception:
        raise HTTPException(status_code=502, detail="Weather service unavailable.")
