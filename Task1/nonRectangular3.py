import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.animation import FuncAnimation

# Load wind data from CSV file
data = pd.read_csv('Signals/tibau_wind.csv', header=None, names=['timestamp', 'speed', 'direction'])

# Extract wind speed and direction
wind_speed = data['speed'].values
wind_direction = data['direction'].values

# Convert wind direction to radians
theta = np.radians(wind_direction)

# Create a polar plot with a black background
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
fig.patch.set_facecolor('black')  # Set figure background color
ax.set_facecolor('black')          # Set polar plot background color

# Set the zero location to the North
ax.set_theta_zero_location('N')  

# Set plot limits and title
ax.set_ylim(0, max(wind_speed) + 1)  # Adjust the Y limit to accommodate the speed
ax.set_title('Wind Speed and Direction', va='bottom', color='white')  # Set title color

# Create a line for the radar effect
radar_line, = ax.plot([], [], color='red', linewidth=2)

# Create a scatter object for the wind data points
scatter = ax.scatter([], [], marker='o', color='blue', alpha=0.7)

# Animation variables
radar_angle = 0  # Initial angle for the radar line
point_index = 0  # Index to track which point to plot
frames_per_point = 30  # Number of frames to show each point
current_frame = 0  # Frame counter to manage visibility

def init():
    radar_line.set_data([], [])
    scatter.set_offsets(np.empty((0, 2)))  # Initialize with an empty 2D array
    return radar_line, scatter

def update(frame):
    global radar_angle, point_index, current_frame

    # Calculate the radar line's end point
    radar_angle += 0.1  # Adjust the speed of rotation here
    radar_x = [radar_angle, radar_angle]
    radar_y = [0, max(wind_speed)]  # Extend line to max speed
    radar_line.set_data(radar_x, radar_y)  # Update the radar line data

    # Manage the visibility of points
    if point_index < len(theta):
        if current_frame < frames_per_point:
            # Show the current point for a number of frames
            scatter.set_offsets(np.c_[theta[point_index], wind_speed[point_index]])  # Set the current point
            current_frame += 1  # Increment frame count
        else:
            # Move to the next point and reset the frame count
            point_index += 1
            current_frame = 0
            scatter.set_offsets(np.empty((0, 2)))  # Clear the points after showing them

    return radar_line, scatter

# Create an animation
ani = FuncAnimation(fig, update, frames=np.arange(0, 360), init_func=init, blit=True, interval=100)

plt.show()
