import nidaqmx
import matplotlib.pyplot as plt
import numpy as np
import time
import math

# Function to update the analog output voltage
def update_analog_output(task_ao, voltage):
    task_ao.write(voltage)

# Create a task for analog input
with nidaqmx.Task() as task_ai:
    # Add analog input channels
    task_ai.ai_channels.add_ai_voltage_chan("Dev2/ai0")

    # Create lists to store time and voltage data for AI0
    times_ai0 = []
    voltages_ai0 = []

    # Set the number of points to display on the plot
    num_points = 500  # Display the last 50 points

    # Create a figure and axis for plotting
    fig, ax = plt.subplots()
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Voltage (V)")
    line_ai0, = ax.plot([], [], lw=2, label="Analog INPUT 0")  # Line for AI0 data
    ax.legend()

    def update_plot():
        # Update the x and y data of the plot for AI0
        line_ai0.set_data(times_ai0[-num_points:], voltages_ai0[-num_points:])
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
        # Add an analog output channel for ao0
        task_ao.ao_channels.add_ao_voltage_chan("Dev2/ao0")

        try:
            oscillation_period = 5.0  # Oscillation period in seconds
            start_time = time.time()

            while not stop_program[0]:
                current_time = time.time()
                elapsed_time = current_time - start_time

                # Calculate the desired voltage using a sine wave
                amplitude = 100.0  # Amplitude in mV
                offset = 200.0  # Offset in mV
                frequency = 1.0 / oscillation_period  # Frequency in Hz
                desired_voltage = amplitude * math.sin(2 * math.pi * frequency * elapsed_time) + offset

                # Update the analog output voltage
                update_analog_output(task_ao, desired_voltage / 1000.0)  # Convert to V

                # Read a single sample from the analog input channel
                data_ai0 = task_ai.read()

                # Append the time and voltage data for AI0
                times_ai0.append(current_time)
                voltages_ai0.append(data_ai0)  # Append the input voltage (analog input AI0)

                # Update the plot
                update_plot()

                # Pause for 0.05 seconds (faster reading)
                time.sleep(0.05)

        except KeyboardInterrupt:
            pass  # Ignore KeyboardInterrupt here

    # Stop the analog input and output tasks when exiting the loop
    task_ai.stop()
    task_ao.stop()
    plt.ioff()
    plt.close()
