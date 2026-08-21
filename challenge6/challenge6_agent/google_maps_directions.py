import googlemaps
import os
from datetime import datetime

import requests

def get_routes_api_directions(
    origin: str,
    destination: str,
    travel_mode: str = "DRIVE",
    language_code: str = "en-US",
    units: str = "IMPERIAL"
) -> dict:
    """
    Fetches directions using the Google Maps Routes API (v2 REST).

    :param origin: Origin address string or 'lat,lng'.
    :param destination: Destination address string or 'lat,lng'.
    :param travel_mode: 'DRIVE', 'BICYCLE', 'WALK', 'TWO_WHEELER', or 'TRANSIT'.
    :param language_code: Language for step instructions (e.g., 'en-US').
    :param units: 'IMPERIAL' or 'METRIC'.
    :return: Formatted dictionary containing route distance, duration, and steps.
    """
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": os.environ.get("GOOGLE_MAPS_API_KEY"),
        # FieldMask determines what data is calculated and billed
        "X-Goog-FieldMask": (
            "routes.distanceMeters,"
            "routes.duration,"
            "routes.legs.steps.navigationInstruction,"
            "routes.legs.steps.distanceMeters,"
            "routes.legs.steps.staticDuration"
        )
    }

    payload = {
        "origin": {
            "address": origin
        },
        "destination": {
            "address": destination
        },
        "travelMode": travel_mode.upper(),
        "routingPreference": "TRAFFIC_AWARE",
        "languageCode": language_code,
        "units": units
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        if not data.get("routes"):
            return {"error": "No route found."}

        route = data["routes"][0]
        legs = route.get("legs", [{}])[0]
        raw_steps = legs.get("steps", [])

        steps = []
        for step in raw_steps:
            nav = step.get("navigationInstruction", {})
            steps.append({
                "instruction": nav.get("instructions", "Continue"),
                "maneuver": nav.get("maneuver", "N/A"),
                "distance_meters": step.get("distanceMeters", 0),
                "duration": step.get("staticDuration", "0s")
            })

        return {
            "distance_meters": route.get("distanceMeters"),
            "duration": route.get("duration"),
            "steps": steps
        }

    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP Error: {e.response.text}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}
