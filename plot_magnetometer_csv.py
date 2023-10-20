import pandas as pd
import matplotlib.pyplot as plt

# Replace this with your actual CSV file path
csv_filename = "C:/Users/QuBiT Data PC/Desktop/Abasalt/Magnetometer/MF.csv"

# Read the CSV file into a pandas DataFrame
df = pd.read_csv(csv_filename)

# Extract columns
time_minutes = df['Time (minutes)']
Bx = df['Bx']
By = df['By']
Bz = df['Bz']

# Create the plot
plt.figure(figsize=(12, 6))
plt.plot(time_minutes, Bx, label='Bx')
plt.plot(time_minutes, By, label='By')
plt.plot(time_minutes, Bz, label='Bz', color='purple')

# Add labels and legend
plt.xlabel('Time (min)')
plt.ylabel('Magnetic Field ($\mu$T)')
plt.legend()

# Add text annotation
text_x = 0.86  # Time = 1 min
text_y = -20  # Magnetic Field = -20 uT
plt.text(text_x, text_y, '@ Time = 0.75 min I intentionally applied external magnetic field', fontsize=10, color='black', verticalalignment='bottom')

# Add dashed horizontal line at MF = 20 uT
plt.axhline(y=10, color='purple', linestyle='--', label='Bz set value = 10 $\mu$T')




# Show the plot
# plt.grid(True)
plt.title('Active Compensation Magnetic Field')
plt.legend()

plt.savefig('MF_compensation.png', dpi=1000, bbox_inches='tight')
plt.show()
