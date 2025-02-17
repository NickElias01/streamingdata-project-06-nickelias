import sqlite3
from threading import Lock
import os
from utils.utils_config import BASE_DATA_DIR, SQLITE_DB_FILE_NAME

class DatabaseHandler:
    def __init__(self):
        self.db_path = os.path.join(BASE_DATA_DIR, SQLITE_DB_FILE_NAME)
        self.lock = Lock()
        os.makedirs(BASE_DATA_DIR, exist_ok=True)
        self.setup_database()

    def setup_database(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS energy_usage
                        (region TEXT,
                         timestamp TEXT,
                         power_usage_kW REAL,
                         temperature_C REAL,
                         renewable_percentage REAL
                        )''')
            conn.commit()

    def store_data(self, data):
        try:
            with self.lock:
                with sqlite3.connect(self.db_path) as conn:
                    c = conn.cursor()
                    c.execute('''INSERT INTO energy_usage 
                                (region, timestamp, power_usage_kW, temperature_C, renewable_percentage) 
                                VALUES (?, ?, ?, ?, ?)''', 
                             (data['region'], 
                              data['timestamp'], 
                              data['power_usage_kW'],
                              data['temperature_C'],
                              data['renewable_percentage']))
                    conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False