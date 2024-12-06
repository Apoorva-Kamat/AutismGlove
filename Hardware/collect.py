import serial
import time

# Replace 'COM3' with your Arduino's port. Adjust the baud rate if necessary.
ser = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)  # Wait for the serial connection to initialize

# Open a file to save the data
file = open("sensor_data_2min.csv", "w")
file.write("Flex1,Flex2,Flex3,Flex4,Flex5,Pressure\n")  # CSV header

start_time = time.time()  # Record the start time
duration = 10  # Duration to collect data in seconds

try:
    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time
        
        # Stop collecting data after the specified duration
        if elapsed_time > duration:
            print("10 seconds elapsed. Stopping data collection.")
            break

        if ser.in_waiting > 0:
            # Read a line of data from the serial port
            data = ser.readline().decode('utf-8').strip()
            print(f"Received: {data}")  # Print received data for debugging
            
            # Split the data into two parts: Flex readings and Pressure
            if 'Flex:' in data and 'Pressure:' in data:
                flex_data, pressure_data = data.split(' Pressure:')
                flex_values = flex_data.replace('Flex:', '').strip().split(',')
                pressure_value = pressure_data.strip()
                
                # Check if we got exactly 5 flex sensor readings and 1 pressure value
                if len(flex_values) == 5 and pressure_value.isdigit():
                    sensor_values = flex_values + [pressure_value]
                    print(f"Writing to file: {sensor_values}")  # Debug the values before writing to file
                    # Save the data to the CSV file
                    file.write(",".join(sensor_values) + "\n")
                    file.flush()  # Ensure data is written immediately
                else:
                    print("Invalid data format for Flex sensors or Pressure!")
            else:
                print("Invalid data format!")
        else:
            print("Collecting Data.")

except KeyboardInterrupt:
    print("Data collection manually stopped.")
finally:
    ser.close()
    file.close()
    print("Serial connection closed, file saved as 'sensor_data_1min.csv'.")
