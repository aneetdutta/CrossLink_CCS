import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Replace 'your_data.csv' with the path to your CSV file
df = pd.read_csv('data/mixzone_11.csv',index_col=0)

# Create a correlation matrix from your dataframe
corr_matrix = df.corr()

plt.figure(figsize=(10, 8))  # Optional: specify figure size

sns.heatmap(
    corr_matrix, 
   
    cmap='coolwarm',  # Choose a color scheme
    fmt='.2f'         # Format for annotation
)

plt.title('Correlation Heatmap')
plt.show()

