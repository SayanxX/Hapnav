import socket
import math

def calculate_heading(mag_x, mag_y):
    """
    Calculate the heading of the device from magnetometer data.
    """
    heading_rad = math.atan2(mag_y, mag_x)
    heading_deg = math.degrees(heading_rad)
    if heading_deg < 0:
        heading_deg += 360
    return heading_deg

# Create a TCP/IP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('0.0.0.0', 2055)
print('Starting up on {} port {}'.format(*server_address))
server_socket.bind(server_address)

# Listen for incoming connections
server_socket.listen(1)

while True:
    # Wait for a connection
    print('Waiting for a connection...')
    connection, client_address = server_socket.accept()

    try:
        print('Connection from', client_address)

        # Receive the data in small chunks and calculate heading
        while True:
            data = connection.recv(16)
            if data:
                # Assume the data is a string formatted as "x_value,y_value"
                data_str = data.decode('utf-8')
                x_str, y_str = data_str.split(',')
                mag_x = float(x_str)
                mag_y = float(y_str)

                heading = calculate_heading(mag_x, mag_y)
                print(f"Received magnetometer data: X={mag_x}, Y={mag_y}. Heading: {heading:.2f} degrees")
            else:
                print('No more data from', client_address)
                break
            
    finally:
        # Clean up the connection
        connection.close()