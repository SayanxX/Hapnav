import socket
import math
import time
import matplotlib.pyplot as plt
import numpy as np

rest_time = 0.3
angle_calibration = -25
threshold_acceleration = 4
step_distance = 1.5
server_ip = "192.168.144.64"
port = 2055

initial_disx = -4
initial_disy = -4

axis_range = 7

def extract_numerical_values(data_str):
    values = []
    for token in data_str.split(','):
        try:
            value = float(token)
            values.append(value)
        except ValueError:
            pass
    return tuple(values)

# Define the matrix of 0s and 1s representing the background
background_matrix = np.array([[0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,1,1,1,0,1,1,0,0,0,1,0,0],
[1,1,0,0,0,1,1,1,1,0,0,1,1,0],
[1,1,0,0,0,1,1,1,1,1,0,0,0,0],
[1,1,1,1,1,1,1,1,1,1,0,0,0,0],
[1,1,1,1,1,1,1,1,1,1,0,0,0,0],
[0,0,0,0,0,1,1,1,1,1,1,1,0,0],
[0,0,0,0,0,1,1,1,1,1,1,1,1,0],
[1,0,0,0,0,0,1,1,1,1,0,0,1,0],
[1,1,1,1,1,1,1,0,1,1,0,0,1,0],
[1,1,1,1,1,1,1,1,1,0,0,0,1,0],
[1,1,1,1,1,1,1,1,1,1,0,0,1,0],
[1,1,1,1,1,1,1,0,0,0,0,0,0,0],
[1,1,1,0,0,1,1,0,0,0,0,0,0,0]])

# Create a TCP/IP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = (server_ip, port)  # Update with your server IP and port
print('Starting up on {} port {}'.format(*server_address))
server_socket.bind(server_address)

# Listen for incoming connections
server_socket.listen(1)

# Initialize empty lists to store coordinates
disx_list = []
disy_list = []

# Plotting
plt.figure()
plt.xlabel('East')
plt.ylabel('North')
plt.xlim(-axis_range, axis_range)
plt.ylim(-axis_range, axis_range)
plt.grid(False)  # Turn off grid lines

# Initialize plot line object
line, = plt.plot([], [], 'r-', linewidth=1)

# Plot background squares based on the background matrix
plt.imshow(background_matrix, cmap='gray', extent=[-axis_range, axis_range, -axis_range, axis_range])

try:
    while True:
        # Wait for a connection
        print('Waiting for a connection...')
        connection, client_address = server_socket.accept()

        try:
            print('Connection from', client_address)
            step_detected = False

            while True:
                data = connection.recv(1024)
                if data:
                    # Decode received data
                    try:
                        data_str = data.decode('utf-8')
                    except UnicodeDecodeError:
                        continue  # Skip processing this data and move to the next iteration
                    
                    # Extract numerical values from received data
                    values = extract_numerical_values(data_str)
                    
                    # Assuming 6 values are received (3 from accelerometer, 3 from orientation)
                    if len(values) == 6:
                        # Extract acceleration values
                        accel_x, accel_y, accel_z = values[:3]

                        # Calculate magnitude of acceleration vector
                        accel_magnitude = math.sqrt(accel_x ** 2 + accel_y ** 2 + accel_z ** 2)

                        # Print step if magnitude is above threshold
                        if accel_magnitude > threshold_acceleration:
                            # Check if a step has already been detected
                            if not step_detected:
                                step_detected = True

                                # Extract angle value
                                angle = int(values[3])

                                # Calculate new coordinates with calibration
                                disx = initial_disx + step_distance * math.sin(math.radians(angle + angle_calibration))
                                disy = initial_disy + step_distance * math.cos(math.radians(angle + angle_calibration))

                                # Update initial_disx and initial_disy
                                initial_disx = disx
                                initial_disy = disy

                                # Append new coordinates to the lists
                                disx_list.append(disx)
                                disy_list.append(disy)

                                # Update plot line with the updated lists
                                line.set_xdata(disx_list)
                                line.set_ydata(disy_list)
                                plt.draw()
                                plt.pause(0.1)  # Pause to update the plot

                                # Introduce a delay of rest_time seconds
                                time.sleep(rest_time)

                        else:
                            # Reset the step_detected flag if magnitude is below threshold
                            step_detected = False

                else:
                    print('No more data from', client_address)
                    break

        finally:
            # Clean up the connection
            connection.close()

except KeyboardInterrupt:
    server_socket.close()
    plt.close()