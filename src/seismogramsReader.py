import numpy as np
import matplotlib.pyplot as plt
import os

# Get the directory of the current script (src/)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Path to the sibling 'output' folder
grm_folder = os.path.join(current_dir, '..', 'output')

# Ask the user for just the filename
print("\nWelcome to the Seismogram Reader!\n")
print("Please provide the filename of the .grm file you want to read.")
print("Make sure the file is located in the '../output/' directory relative to this script.\n")
filename = input("Enter the .grm filename: ").strip()

# Full path to the .grm file
filepath = os.path.join(grm_folder, filename)

# Check if the file exists
if not os.path.isfile(filepath):
    print(f"Error: File '{filename}' not found in '../output/'.")
    exit(1)

# Read the file
try:
    with open(filepath, 'rb') as f:
        data = np.fromfile(f, dtype=np.float32)
except Exception as e:
    print(f"Failed to read file: {e}")
    exit(1)

# Show first 10 values
print("First 10 values from the file:")
print(data[:10])

# Plot
plt.figure(figsize=(12, 5))
plt.plot(data, color='midnightblue', linewidth=1)
plt.title(f"Seismogram: {filename}", fontsize=14, fontweight='bold')
plt.xlabel("Sample Index (Time Steps)", fontsize=12)
plt.ylabel("Amplitude (Ground Motion)", fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()
