# Loading the dataset and performing curve fitting and KS test for combined "ble", "wifi", and "lte" keys
import json
import numpy as np
import pandas as pd
from scipy.stats import kstest, expon
from scipy.optimize import curve_fit

# Load the data
with open('/home/aneet_wisec/usenix_2025/path-leakage/real_world/ti.json', 'r') as file:
    data_combined = json.load(file)

# Combine all keys containing "ble", "wifi", and "lte"
combined_data = []
for key in data_combined.keys():
    if any(substring in key for substring in ["ble", "wifi", "lte"]):
        combined_data.extend(data_combined[key])

combined_data = np.array(combined_data)

# Exponential PDF function for fitting
def exp_pdf(x, lambd):
    return lambd * np.exp(-lambd * x)

# Prepare histogram data
hist, bin_edges = np.histogram(combined_data, bins='auto', density=True)
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

# Fit exponential distribution using curve_fit
popt, _ = curve_fit(exp_pdf, bin_centers, hist, p0=[1/np.mean(combined_data)])
optimized_lambda = popt[0]
optimized_scale = 1 / optimized_lambda

# Perform Kolmogorov-Smirnov test
ks_stat, p_value = kstest(combined_data, 'expon', args=(0, optimized_scale))

# Output results
results_combined = {
    'Optimized Scale': optimized_scale,
    'KS Statistic': ks_stat,
    'p-value': p_value
}

print(results_combined)

