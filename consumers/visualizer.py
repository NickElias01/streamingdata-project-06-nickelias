import matplotlib
matplotlib.use('TkAgg')  # Must be called before importing pyplot

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import datetime

class EnergyVisualizer:
    def __init__(self, max_points=5):  # Reduce max_points to show fewer data points
        self.max_points = max_points
        self.regions = ['Denver', 'Boulder', 'Aurora', 'Lakewood', 'Golden']
        # Use deque with maxlen to automatically maintain window size
        self.data = {region: {'times': deque(maxlen=max_points),
                             'usage': deque(maxlen=max_points),
                             'temperature': deque(maxlen=1)
            } for region in self.regions}
        
        # Store animation object as instance variable
        self.ani = None

        # Setup the plot
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(20, 8))
        self.lines = {}
        self.setup_plot()

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
        """Update data for a specific region."""
        region = data['region']
        self.data[region]['times'].append(
            datetime.datetime.strptime(data['timestamp'], '%Y-%m-%d %H:%M:%S'))
        self.data[region]['usage'].append(data['power_usage_kW'])
        self.data[region]['temperature'].append(data['temperature_C'])

    def animate(self, frame):
        """Update the line plot."""
        for region in self.regions:
            times = list(self.data[region]['times'])
            usage = list(self.data[region]['usage'])
            if times and usage:
                self.lines[region].set_data(times, usage)

            # Update bar plot
        temperatures = [self.data[region]['temperature'][-1] 
                   if self.data[region]['temperature'] 
                   else 0 
                   for region in self.regions]
    
        for bar, temp in zip(self.bars, temperatures):
            bar.set_height(temp)
            # Remove existing text if present
            for txt in self.ax2.texts:
                txt.remove()
            # Add new temperature labels on top of each bar
            for rect in self.bars:
                height = rect.get_height()
                self.ax2.text(rect.get_x() + rect.get_width()/2., height,
                            f'{height:.1f}°C',
                            ha='center', va='bottom')

        # Adjust line plot limits
        if any(len(self.data[region]['times']) > 0 for region in self.regions):
            all_times = [t for r in self.regions for t in self.data[r]['times']]
            if all_times:
                min_time = min(all_times)
                max_time = max(all_times)
                time_range = max_time - min_time
                padding = time_range * 0.1
                self.ax1.set_xlim(
                    min_time - datetime.timedelta(seconds=padding.total_seconds()),
                    max_time + datetime.timedelta(seconds=padding.total_seconds())
                )
            self.ax1.set_ylim(0, 10000)
        
        # Adjust layout
        self.fig.tight_layout()
        return self.lines.values()

       
    def start(self):
        """Start the animation."""
        self.ani = FuncAnimation(
            self.fig, 
            self.animate, 
            interval=1000,
            cache_frame_data=False,
            blit=False  # Changed to False for better stability
        )
        plt.show(block=True)  # Added block=True