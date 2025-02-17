from utils.utils_config import (
    KAFKA_TOPIC, 
    KAFKA_BROKER, 
    MESSAGE_INTERVAL, 
    REGIONS,
    POWER_HIGH_THRESHOLD,
    POWER_LOW_THRESHOLD,
    TEMP_HIGH_THRESHOLD,
    TEMP_LOW_THRESHOLD,
    RENEWABLE_LOW_THRESHOLD
)
import time
import json
import random
from kafka import KafkaProducer
from datetime import datetime

def generate_fake_data(region):
    """Generate fake energy data with temperature and renewable metrics."""
    # Base power usage with random variation
    power_usage = random.uniform(POWER_LOW_THRESHOLD, POWER_HIGH_THRESHOLD)  # kW
    temperature = random.uniform(TEMP_LOW_THRESHOLD, TEMP_HIGH_THRESHOLD)  # Celsius
    renewable_pct = random.uniform(RENEWABLE_LOW_THRESHOLD, 40)  # Percentage

    current_time = datetime.now()
    timestamp = current_time.strftime('%Y-%m-%d %H:%M:%S')

    data = {
        'region': region,
        'timestamp': timestamp,
        'power_usage_kW': round(power_usage, 2),
        'temperature_C': round(temperature, 2),
        'renewable_percentage': round(renewable_pct, 2)
    }
    return data

def send_data():
    """Send fake energy usage data to Kafka."""
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    while True:
        for region in REGIONS:
            data = generate_fake_data(region)
            producer.send(KAFKA_TOPIC, value=data)
            print(f"Sent data to {region}: {data}")
        time.sleep(MESSAGE_INTERVAL)

if __name__ == '__main__':
    print(f"Producer starting... Sending data every {MESSAGE_INTERVAL} seconds")
    try:
        send_data()
    except KeyboardInterrupt:
        print("\nProducer stopped by user")
    except Exception as e:
        print(f"\nProducer stopped due to error: {e}")