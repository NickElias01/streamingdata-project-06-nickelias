# streamingdata-project-06-nickelias

# Elias Analytics
# Project Consumer: `project_consumer_nickelias.py`

## Overview



## Requirements

- Python 3.x
- Kafka broker running
- Required Python packages:
  ```bash
  pip install kafka-python python-dotenv matplotlib

## Setting Up Kafka & Zookeeper

Before running the producer and consumer, ensure that both Zookeeper and Kafka services are running.

### Start Zookeeper Service (Terminal 1)
1. Open a terminal (WSL/Mac/Linux).
2. Navigate to the Kafka directory:
   ```bash
   cd ~/kafka
   ```
3. Ensure the script has execute permissions (may not be necessary):
   ```bash
   chmod +x zookeeper-server-start.sh
   ```
4. Start the Zookeeper service:
   ```bash
   bin/zookeeper-server-start.sh config/zookeeper.properties
   ```
5. **Keep this terminal open** while working with Kafka.

### Start Kafka (Terminal 2)
1. Open a **new terminal**. (On Windows, open PowerShell and run `wsl` to get a WSL terminal first.)
2. Navigate to the Kafka directory:
   ```bash
   cd ~/kafka
   ```
3. Ensure the script has execute permissions (may not be necessary):
   ```bash
   chmod +x kafka-server-start.sh
   ```
4. Start the Kafka service:
   ```bash
   bin/kafka-server-start.sh config/server.properties
   ```
5. **Keep this terminal open** while working with Kafka.


## Running the Project Producer (Terminal 3)

To run the Kafka producer provided in the project without modifications, open a terminal and run:

```bash
.\.venv\Scripts\activate
py -m producers.energy_data_producer
```

> **Note:** Ensure that Kafka is running before executing the producer to avoid connection issues.

## Running the New Project Consumer (Terminal 4)

To run the `project_consumer_nickelias.py` script, open a terminal and execute:

```bash
.\.venv\Scripts\activate
py -m consumers.energy_data_consumer
```

This will start the consumer, and you'll see the real-time bar chart updating as new messages are processed.



## Additional Notes

- **Dependencies:** Ensure you have installed the required dependencies:
  - `matplotlib`
  - `kafka-python` (or your preferred Kafka client library)
  - `python-dotenv`
- **Configuration:** Update your `.env` file with the correct Kafka topic and consumer group ID.
- **Kafka Setup:** Refer to the Kafka and Zookeeper setup instructions above to ensure both services are running before starting the producer and consumer.