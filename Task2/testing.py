import numpy as np
import pandas as pd

# Parameters
f1 = 30  # Frequency of the first sine wave (Hz)
f2 = 70  # Frequency of the second sine wave (Hz)
f3 = 50  # Frequency of the third sine wave (Hz)
A1 = 0.5  # Amplitude of the first sine wave
A2 = 1  # Amplitude of the second sine wave
A3 = 0.2  # Amplitude of the third sine wave
T = 4  # Total duration of the signal (seconds)
num_samples = 15000  # Number of samples to generate

# Create the time array
t_orig = np.linspace(0, T, num_samples, endpoint=False)

# Create the original signal (composite of 10, 30, and 50 Hz)
original_signal = (A1 * np.sin(2 * np.pi * f1 * t_orig) +
                   A2 * np.sin(2 * np.pi * f2 * t_orig) + 
                   A3 * np.sin(2 * np.pi * f3 * t_orig))

# Create a DataFrame to hold the time and signal values
data = pd.DataFrame({'time': t_orig, 'voltage': original_signal})

# Save to CSV
csv_file_path = 'composite.csv'
data.to_csv(csv_file_path, index=False)

print(f"CSV file saved at: {csv_file_path}")
