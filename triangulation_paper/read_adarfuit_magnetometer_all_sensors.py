import serial
import keyboard  # Import the keyboard library
import re  # Import the regular expression library

# Define the list of serial ports and baud rate
serial_ports = ['COM16', 'COM18', 'COM19', 'COM20', 'COM21']  # Change these to your microcontroller's ports
baud_rate = 9600  # Change this to match your microcontroller's baud rate
values_to_read = 10  # Number of values to read from each port

try:
    for serial_port in serial_ports:
        try:
            # Open the serial port
            ser = serial.Serial(serial_port, baud_rate)
            # print(f"Connected to {serial_port} at {baud_rate} baud.")
            
            values_read = 0  # Initialize a counter for the values read
            total_values = [0.0, 0.0, 0.0]  # Initialize a list to accumulate the values
            
            # Read and accumulate data until the desired number of values is reached
            while values_read < values_to_read:
                data = ser.readline()  # Read a line of data
                match = re.search(r'\((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\)', data.decode('utf-8'))
                
                if match:
                    # Extract the three values from the regex match and convert them to floats
                    x, y, z = map(float, match.groups())
                    
                    # Accumulate the values
                    total_values[0] += x
                    total_values[1] += y
                    total_values[2] += z
                    
                    values_read += 1  # Increment the counter
                
                # Check if the "ESC" key is pressed
                if keyboard.is_pressed('esc'):
                    print("Exiting the program.")
                    exit()

            # Calculate and print the average in the (x, y, z) format with 2 decimal places
            average_x = total_values[0] / values_to_read
            average_y = total_values[1] / values_to_read
            average_z = total_values[2] / values_to_read
            
            # Use f-strings with formatting to display two decimal places
            print(f"({serial_port}): ({average_x:.2f}, {average_y:.2f}, {average_z:.2f})")

        except serial.SerialException as e:
            print(f"Error reading data from {serial_port}: {e}")
        finally:
            # Close the serial port when done reading from it
            ser.close()
            
except KeyboardInterrupt:
    print("Exiting the program.")
except serial.SerialException as e:
    print(f"Error: {e}")
