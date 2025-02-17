import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Kafka Configuration
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC')
KAFKA_BROKER = os.getenv('KAFKA_BROKER_ADDRESS')
GROUP_ID = os.getenv('ENERGY_CONSUMER_GROUP_ID')

# Database Configuration
BASE_DATA_DIR = os.getenv('BASE_DATA_DIR', 'data')
SQLITE_DB_FILE_NAME = os.getenv('SQLITE_DB_FILE_NAME', 'energy_usage.sqlite')
MESSAGE_INTERVAL = int(os.getenv('MESSAGE_INTERVAL_SECONDS', '5'))

# Regions
REGIONS = ['Denver', 'Boulder', 'Aurora', 'Lakewood', 'Golden']

# Alert Thresholds
POWER_HIGH_THRESHOLD = 5000
POWER_LOW_THRESHOLD = 500
TEMP_HIGH_THRESHOLD = 50
TEMP_LOW_THRESHOLD = 0
RENEWABLE_LOW_THRESHOLD = 5