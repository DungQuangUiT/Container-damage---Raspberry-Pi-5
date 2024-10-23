import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import savgol_filter

# Read the CSV file
df = pd.read_csv('results.csv')

# Define the columns to plot
columns_to_plot = [
    '           train/box_om', '           train/cls_om', '           train/dfl_om', '           train/box_oo', '           train/cls_oo',
    '             val/box_om','             val/cls_om','             val/dfl_om','             val/box_oo','             val/cls_oo','             val/dfl_oo'
]

# Create a 3x4 grid of subplots (we'll only use 11 of them)
fig, axes = plt.subplots(3, 4, figsize=(20, 15))
fig.suptitle(' ', fontsize=16)

# Flatten the axes array for easier iteration
axes = axes.flatten()

# Plot each metric
for i, column in enumerate(columns_to_plot):
    ax = axes[i]
    
    # Plot original data
    ax.plot(df['                  epoch'], df[column], label='results', color='blue', alpha=0.5)
    
    # Apply smoothing
    smooth_data = savgol_filter(df[column], window_length=21, polyorder=3)
    
    # Plot smoothed data
    ax.plot(df['                  epoch'], smooth_data, label='smooth', color='orange', linestyle='--')
    
    # Remove leading spaces from column name for title
    ax.set_title(column.strip())
    ax.set_xlabel(' ')
    ax.set_ylabel(' ')
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Only add legend to the first subplot
    if i == 0:
        ax.legend()

# Remove the unused 12th subplot
fig.delaxes(axes[-1])

# Adjust the layout and display the plot
plt.tight_layout()
plt.show()