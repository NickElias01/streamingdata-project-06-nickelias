"""
Alert Handler Utility
-------------------

Monitors and generates alerts for energy metrics that exceed defined thresholds.
Part of the Energy Monitoring Suite's utility collection.

This module provides alert handling functionality for:
    - Power usage (high/low thresholds)
    - Temperature (high/low thresholds)
    - Renewable energy percentage (minimum threshold)

Author: Elias Analytics
Version: 1.0.0
License: MIT
"""

from utils.utils_config import (
    POWER_HIGH_THRESHOLD,
    POWER_LOW_THRESHOLD,
    TEMP_HIGH_THRESHOLD,
    TEMP_LOW_THRESHOLD,
    RENEWABLE_LOW_THRESHOLD
)

class AlertHandler:
    """
    Handles threshold monitoring and alert generation for energy metrics.
    
    This class provides static methods to check incoming data against
    predefined thresholds and generate appropriate warning messages.
    """

    @staticmethod
    def check_alerts(data):
        """
        Check data points against configured thresholds and generate alerts.

        Args:
            data (dict): Dictionary containing energy metrics with keys:
                - region (str): Geographic region name
                - timestamp (str): Reading timestamp
                - power_usage_kW (float): Power usage in kilowatts
                - temperature_C (float): Temperature in Celsius
                - renewable_percentage (float): Renewable energy percentage

        Returns:
            list: List of formatted alert messages for any exceeded thresholds
        
        Example:
            >>> data = {
            ...     'region': 'Denver',
            ...     'timestamp': '2024-02-17 10:00:00',
            ...     'power_usage_kW': 6000,
            ...     'temperature_C': 35,
            ...     'renewable_percentage': 2
            ... }
            >>> alerts = AlertHandler.check_alerts(data)
            >>> print(alerts[0])
            "WARNING [2024-02-17 10:00:00] - HIGH POWER USAGE: Denver at 6000.0 kW"
        """
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