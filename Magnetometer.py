import serial
import re
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading
from collections import deque
import time

# Define a global variable to track the plot state
plot_closed = False

# Function to handle key press events
def on_key(event):
    global plot_closed
    if event.key == '0':
        print("Closing the plot...")
        plt.close()
        plot_closed = True

# Function to read and process data
def read_and_process_data(ser, time_steps, readings_x, readings_y, readings_z, measurement_duration, time_step_seconds):
    i = 0
    duty_cycle = 0  # Initialize duty cycle to 0
    duty_cycle_increment = int(255 / (measurement_duration / time_step_seconds))  # Calculate the duty cycle increment per step
    while i * time_step_seconds <= measurement_duration and not plot_closed:
        # Send the PWM duty cycle command
        pwm_command = str(duty_cycle).encode()
        ser.write(pwm_command)
        
        line = ser.readline()
        if line:
            string = line.decode().strip()
            match = re.match(r'X: (\S+) uTesla\s+Y: (\S+) uTesla\s+Z: (\S+) uTesla', string)
            if match:
                x, y, z = map(float, match.groups())
                print(f"X: {x}, Y: {y}, Z: {z}")
                time_in_minutes = i * time_step_seconds / 60.0
                time_steps.append(time_in_minutes)
                readings_x.append(x)
                readings_y.append(y)
                readings_z.append(z)
                i += 1

                # Increment the duty cycle for the next step
                duty_cycle += duty_cycle_increment
                duty_cycle = min(255, duty_cycle)  # Ensure duty cycle doesn't exceed 255

# Make sure the 'COM#' is set according to the Windows Device Manager
maxlenNumber = 300
with serial.Serial('COM12', 115200, timeout=None) as ser:
    time.sleep(2)

    # Initialize empty lists to store time steps and corresponding readings
    time_steps = deque(maxlen=maxlenNumber)  # Adjust the maximum number of data points to store
    readings_x = deque(maxlen=maxlenNumber)
    readings_y = deque(maxlen=maxlenNumber)
    readings_z = deque(maxlen=maxlenNumber)

    # Create a figure and axis for plotting
    fig, ax = plt.subplots(figsize=(16, 12)) 
    ax.set_xlabel("Time (minutes)")
    ax.set_ylabel("Magnetic Field ($\mu$T)")
    line_x, = ax.plot([], [], 'b-', label='Bx')
    line_y, = ax.plot([], [], 'g-', label='By')
    line_z, = ax.plot([], [], 'r-', label='Bz')
    ax.legend()

    # Define the time step in seconds
    time_step_seconds = 0.05

    # Set the measurement duration (in seconds)
    measurement_duration = 60*100

    # Start a separate thread to read and process data
    data_thread = threading.Thread(target=read_and_process_data, args=(ser, time_steps, readings_x, readings_y, readings_z, measurement_duration, time_step_seconds))
    data_thread.start()

    # Connect the key press event handler
    fig.canvas.mpl_connect('key_press_event', on_key)

    # Function to update the plot
    def update(i):
        line_x.set_data(time_steps, readings_x)
        line_y.set_data(time_steps, readings_y)
        line_z.set_data(time_steps, readings_z)
        ax.relim()
        ax.autoscale_view()

    ani = FuncAnimation(fig, update, frames=None, interval=time_step_seconds * 500)  # interval is in milliseconds for 1-minute steps

    plt.show()

    # Wait for the data thread to finish
    data_thread.join()
