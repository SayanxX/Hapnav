import socket
import math

def extract_numerical_values(data_str):
    """
    Extract numerical values from a string and return them as a tuple.
    Ignore non-numeric characters.
    """
    values = []
    for token in data_str.split(','):
        try:
            value = float(token)
            values.append(value)
        except ValueError:
            pass  # Ignore non-numeric tokens
    return tuple(values)

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
server_address = ('192.168.144.64', 2055)  # Update with your server IP and port
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
                # Assume the data is a string with numerical values separated by commas
                data_str = data.decode('utf-8')
                
                # Extract numerical values from the data string
                values = extract_numerical_values(data_str)
                if len(values) == 2:
                    mag_x, mag_y = values
                    heading = calculate_heading(mag_x, mag_y)
                    print(f"Received magnetometer data: X={mag_x}, Y={mag_y}. Heading: {heading:.2f} degrees")
                else:
                    # Skip printing invalid data
                    pass
            else:
                print('No more data from', client_address)
                break
            
    finally:
        # Clean up the connection
        connection.close()
