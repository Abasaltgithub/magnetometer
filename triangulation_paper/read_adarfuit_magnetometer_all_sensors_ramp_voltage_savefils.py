import random
import serial
import msvcrt
import re
import nidaqmx
import csv
import datetime  # Import the datetime module

def read_and_calculate_average(serial_port, baud_rate, values_to_read, csv_writer, voltage, task_do):
    try:
        ser = serial.Serial(serial_port, baud_rate)
        total_values = [0.0, 0.0, 0.0]

        for _ in range(values_to_read):
            data = ser.readline()
            match = re.search(r'\((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\)', data.decode('utf-8'))

            if match:
                x, y, z = map(float, match.groups())
                total_values[0] += x
                total_values[1] += y
                total_values[2] += z

        average_x = total_values[0] / values_to_read
        average_y = total_values[1] / values_to_read
        average_z = total_values[2] / values_to_read

        # Format the values with two digits after the decimal point
        formatted_average_x = round(average_x, 2)
        formatted_average_y = round(average_y, 2)
        formatted_average_z = round(average_z, 2)

        # Print the values
        print(f"({serial_port}): ({formatted_average_x:.2f}, {formatted_average_y:.2f}, {formatted_average_z:.2f})")

        # Write the values to the CSV file
        csv_writer.writerow([serial_port, round(voltage, 4), formatted_average_x, formatted_average_y, formatted_average_z])

    except serial.SerialException as e:
        print(f"Error reading data from {serial_port}: {e}")
    finally:
        ser.close()

# Get the current date in YYYY-MM-DD format
current_date = datetime.datetime.now().strftime('%Y-%m-%d')

# Specify the path to save the CSV file using the current date
csv_file_path = rf'C:\Users\QuBiT Data PC\Desktop\Abasalt\Magnetometer\triangulation_paper\{current_date}_output.csv'

# Create a CSV file to store the data
with open(csv_file_path, mode='w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['Serial Port', 'Voltage (V)', 'Average X', 'Average Y', 'Average Z'])  # Write header row
    csv_writer.writerow([])

    # Create a task for analog output
    with nidaqmx.Task() as task_ao:
        task_ao.ao_channels.add_ao_voltage_chan("Dev2/ao0")

        # Create a task for digital output
        with nidaqmx.Task() as task_do:
            task_do.do_channels.add_do_chan("Dev2/port1/line4")
            task_do.do_channels.add_do_chan("Dev2/port1/line5")

            serial_ports = ['COM16', 'COM18', 'COM19', 'COM20', 'COM21']
            baud_rate = 9600
            values_to_read = 10

            try:
                num_measurements = 1000
                for _ in range(num_measurements):
                    voltage = random.uniform(0, 0.7)
                    task_ao.write(voltage)
                    print(f"Set voltage = {voltage:.2f} V")

                    # Set digital output channels randomly to True or False
                    task_do.write([random.choice([True, False]), random.choice([True, False])])

                    for serial_port in serial_ports:
                        read_and_calculate_average(serial_port, baud_rate, values_to_read, csv_writer, voltage, task_do)

                    # Check for 'esc' key press
                    if msvcrt.kbhit() and msvcrt.getch() == b'\x1b':
                        print("Exiting the program.")
                        break

            except KeyboardInterrupt:
                print("Exiting the program.")
            finally:
                # When the program exits, make sure to set voltage to zero and digital outs to False
                task_ao.write(0)  # Set voltage to zero
                task_do.write([False, False])  # Set digital outputs to False
