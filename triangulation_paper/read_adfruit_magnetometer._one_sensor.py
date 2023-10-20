import serial
import keyboard  # Import the keyboard library

# Define the serial port and baud rate
serial_port = 'COM20'  # Change this to your microcontroller's port
baud_rate = 9600  # Change this to match your microcontroller's baud rate

try:
    # Open the serial port
    ser = serial.Serial(serial_port, baud_rate)
    print(f"Connected to {serial_port} at {baud_rate} baud.")

    # Read and print data continuously
    while True:
        data = ser.readline()  # Read a line of data
        print(data.decode('utf-8'), end='')  # Print the data as a string (UTF-8 encoding)

        # Check if the "ESC" key is pressed
        if keyboard.is_pressed('esc'):
            print("Exiting the program.")
            break  # Exit the loop when the "ESC" key is pressed

except serial.SerialException as e:
    print(f"Error: {e}")
finally:
    # Close the serial port when done
    ser.close()
