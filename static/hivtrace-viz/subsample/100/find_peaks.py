import pandas as pd
from scipy.signal import find_peaks, peak_prominences
import matplotlib.pyplot as plt
import numpy as np

# Read in the data
raw_data = pd.read_csv("sequence.tn93output.report.tsv", sep="\t")
threshold = 0.5
mask = raw_data['Score'] > threshold
data = raw_data[mask]



# Find peaks
peaks, _ = find_peaks(data['Score'], distance=10)

# If less than 2 peaks are found, print a message and exit
if len(peaks) < 2:
    print("Less than 2 peaks found!")
    exit()

peak_values = data['Score'].iloc[peaks]
top_peaks = peak_values.nlargest(5)

prominences = peak_prominences(data['Score'], peaks, wlen=10)[0]

# Calculate IQR
Q1 = data['Score'].quantile(0.25)
Q3 = data['Score'].quantile(0.75)
IQR = Q3 - Q1

# Define data within IQR
data_IQR = data[(data['Score'] >= Q1) & (data['Score'] <= Q3)]

# Calculate standard deviation within IQR
std_dev_IQR = np.std(data_IQR['Score'])

# Print top 2 peaks
for i, (index, value) in enumerate(top_peaks.items()):
    print(f"Peak with Score {data['Score'].loc[index]} at Threshold {data['Threshold'].loc[index]} with Prominence {prominences[i]}")


print(f"Score STD {std_dev_IQR}")
