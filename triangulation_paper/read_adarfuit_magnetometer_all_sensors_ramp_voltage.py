import random
import serial
import msvcrt
import re
import nidaqmx

def read_and_calculate_average(serial_port, baud_rate, values_to_read):
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

        print(f"({serial_port}): ({average_x:.2f}, {average_y:.2f}, {average_z:.2f})")

    except serial.SerialException as e:
        print(f"Error reading data from {serial_port}: {e}")
    finally:
        ser.close()

# Create a task for analog output
with nidaqmx.Task() as task_ao:
    task_ao.ao_channels.add_ao_voltage_chan("Dev2/ao0")
    
    serial_ports = ['COM16', 'COM18', 'COM19', 'COM20', 'COM21']
    baud_rate = 9600
    values_to_read = 10

    try:
        for _ in range(5):
            voltage = random.uniform(0, 0.3)
            task_ao.write(voltage)
            print(f"Setting voltage to {voltage:.2f} V on analog output")

            for serial_port in serial_ports:
                read_and_calculate_average(serial_port, baud_rate, values_to_read)

            # Check for 'esc' key press
            if msvcrt.kbhit() and msvcrt.getch() == b'\x1b':
                print("Exiting the program.")
                break

    except KeyboardInterrupt:
        print("Exiting the program.")
