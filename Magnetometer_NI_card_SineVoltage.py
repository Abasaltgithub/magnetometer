import serial
import re
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading
from collections import deque
import time
import nidaqmx
import numpy as np
import math

# Function to handle key press events
def on_key(event):
    if event.key == '0':
        print("Closing the plot and stopping the program...")
        plt.close()
        stop_program[0] = True

# Function to update the analog output voltage
def update_analog_output(task_ao, voltage):
    task_ao.write(voltage)

# Function to read and process data
def read_and_process_data(ser, time_steps, readings_x, readings_y, readings_z, measurement_duration, time_step_seconds, stop_program):
    i = 0
    duty_cycle = 0  # Initialize duty cycle to 0
    duty_cycle_increment = int(255 / (measurement_duration / time_step_seconds))  # Calculate the duty cycle increment per step
    while i * time_step_seconds <= measurement_duration and not stop_program[0]:
        # Send the PWM duty cycle command
        pwm_command = str(duty_cycle).encode()
        ser.write(pwm_command)
        
        line = ser.readline()
        if line:
            try:
                # Decode the line as UTF-8 and strip whitespace
                decoded_line = line.decode('utf-8').strip()
                match = re.match(r'X: (\S+) uTesla\s+Y: (\S+) uTesla\s+Z: (\S+) uTesla', decoded_line)
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
            except UnicodeDecodeError:
                print("Error decoding data:", line)

# Rest of your code remains unchanged


# Make sure the 'COM#' is set according to the Windows Device Manager
maxlenNumber = 300
with serial.Serial('COM11', 115200, timeout=None) as ser:
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

    # Create a task for analog output
    with nidaqmx.Task() as task_ao:
        # Add an analog output channel for ao0
        task_ao.ao_channels.add_ao_voltage_chan("Dev2/ao0")
        
        stop_program = [False]

        try:
            oscillation_period = 5.0  # Oscillation period in seconds
            start_time = time.time()

            # Define the time step in seconds
            time_step_seconds = 0.05

            # Set the measurement duration (in seconds)
            measurement_duration = 60 * 100

            # Start a separate thread to read and process data
            data_thread = threading.Thread(target=read_and_process_data, args=(ser, time_steps, readings_x, readings_y, readings_z, measurement_duration, time_step_seconds, stop_program))
            data_thread.start()

            # Connect the key press event handler
            fig.canvas.mpl_connect('key_press_event', on_key)

            # Function to update the plot
            def update(i):
                # Calculate the desired voltage using a sine wave
                current_time = time.time()
                elapsed_time = current_time - start_time
                amplitude = 100.0  # Amplitude in mV
                offset = 100.0  # Offset in mV
                frequency = 0.5 / oscillation_period  # Frequency in Hz
                desired_voltage = amplitude * math.sin(2 * math.pi * frequency * elapsed_time) + offset

                # Update the analog output voltage
                update_analog_output(task_ao, desired_voltage / 1000.0)  # Convert to V

                # Update the plot
                line_x.set_data(time_steps, readings_x)
                line_y.set_data(time_steps, readings_y)
                line_z.set_data(time_steps, readings_z)
                ax.relim()
                ax.autoscale_view()

            ani = FuncAnimation(fig, update, frames=None, interval=time_step_seconds * 500)  # interval is in milliseconds for 1-minute steps

            plt.show()

        except KeyboardInterrupt:
            stop_program[0] = True  # Exit the program gracefully

    # Wait for the data thread to finish
    data_thread.join()
