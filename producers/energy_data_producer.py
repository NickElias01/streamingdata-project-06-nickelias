"""
Energy Data Producer
------------------

Simulated energy data producer for the Energy Monitoring Suite.
Generates and publishes synthetic power usage, temperature, and renewable energy data
for multiple regions to a Kafka message queue.

This module is part of the Energy Monitoring Suite developed by Elias Analytics.
It simulates real-world energy metrics by generating realistic data patterns
and publishing them to a message queue for downstream processing.

Features:
    - Synthetic data generation for multiple regions
    - Configurable data ranges and intervals
    - Kafka message queue integration
    - Automated continuous data publishing
    - Graceful shutdown handling
    - Configurable thresholds for different metrics

Author: Elias Analytics
Version: 1.0.0
License: MIT
"""

# Import configuration from utilities
from utils.utils_config import (
    KAFKA_TOPIC,          # Topic name for energy data messages
    KAFKA_BROKER,         # Kafka broker connection address
    MESSAGE_INTERVAL,     # Delay between message batches
    REGIONS,             # List of monitored regions
    POWER_HIGH_THRESHOLD, # Maximum normal power usage
    POWER_LOW_THRESHOLD,  # Minimum normal power usage
    TEMP_HIGH_THRESHOLD,  # Maximum normal temperature
    TEMP_LOW_THRESHOLD,   # Minimum normal temperature
    RENEWABLE_LOW_THRESHOLD  # Minimum acceptable renewable percentage
)

# Standard library imports
import time
import json
import random
from datetime import datetime
from kafka import KafkaProducer

def generate_fake_data(region):
    """
    Generate synthetic energy metrics for a specific region.
    
    Simulates realistic power usage, temperature, and renewable energy
    percentages with random variations within configured thresholds.
    
    Args:
        region (str): Name of the region to generate data for
        
    Returns:
        dict: Dictionary containing the generated metrics with keys:
            - region: Region name
            - timestamp: Current timestamp
            - power_usage_kW: Power usage in kilowatts
            - temperature_C: Temperature in Celsius
            - renewable_percentage: Renewable energy percentage
    """
    # Generate random values within realistic ranges
    power_usage = random.uniform(POWER_LOW_THRESHOLD, POWER_HIGH_THRESHOLD)  # kW
    temperature = random.uniform(TEMP_LOW_THRESHOLD, TEMP_HIGH_THRESHOLD)    # Celsius
    renewable_pct = random.uniform(RENEWABLE_LOW_THRESHOLD, 40)             # Percentage

    # Create timestamp for current reading
    current_time = datetime.now()
    timestamp = current_time.strftime('%Y-%m-%d %H:%M:%S')

    # Package data into structured format
    data = {
        'region': region,
        'timestamp': timestamp,
        'power_usage_kW': round(power_usage, 2),
        'temperature_C': round(temperature, 2),
        'renewable_percentage': round(renewable_pct, 2)
    }
    return data

def send_data():
    """
    Continuously generate and publish energy data to Kafka.
    
    Creates a Kafka producer and enters an infinite loop to generate
    and send data for each configured region at regular intervals.
    Data is serialized to JSON before sending.
    
    Raises:
        KafkaTimeoutError: If connection to Kafka broker fails
        KeyboardInterrupt: If user terminates the program
    """
    # Initialize Kafka producer with JSON serialization
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    # Main data generation and sending loop
    while True:
        for region in REGIONS:
            # Generate and send data for each region
            data = generate_fake_data(region)
            producer.send(KAFKA_TOPIC, value=data)
            print(f"Sent data to {region}: {data}")
            
        # Wait for configured interval before next batch
        time.sleep(MESSAGE_INTERVAL)

if __name__ == '__main__':
    print(f"Producer starting... Sending data every {MESSAGE_INTERVAL} seconds")
    try:
        # Start continuous data generation and sending
        send_data()
    except KeyboardInterrupt:
        # Handle graceful shutdown on Ctrl+C
        print("\nProducer stopped by user")
    except Exception as e:
        # Handle unexpected errors
        print(f"\nProducer stopped due to error: {e}")