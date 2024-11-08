import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Step 1: Load ECG data from a CSV file
# Replace 'D:/Projects/My_repos/DSP_Tasks/Task1/Signals/normal_ecg.csv' with the actual path to your CSV file
df = pd.read_csv('D:/Projects/My_repos/DSP_Tasks/Task1/Signals/normal_ecg.csv', header=None)

# Step 2: Extract the ECG signal from the single column
ecg_signal = df.values.flatten()  # Assuming the ECG values are in the first column

# Step 3: Check for any NaN or Inf values and remove them
ecg_signal = ecg_signal[~np.isnan(ecg_signal)]
ecg_signal = ecg_signal[~np.isinf(ecg_signal)]

# Step 4: Normalize the ECG signal to avoid negative values and ensure better plotting
r = (ecg_signal - np.min(ecg_signal)) / (np.max(ecg_signal) - np.min(ecg_signal))

# Step 5: Generate theta values (index) for polar coordinates
theta = np.linspace(0, 2 * np.pi, len(ecg_signal))

# Step 6: Set up the figure and axis for the polar plot
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
ax.set_title('ECG Signal in Polar Coordinates - Cine Mode')

# Initialize the line that will be updated in the animation
line, = ax.plot([], [], color='blue', lw=2)

# Step 7: Function to initialize the plot (called once at the start)
def init():
    line.set_data([], [])
    return line,

# Step 8: Function to update the plot dynamically in cine mode
def update(frame):
    # Update the data to plot up to the current frame
    line.set_data(theta[:frame], r[:frame])
    return line,

# Step 9: Create the animation
ani = FuncAnimation(fig, update, frames=len(theta), init_func=init, blit=True, interval=20, repeat=False)

# Step 10: Show the plot with animation
plt.show()
