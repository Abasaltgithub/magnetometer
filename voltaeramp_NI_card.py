import nidaqmx
import time
import math

# Function to update the analog output voltage
def update_analog_output(task_ao, voltage):
    task_ao.write(voltage)

# Create a task for analog output
with nidaqmx.Task() as task_ao:
    # Add an analog output channel for ao0
    task_ao.ao_channels.add_ao_voltage_chan("Dev2/ao0")
    stop_program = [False] 

    try:
        oscillation_period = 5.0  # Oscillation period in seconds
        start_time = time.time()

        while not stop_program[0]:
            current_time = time.time()
            elapsed_time = current_time - start_time

            # Calculate the desired voltage using a sine wave
            amplitude = 100.0  # Amplitude in mV
            offset = 200.0  # Offset in mV
            frequency = 0.5 / oscillation_period  # Frequency in Hz
            desired_voltage = amplitude * math.sin(2 * math.pi * frequency * elapsed_time) + offset

            # Update the analog output voltage
            update_analog_output(task_ao, desired_voltage / 1000.0)  # Convert to V
            time.sleep(0.05)

    except KeyboardInterrupt:
        pass  # Ignore KeyboardInterrupt here
