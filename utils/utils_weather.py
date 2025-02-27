"""
Weather Data Utility
------------------

Handles fetching real-time weather data from Open-Meteo API for the
Energy Monitoring Suite.

Author: Elias Analytics
Version: 1.0.0
License: MIT
"""

import requests
from utils.utils_config import REGIONS_CONFIG
from utils.utils_logger import setup_logger

logger = setup_logger(__name__)

def fetch_current_temperature(latitude, longitude):
    """
    Fetch the current temperature for the specified latitude and longitude
    using the Open-Meteo API.

    Args:
        latitude (float): Latitude of the location
        longitude (float): Longitude of the location

    Returns:
        float: Current temperature in Celsius, None if fetch fails
    """
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}&longitude={longitude}"
        "&current_weather=true"
    )
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['current_weather']['temperature']
    except (requests.RequestException, KeyError) as e:
        logger.error(f"Error fetching temperature data: {e}")
        return None

def get_region_temperature(region):
    """
    Get the current temperature for a specific region.

    Args:
        region (str): Name of the region

    Returns:
        float: Current temperature in Celsius, None if fetch fails
    """
    if region not in REGIONS_CONFIG:
        logger.error(f"Unknown region: {region}")
        return None
    
    region_data = REGIONS_CONFIG[region]
    temp = fetch_current_temperature(region_data['lat'], region_data['lon'])
    if temp is not None:
        logger.debug(f"Fetched temperature for {region}: {temp}°C")
    return temp