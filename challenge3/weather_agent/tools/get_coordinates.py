import os
import googlemaps
from google import genai
from google.genai import types

# 1. Initialize the Google Maps client
# Ensure GOOGLE_MAPS_API_KEY is set in your environment
gmaps = googlemaps.Client(key=os.environ.get("GOOGLE_MAPS_API_KEY"))

def get_city_coordinates(city_name: str) -> dict:
    """Converts a city name or address into latitude and longitude coordinates using Google Maps.

    Args:
        city_name: The name of the city (e.g., 'Paris, France', 'Tokyo, Japan').

    Returns:
        A dictionary containing latitude, longitude, and formatted address,
        or an error message if not found.
    """
    try:
        geocode_result = gmaps.geocode(city_name)
        
        if not geocode_result:
            return {"error": f"Coordinates not found for city: {city_name}"}
        
        location = geocode_result[0]["geometry"]["location"]
        formatted_address = geocode_result[0].get("formatted_address", city_name)
        
        return {
            "city": city_name,
            "formatted_address": formatted_address,
            "latitude": location["lat"],
            "longitude": location["lng"]
        }
    except Exception as e:
        return {"error": f"Geocoding API call failed: {str(e)}"}