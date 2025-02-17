"""
Database Handler Utility
----------------------

SQLite database management for the Energy Monitoring Suite.
Handles data persistence, connection management, and query operations
for energy monitoring metrics.

This module provides database functionality for:
    - Storing energy usage readings
    - Managing database connections
    - Handling concurrent database access
    - Automated table creation and management

Author: Elias Analytics
Version: 1.0.0
License: MIT
"""

import sqlite3
from threading import Lock
import os
from utils.utils_config import BASE_DATA_DIR, SQLITE_DB_FILE_NAME

class DatabaseHandler:
    """
    Handles SQLite database operations with thread-safe access.
    
    This class manages database connections, table creation, and data storage
    operations while ensuring thread safety for concurrent access.

    Attributes:
        db_path (str): Full path to SQLite database file
        lock (Lock): Thread lock for synchronizing database access
    """

    def __init__(self):
        """
        Initialize database handler and create required database structures.
        
        Creates the database directory if it doesn't exist and initializes
        the energy_usage table with the required schema.
        
        Raises:
            sqlite3.Error: If database initialization fails
            OSError: If directory creation fails
        """
        self.db_path = os.path.join(BASE_DATA_DIR, SQLITE_DB_FILE_NAME)
        self.lock = Lock()
        
        # Ensure data directory exists
        os.makedirs(BASE_DATA_DIR, exist_ok=True)
        
        # Initialize database schema
        self.setup_database()

    def setup_database(self):
        """
        Create the energy_usage table if it doesn't exist.
        
        Defines the schema for storing energy monitoring data including
        region, timestamp, power usage, temperature, and renewable percentage.
        
        Raises:
            sqlite3.Error: If table creation fails
        """
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS energy_usage (
                    region TEXT,
                    timestamp TEXT,
                    power_usage_kW REAL,
                    temperature_C REAL,
                    renewable_percentage REAL
                )
            ''')
            conn.commit()

    def store_data(self, data):
        """
        Store energy monitoring data in the database.
        
        Args:
            data (dict): Dictionary containing energy metrics with keys:
                - region (str): Geographic region name
                - timestamp (str): Reading timestamp
                - power_usage_kW (float): Power usage in kilowatts
                - temperature_C (float): Temperature in Celsius
                - renewable_percentage (float): Renewable energy percentage
        
        Returns:
            bool: True if data was stored successfully, False otherwise
        
        Example:
            >>> data = {
            ...     'region': 'Denver',
            ...     'timestamp': '2024-02-17 10:00:00',
            ...     'power_usage_kW': 3500.5,
            ...     'temperature_C': 25.6,
            ...     'renewable_percentage': 15.2
            ... }
            >>> db_handler = DatabaseHandler()
            >>> success = db_handler.store_data(data)
        """
        try:
            with self.lock:  # Ensure thread-safe database access
                with sqlite3.connect(self.db_path) as conn:
                    c = conn.cursor()
                    c.execute('''
                        INSERT INTO energy_usage 
                        (region, timestamp, power_usage_kW, temperature_C, renewable_percentage) 
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        data['region'],
                        data['timestamp'],
                        data['power_usage_kW'],
                        data['temperature_C'],
                        data['renewable_percentage']
                    ))
                    conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False

    def close(self):
        """
        Clean up database resources.
        
        This method should be called when shutting down the application
        to ensure proper resource cleanup.
        """
        # Currently a placeholder for future cleanup operations
        pass