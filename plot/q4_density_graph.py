import os
import glob
import numpy as np
import pandas as pd
import sys
import matplotlib.pyplot as plt
marker_interval = 50
def compute_ecdf(data):
    """
    Compute ECDF values for the given 1D data array.
    Returns sorted data and corresponding ECDF values.
    """
    # Sort the data
    x = np.sort(data)
    # Calculate ECDF values: proportion of data <= each x
    n = x.size
    ecdf = np.arange(1, n + 1) / n
    return x, ecdf

# Path to directory containing CSV files (update as needed)
csv_directory_mix = '/path-leakage/plot/q4_mix'
csv_directory_score = '/path-leakage/plot/q4_density_data'
# Pattern to match CSV files
csv_pattern = os.path.join(csv_directory_score, '*.csv')

# List of CSV files to process
csv_files = glob.glob(csv_pattern)

# Initialize a plot
#plt.figure(figsize=(10, 6))
plt.figure(figsize=(2.2,1.5))
# print(sorted(csv_files), len(csv_files))
# sys.exit()

# Loop over each CSV file, compute ECDF, and plot using ECDF values as x-axis
for csv_file in sorted(csv_files):
    # Read CSV file into a DataFrame. 
    # Adjust 'column_name' to the actual column if needed.
    df = pd.read_csv(csv_file)
    
    # Assume the column of interest is the first column. 
    # Change 'df.iloc[:, 0]' if a different column is required.
    data = df['privacy_score'].dropna().values 
    
    # Compute ECDF for the data
    sorted_data, ecdf_values = compute_ecdf(data)
    
    # Use ECDF values as x-axis (percentile) and original sorted data as y-axis
    # This plots the original values against their percentile rank.
    s=os.path.basename(csv_file)
    cleaned_str = s.split("_")
    print(cleaned_str)
    num_users=cleaned_str[5]
    if cleaned_str[6]=='sumo':
        dataset='SuMO'
    else:
        dataset='Synthetic'
        
    print(dataset)
    label_name=str(num_users)+" "+str(dataset)
    if dataset=='SuMO' and num_users=='512':
        plt.plot(ecdf_values, sorted_data, label=label_name,alpha=0.6, linewidth=1,color="#000000", marker='*', markevery=marker_interval,markersize=2)
    if dataset=='SuMO' and num_users=='1024':
        plt.plot(ecdf_values, sorted_data, label=label_name,alpha=0.6, linewidth=1,color="#81b29a", marker='v', markevery=marker_interval,markersize=2)
    if dataset=='SuMO' and num_users=='1536':
        plt.plot(ecdf_values, sorted_data, label=label_name,alpha=0.6, linewidth=1,color="#e07a5f", marker='x', markevery=marker_interval,markersize=2)
    if dataset=='Synthetic' and num_users=='512':
        plt.plot(ecdf_values, sorted_data, label=label_name,alpha=0.6, linestyle='dotted', linewidth=1,color="#000000", marker='D', markevery=marker_interval,markersize=2)
    if dataset=='Synthetic' and num_users=='1024':
        plt.plot(ecdf_values, sorted_data, label=label_name,alpha=0.6, linestyle='dotted', linewidth=1,color="#81b29a", marker='^', markevery=marker_interval,markersize=2)
    if dataset=='Synthetic' and num_users=='1536':
        plt.plot(ecdf_values, sorted_data, label=label_name,alpha=0.6, linestyle='dotted', linewidth=1,color="#e07a5f", marker='o', markevery=marker_interval,markersize=2)
    


#xticks_vals = np.linspace(0, 1, 11)  # [0.0, 0.1, 0.2, ... 1.0]
xticks_vals = [0.0,0.2,0.4,0.6,0.8,1.0]
# Format them as percentages
xticks_labels = [f"{int(x * 100)}%" for x in xticks_vals]

plt.xticks(xticks_vals, xticks_labels, fontsize=8)
plt.yticks(fontsize=7)
plt.ylim(0,None)
#xticks_vals = [0, 10, 20, 30, 40, 50, 60,70,80,90,100]

# You can manually format and set them:
#plt.xticks(xticks_vals, [f"{val}%" for val in xticks_vals],fontsize=22)
#plt.xticks(xticks, fontsize=22)
#plt.yticks(fontsize=22)
# Customize the plot
#plt.title('ECDF with Percentile-Normalized X-axis')
plt.xlabel('Percentage of Users',fontsize=7)
plt.ylabel('Privacy Leakage',fontsize=7)
plt.legend(loc='lower right',fontsize=5)
plt.grid(True,linewidth=0.2)
plt.rc('savefig', bbox='tight')
plt.rc('savefig', pad_inches=0.02) # 0 and 0.01 crop the frame/axis labels


#plt.yscale('log')
# Show the plot
plt.savefig(f'output/images/privacy_leakage_q4_density.pdf', dpi=600, bbox_inches='tight')
plt.show()
plt.show()

