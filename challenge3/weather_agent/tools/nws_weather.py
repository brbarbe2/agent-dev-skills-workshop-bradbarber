import os
import requests
from google import genai
from google.genai import types

def get_nws_forecast(latitude: float, longitude: float) -> dict:
    """Fetches the latest National Weather Service (NWS) forecast for given latitude and longitude coordinates.
    Only supports locations within the United States.

    Args:
        latitude: Latitude in decimal degrees (e.g., 38.8894).
        longitude: Longitude in decimal degrees (e.g., -77.0352).

    Returns:
        A dictionary containing the current and upcoming forecast periods, 
        or an error message if the location is outside US coverage or unreachable.
    """
    # NWS requires a custom User-Agent identifying the app/contact
    headers = {
        "User-Agent": "(my_adk_agent_app, contact@example.com)",
        "Accept": "application/geo+json",
    }
    
    try:
        # Step 1: Resolve coordinates to grid forecast URL
        points_url = f"https://api.weather.gov/points/{latitude:.4f},{longitude:.4f}"
        points_res = requests.get(points_url, headers=headers, timeout=10)
        
        if points_res.status_code == 404:
            return {"error": "Location coordinates are outside NWS coverage (US territories only)."}
        points_res.raise_for_status()
        
        points_data = points_res.json()
        forecast_url = points_data.get("properties", {}).get("forecast")
        
        if not forecast_url:
            return {"error": "Forecast endpoint not available for this location."}

        # Step 2: Fetch actual forecast periods
        forecast_res = requests.get(forecast_url, headers=headers, timeout=10)
        forecast_res.raise_for_status()
        forecast_data = forecast_res.json()
        
        periods = forecast_data.get("properties", {}).get("periods", [])
        
        # Format top periods for clean agent consumption
        formatted_forecast = []
        for period in periods[:3]:  # Capture current/immediate upcoming periods
            formatted_forecast.append({
                "name": period.get("name"),
                "temperature": f"{period.get('temperature')}°{period.get('temperatureUnit')}",
                "wind": f"{period.get('windSpeed')} {period.get('windDirection')}",
                "short_forecast": period.get("shortForecast"),
                "detailed_forecast": period.get("detailedForecast"),
            })
            
        return {
            "latitude": latitude,
            "longitude": longitude,
            "forecast": formatted_forecast,
        }

    except requests.exceptions.RequestException as e:
        return {"error": f"NWS API request failed: {str(e)}"}