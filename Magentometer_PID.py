import serial
import re
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading
import time
import nidaqmx
import simple_pid

# Constants for PID control
Kp = 0.01  # Proportional gain
Ki = 0.5  # Integral gain
Kd = 0  # Derivative gain (set to 0 for now)

# Create a PID controller
pid = simple_pid.PID(Kp, Ki, Kd)

# Variables for PID control
desired_Bz = 10  # Desired Bz value
prev_time = [time.time()]  # List to store previous time (workaround for nonlocal)

# Function to handle key press events
def on_key(event):
    if event.key == '0':
        print("Closing the plot and stopping the program...")
        plt.close()
        stop_program[0] = True

# Function to read and process data
def read_and_process_data(ser, time_steps, readings_x, readings_y, readings_z, measurement_duration, time_step_seconds, stop_program):
    i = 0
    while i * time_step_seconds <= measurement_duration and not stop_program[0]:
        # Send the PWM duty cycle command
        pwm_command = str(i).encode()
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
            except UnicodeDecodeError:
                print("Error decoding data:", line)

# Make sure the 'COM#' is set according to the Windows Device Manager
maxlenNumber = 300
with serial.Serial('COM12', 115200, timeout=None) as ser:
    time.sleep(2)

    # Initialize empty lists to store time steps and corresponding readings
    time_steps = []
    readings_x = []
    readings_y = []
    readings_z = []

    # Create a figure and axis for plotting
    fig, ax = plt.subplots(figsize=(16, 12)) 
    ax.set_xlabel("Time (minutes)", fontsize=20)
    ax.set_ylabel("Magnetic Field ($\mu$T)", fontsize=20)
    ax.set_ylim(-60, 60)  # Set the y-axis limits
    line_x, = ax.plot([], [], 'b-', label='Bx')
    line_y, = ax.plot([], [], 'g-', label='By')
    line_z, = ax.plot([], [], 'r-', label='Bz')
    legend = ax.legend(fontsize=20)

    # Create a task for analog output
    with nidaqmx.Task() as task_ao:
        # Add an analog output channel for ao0
        task_ao.ao_channels.add_ao_voltage_chan("Dev2/ao0")
        
        stop_program = [False]

        try:
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
                current_time = time.time()
                elapsed_time = current_time - prev_time[0]
                prev_time[0] = current_time

                # Calculate the error (difference between desired and current Bz)
                current_Bz = readings_z[-1] if readings_z else 0
                error = desired_Bz - current_Bz

                # Update the PID setpoint and compute the PID output
                pid.setpoint = desired_Bz
                pid_output = pid(current_Bz)

                # Update the analog output voltage
                task_ao.write(pid_output / 1000.0)  # Convert to V

                # Update the plot
                line_x.set_data(time_steps, readings_x)
                line_y.set_data(time_steps, readings_y)
                line_z.set_data(time_steps, readings_z)
                ax.relim()
                ax.autoscale_view()

            expected_data_points = measurement_duration / time_step_seconds
            num_frames = int(expected_data_points)
            ani = FuncAnimation(fig, update, frames=num_frames, interval=time_step_seconds * 1000)

            plt.show()

        except KeyboardInterrupt:
            stop_program[0] = True  # Exit the program gracefully

    # Wait for the data thread to finish
    data_thread.join()
