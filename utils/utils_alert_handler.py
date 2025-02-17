from utils.utils_config import (POWER_HIGH_THRESHOLD, POWER_LOW_THRESHOLD,
                         TEMP_HIGH_THRESHOLD, TEMP_LOW_THRESHOLD,
                         RENEWABLE_LOW_THRESHOLD)

class AlertHandler:
    @staticmethod
    def check_alerts(data):
        """Check data for alert conditions and return list of warnings."""
        alerts = []
        region = data['region']
        timestamp = data['timestamp']
        
        # Power usage alerts
        if data['power_usage_kW'] > POWER_HIGH_THRESHOLD:
            alerts.append(f"WARNING [{timestamp}] - HIGH POWER USAGE: {region} at {data['power_usage_kW']:.1f} kW")
        elif data['power_usage_kW'] < POWER_LOW_THRESHOLD:
            alerts.append(f"WARNING [{timestamp}] - LOW POWER USAGE: {region} at {data['power_usage_kW']:.1f} kW")
        
        # Temperature alerts
        if data['temperature_C'] > TEMP_HIGH_THRESHOLD:
            alerts.append(f"WARNING [{timestamp}] - HIGH TEMPERATURE: {region} at {data['temperature_C']:.1f}°C")
        elif data['temperature_C'] < TEMP_LOW_THRESHOLD:
            alerts.append(f"WARNING [{timestamp}] - LOW TEMPERATURE: {region} at {data['temperature_C']:.1f}°C")
        
        # Renewable percentage alert
        if data['renewable_percentage'] < RENEWABLE_LOW_THRESHOLD:
            alerts.append(f"WARNING [{timestamp}] - LOW RENEWABLE %: {region} at {data['renewable_percentage']:.1f}%")
        
        return alerts