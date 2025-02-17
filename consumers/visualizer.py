"""
Energy Data Visualizer
--------------------

Real-time visualization component for the Energy Monitoring Suite.
Provides dynamic plotting capabilities for power usage and temperature data
across multiple regions.

This module is part of the Energy Monitoring Suite developed by Elias Analytics.
It handles the real-time visualization of energy metrics using matplotlib,
featuring a dual-plot display with line graphs for power usage trends and
bar charts for current temperature readings.

Features:
    - Real-time line plot of power usage over time
    - Dynamic bar chart of current temperatures
    - Auto-scaling axes with time-based padding
    - Color-coded regions for easy identification
    - Temperature labels on bar charts
    - Configurable data point window

Author: Elias Analytics
Version: 1.0.0
License: MIT
"""

# Set matplotlib backend before importing pyplot
import matplotlib
matplotlib.use('TkAgg')  # Must be called before importing pyplot

# Standard library imports
import datetime
from collections import deque

# Third-party visualization imports
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class EnergyVisualizer:
    """
    Real-time energy data visualizer using matplotlib.
    
    Creates and manages two synchronized plots:
    1. Line plot showing power usage over time for each region
    2. Bar chart showing current temperature readings for each region
    
    Args:
        max_points (int): Maximum number of data points to display in line plot
    """
    
    def __init__(self, max_points=5):
        # Initialize basic parameters
        self.max_points = max_points
        self.regions = ['Denver', 'Boulder', 'Aurora', 'Lakewood', 'Golden']
        
        # Initialize data storage using deque for automatic size management
        self.data = {region: {
            'times': deque(maxlen=max_points),      # Timestamp storage
            'usage': deque(maxlen=max_points),      # Power usage storage
            'temperature': deque(maxlen=1)          # Current temperature
        } for region in self.regions}
        
        # Create matplotlib figure with two subplots
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(20, 8))
        self.lines = {}                            # Store line objects for updating
        self.ani = None                           # Animation object placeholder
        self.setup_plot()                         # Initialize plot settings

    def setup_plot(self):
        """Initialize the plot settings."""
        plt.style.use('seaborn-v0_8-darkgrid')  # Use a cleaner style

        # Setup the first plot
        self.ax1.set_title('Real-time Energy Usage by Region', fontsize=12, pad=20)
        self.ax1.set_xlabel('Time', fontsize=10)
        self.ax1.set_ylabel('Power Usage (kW)', fontsize=10)
        
        # Use distinct colors and line styles
        styles = [
            ('Denver', 'red', '-'),
            ('Boulder', 'blue', '-'),
            ('Aurora', 'green', '-'),
            ('Lakewood', 'purple', '-'),
            ('Golden', 'orange', '-')
        ]
        
        for region, color, style in styles:
            line, = self.ax1.plot([], [], 
                               label=region, 
                               color=color, 
                               linestyle=style,
                               linewidth=2,
                               marker='o',  # Add markers
                               markersize=4)
            self.lines[region] = line
        
        # Improve legend
        self.ax1.legend(loc='upper right')
        
        # Rotate x-axis labels
        self.ax1.tick_params(axis='x', rotation=45)
        
        # Add grid with alpha
        self.ax1.grid(True, alpha=0.3)
        
        # Setup bar plot (right side)
        self.ax2.set_title('Current Temperature by Region', fontsize=12)
        self.ax2.set_xlabel('Region', fontsize=10)
        self.ax2.set_ylabel('Temperature (°C)', fontsize=10)
        self.bars = self.ax2.bar(self.regions, [0] * len(self.regions))
        self.ax2.set_ylim(-5, 60)  # Temperature range 0-40°C
        
        # Rotate x-axis labels for bar chart
        self.ax2.tick_params(axis='x', rotation=45)

        # Color the bars using the same colors as the lines
        for bar, (_, color, _) in zip(self.bars, styles):
            bar.set_color(color)

        # Adjust layout to prevent label cutoff
        plt.tight_layout()

    def update_data(self, data):
        """
        Update data storage with new readings.
        
        Args:
            data (dict): Dictionary containing new readings with keys:
                        'region', 'timestamp', 'power_usage_kW', 'temperature_C'
        """
        region = data['region']
        # Convert timestamp string to datetime object and store new data
        self.data[region]['times'].append(
            datetime.datetime.strptime(data['timestamp'], '%Y-%m-%d %H:%M:%S'))
        self.data[region]['usage'].append(data['power_usage_kW'])
        self.data[region]['temperature'].append(data['temperature_C'])

    def animate(self, frame):
        """
        Animation function called by FuncAnimation.
        Updates both plots with current data.
        
        Args:
            frame: Frame number (unused but required by FuncAnimation)
        
        Returns:
            list: Collection of line objects for blitting
        """
        # Update line plot for each region
        for region in self.regions:
            times = list(self.data[region]['times'])
            usage = list(self.data[region]['usage'])
            if times and usage:
                self.lines[region].set_data(times, usage)

        # Update temperature bar chart
        temperatures = [
            self.data[region]['temperature'][-1] 
            if self.data[region]['temperature'] 
            else 0 
            for region in self.regions
        ]
    
        # Update bar heights and labels
        for bar, temp in zip(self.bars, temperatures):
            bar.set_height(temp)
            # Clear existing temperature labels
            for txt in self.ax2.texts:
                txt.remove()
            # Add updated temperature labels
            for rect in self.bars:
                height = rect.get_height()
                self.ax2.text(
                    rect.get_x() + rect.get_width()/2., 
                    height,
                    f'{height:.1f}°C',
                    ha='center', 
                    va='bottom'
                )

        # Adjust line plot time axis with padding
        if any(len(self.data[region]['times']) > 0 for region in self.regions):
            all_times = [t for r in self.regions for t in self.data[r]['times']]
            if all_times:
                # Calculate time range and add 10% padding
                min_time = min(all_times)
                max_time = max(all_times)
                time_range = max_time - min_time
                padding = time_range * 0.1
                self.ax1.set_xlim(
                    min_time - datetime.timedelta(seconds=padding.total_seconds()),
                    max_time + datetime.timedelta(seconds=padding.total_seconds())
                )
            self.ax1.set_ylim(0, 10000)  # Fixed power usage range
        
        # Ensure proper layout
        self.fig.tight_layout()
        return self.lines.values()

    def start(self):
        """
        Start the real-time visualization.
        Initializes animation and displays the plot window.
        """
        self.ani = FuncAnimation(
            self.fig, 
            self.animate, 
            interval=1000,          # Update every second
            cache_frame_data=False, # Disable caching for real-time display
            blit=False             # Disable blitting for stability
        )
        plt.show(block=True)      # Show plot window and block execution