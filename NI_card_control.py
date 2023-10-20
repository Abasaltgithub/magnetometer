# I am reading analog input 0,
# scaling it by multiplying it by 2, and then
# using the scaled value as the input for analog input 1

import nidaqmx
import matplotlib.pyplot as plt
import numpy as np
import time
import threading

# Function to update the analog output voltage
def update_analog_output(task_ao, voltage):
    task_ao.write(voltage)

# Create a task for analog input
with nidaqmx.Task() as task_ai:
    # Add analog input channels
    task_ai.ai_channels.add_ai_voltage_chan("Dev2/ai0")
    task_ai.ai_channels.add_ai_voltage_chan("Dev2/ai1")  # Add ai1 channel

    # Create lists to store time and voltage data for both channels
    times_ai0 = []
    voltages_ai0 = []
    times_ai1 = []
    voltages_ai1 = []

    # Set the desired sampling rate (samples per second)
    sampling_rate = 20  # 20 samples per second

    # Set the number of points to display on the plot
    num_points = 500  # Display the last 50 points

    # Create a figure and axis for plotting
    fig, ax = plt.subplots()
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Voltage (V)")
    line_ai0, = ax.plot([], [], lw=2, label="AnLOG INPUT 0")  # Line for AI0 data
    line_ai1, = ax.plot([], [], lw=2, label="ANALOG INPUT 1")  # Line for AI1 data
    ax.legend()

    def update_plot():
        # Update the x and y data of the plot for both channels
        line_ai0.set_data(times_ai0[-num_points:], voltages_ai0[-num_points:])
        line_ai1.set_data(times_ai1[-num_points:], voltages_ai1[-num_points:])
        ax.relim()
        ax.autoscale_view()
        plt.pause(0.01)  # Pause briefly to update the plot

    plt.ion()  # Turn on interactive mode for plotting
    plt.show()

    stop_program = [False]  # List to store the stop_program flag

    def close_plot_and_stop(event):
        stop_program[0] = True
        plt.close()

    # Register a callback for the '0' key
    fig.canvas.mpl_connect('key_press_event', close_plot_and_stop)

    # Create a task for analog output
    with nidaqmx.Task() as task_ao:
        # Add an analog output channel
        task_ao.ao_channels.add_ao_voltage_chan("Dev2/ao0")

        try:
            while not stop_program[0]:
                # Read a single sample from the analog input channels
                data_ai0, data_ai1 = task_ai.read()  # Read from both channels

                # Multiply the input voltage (data) by a scaling factor
                scaling_factor = 2.0  # Adjust as needed
                output_voltage = data_ai0 * scaling_factor

                # Update the analog output voltage
                update_analog_output(task_ao, output_voltage)

                # Get the current time
                current_time = time.time()

                # Append the time and voltage data for both channels
                times_ai0.append(current_time)
                voltages_ai0.append(data_ai0)  # Append the input voltage (analog input AI0)
                times_ai1.append(current_time)
                voltages_ai1.append(data_ai1)  # Append the input voltage (analog input AI1)

                # Update the plot
                update_plot()

                # Pause for 0.05 seconds (faster reading)
                time.sleep(0.05)

        except KeyboardInterrupt:
            pass  # Ignore KeyboardInterrupt here

    # Stop both the analog input and output tasks when exiting the loop
    task_ai.stop()
    task_ao.stop()
    plt.ioff()
    plt.close()
