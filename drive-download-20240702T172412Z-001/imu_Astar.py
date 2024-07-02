import socket
import math
import time
import matplotlib.pyplot as plt
import numpy as np
import re  # Import the re module for regular expressions


# Define global variables and constants
rest_time = 0
angle_calibration = -25
threshold_acceleration = 4
step_distance = 1
server_ip = "192.168.80.64"
port = 2055

initial_disx = 4
initial_disy = 5

final_disx = 1
final_disy = 12

negative_x_axis_range = 0
positive_x_axis_range = 14
negative_y_axis_range = 13
positive_y_axis_range = 0

# Define background matrix and plot settings
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
                              [1,1,1,1,1,1,1,0,0,0,0,0,0,0]])
plt.figure()
plt.xlabel('East')
plt.ylabel('North')
plt.xlim(negative_x_axis_range, positive_x_axis_range)
plt.ylim(negative_y_axis_range, positive_y_axis_range)
plt.grid(False)  # Turn off grid lines
plt.imshow(background_matrix, cmap='gray', extent=[negative_x_axis_range, positive_x_axis_range, negative_y_axis_range, positive_y_axis_range])

# Define a function to extract numerical values from a string
def extract_numerical_values(data_str):
    numerical_values = re.findall(r'[-+]?\d*\.\d+|\d+', data_str)
    return [float(value) for value in numerical_values]

# Define A* algorithm functions
def is_valid(row, col):
    return 0 <= row < len(background_matrix) and 0 <= col < len(background_matrix[0])

def is_unblocked(row, col):
    return background_matrix[row][col] == 1

def calculate_h_value(row, col):
    return math.sqrt((row - final_disy) ** 2 + (col - final_disx) ** 2)

def trace_path(cell_details):
    path = []
    row, col = final_disy, final_disx

    while not (cell_details[row][col]['parent_i'] == row and cell_details[row][col]['parent_j'] == col):
        path.append((col, row))
        temp_row, temp_col = cell_details[row][col]['parent_i'], cell_details[row][col]['parent_j']
        row, col = temp_row, temp_col

    path.append((col, row))
    return path[::-1]

def a_star_search():
    if not is_valid(initial_disy, initial_disx) or not is_valid(final_disy, final_disx):
        return None

    if not is_unblocked(initial_disy, initial_disx) or not is_unblocked(final_disy, final_disx):
        return None

    closed_list = [[False for _ in range(len(background_matrix[0]))] for _ in range(len(background_matrix))]
    cell_details = [[{'f': float('inf'), 'g': float('inf'), 'h': 0, 'parent_i': -1, 'parent_j': -1} for _ in range(len(background_matrix[0]))] for _ in range(len(background_matrix))]

    i, j = initial_disy, initial_disx
    cell_details[i][j]['f'] = 0
    cell_details[i][j]['g'] = 0
    cell_details[i][j]['h'] = 0
    cell_details[i][j]['parent_i'] = i
    cell_details[i][j]['parent_j'] = j

    open_list = []
    open_list.append((0.0, i, j))

    while open_list:
        p = open_list.pop(0)

        i, j = p[1], p[2]
        closed_list[i][j] = True

        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dir in directions:
            new_i, new_j = i + dir[0], j + dir[1]

            if is_valid(new_i, new_j) and is_unblocked(new_i, new_j) and not closed_list[new_i][new_j]:
                if new_i == final_disy and new_j == final_disx:
                    cell_details[new_i][new_j]['parent_i'] = i
                    cell_details[new_i][new_j]['parent_j'] = j
                    return trace_path(cell_details)

                g_new = cell_details[i][j]['g'] + 1.0
                h_new = calculate_h_value(new_i, new_j)
                f_new = g_new + h_new

                if cell_details[new_i][new_j]['f'] == float('inf') or cell_details[new_i][new_j]['f'] > f_new:
                    open_list.append((f_new, new_i, new_j))
                    cell_details[new_i][new_j]['f'] = f_new
                    cell_details[new_i][new_j]['g'] = g_new
                    cell_details[new_i][new_j]['h'] = h_new
                    cell_details[new_i][new_j]['parent_i'] = i
                    cell_details[new_i][new_j]['parent_j'] = j

    return None

# Plot initial A* path before waiting for accelerometer data
path = a_star_search()
if path:
    path_x, path_y = zip(*path)
    plt.plot(path_x, path_y, 'g--')
    plt.draw()
    plt.pause(0.1)

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

# Initialize plot line object
line, = plt.plot([], [], 'r-', linewidth=1)

# Initialize a variable to store the quiver plot object
quiver_plot = None

# Define a function to calculate the angle between two vectors
def calculate_angle(vector1, vector2):
    cross_product = vector1[0] * vector2[1] - vector1[1] * vector2[0]
    dot_product = vector1[0] * vector2[0] + vector1[1] * vector2[1]
    magnitude1 = math.sqrt(vector1[0] ** 2 + vector1[1] ** 2)
    magnitude2 = math.sqrt(vector2[0] ** 2 + vector2[1] ** 2)
    angle_rad = math.atan2(cross_product, dot_product)
    angle_deg = math.degrees(angle_rad)
    
    # Adjust angle to be within -180 to +180 range
    angle_deg = (angle_deg + 180) % 360 - 180
    
    return angle_deg

try:
    while True:
        # Wait for a connection
        print('Waiting for a connection...')
        connection, client_address = server_socket.accept()

        try:
            print('Connection from', client_address)

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
                        # Extract angle value
                        angle = int(values[3])
                        # Calculate orientation vector components
                        vector_x = math.sin(math.radians(angle + angle_calibration))
                        vector_y = -math.cos(math.radians(angle + angle_calibration))

                        # Clear previous quiver plot if exists
                        if quiver_plot:
                            quiver_plot.remove()

                        # Update plot with orientation vector
                        quiver_plot = plt.quiver(initial_disx, initial_disy, vector_x, vector_y, scale=1, scale_units='xy', angles='xy', color='blue')
                        plt.draw()
                        plt.pause(0.1)  # Pause to update the plot

                        # Extract acceleration values
                        accel_x, accel_y, accel_z = values[:3]

                        # Calculate magnitude of acceleration vector
                        accel_magnitude = math.sqrt(accel_x ** 2 + accel_y ** 2 + accel_z ** 2)

                        # Print angle between orientation vector and recommended path
                        orientation_vector = [vector_x, vector_y]  # Update with your actual orientation vector
                        recommended_path_vector = [(path_x[1] - path_x[0]), (path_y[1] - path_y[0])]  # Update with the first segment of your A* path

                        # Calculate the angle between the vectors
                        angle_between = calculate_angle(orientation_vector, recommended_path_vector)
                        #print(f"Angle between orientation vector and recommended path: {angle_between} degrees")

                        if 30<angle_between<175 :
                            print("turn Right")
                            
                        elif -175<angle_between<-30:
                            print("Turn Left")
                           


                

                        # Check for step detection
                        if accel_magnitude > threshold_acceleration:
                            # Extract angle value and calculate new coordinates
                            final_angle = (round((angle + angle_calibration) / 90)) * 90
                            disx = initial_disx + step_distance * round(math.sin(math.radians(final_angle)))
                            disy = initial_disy - step_distance * round(math.cos(math.radians(final_angle)))

                            # Update initial_disx and initial_disy
                            initial_disx = disx
                            initial_disy = disy

                            # Print "Step detected"
                            print("Step detected")
                            

                            # Clear previous path
                            plt.clf()

                            # Append new coordinates to the lists
                            disx_list.append(disx)
                            disy_list.append(disy)

                            # Call A* algorithm to find path
                            path = a_star_search()

                            # Update plot line with the new coordinates
                            line.set_xdata(disx_list)
                            line.set_ydata(disy_list)

                            # Plot the background and new path
                            plt.imshow(background_matrix, cmap='gray', extent=[negative_x_axis_range, positive_x_axis_range, negative_y_axis_range, positive_y_axis_range])
                            
                            # Plot the path if found
                            if path:
                                path_x, path_y = zip(*path)
                                plt.plot(path_x, path_y, 'g--')

                            plt.draw()
                            plt.pause(0.1)  # Pause to update the plot

                else:
                    print('No more data from', client_address)
                    break

        finally:
            # Clean up the connection
            connection.close()

except KeyboardInterrupt:
    server_socket.close()
    plt.close()  # Close the plot window
