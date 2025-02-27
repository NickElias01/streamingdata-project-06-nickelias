from utils.utils_weather import get_region_temperature
from utils.utils_config import REGIONS_CONFIG

def test_api_connection():
    """Test API connectivity for all configured regions."""
    print("\nTesting Open-Meteo API connection for all regions...")
    print("-" * 50)

    for region, config in REGIONS_CONFIG.items():
        temp = get_region_temperature(region)
        if temp is not None:
            print(f"✅ {region}: {temp}°C")
        else:
            print(f"❌ {region}: Failed to fetch temperature")
    
    print("-" * 50)

if __name__ == "__main__":
    test_api_connection()