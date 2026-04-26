import json
import pandas as pd
import numpy as np
from scipy.stats import expon
import matplotlib.pyplot as plt

# Load JSON data
with open('/home/aneet_wisec/usenix_2025/path-leakage/real_world/ti.json', 'r') as file:
    data = json.load(file)

# Extract keys from JSON
keys = list(data.keys())

# Function to perform exponential curve fitting and calculate scale (1/rate) parameter
def fit_exponential(data):
    # Fit the data to an exponential distribution
    loc, scale = expon.fit(data, floc=0)  # Force location parameter to 0 for exponential
    
    return scale

# Perform fitting for each key and store results
fitting_results = {}
for key in keys:
    scale = fit_exponential(data[key])
    fitting_results[key] = {
        'scale_parameter': scale,
        
    }

# Convert results to DataFrame for better visualization
df_results = pd.DataFrame(fitting_results).T.reset_index().rename(columns={'index': 'key'})

#import ace_tools as tools; tools.display_dataframe_to_user(name="Exponential Curve Fitting Results", dataframe=df_results)

df_results.to_csv('/home/aneet_wisec/usenix_2025/path-leakage/real_world/scale.csv')

# Generate separate plots for each key
# Define directory to save plots
output_dir = '/home/aneet_wisec/usenix_2025/path-leakage/real_world/'
import os
plt.figure(figsize=(3.3, 2.1))
# Create directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Generate and save separate plots for each key
plot_paths = []
for key in keys:
    #plt.figure(figsize=(10, 6))
    plt.figure(figsize=(3.3, 2.1))
    # Get data and fitted scale parameter
    data_points = data[key]
    scale_param = fitting_results[key]['scale_parameter']
    
    # Histogram of the data
    plt.hist(data_points, bins=30, density=True, alpha=0.6, color='g', label='Histogram of Data')

    # Fitted exponential curve
    x = np.linspace(0, max(data_points), 1000)
    y = expon.pdf(x, scale=scale_param)
    plt.plot(x, y, 'r-', lw=2, label=f'Exponential fit\n(scale={scale_param:.4f})')
    
    plt.yticks(fontsize=8)

    plt.xlabel('Transmission Interval', fontsize=8)
    plt.ylabel('Density', fontsize=8)
    plt.legend(loc='lower right', fontsize=5)
    plt.grid(True,linewidth=0.2)

    # Plot labels and titles
    plt.title(f'Exponential Curve Fit for "{key}"',fontsize=5)
    #plt.xlabel('Data')
    #plt.ylabel('Density')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    # Save plot
    plot_path = os.path.join(output_dir, f'{key}_exp_curve_fit.pdf')
    plt.savefig(plot_path,dpi=600, bbox_inches='tight')
    plt.close()
    plot_paths.append(plot_path)

#plot_paths


