import socket
import pickle
import io
import sys
import settings as s
import numpy as np

# Helper function to ensure all bytes are received
def recv_all(connection, data_length):
    data = bytearray()
    while len(data) < data_length:
        packet = connection.recv(data_length - len(data))
        if not packet:
            raise ConnectionError("Connection closed prematurely")
        data.extend(packet)
    return bytes(data) # converts bytearray back to bytes


def send_data_to_socket(data_to_send):
    # Create an in-memory bytes buffer and pickle the data
    memory_buffer = io.BytesIO()
    pickle.dump(data_to_send, memory_buffer)

    # Reset buffer to the beginning
    memory_buffer.seek(0)

    # Convert memory buffer to bytes for sending
    pickled_data = memory_buffer.read()

    # Create a socket
    client_socket = socket.socket(socket.AF_INET , socket.SOCK_STREAM)

    # Connect to the server (running on localhost, port 5000)
    client_socket.connect(('localhost' , s.server_port))

    # Send the length of the pickled data first (for the server to know how much to expect)
    client_socket.sendall(len(pickled_data).to_bytes(4 , 'big'))

    # Send the actual pickled data
    client_socket.sendall(pickled_data)

    # Wait for the length of the incoming pickled data from the server
    pickled_data_length = int.from_bytes(client_socket.recv(4) , 'big')

    # Receive the pickled data from the server
    pickled_data = recv_all(client_socket , pickled_data_length)

    # Create a memory buffer and load the pickled data from the server
    response_buffer = io.BytesIO(pickled_data)
    response_buffer.seek(0)

    # Unpickle the response data
    response_data = pickle.load(response_buffer)
    # Close the connection
    client_socket.close()

    status = response_data['status']
    if status != s.OK:
        print("Error: ", response_data['error'])
        sys.exit()

    data = response_data['data']
    return data